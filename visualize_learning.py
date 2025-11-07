#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Visualização da curva de aprendizado do sistema
Gera gráficos de performance e economia
"""

def print_chart():
    """Imprime gráfico ASCII de performance"""

    # Dados do teste
    docs = [
        {"nome": "Doc 1 (baseline)", "tempo": 16.707, "custo": 0.000623, "tokens": 680},
        {"nome": "Doc 2 (few-shot)", "tempo": 5.966, "custo": 0.000751, "tokens": 745},
        {"nome": "Doc 3 (few-shot)", "tempo": 5.942, "custo": 0.000619, "tokens": 678},
        {"nome": "Doc 4 (few-shot)", "tempo": 5.808, "custo": 0.000750, "tokens": 744},
        {"nome": "Doc 5 (few-shot)", "tempo": 5.650, "custo": 0.000752, "tokens": 747},
    ]

    print("="*80)
    print("  VISUALIZACAO DA CURVA DE APRENDIZADO")
    print("="*80)

    # Gráfico de tempo
    print("\n[GRAFICO 1] TEMPO DE EXTRACAO (segundos)")
    print("-"*80)
    max_tempo = max(d['tempo'] for d in docs)

    for i, doc in enumerate(docs, 1):
        barra_len = int((doc['tempo'] / max_tempo) * 60)
        barra = "#" * barra_len
        print(f"  Doc {i}: {barra} {doc['tempo']:.2f}s")

    print("-"*80)
    reducao = ((docs[0]['tempo'] - docs[-1]['tempo']) / docs[0]['tempo']) * 100
    print(f"  Reducao: {reducao:.1f}% (de {docs[0]['tempo']:.1f}s para {docs[-1]['tempo']:.1f}s)")

    # Gráfico de custo
    print("\n[GRAFICO 2] CUSTO POR EXTRACAO (USD)")
    print("-"*80)
    max_custo = max(d['custo'] for d in docs)

    for i, doc in enumerate(docs, 1):
        barra_len = int((doc['custo'] / max_custo) * 60)
        barra = "#" * barra_len
        print(f"  Doc {i}: {barra} ${doc['custo']:.6f}")

    print("-"*80)
    custo_total = sum(d['custo'] for d in docs)
    custo_medio = custo_total / len(docs)
    print(f"  Custo total: ${custo_total:.6f}")
    print(f"  Custo medio: ${custo_medio:.6f}")

    # Gráfico de tokens
    print("\n[GRAFICO 3] TOKENS CONSUMIDOS")
    print("-"*80)
    max_tokens = max(d['tokens'] for d in docs)

    for i, doc in enumerate(docs, 1):
        barra_len = int((doc['tokens'] / max_tokens) * 60)
        barra = "#" * barra_len
        print(f"  Doc {i}: {barra} {doc['tokens']} tokens")

    print("-"*80)
    tokens_total = sum(d['tokens'] for d in docs)
    print(f"  Tokens total: {tokens_total}")

    # Projeção para 100 documentos
    print("\n[PROJECAO] PERFORMANCE EM 100 DOCUMENTOS")
    print("-"*80)

    # Sem otimização
    tempo_sem_opt = docs[0]['tempo'] * 100
    custo_sem_opt = docs[0]['custo'] * 100

    # Com otimização (1 baseline + 99 few-shot)
    tempo_medio_few_shot = sum(d['tempo'] for d in docs[1:]) / len(docs[1:])
    custo_medio_few_shot = sum(d['custo'] for d in docs[1:]) / len(docs[1:])

    tempo_com_opt = docs[0]['tempo'] + (tempo_medio_few_shot * 99)
    custo_com_opt = docs[0]['custo'] + (custo_medio_few_shot * 99)

    print("\n  SEM Few-Shot Learning:")
    print(f"    Tempo total: {tempo_sem_opt:.1f}s (~{tempo_sem_opt/60:.1f} min)")
    print(f"    Custo total: ${custo_sem_opt:.4f}")

    print("\n  COM Few-Shot Learning:")
    print(f"    Tempo total: {tempo_com_opt:.1f}s (~{tempo_com_opt/60:.1f} min)")
    print(f"    Custo total: ${custo_com_opt:.4f}")

    print("\n  ECONOMIA:")
    tempo_economizado = tempo_sem_opt - tempo_com_opt
    custo_economizado_pct = ((custo_sem_opt - custo_com_opt) / custo_sem_opt) * 100
    print(f"    Tempo: {tempo_economizado:.1f}s ({(tempo_economizado/tempo_sem_opt)*100:.1f}%)")
    print(f"    Performance: {tempo_sem_opt/tempo_com_opt:.1f}x mais rapido")

    # Gráfico comparativo visual
    print("\n[GRAFICO 4] COMPARACAO: 100 DOCS (tempo em minutos)")
    print("-"*80)

    barra_sem = int((tempo_sem_opt/60 / (tempo_sem_opt/60)) * 60)
    barra_com = int((tempo_com_opt/60 / (tempo_sem_opt/60)) * 60)

    print(f"  Sem otimizacao: {'#' * barra_sem} {tempo_sem_opt/60:.1f} min")
    print(f"  Com few-shot:   {'#' * barra_com} {tempo_com_opt/60:.1f} min")
    print(f"                  {'^' * barra_com}{' ' * (barra_sem - barra_com)}^")
    print(f"                  Economiza {tempo_economizado/60:.1f} min")

    print("-"*80)

    # Projeção com cache (20% de repetição)
    print("\n[PROJECAO BONUS] COM CACHE DE DOCUMENTOS REPETIDOS")
    print("-"*80)

    cache_hit_rate = 0.20  # 20% dos docs são repetidos
    cache_time = 0.001  # 1ms para cache hit

    docs_unicos = int(100 * (1 - cache_hit_rate))
    docs_cache = 100 - docs_unicos

    tempo_com_cache = docs[0]['tempo'] + (tempo_medio_few_shot * (docs_unicos - 1)) + (cache_time * docs_cache)
    custo_com_cache = docs[0]['custo'] + (custo_medio_few_shot * (docs_unicos - 1))  # cache = custo zero

    print(f"\n  Assumindo {int(cache_hit_rate*100)}% de documentos repetidos:")
    print(f"    Docs unicos: {docs_unicos}")
    print(f"    Docs do cache: {docs_cache}")
    print(f"    Tempo total: {tempo_com_cache:.1f}s (~{tempo_com_cache/60:.1f} min)")
    print(f"    Custo total: ${custo_com_cache:.4f}")

    print("\n  ECONOMIA vs baseline (sem otimizacoes):")
    tempo_total_economizado = tempo_sem_opt - tempo_com_cache
    custo_total_economizado = custo_sem_opt - custo_com_cache
    print(f"    Tempo: {tempo_total_economizado:.1f}s ({(tempo_total_economizado/tempo_sem_opt)*100:.1f}%)")
    print(f"    Custo: ${custo_total_economizado:.4f} ({(custo_total_economizado/custo_sem_opt)*100:.1f}%)")
    print(f"    Performance: {tempo_sem_opt/tempo_com_cache:.1f}x mais rapido")

    # Resumo final
    print("\n" + "="*80)
    print("  RESUMO EXECUTIVO")
    print("="*80)
    print("\n  O sistema demonstra APRENDIZADO PROGRESSIVO:")
    print(f"    1. Primeira extracao: {docs[0]['tempo']:.1f}s (baseline)")
    print(f"    2. Proximas extracoes: ~{tempo_medio_few_shot:.1f}s (few-shot learning)")
    print(f"    3. Docs repetidos: ~0.001s (cache)")
    print()
    print(f"  Em 100 documentos:")
    print(f"    - Few-shot: {tempo_sem_opt/tempo_com_opt:.1f}x mais rapido")
    print(f"    - Few-shot + Cache: {tempo_sem_opt/tempo_com_cache:.1f}x mais rapido")
    print()
    print("  QUANTO MAIS DOCUMENTOS, MAIOR A ECONOMIA!")
    print("="*80)

if __name__ == '__main__':
    print_chart()
