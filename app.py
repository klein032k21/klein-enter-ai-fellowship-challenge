# -*- coding: utf-8 -*-
"""
API Flask para extração de dados de PDFs.
Responde com APENAS os dados extraídos no body.
Metadados (custo, tokens, tempo) vão nos headers HTTP.
"""
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from extractor import PDFExtractor
import json
import time
import os

app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app)  # Habilita CORS para uso em frontend

# Inicializar extrator (singleton)
extractor = PDFExtractor()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


@app.route('/extract', methods=['POST'])
def extract():
    """
    Endpoint principal de extração (síncrono).

    Input JSON:
    {
        "label": "carteira_oab",
        "extraction_schema": {
            "nome": "Nome do profissional",
            "inscricao": "Número de inscrição"
        },
        "pdf": "base64_encoded_pdf_content"
    }

    Output JSON (sucesso):
    {
        "nome": "SON GOKU",
        "inscricao": "101943",
        ...
    }

    Headers (metadados):
    - X-Extraction-Cost-USD: 0.002499
    - X-Extraction-Tokens-Input: 450
    - X-Extraction-Tokens-Output: 120
    - X-Extraction-Tokens-Total: 570
    - X-Extraction-From-Cache: false
    - X-Extraction-Used-Examples: true

    Output JSON (erro):
    {
        "error": "Mensagem de erro"
    }
    """
    try:
        # Validar Content-Type
        if not request.is_json:
            return jsonify({"error": "Content-Type deve ser application/json"}), 400

        data = request.get_json()

        # Validar campos obrigatórios
        if not data:
            return jsonify({"error": "Corpo da requisição vazio"}), 400

        required_fields = ['label', 'extraction_schema', 'pdf']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório ausente: {field}"}), 400

        label = data['label']
        extraction_schema = data['extraction_schema']
        pdf_base64 = data['pdf']

        # Validar tipos
        if not isinstance(label, str) or not label.strip():
            return jsonify({"error": "label deve ser uma string não vazia"}), 400

        if not isinstance(extraction_schema, dict) or len(extraction_schema) == 0:
            return jsonify({"error": "extraction_schema deve ser um objeto não vazio"}), 400

        if not isinstance(pdf_base64, str) or not pdf_base64.strip():
            return jsonify({"error": "pdf deve ser uma string Base64 não vazia"}), 400

        # Executar extração
        start_time = time.time()
        result = extractor.extract_from_base64(
            pdf_base64=pdf_base64,
            label=label,
            extraction_schema=extraction_schema
        )
        elapsed_time = time.time() - start_time

        # Verificar sucesso
        if not result.get('success', False):
            error_message = result.get('error', 'Erro desconhecido na extração')
            return jsonify({"error": error_message}), 500

        # Preparar resposta
        extracted_data = result.get('data', {})

        # Preparar headers com metadados
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Extraction-Cost-USD': str(result.get('cost', 0.0)),
            'X-Extraction-Time-Seconds': str(round(elapsed_time, 3)),
            'X-Extraction-From-Cache': str(result.get('from_cache', False)).lower(),
            'X-Extraction-Used-Examples': str(result.get('used_examples', False)).lower()
        }

        # Adicionar metadados de tokens (se disponíveis)
        tokens = result.get('tokens', {})
        if tokens:
            headers['X-Extraction-Tokens-Input'] = str(tokens.get('input', 0))
            headers['X-Extraction-Tokens-Output'] = str(tokens.get('output', 0))
            headers['X-Extraction-Tokens-Total'] = str(tokens.get('total', 0))

        # Retornar APENAS os dados extraídos no body
        response = jsonify(extracted_data)
        for key, value in headers.items():
            response.headers[key] = value

        return response, 200

    except Exception as e:
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500


@app.route('/extract/stream', methods=['POST'])
def extract_stream():
    """
    Endpoint de extração com streaming SSE (Server-Sent Events).
    Retorna eventos de progresso e resultado final.

    Input: Mesmo formato do /extract

    Output (SSE events):
    - event: status, data: {"status": "processing"}
    - event: status, data: {"status": "completed"}
    - event: metadata, data: {"cost": 0.002, "tokens": {...}}
    - event: result, data: {dados extraídos}
    - event: error, data: {"error": "mensagem"}
    """
    # Validar entrada ANTES do generator (dentro do contexto da requisição)
    try:
        if not request.is_json:
            return Response(
                f"event: error\ndata: {json.dumps({'error': 'Content-Type deve ser application/json'}, ensure_ascii=False)}\n\n",
                mimetype='text/event-stream'
            )

        data = request.get_json()

        if not data:
            return Response(
                f"event: error\ndata: {json.dumps({'error': 'Corpo vazio'}, ensure_ascii=False)}\n\n",
                mimetype='text/event-stream'
            )

        required_fields = ['label', 'extraction_schema', 'pdf']
        for field in required_fields:
            if field not in data:
                return Response(
                    f"event: error\ndata: {json.dumps({'error': f'Campo ausente: {field}'}, ensure_ascii=False)}\n\n",
                    mimetype='text/event-stream'
                )

        label = data['label']
        extraction_schema = data['extraction_schema']
        pdf_base64 = data['pdf']
    except Exception as e:
        return Response(
            f"event: error\ndata: {json.dumps({'error': f'Erro ao validar requisição: {str(e)}'}, ensure_ascii=False)}\n\n",
            mimetype='text/event-stream'
        )

    # Generator agora recebe os dados já validados
    def generate(label, extraction_schema, pdf_base64):
        try:

            # Enviar status: processando
            yield f"event: status\ndata: {json.dumps({'status': 'processing'}, ensure_ascii=False)}\n\n"

            # Executar extração
            start_time = time.time()
            result = extractor.extract_from_base64(
                pdf_base64=pdf_base64,
                label=label,
                extraction_schema=extraction_schema
            )
            elapsed_time = time.time() - start_time

            # Verificar sucesso
            if not result.get('success', False):
                error_message = result.get('error', 'Erro desconhecido')
                yield f"event: error\ndata: {json.dumps({'error': error_message}, ensure_ascii=False)}\n\n"
                return

            # Enviar status: completo
            yield f"event: status\ndata: {json.dumps({'status': 'completed'}, ensure_ascii=False)}\n\n"

            # Enviar metadados
            metadata = {
                'cost_usd': result.get('cost', 0.0),
                'time_seconds': round(elapsed_time, 3),
                'from_cache': result.get('from_cache', False),
                'used_examples': result.get('used_examples', False),
                'tokens': result.get('tokens', {})
            }
            yield f"event: metadata\ndata: {json.dumps(metadata, ensure_ascii=False)}\n\n"

            # Enviar resultado (APENAS dados extraídos)
            extracted_data = result.get('data', {})
            yield f"event: result\ndata: {json.dumps(extracted_data, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return Response(
        generate(label, extraction_schema, pdf_base64),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Content-Type': 'text/event-stream; charset=utf-8'
        }
    )


@app.route('/')
def serve_frontend():
    """Serve o frontend React"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve arquivos estáticos do frontend (JS, CSS, imagens)"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Se o arquivo não existe, retorna index.html para suportar React Router
        return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(404)
def not_found(error):
    # Se for uma requisição para API, retorna JSON
    if request.path.startswith('/api/') or request.path.startswith('/extract') or request.path.startswith('/health'):
        return jsonify({"error": "Endpoint não encontrado"}), 404
    # Caso contrário, retorna o frontend
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Método HTTP não permitido"}), 405


if __name__ == '__main__':
    # Configuração para desenvolvimento
    print("=" * 80)
    print("  PDF EXTRACTOR API - ENTER AI FELLOWSHIP")
    print("=" * 80)
    print("\nEndpoints disponiveis:")
    print("  - GET  /health           - Health check")
    print("  - POST /extract          - Extracao sincrona")
    print("  - POST /extract/stream   - Extracao com SSE streaming")
    print("\nServidor iniciando em http://0.0.0.0:5000")
    print("=" * 80 + "\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Desabilitado para produção
        threaded=True
    )
