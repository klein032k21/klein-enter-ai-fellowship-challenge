#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste da API Flask
"""
import requests
import json
import base64
import fitz
import tempfile

def create_test_pdf():
    """Cria PDF de teste e retorna Base64"""
    test_data = """
ORDEM DOS ADVOGADOS DO BRASIL
CARTEIRA DE IDENTIDADE PROFISSIONAL

Nome: VEGETA PRINCE
Inscricao: 789012
Seccional: RJ
Subsecao: Rio de Janeiro
Categoria: Advogado
Data de expedicao: 15/03/2021
Validade: 15/03/2026
    """.strip()

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), test_data, fontsize=11)

    tmp_path = tempfile.mktemp(suffix='.pdf')
    doc.save(tmp_path)
    doc.close()

    with open(tmp_path, 'rb') as f:
        pdf_bytes = f.read()

    import os
    os.remove(tmp_path)

    return base64.b64encode(pdf_bytes).decode('utf-8')

def test_health():
    """Testa endpoint /health"""
    print("\n[1] Testando /health...")
    response = requests.get('http://localhost:5000/health')
    print(f"    Status: {response.status_code}")
    print(f"    Resposta: {response.json()}")
    return response.status_code == 200

def test_extract():
    """Testa endpoint /extract"""
    print("\n[2] Testando /extract...")

    pdf_base64 = create_test_pdf()
    print(f"    PDF criado ({len(pdf_base64)} chars)")

    payload = {
        "label": "carteira_oab",
        "extraction_schema": {
            "nome": "Nome completo do profissional",
            "inscricao": "Numero de inscricao na OAB",
            "seccional": "Sigla da seccional (ex: SP, RJ)",
            "subsecao": "Nome completo da subsecao",
            "categoria": "Categoria profissional",
            "data_expedicao": "Data de expedicao da carteira",
            "validade": "Data de validade da carteira"
        },
        "pdf": pdf_base64
    }

    print("    Enviando requisicao...")
    response = requests.post(
        'http://localhost:5000/extract',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )

    print(f"    Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n    Dados extraidos:")
        for field, value in data.items():
            print(f"      {field}: {value}")

        print("\n    Headers (metadados):")
        print(f"      Custo: ${response.headers.get('X-Extraction-Cost-USD', 'N/A')}")
        print(f"      Tempo: {response.headers.get('X-Extraction-Time-Seconds', 'N/A')}s")
        print(f"      Do cache: {response.headers.get('X-Extraction-From-Cache', 'N/A')}")
        print(f"      Tokens total: {response.headers.get('X-Extraction-Tokens-Total', 'N/A')}")

        return True
    else:
        print(f"    Erro: {response.text}")
        return False

if __name__ == '__main__':
    print("=" * 80)
    print("  TESTE DA API FLASK")
    print("=" * 80)

    success = True

    try:
        if not test_health():
            success = False

        if not test_extract():
            success = False

        print("\n" + "=" * 80)
        if success:
            print("  [OK] TODOS OS TESTES PASSARAM!")
        else:
            print("  [FALHA] Alguns testes falharam")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
