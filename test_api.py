# -*- coding: utf-8 -*-
"""
Script de teste da API Flask.
Testa endpoint /extract com PDFs do dataset.
"""
import requests
import base64
import json
from pathlib import Path

# URL da API
API_URL = "http://localhost:5000"

def pdf_to_base64(pdf_path):
    """Converte PDF para Base64"""
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
        return base64.b64encode(pdf_bytes).decode('utf-8')

def test_extract():
    """Testa endpoint /extract"""
    print("=" * 80)
    print("  TESTE DA API - /extract")
    print("=" * 80 + "\n")

    # Teste 1: carteira_oab
    print("[TESTE 1] Extraindo carteira_oab...")
    pdf_base64 = pdf_to_base64("data/files/oab_3.pdf")

    payload = {
        "label": "carteira_oab",
        "extraction_schema": {
            "nome": "Nome do profissional",
            "inscricao": "Número de inscrição do profissional",
            "seccional": "Seccional do profissional",
            "situacao": "Situação do profissional"
        },
        "pdf": pdf_base64
    }

    response = requests.post(
        f"{API_URL}/extract",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status Code: {response.status_code}")
    print(f"\nHeaders (metadados):")
    for key, value in response.headers.items():
        if key.startswith('X-Extraction'):
            print(f"  {key}: {value}")

    print(f"\nResponse Body (apenas dados):")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print("\n" + "=" * 80 + "\n")

    # Teste 2: Mesmo PDF novamente (deve usar cache)
    print("[TESTE 2] Mesmo PDF (deve usar cache)...")
    response2 = requests.post(
        f"{API_URL}/extract",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status Code: {response2.status_code}")
    print(f"\nHeaders (metadados):")
    for key, value in response2.headers.items():
        if key.startswith('X-Extraction'):
            print(f"  {key}: {value}")

    print(f"\nResponse Body:")
    print(json.dumps(response2.json(), indent=2, ensure_ascii=False))
    print("\n" + "=" * 80 + "\n")

def test_health():
    """Testa endpoint /health"""
    print("[TESTE] Health check...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    try:
        test_health()
        test_extract()
        print("\n✅ Todos os testes concluídos!")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API.")
        print("   Certifique-se de que o servidor está rodando (python app.py)")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
