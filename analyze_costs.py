# -*- coding: utf-8 -*-
"""
Script para analisar custos e performance do sistema de extracao.
Calcula tamanho real de prompts, tokens e custos.
"""
import json
from extractor import PDFExtractor

def analyze_extraction_cost():
    """Analisa custo de uma extracao real"""

    print("=" * 80)
    print("ANALISE DE CUSTOS E PERFORMANCE - PDF Extractor")
    print("=" * 80)

    # Configuracao de teste (oab_1.pdf)
    test_config = {
        "label": "carteira_oab",
        "extraction_schema": {
            "nome": "Nome do profissional, normalmente no canto superior esquerdo da imagem",
            "inscricao": "Numero de inscricao do profissional",
            "seccional": "Seccional do profissional",
            "subsecao": "Subsecao a qual o profissional faz parte",
            "categoria": "Categoria, pode ser ADVOGADO, ADVOGADA, SUPLEMENTAR, ESTAGIARIO, ESTAGIARIA",
            "endereco_profissional": "Endereco do profissional",
            "telefone_profissional": "Telefone do profissional",
            "situacao": "Situacao do profissional, normalmente no canto inferior direito."
        },
        "pdf_path": "data/files/oab_1.pdf"
    }

    # Inicializar extrator
    extractor = PDFExtractor()

    print(f"\n[1] Extraindo texto do PDF...")
    pdf_text = extractor.extract_text_from_pdf(test_config['pdf_path'])
    print(f"    Texto extraido: {len(pdf_text)} caracteres")

    # Buscar contexto do cache
    print(f"\n[2] Buscando contexto do cache...")
    context = extractor.cache.get_context(test_config['label'], test_config['extraction_schema'])
    print(f"    Exemplos no cache: {len(context['examples'])}")

    # Construir prompt completo
    print(f"\n[3] Construindo prompt...")
    prompt = extractor.build_optimized_prompt(
        pdf_text,
        test_config['label'],
        test_config['extraction_schema'],
        context
    )

    print(f"    Tamanho do prompt: {len(prompt)} caracteres")

    # Estimativa de tokens (regra conservadora: 4 chars = 1 token em portugues)
    estimated_input_tokens = len(prompt) // 4
    estimated_output_tokens = 200  # JSON com 8 campos
    total_tokens = estimated_input_tokens + estimated_output_tokens

    print(f"\n[4] Estimativa de tokens:")
    print(f"    Input tokens: ~{estimated_input_tokens}")
    print(f"    Output tokens (estimado): ~{estimated_output_tokens}")
    print(f"    Total: ~{total_tokens} tokens")

    # Pricing do gpt-5-mini (valores precisam ser confirmados)
    print(f"\n[5] Pricing gpt-5-mini:")
    print(f"    IMPORTANTE: Precisa confirmar pricing oficial!")
    print(f"    Assumindo (exemplo): $0.10/1M input tokens, $0.30/1M output tokens")

    input_cost_per_million = 0.10
    output_cost_per_million = 0.30

    cost_input = (estimated_input_tokens / 1_000_000) * input_cost_per_million
    cost_output = (estimated_output_tokens / 1_000_000) * output_cost_per_million
    total_cost = cost_input + cost_output

    print(f"\n[6] Custo estimado por documento:")
    print(f"    Input: ${cost_input:.6f}")
    print(f"    Output: ${cost_output:.6f}")
    print(f"    Total: ${total_cost:.6f}")
    print(f"    Total (em centavos): {total_cost * 100:.4f} centavos")

    # Custo para 1000 documentos
    cost_1k = total_cost * 1000
    print(f"\n[7] Projecao de custos:")
    print(f"    1.000 documentos: ${cost_1k:.2f}")
    print(f"    10.000 documentos: ${cost_1k * 10:.2f}")

    # Analise do prompt
    print(f"\n[8] Analise detalhada do prompt:")
    print(f"    Primeira linha: {prompt[:100]}...")
    print(f"    Ultima linha: ...{prompt[-100:]}")

    # Salvar prompt completo para inspecao
    with open('prompt_sample.txt', 'w', encoding='utf-8') as f:
        f.write(prompt)
    print(f"\n[INFO] Prompt completo salvo em: prompt_sample.txt")

    print("\n" + "=" * 80)
    print("RECOMENDACOES:")
    print("=" * 80)

    # Recomendacoes baseadas no tamanho
    if len(prompt) > 8000:
        print("  [ATENCAO] Prompt muito grande (>8000 chars)")
        print("  Sugestao: Reduzir exemplos do cache ou limitar texto do PDF")

    if estimated_input_tokens > 2000:
        print("  [ATENCAO] Input tokens alto (>2000)")
        print("  Sugestao: Remover exemplos ou comprimir texto")

    print("\n")

if __name__ == "__main__":
    analyze_extraction_cost()
