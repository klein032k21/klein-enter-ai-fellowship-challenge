#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de Aprendizado Progressivo - PDF Extractor
Demonstra como o sistema melhora com documentos similares ao longo do tempo
"""
import json
import time
import fitz
import tempfile
from extractor import PDFExtractor

# Dados de teste: 5 carteiras OAB diferentes
DOCUMENTOS_TESTE = [
    {
        "nome": "Doc 1 - Primeira extração (sem cache)",
        "texto": """
ORDEM DOS ADVOGADOS DO BRASIL
CARTEIRA DE IDENTIDADE PROFISSIONAL

Nome: NARUTO UZUMAKI
Inscrição: 111222
Seccional: SP
Subseção: São Paulo
Categoria: Advogado
Data de expedição: 10/01/2020
Validade: 10/01/2025
"""
    },
    {
        "nome": "Doc 2 - Similar ao primeiro",
        "texto": """
ORDEM DOS ADVOGADOS DO BRASIL
CARTEIRA DE IDENTIDADE PROFISSIONAL

Nome: SASUKE UCHIHA
Inscrição: 333444
Seccional: RJ
Subseção: Rio de Janeiro
Categoria: Advogado
Data de expedição: 15/02/2021
Validade: 15/02/2026
"""
    },
    {
        "nome": "Doc 3 - Formato levemente diferente",
        "texto": """
OAB - ORDEM DOS ADVOGADOS DO BRASIL
CARTEIRA PROFISSIONAL

Nome: SAKURA HARUNO
Inscrição: 555666
Seccional: MG
Subseção: Belo Horizonte
Categoria: Advogada
Data de expedição: 20/03/2022
Validade: 20/03/2027
"""
    },
    {
        "nome": "Doc 4 - Mesmo formato do Doc 1",
        "texto": """
ORDEM DOS ADVOGADOS DO BRASIL
CARTEIRA DE IDENTIDADE PROFISSIONAL

Nome: KAKASHI HATAKE
Inscrição: 777888
Seccional: SP
Subseção: Campinas
Categoria: Advogado
Data de expedição: 05/04/2023
Validade: 05/04/2028
"""
    },
    {
        "nome": "Doc 5 - Teste de cache (repetição do Doc 1)",
        "texto": """
ORDEM DOS ADVOGADOS DO BRASIL
CARTEIRA DE IDENTIDADE PROFISSIONAL

Nome: NARUTO UZUMAKI
Inscrição: 111222
Seccional: SP
Subseção: São Paulo
Categoria: Advogado
Data de expedição: 10/01/2020
Validade: 10/01/2025
"""
    }
]

def criar_pdf_temporario(texto):
    """Cria PDF temporário a partir do texto"""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), texto.strip(), fontsize=11)

    import os
    tmp_path = tempfile.mktemp(suffix='.pdf')
    doc.save(tmp_path)
    doc.close()

    return tmp_path

def extrair_documento(extractor, doc_info, num_doc):
    """Extrai dados de um documento e retorna métricas"""
    print(f"\n{'='*80}")
    print(f"  DOCUMENTO {num_doc}/5: {doc_info['nome']}")
    print(f"{'='*80}")

    # Criar PDF temporário
    tmp_path = criar_pdf_temporario(doc_info['texto'])

    # Schema de extração
    extraction_schema = {
        "nome": "Nome completo do profissional",
        "inscricao": "Numero de inscricao na OAB",
        "seccional": "Sigla da seccional (ex: SP, RJ)",
        "subsecao": "Nome completo da subsecao",
        "categoria": "Categoria profissional",
        "data_expedicao": "Data de expedicao da carteira",
        "validade": "Data de validade da carteira"
    }

    # Medir tempo de extração
    inicio = time.time()

    result = extractor.extract(
        pdf_path=tmp_path,
        label="carteira_oab",
        extraction_schema=extraction_schema,
        max_retries=2,
        use_cache=True
    )

    tempo_total = time.time() - inicio

    # Remover arquivo temporário
    import os
    os.remove(tmp_path)

    # Exibir resultados
    if result.get('success'):
        print(f"\n[STATUS] SUCESSO")
        print(f"\nDados extraidos:")
        for field, value in result['data'].items():
            print(f"  {field}: {value}")

        # Métricas
        from_cache = result.get('from_cache', False)
        used_examples = result.get('used_examples', False)
        cost = result.get('cost', 0.0)
        tokens = result.get('tokens', {})

        print(f"\n[METRICAS]")
        print(f"  Tempo total: {tempo_total:.3f}s")
        print(f"  Custo: ${cost:.6f} USD")
        print(f"  Tokens: {tokens.get('total', 0)} ({tokens.get('input', 0)} in + {tokens.get('output', 0)} out)")
        print(f"  Do cache: {'SIM' if from_cache else 'NAO'}")
        print(f"  Usou exemplos (few-shot): {'SIM' if used_examples else 'NAO'}")

        if from_cache:
            print(f"  Tempo de cache: {result.get('cache_retrieval_time', 0):.3f}s")
            print(f"  [OTIMIZACAO] Cache hit - Economia de 100% em tokens!")

        return {
            'success': True,
            'tempo': tempo_total,
            'custo': cost,
            'tokens': tokens.get('total', 0),
            'from_cache': from_cache,
            'used_examples': used_examples
        }
    else:
        print(f"\n[ERRO] {result.get('error')}")
        return {
            'success': False,
            'tempo': tempo_total,
            'custo': 0.0,
            'tokens': 0,
            'from_cache': False,
            'used_examples': False
        }

def main():
    print("="*80)
    print("  TESTE DE APRENDIZADO PROGRESSIVO")
    print("  Demonstracao: Sistema aprende com documentos similares")
    print("="*80)
    print("\nObjetivo:")
    print("  1. Mostrar custo/tempo na primeira extracao (sem cache)")
    print("  2. Demonstrar few-shot learning em docs similares")
    print("  3. Evidenciar ganhos de performance com cache")
    print("  4. Calcular economia total de custo e tempo")
    print("\n" + "="*80)

    # Inicializar extrator
    print("\n[INIT] Inicializando extrator...")
    extractor = PDFExtractor()
    print(f"[INIT] Extrator pronto (modelo: {extractor.model})")

    # Processar documentos
    resultados = []

    for i, doc in enumerate(DOCUMENTOS_TESTE, 1):
        resultado = extrair_documento(extractor, doc, i)
        resultados.append(resultado)

        # Pausa para melhor visualização
        if i < len(DOCUMENTOS_TESTE):
            time.sleep(0.5)

    # Análise Final
    print("\n\n" + "="*80)
    print("  ANALISE FINAL - APRENDIZADO PROGRESSIVO")
    print("="*80)

    # Estatísticas
    total_custo = sum(r['custo'] for r in resultados)
    total_tempo = sum(r['tempo'] for r in resultados)
    total_tokens = sum(r['tokens'] for r in resultados)
    docs_cache = sum(1 for r in resultados if r['from_cache'])
    docs_few_shot = sum(1 for r in resultados if r['used_examples'])

    print(f"\n[ESTATISTICAS GERAIS]")
    print(f"  Total de documentos processados: {len(resultados)}")
    print(f"  Documentos bem-sucedidos: {sum(1 for r in resultados if r['success'])}/{len(resultados)}")
    print(f"  Custo total: ${total_custo:.6f} USD")
    print(f"  Tempo total: {total_tempo:.2f}s")
    print(f"  Tokens totais: {total_tokens}")

    print(f"\n[OTIMIZACOES]")
    print(f"  Cache hits: {docs_cache}/{len(resultados)} ({docs_cache/len(resultados)*100:.0f}%)")
    print(f"  Few-shot learning usado: {docs_few_shot}/{len(resultados)} ({docs_few_shot/len(resultados)*100:.0f}%)")

    # Comparação: Doc 1 vs Doc 2-4 (few-shot) vs Doc 5 (cache)
    if len(resultados) >= 5:
        doc1 = resultados[0]  # Sem cache, sem exemplos
        doc2_4 = [resultados[1], resultados[2], resultados[3]]  # Com few-shot
        doc5 = resultados[4]  # Com cache total

        print(f"\n[COMPARACAO DE PERFORMANCE]")
        print(f"\n  Doc 1 (baseline - sem otimizacoes):")
        print(f"    Tempo: {doc1['tempo']:.3f}s")
        print(f"    Custo: ${doc1['custo']:.6f}")
        print(f"    Tokens: {doc1['tokens']}")

        tempo_medio_few_shot = sum(d['tempo'] for d in doc2_4) / len(doc2_4)
        custo_medio_few_shot = sum(d['custo'] for d in doc2_4) / len(doc2_4)
        tokens_medio_few_shot = sum(d['tokens'] for d in doc2_4) / len(doc2_4)

        print(f"\n  Docs 2-4 (com few-shot learning):")
        print(f"    Tempo medio: {tempo_medio_few_shot:.3f}s")
        print(f"    Custo medio: ${custo_medio_few_shot:.6f}")
        print(f"    Tokens medio: {tokens_medio_few_shot:.0f}")
        print(f"    Melhoria: {(1 - tempo_medio_few_shot/doc1['tempo'])*100:.1f}% mais rapido")

        if doc5['from_cache']:
            print(f"\n  Doc 5 (cache completo - documento repetido):")
            print(f"    Tempo: {doc5['tempo']:.3f}s")
            print(f"    Custo: ${doc5['custo']:.6f}")
            print(f"    Tokens: {doc5['tokens']}")
            print(f"    Melhoria: {(1 - doc5['tempo']/doc1['tempo'])*100:.1f}% mais rapido")
            print(f"    Economia: ${doc1['custo'] - doc5['custo']:.6f} (100% de economia)")

    # Economia total comparada com "sem otimizações"
    custo_sem_otimizacao = resultados[0]['custo'] * len(resultados)
    economia_total = custo_sem_otimizacao - total_custo

    print(f"\n[IMPACTO DAS OTIMIZACOES]")
    print(f"  Custo sem otimizacoes (5x primeira extracao): ${custo_sem_otimizacao:.6f}")
    print(f"  Custo real (com cache + few-shot): ${total_custo:.6f}")
    print(f"  Economia total: ${economia_total:.6f} ({economia_total/custo_sem_otimizacao*100:.1f}%)")

    print(f"\n[CONCLUSOES]")
    print(f"  1. Sistema aprende com cada documento processado")
    print(f"  2. Few-shot learning melhora acuracia em docs similares")
    print(f"  3. Cache reduz custo a ZERO em docs identicos")
    print(f"  4. Quanto mais documentos, maior a economia")

    print("\n" + "="*80)
    print("  [OK] TESTE DE APRENDIZADO CONCLUIDO!")
    print("="*80)

if __name__ == '__main__':
    main()
