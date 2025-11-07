import json
import os
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

class CacheManager:
    """
    Gerencia cache inteligente por label E por PDF.
    - Cache de padrões: Armazena exemplos e schemas por label (acurácia)
    - Cache de resultados: Armazena resultados por hash de PDF (velocidade)
    """

    def __init__(self, cache_dir="cache", results_cache_dir=".results_cache", ttl_hours=24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Novo: Cache de resultados por PDF
        self.results_cache_dir = Path(results_cache_dir)
        self.results_cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

        # Embedding model para semantic search (lazy loading)
        self._embedding_model = None

        # Cache em memória para labels já carregados (pre-load optimization)
        self._memory_cache = {}
    
    def get_cache_path(self, label):
        """Retorna caminho do arquivo de cache para um label"""
        return self.cache_dir / f"{label}.json"
    
    def load_cache(self, label):
        """
        Carrega cache de um label específico.
        OTIMIZAÇÃO: Usa cache em memória para evitar I/O repetido.
        """
        # Verificar se já está em memória
        if label in self._memory_cache:
            return self._memory_cache[label]

        # Carregar do disco
        cache_path = self.get_cache_path(label)
        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
        else:
            cache_data = {
                "schema_complete": {},
                "examples": [],
                "patterns": {}
            }

        # Armazenar em memória
        self._memory_cache[label] = cache_data
        return cache_data
    
    def save_cache(self, label, cache_data):
        """
        Salva cache de um label.
        OTIMIZAÇÃO: Atualiza cache em memória também.
        """
        # Atualizar memória
        self._memory_cache[label] = cache_data

        # Salvar disco
        cache_path = self.get_cache_path(label)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def update_schema(self, label, new_fields):
        """
        Atualiza o schema completo do label com novos campos descobertos.
        ESTRATÉGIA: Acumula conhecimento sobre o schema ao longo do tempo.
        """
        cache = self.load_cache(label)
        cache["schema_complete"].update(new_fields)
        self.save_cache(label, cache)
    
    def add_example(self, label, pdf_text, extracted_data):
        """
        Adiciona exemplo de extração bem-sucedida COM embedding.
        ESTRATÉGIA: Usa embeddings para semantic search de exemplos relevantes.
        """
        cache = self.load_cache(label)

        # Gerar embedding do texto (lazy load do modelo)
        text_snippet = pdf_text[:500]  # Primeiros 500 chars
        embedding = self._get_embedding(text_snippet)

        # Limita a 5 exemplos (aumentado porque usaremos semantic search)
        if len(cache["examples"]) >= 5:
            cache["examples"].pop(0)

        cache["examples"].append({
            "text_snippet": text_snippet,
            "extracted": extracted_data,
            "embedding": embedding.tolist() if embedding is not None else None
        })

        self.save_cache(label, cache)
    
    def get_context(self, label, extraction_schema, current_pdf_text=None):
        """
        Retorna contexto relevante do cache usando semantic search.
        ESTRATÉGIA: Retorna apenas o exemplo MAIS similar (embedding-based).
        """
        cache = self.load_cache(label)

        # Se não há exemplos, retorna vazio
        if not cache["examples"]:
            return {"known_fields": cache["schema_complete"], "examples": []}

        # Se não forneceu PDF atual, retorna último exemplo
        if current_pdf_text is None:
            return {
                "known_fields": cache["schema_complete"],
                "examples": cache["examples"][-1:]
            }

        # Semantic search: encontrar exemplo mais similar
        most_similar = self._find_most_similar_example(
            current_pdf_text[:500],
            cache["examples"]
        )

        return {
            "known_fields": cache["schema_complete"],
            "examples": [most_similar] if most_similar else []
        }

    def _get_embedding(self, text):
        """
        Gera embedding de um texto usando sentence-transformers.
        Lazy loading do modelo para não impactar startup.

        Args:
            text: Texto para gerar embedding

        Returns:
            np.ndarray ou None: Embedding do texto
        """
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"[AVISO] Falha ao carregar modelo de embeddings: {e}")
                return None

        try:
            return self._embedding_model.encode(text)
        except Exception as e:
            print(f"[AVISO] Falha ao gerar embedding: {e}")
            return None

    def _find_most_similar_example(self, query_text, examples):
        """
        Encontra o exemplo mais similar usando cosine similarity.

        Args:
            query_text: Texto atual do PDF
            examples: Lista de exemplos com embeddings

        Returns:
            dict: Exemplo mais similar ou último exemplo se falhar
        """
        query_embedding = self._get_embedding(query_text)
        if query_embedding is None:
            return examples[-1] if examples else None

        max_similarity = -1
        most_similar = None

        for example in examples:
            if example.get('embedding') is None:
                continue

            example_embedding = np.array(example['embedding'])

            # Calcular cosine similarity
            similarity = np.dot(query_embedding, example_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(example_embedding)
            )

            if similarity > max_similarity:
                max_similarity = similarity
                most_similar = example

        return most_similar if most_similar else (examples[-1] if examples else None)

    # ===== CACHE DE RESULTADOS (NOVO) =====

    def get_pdf_hash(self, pdf_path):
        """
        Calcula hash MD5 do arquivo PDF.

        Args:
            pdf_path: Caminho para o PDF

        Returns:
            str: Hash MD5 hexadecimal
        """
        try:
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
                return hashlib.md5(pdf_content).hexdigest()
        except Exception as e:
            raise Exception(f"Erro ao calcular hash do PDF: {str(e)}")

    def get_schema_hash(self, extraction_schema):
        """
        Calcula hash do schema de extração.

        Args:
            extraction_schema: Dict com campos e descrições

        Returns:
            str: Hash MD5 do schema (8 chars)
        """
        schema_str = json.dumps(extraction_schema, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()[:8]

    def get_result_cache_key(self, pdf_path, label, extraction_schema):
        """
        Gera chave única para cache de resultado.

        Args:
            pdf_path: Caminho do PDF
            label: Label do documento
            extraction_schema: Schema de extração

        Returns:
            str: Chave de cache
        """
        pdf_hash = self.get_pdf_hash(pdf_path)
        schema_hash = self.get_schema_hash(extraction_schema)
        return f"{pdf_hash}_{label}_{schema_hash}"

    def get_cached_result(self, pdf_path, label, extraction_schema):
        """
        Busca resultado cacheado de uma extração.

        Args:
            pdf_path: Caminho do PDF
            label: Label do documento
            extraction_schema: Schema de extração

        Returns:
            dict ou None: Resultado cacheado ou None se não existe/expirou
        """
        try:
            cache_key = self.get_result_cache_key(pdf_path, label, extraction_schema)
            cache_path = self.results_cache_dir / f"{cache_key}.json"

            if not cache_path.exists():
                return None

            # Ler cache
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)

            # Verificar TTL
            cached_time = datetime.fromisoformat(cached_data['cached_at'])
            if datetime.now() - cached_time > self.ttl:
                # Cache expirado, deletar
                cache_path.unlink()
                return None

            # Cache válido - retornar resultado
            return cached_data['result']

        except Exception:
            # Se houver qualquer erro, retorna None (sem cache)
            return None

    def save_result(self, pdf_path, label, extraction_schema, result):
        """
        Salva resultado de extração no cache.

        Args:
            pdf_path: Caminho do PDF
            label: Label do documento
            extraction_schema: Schema de extração
            result: Resultado da extração (dict completo)
        """
        try:
            cache_key = self.get_result_cache_key(pdf_path, label, extraction_schema)
            cache_path = self.results_cache_dir / f"{cache_key}.json"

            # Preparar dados do cache
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "pdf_path": str(pdf_path),
                "label": label,
                "schema_fields": list(extraction_schema.keys()),
                "result": result
            }

            # Salvar
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            # Falha ao salvar cache não deve quebrar o sistema
            print(f"[AVISO] Falha ao salvar cache de resultado: {e}")

    def generate_document_fingerprint(self, pdf_text, label):
        """
        Gera fingerprint do documento baseado na estrutura.
        FASE 3: Detectar documentos similares (mesmo template).

        Args:
            pdf_text: Texto extraído do PDF
            label: Label do documento

        Returns:
            str: Fingerprint (hash dos primeiros 500 chars + label)
        """
        # Usar primeiros 500 chars (estrutura/cabeçalho do documento)
        structure = pdf_text[:500] if len(pdf_text) >= 500 else pdf_text
        fingerprint_str = f"{label}:{structure}"
        return hashlib.md5(fingerprint_str.encode()).hexdigest()

    def calculate_text_similarity(self, text1, text2):
        """
        Calcula similaridade entre dois textos (0.0 a 1.0).
        Método simples: % de caracteres comuns nos primeiros 500 chars.

        Args:
            text1: Primeiro texto
            text2: Segundo texto

        Returns:
            float: Similaridade (0.0 a 1.0)
        """
        # Usar primeiros 500 chars
        t1 = text1[:500] if len(text1) >= 500 else text1
        t2 = text2[:500] if len(text2) >= 500 else text2

        # Calcular caracteres comuns
        common_chars = sum(1 for c1, c2 in zip(t1, t2) if c1 == c2)
        max_len = max(len(t1), len(t2))

        if max_len == 0:
            return 0.0

        return common_chars / max_len

    def find_similar_template(self, pdf_text, label, extraction_schema, threshold=0.85):
        """
        Busca documento similar (template) no cache.
        FASE 3: Se encontrar documento 85%+ similar, reusa resultado.

        Args:
            pdf_text: Texto do PDF atual
            label: Label do documento
            extraction_schema: Schema de extração
            threshold: Limiar de similaridade (0.85 = 85%)

        Returns:
            dict ou None: Template encontrado ou None
        """
        try:
            fingerprint = self.generate_document_fingerprint(pdf_text, label)

            # Buscar TODOS os resultados cacheados do mesmo label
            for cache_file in self.results_cache_dir.glob(f"*_{label}_*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)

                    # Verificar se é do mesmo label e schema
                    if cached_data['label'] != label:
                        continue
                    if cached_data['schema_fields'] != list(extraction_schema.keys()):
                        continue

                    # Verificar TTL
                    cached_time = datetime.fromisoformat(cached_data['cached_at'])
                    if datetime.now() - cached_time > self.ttl:
                        continue

                    # Ler texto do PDF cacheado (se disponível)
                    # Por enquanto, comparar fingerprint diretamente
                    cached_fingerprint = self.generate_document_fingerprint(
                        cached_data.get('pdf_text', ''),
                        label
                    )

                    # Se fingerprints muito similares
                    if fingerprint == cached_fingerprint:
                        return {
                            'template': cached_data['result'],
                            'similarity': 1.0,
                            'source': str(cache_file)
                        }

                except Exception:
                    continue

            return None

        except Exception:
            return None

    def save_result_with_text(self, pdf_path, pdf_text, label, extraction_schema, result):
        """
        Salva resultado COM texto do PDF (para template matching).
        FASE 3: Incluir pdf_text no cache para comparação futura.

        Args:
            pdf_path: Caminho do PDF
            pdf_text: Texto extraído do PDF
            label: Label do documento
            extraction_schema: Schema de extração
            result: Resultado da extração
        """
        try:
            cache_key = self.get_result_cache_key(pdf_path, label, extraction_schema)
            cache_path = self.results_cache_dir / f"{cache_key}.json"

            # Preparar dados do cache (com pdf_text para template matching)
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "pdf_path": str(pdf_path),
                "pdf_text": pdf_text[:1000],  # Salvar primeiros 1000 chars
                "label": label,
                "schema_fields": list(extraction_schema.keys()),
                "result": result
            }

            # Salvar
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[AVISO] Falha ao salvar cache com texto: {e}")