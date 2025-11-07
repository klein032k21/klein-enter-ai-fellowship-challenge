# -*- coding: utf-8 -*-
"""
Teste unitário para validar precisão de extração.
Foco: OAB_1.pdf - validar cada campo contra valor esperado.
"""
import json
from extractor import PDFExtractor

# Valores esperados (da imagem)
EXPECTED_OAB_1 = {
    "nome": "JOANA D'ARC",
    "inscricao": "101943",
    "seccional": "PR",  # APENAS "PR", não "PR - CONSELHO..."
    "subsecao": "CONSELHO SECCIONAL - PARANÁ",  # Este é o valor correto!
    "categoria": "SUPLEMENTAR",
    "endereco_profissional": "AVENIDA PAULISTA, No 2300 andar Pilotis, Bela Vista\nSÃO PAULO - SP\n01310300",  # Com CEP
    "telefone_profissional": None,  # Não há telefone no documento!
    "situacao": "SITUAÇÃO REGULAR"
}

def test_oab_1():
    """Testa extração do OAB_1.pdf"""
    print("=" * 80)
    print("TESTE UNITÁRIO: OAB_1.pdf")
    print("=" * 80)

    # Schema do dataset
    schema = {
        "nome": "Nome do profissional, normalmente no canto superior esquerdo da imagem",
        "inscricao": "Número de inscrição do profissional",
        "seccional": "Seccional do profissional",
        "subsecao": "Subseção à qual o profissional faz parte",
        "categoria": "Categoria, pode ser ADVOGADO, ADVOGADA, SUPLEMENTAR, ESTAGIARIO, ESTAGIARIA",
        "endereco_profissional": "Endereço do profissional",
        "telefone_profissional": "Telefone do profissional",
        "situacao": "Situação do profissional, normalmente no canto inferior direito."
    }

    # Extrair
    extractor = PDFExtractor()
    result = extractor.extract(
        "data/files/oab_1.pdf",
        "carteira_oab",
        schema
    )

    print(f"\nSucesso: {result['success']}")
    print(f"Custo: ${result.get('cost', 0):.6f}")
    print(f"Tempo: {result.get('tokens', {}).get('total', 0)} tokens")

    if not result['success']:
        print(f"\n[ERRO] Extração falhou: {result.get('error')}")
        return False

    # Validar cada campo
    extracted = result['data']
    print("\n" + "=" * 80)
    print("VALIDAÇÃO CAMPO POR CAMPO:")
    print("=" * 80)

    all_correct = True
    for field, expected_value in EXPECTED_OAB_1.items():
        actual_value = extracted.get(field)

        # Normalizar para comparação
        if actual_value:
            actual_normalized = actual_value.strip() if isinstance(actual_value, str) else actual_value
        else:
            actual_normalized = None

        if expected_value:
            expected_normalized = expected_value.strip() if isinstance(expected_value, str) else expected_value
        else:
            expected_normalized = None

        # Comparar (flexível para formatação)
        is_correct = False
        if expected_normalized is None and actual_normalized is None:
            is_correct = True
        elif expected_normalized and actual_normalized:
            # Para seccional e subsecao, verificar conteúdo
            if field in ['seccional', 'subsecao']:
                is_correct = expected_normalized.lower() in actual_normalized.lower() or actual_normalized.lower() in expected_normalized.lower()
            else:
                # Comparação flexível para outros campos
                is_correct = expected_normalized.lower() == actual_normalized.lower()

        status = "[OK]" if is_correct else "[ERRO]"
        print(f"\n{field}:")
        print(f"  Esperado: {expected_value}")
        print(f"  Extraido: {actual_value}")
        print(f"  Status: {status}")

        if not is_correct:
            all_correct = False

    print("\n" + "=" * 80)
    if all_correct:
        print("[OK] TESTE PASSOU - Todos os campos corretos!")
    else:
        print("[FALHA] TESTE FALHOU - Ha campos incorretos!")
    print("=" * 80)

    return all_correct

if __name__ == "__main__":
    success = test_oab_1()
    exit(0 if success else 1)
