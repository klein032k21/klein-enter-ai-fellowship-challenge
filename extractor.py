import os
import json
import re
import unicodedata
from openai import OpenAI
import fitz  # PyMuPDF
from cache_manager import CacheManager
from pattern_matcher import PatternMatcher
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class PDFExtractor:
    """
    Motor de extração de dados de PDFs usando gpt-5-mini com cache inteligente.
    ESTRATÉGIA: Minimiza custos e maximiza acurácia.
    """
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")
        self.client = OpenAI(api_key=api_key)
        self.cache = CacheManager()
        self.pattern_matcher = PatternMatcher()  # Extração local
        self.model = "gpt-5-mini"  # Modelo especificado no desafio

    def clean_text(self, text):
        """
        Limpa e otimiza o texto extraído do PDF.
        ESTRATÉGIA: Reduzir tokens sem perder informação relevante.
        """
        # Normaliza Unicode (corrige caracteres especiais)
        text = unicodedata.normalize('NFKC', text)

        # Remove caracteres de controle (exceto \n e \t)
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # Normaliza espaços em branco (múltiplos espaços -> um espaço)
        text = re.sub(r'[ \t]+', ' ', text)

        # Remove linhas vazias excessivas (max 2 linhas vazias consecutivas)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove espaços no início e fim de cada linha
        text = '\n'.join(line.strip() for line in text.split('\n'))

        return text.strip()
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extrai texto do PDF usando PyMuPDF (fitz).
        ESTRATÉGIA: Extração local (custo ZERO) com performance 35x superior.
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            # Limpa e otimiza o texto extraído
            text = self.clean_text(text)

            return text
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")

    def extract_from_base64(self, pdf_base64, label, extraction_schema, max_retries=2, use_cache=True):
        """
        Extrai dados de PDF codificado em Base64.
        ESTRATÉGIA: Decodifica → Salva temp → Extrai → Remove temp

        Args:
            pdf_base64: PDF codificado em Base64
            label: Label do documento
            extraction_schema: Schema de extração
            max_retries: Número máximo de tentativas
            use_cache: Se deve usar cache

        Returns:
            dict: Resultado da extração
        """
        import base64
        import tempfile

        try:
            # Decodificar Base64
            pdf_bytes = base64.b64decode(pdf_base64)

            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_bytes)
                temp_path = temp_file.name

            try:
                # Extrair dados do PDF temporário
                result = self.extract(temp_path, label, extraction_schema, max_retries, use_cache)
                return result
            finally:
                # Remover arquivo temporário
                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar PDF Base64: {str(e)}"
            }
    
    def build_system_message(self, label, extraction_schema, use_examples=False, context=None):
        """
        Constrói mensagem de system OTIMIZADA: compacta + precisa.
        ESTRATÉGIA: Reduzir tokens mantendo instruções críticas para acurácia.
        """
        system_msg = f"Extrator de dados '{label}'. Retorne apenas JSON válido.\n\n"
        system_msg += "REGRAS:\n"
        system_msg += "1. Campo inexistente = null\n"
        system_msg += "2. Mantenha formatação original\n"
        system_msg += "3. 'seccional' = sigla (PR, SP), 'subsecao' = nome completo\n"
        system_msg += "4. CEP: 8 dígitos, telefone: 10-11 dígitos\n\n"

        system_msg += "CAMPOS:\n"
        for field_name, field_description in extraction_schema.items():
            system_msg += f'"{field_name}": {field_description}\n'

        # Dica estrutural condensada para OAB
        if label == "carteira_oab":
            system_msg += "\nESTRUTURA OAB: Nome | Labels | Inscrição(5-6 dig) | Seccional(2 letras) | Subseção(texto completo) | Categoria\n"

        # Exemplo compacto se disponível
        if use_examples and context and context.get('examples'):
            example = context['examples'][0]
            example_json = json.dumps(example['extracted'], ensure_ascii=False)
            system_msg += f"\nEXEMPLO:\n{example_json}\n"

        return system_msg

    def build_user_message(self, pdf_text, extraction_schema, local_extracted=None, all_dates=None):
        """
        Constrói mensagem de user OTIMIZADA.
        FASE 2 (conservador): Apenas informar datas múltiplas, sem pattern matching.
        """
        msg = f"DOCUMENTO:\n{pdf_text}\n\n"

        # Se há múltiplas datas, listar todas para ajudar o LLM
        if all_dates and len(all_dates) > 1:
            msg += f"INFO: Há {len(all_dates)} datas no documento: {', '.join(all_dates)}\n"
            msg += "Para campos de data/vencimento, escolha a CORRETA baseado no contexto e descrição do campo.\n\n"

        msg += "RESPOSTA (JSON compacto):"
        return msg
    
    def extract(self, pdf_path, label, extraction_schema, max_retries=2, use_cache=True):
        """
        Método principal de extração com retry logic e cache inteligente.
        ESTRATÉGIA: Cache → Extração local → LLM otimizado → Retry se falhar
        """

        # 0. Verificar cache de resultados (velocidade máxima)
        if use_cache:
            import time
            cache_start = time.time()
            cached_result = self.cache.get_cached_result(pdf_path, label, extraction_schema)
            if cached_result:
                cache_time = time.time() - cache_start
                print(f"         [CACHE HIT] Resultado cacheado retornado em {cache_time:.3f}s")
                # Adicionar flag indicando que veio do cache
                cached_result['from_cache'] = True
                cached_result['cache_retrieval_time'] = cache_time
                return cached_result

        # 1. Extrair texto do PDF (custo zero)
        pdf_text = self.extract_text_from_pdf(pdf_path)

        if not pdf_text:
            raise Exception("PDF vazio ou sem texto extraível")

        # FASE 4A: Truncar texto para reduzir prompt tokens e reasoning time
        if len(pdf_text) > 2000:
            pdf_text = pdf_text[:2000]
            print(f"         [TRUNCATE] Texto reduzido para 2000 chars")

        # 2. Pattern matching DESABILITADO (estava causando mais confusão que ajuda)
        # FASE 2 ROLLBACK: pattern matching agressivo piorou acurácia de 94.59% → 83.78%
        local_extracted = {}
        confidence = 0.0
        all_dates = []

        # Manter apenas extração de datas múltiplas (info adicional para LLM)
        all_dates = self.pattern_matcher.extract_all_dates(pdf_text)
        if all_dates and len(all_dates) > 1:
            print(f"         [DATAS] {len(all_dates)} data(s) encontrada(s): {all_dates}")

        # FASE 4A: Template matching DESABILITADO (não funciona, adiciona overhead)
        # # 2.5 FASE 3: Buscar template similar (documento repetido)
        # template_match = self.cache.find_similar_template(pdf_text, label, extraction_schema)
        # if template_match and use_cache:
        #     similarity = template_match['similarity']
        #     print(f"         [TEMPLATE] Documento similar encontrado ({int(similarity*100)}% match)")
        #     print(f"         [TEMPLATE] Reusando estrutura, LLM NÃO chamado")
        #
        #     # Reusar resultado do template (assumindo valores idênticos para docs idênticos)
        #     # Em produção, poderia extrair apenas campos variáveis
        #     template_result = template_match['template']
        #
        #     # Retornar resultado do template
        #     return {
        #         "success": True,
        #         "data": template_result['data'],
        #         "label": label,
        #         "cost": 0.0,  # Cache = custo zero
        #         "tokens": {
        #             "input": 0,
        #             "output": 0,
        #             "total": 0
        #         },
        #         "from_cache": True,
        #         "from_template": True,
        #         "template_similarity": similarity
        #     }

        # 3. Atualizar schema conhecido ANTES de buscar contexto
        self.cache.update_schema(label, extraction_schema)

        # 4. Buscar contexto do cache para few-shot learning com semantic search
        # IMPORTANTE: Busca DEPOIS de atualizar schema para pegar exemplos mais recentes
        context = self.cache.get_context(label, extraction_schema, pdf_text)
        has_examples = context and len(context.get('examples', [])) > 0

        if has_examples:
            print(f"         [FEW-SHOT] Usando {len(context['examples'])} exemplo(s) similar(es)")

        # 5. Tentar extração com retry
        for attempt in range(max_retries):
            try:
                # 6. Construir mensagens OTIMIZADAS (system cacheable + user conciso)
                system_message = self.build_system_message(
                    label, extraction_schema,
                    use_examples=has_examples,
                    context=context
                )

                user_message = self.build_user_message(
                    pdf_text, extraction_schema,
                    local_extracted=None,  # FASE 2 conservador: sem pattern matching
                    all_dates=all_dates if len(all_dates) > 1 else None
                )

                # 7. Chamar LLM (formato simples e otimizado)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_message
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    # FASE 4A: 2500 tokens (mais confortável para reasoning)
                    # Reasoning tokens variável (~800-1200) + JSON compacto (~200-300)
                    # Aumentado de 1500 para reduzir tempo de reasoning
                    max_completion_tokens=2500
                )

                # 7. Calcular custo (pricing oficial gpt-5-mini)
                usage = response.usage
                input_cost = (usage.prompt_tokens / 1_000_000) * 0.25
                output_cost = (usage.completion_tokens / 1_000_000) * 2.00
                total_cost = input_cost + output_cost

                # 8. Parsear resposta
                result_text = response.choices[0].message.content

                # DEBUG: Verificar se conteúdo existe
                if not result_text or result_text.strip() == "":
                    raise ValueError(f"LLM retornou resposta vazia. Response object: {response}")

                result_text = result_text.strip()

                # Remove markdown se houver
                if result_text.startswith("```json"):
                    result_text = result_text.replace("```json", "").replace("```", "").strip()
                elif result_text.startswith("```"):
                    result_text = result_text.replace("```", "").strip()

                extracted_data = json.loads(result_text)

                # 9. Validar schema da resposta e MERGE com dados locais
                validated_data = {}
                for field_name in extraction_schema.keys():
                    # Prioridade: dados locais (mais precisos) > dados LLM
                    if local_extracted.get(field_name) is not None:
                        validated_data[field_name] = local_extracted[field_name]
                    else:
                        validated_data[field_name] = extracted_data.get(field_name, None)

                # 10. Salvar no cache para aprendizado (few-shot futuro)
                self.cache.add_example(label, pdf_text, validated_data)

                # 11. Preparar resultado
                result = {
                    "success": True,
                    "data": validated_data,
                    "label": label,
                    "cost": total_cost,
                    "tokens": {
                        "input": usage.prompt_tokens,
                        "output": usage.completion_tokens,
                        "total": usage.total_tokens
                    },
                    "from_cache": False,
                    "used_examples": has_examples  # Indica se usou few-shot
                }

                # 12. Salvar resultado no cache para futuras consultas
                # FASE 4A: Salvar SEM texto (template matching desabilitado)
                if use_cache:
                    # self.cache.save_result_with_text(pdf_path, pdf_text, label, extraction_schema, result)
                    pass  # Cache de resultado já gerenciado por get_cached_result

                return result

            except json.JSONDecodeError as e:
                # Se JSON inválido e ainda há tentativas, retry
                if attempt < max_retries - 1:
                    continue
                # DEBUG: Mostrar resposta completa
                return {
                    "success": False,
                    "error": f"Erro ao parsear JSON após {max_retries} tentativas: {str(e)}",
                    "raw_response": result_text,
                    "response_length": len(result_text),
                    "response_preview": result_text[:200] if result_text else "VAZIO"
                }
            except Exception as e:
                # Se erro genérico e ainda há tentativas, retry
                if attempt < max_retries - 1:
                    continue
                return {
                    "success": False,
                    "error": f"Erro na extração após {max_retries} tentativas: {str(e)}"
                }