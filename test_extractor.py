#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste final do PDF Extractor
Testa extração com exemplo simples
"""
import json
from extractor import PDFExtractor

def test_basic_extraction():
    """Teste básico de extração"""
    print("=" * 80)
    print("  TESTE FINAL - PDF EXTRACTOR")
    print("=" * 80)
    print()

    # Criar extrator
    print("[1/4] Inicializando extrator...")
    try:
        extractor = PDFExtractor()
        print("      [OK] Extrator inicializado com sucesso")
        print(f"      [OK] Modelo: {extractor.model}")
    except Exception as e:
        print(f"      [ERRO] ERRO: {e}")
        return False

    # Criar texto de teste simples (sem precisar de PDF real)
    print("\n[2/4] Criando documento de teste...")
    test_data = """
ORDEM DOS ADVOGADOS DO BRASIL
CARTEIRA DE IDENTIDADE PROFISSIONAL

Nome: MARIA DA SILVA
Inscrição: 123456
Seccional: SP
Subseção: São Paulo
Categoria: Advogado
Data de expedição: 01/01/2020
Validade: 01/01/2025
    """.strip()

    print("      [OK] Documento de teste criado")
    print(f"      [OK] Tamanho: {len(test_data)} caracteres")

    # Schema de extração
    extraction_schema = {
        "nome": "Nome completo do profissional",
        "inscricao": "Número de inscrição na OAB",
        "seccional": "Sigla da seccional (ex: SP, RJ)",
        "subsecao": "Nome completo da subseção",
        "categoria": "Categoria profissional",
        "data_expedicao": "Data de expedição da carteira",
        "validade": "Data de validade da carteira"
    }

    print("\n[3/4] Executando extração...")
    print("      Schema com 7 campos:")
    for field in extraction_schema.keys():
        print(f"        - {field}")

    try:
        # Simular extração direta (sem PDF)
        import tempfile
        import fitz  # PyMuPDF

        # Criar PDF temporário com o texto
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)  # A4
        page.insert_text((50, 50), test_data, fontsize=11)

        # Usar caminho temporário direto
        import os
        tmp_path = tempfile.mktemp(suffix='.pdf')
        doc.save(tmp_path)
        doc.close()

        # Extrair dados
        result = extractor.extract(
            pdf_path=tmp_path,
            label="carteira_oab",
            extraction_schema=extraction_schema,
            max_retries=2,
            use_cache=True
        )

        # Remover arquivo temporário
        import os
        os.remove(tmp_path)

        print("\n[4/4] Resultado da extracao:")
        print("=" * 80)

        if result.get('success'):
            print("[SUCESSO!]")
            print()
            print("Dados extraidos:")
            for field, value in result['data'].items():
                print(f"  {field}: {value}")

            print()
            print("Metadados:")
            print(f"  Custo: ${result['cost']:.6f} USD")
            print(f"  Tokens input: {result['tokens']['input']}")
            print(f"  Tokens output: {result['tokens']['output']}")
            print(f"  Tokens total: {result['tokens']['total']}")
            print(f"  Do cache: {result.get('from_cache', False)}")
            print(f"  Usou exemplos: {result.get('used_examples', False)}")

            print()
            print("=" * 80)
            print("[OK] TODOS OS TESTES PASSARAM!")
            print("=" * 80)
            return True
        else:
            print(f"[FALHA]: {result.get('error')}")
            return False

    except Exception as e:
        print(f"      [ERRO] durante extracao: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_basic_extraction()
    exit(0 if success else 1)