# -*- coding: utf-8 -*-
"""
Script para processar dataset.json com todos os PDFs de teste.
Executa extracoes em serie e exibe metricas.
"""
import json
import time
from pathlib import Path
from extractor import PDFExtractor
from currency_converter import CurrencyConverter

def load_dataset(dataset_path="data/dataset.json"):
    """Carrega o dataset.json"""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_extractions():
    """Executa todas as extra��es do dataset"""

    print("=" * 80)
    print("  PDF EXTRACTOR - ENTER AI FELLOWSHIP CHALLENGE")
    print("  Processamento em Serie (Serial Processing)")
    print("=" * 80)

    # Carregar dataset
    try:
        dataset = load_dataset()
        print(f"\n[DATASET] Carregado: {len(dataset)} documentos")
    except Exception as e:
        print(f"\n[ERRO] Falha ao carregar dataset.json: {e}")
        return

    # Inicializar extrator
    try:
        extractor = PDFExtractor()
        print(f"[EXTRATOR] Inicializado com modelo: {extractor.model}")
    except Exception as e:
        print(f"\n[ERRO] Falha ao inicializar extrator: {e}")
        return

    # Inicializar conversor de moedas
    try:
        currency = CurrencyConverter()
        exchange_rate = currency.get_usd_brl_rate()
        print(f"[COTACAO] USD/BRL: R$ {exchange_rate:.4f}")
    except Exception as e:
        print(f"\n[AVISO] Falha ao obter cotacao: {e}. Usando fallback.")
        currency = CurrencyConverter()
        exchange_rate = currency.fallback_rate

    print("\n" + "=" * 80)
    print("INICIANDO PROCESSAMENTO")
    print("=" * 80 + "\n")

    # Estat�sticas
    total_start_time = time.time()
    results = []
    successful = 0
    failed = 0
    total_processing_time = 0
    total_cost = 0.0  # Rastreamento de custo total

    # Processar cada documento em S�RIE
    for idx, item in enumerate(dataset, 1):
        label = item.get('label', 'unknown')
        pdf_filename = item.get('pdf_path', '')

        # Ajustar caminho do PDF (adicionar data/files/)
        pdf_path = f"data/files/{pdf_filename}"

        extraction_schema = item.get('extraction_schema', {})

        print(f"[{idx}/{len(dataset)}] Processando: {pdf_filename}")
        print(f"         Label: {label}")
        print(f"         Campos: {len(extraction_schema)}")

        # Verificar se arquivo existe
        if not Path(pdf_path).exists():
            print(f"         [ERRO] Arquivo nao encontrado: {pdf_path}\n")
            failed += 1
            results.append({
                "index": idx,
                "pdf": pdf_filename,
                "label": label,
                "success": False,
                "error": f"Arquivo n�o encontrado: {pdf_path}"
            })
            continue

        # Executar extra��o
        start_time = time.time()

        try:
            result = extractor.extract(pdf_path, label, extraction_schema)
            elapsed_time = time.time() - start_time
            total_processing_time += elapsed_time

            if result['success']:
                extraction_cost = result.get('cost', 0.0)
                total_cost += extraction_cost
                from_cache = result.get('from_cache', False)

                if from_cache:
                    print(f"         [OK] Extracao bem-sucedida em {elapsed_time:.2f}s [CACHE]")
                    print(f"         Custo: $0.000000 (R$ 0.0000) [CACHE - sem custo LLM]")
                else:
                    print(f"         [OK] Extracao bem-sucedida em {elapsed_time:.2f}s")
                    print(f"         Custo: {currency.format_dual_currency(extraction_cost)}")
                successful += 1

                # Exibir TODOS os dados extraidos
                print(f"         Campos extraidos ({len(result['data'])}):")
                for key, value in result['data'].items():
                    value_str = str(value) if value else "null"
                    print(f"              - {key}: {value_str}")

                results.append({
                    "index": idx,
                    "pdf": pdf_filename,
                    "label": label,
                    "success": True,
                    "processing_time": elapsed_time,
                    "cost": extraction_cost,
                    "cost_brl": currency.usd_to_brl(extraction_cost),
                    "fields_extracted": len(result['data']),
                    "extracted_data": result['data']  # Adicionar dados completos
                })
            else:
                print(f"         [FALHA] {result.get('error', 'Erro desconhecido')}")
                failed += 1
                results.append({
                    "index": idx,
                    "pdf": pdf_filename,
                    "label": label,
                    "success": False,
                    "error": result.get('error', 'Erro desconhecido'),
                    "processing_time": elapsed_time
                })

        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"         [EXCECAO] {str(e)}")
            failed += 1
            results.append({
                "index": idx,
                "pdf": pdf_filename,
                "label": label,
                "success": False,
                "error": str(e),
                "processing_time": elapsed_time
            })

        print()  # Linha em branco

    # M�tricas finais
    total_elapsed_time = time.time() - total_start_time

    print("=" * 80)
    print("RESULTADOS FINAIS")
    print("=" * 80)
    print(f"Total de documentos: {len(dataset)}")
    print(f"Bem-sucedidos: {successful}")
    print(f"Falhas: {failed}")
    print(f"Taxa de sucesso: {(successful/len(dataset)*100):.1f}%")
    print()
    print(f"Tempo total (incluindo overhead): {total_elapsed_time:.2f}s")
    print(f"Tempo de processamento (apenas LLM): {total_processing_time:.2f}s")
    print()
    print(f"Custo total: {currency.format_dual_currency(total_cost)}")

    if successful > 0:
        avg_time = total_processing_time / successful
        avg_cost = total_cost / successful
        print(f"Tempo medio por extracao: {avg_time:.2f}s")
        print(f"Custo medio por extracao: {currency.format_dual_currency(avg_cost)}")

        # Validar requisito de <10s
        if avg_time < 10:
            print(f"[OK] Requisito de tempo atendido (< 10s por extracao)")
        else:
            print(f"[ATENCAO] Tempo medio acima de 10s")

    print()

    # An�lise por label
    labels_stats = {}
    for r in results:
        label = r['label']
        if label not in labels_stats:
            labels_stats[label] = {"total": 0, "successful": 0}
        labels_stats[label]["total"] += 1
        if r['success']:
            labels_stats[label]["successful"] += 1

    print("Estatisticas por label:")
    for label, stats in labels_stats.items():
        success_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"  - {label}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)")

    print()
    print("=" * 80)

    # Salvar resultados em arquivo JSON (opcional)
    output_path = "extraction_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total": len(dataset),
                "successful": successful,
                "failed": failed,
                "success_rate": f"{(successful/len(dataset)*100):.1f}%",
                "total_time": f"{total_elapsed_time:.2f}s",
                "avg_time_per_extraction": f"{(total_processing_time/successful):.2f}s" if successful > 0 else "N/A",
                "total_cost_usd": f"${total_cost:.6f}",
                "total_cost_brl": f"R$ {currency.usd_to_brl(total_cost):.4f}",
                "avg_cost_usd": f"${(total_cost/successful):.6f}" if successful > 0 else "N/A",
                "avg_cost_brl": f"R$ {currency.usd_to_brl(total_cost/successful):.4f}" if successful > 0 else "N/A",
                "exchange_rate_usd_brl": f"{exchange_rate:.4f}"
            },
            "results": results
        }, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Resultados salvos em: {output_path}")
    print()

if __name__ == "__main__":
    run_extractions()
