# -*- coding: utf-8 -*-
"""
Framework de validação de acurácia campo-a-campo.
Compara extraction_results.json com ground_truth.json.
"""
import json
from typing import Dict, Any, Tuple, List

class AccuracyValidator:
    """
    Valida acurácia dos dados extraídos comparando com ground truth.
    """

    def __init__(self, ground_truth_path: str = "ground_truth.json", results_path: str = "extraction_results.json"):
        self.ground_truth_path = ground_truth_path
        self.results_path = results_path
        self.ground_truth = self.load_ground_truth()
        self.results = self.load_results()

    def load_ground_truth(self) -> Dict:
        """Carrega valores esperados"""
        with open(self.ground_truth_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_results(self) -> Dict:
        """Carrega resultados da extração"""
        with open(self.results_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Converter lista de results para dict por pdf_path
            results_dict = {}
            for result in data['results']:
                pdf_name = result['pdf']
                results_dict[pdf_name] = result
            return results_dict

    def normalize_value(self, value: Any) -> Any:
        """Normaliza valor para comparação"""
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip().lower()
        return value

    def compare_field(self, expected: Any, actual: Any, field_name: str) -> Tuple[bool, str]:
        """
        Compara um campo específico.

        Returns:
            (is_correct, message)
        """
        expected_norm = self.normalize_value(expected)
        actual_norm = self.normalize_value(actual)

        # Ambos null = correto
        if expected_norm is None and actual_norm is None:
            return (True, "")

        # Um é null e outro não = erro
        if expected_norm is None or actual_norm is None:
            return (False, f"Esperado: {expected}, Extraído: {actual}")

        # Comparação de strings
        if isinstance(expected_norm, str) and isinstance(actual_norm, str):
            # Comparação exata (já normalizado)
            if expected_norm == actual_norm:
                return (True, "")

            # Comparação flexível para alguns campos
            if field_name in ['seccional', 'subsecao']:
                # Verificar se um contém o outro
                if expected_norm in actual_norm or actual_norm in expected_norm:
                    return (True, "")

            return (False, f"Esperado: '{expected}', Extraído: '{actual}'")

        # Comparação direta
        if expected == actual:
            return (True, "")

        return (False, f"Esperado: {expected}, Extraído: {actual}")

    def validate_document(self, pdf_name: str) -> Dict:
        """
        Valida um documento específico.

        Returns:
            {
                'total_fields': int,
                'correct_fields': int,
                'errors': [{field, expected, actual, message}]
            }
        """
        if pdf_name not in self.ground_truth:
            return {'error': f'PDF {pdf_name} não encontrado no ground truth'}

        if pdf_name not in self.results:
            return {'error': f'PDF {pdf_name} não encontrado nos resultados'}

        expected_data = self.ground_truth[pdf_name]['expected']
        result = self.results[pdf_name]

        if not result.get('success', False):
            return {'error': f'Extração falhou: {result.get("error", "unknown")}'}

        extracted_data = result['extracted_data']

        total_fields = len(expected_data)
        correct_fields = 0
        errors = []

        for field_name, expected_value in expected_data.items():
            actual_value = extracted_data.get(field_name)
            is_correct, message = self.compare_field(expected_value, actual_value, field_name)

            if is_correct:
                correct_fields += 1
            else:
                errors.append({
                    'field': field_name,
                    'expected': expected_value,
                    'actual': actual_value,
                    'message': message
                })

        return {
            'total_fields': total_fields,
            'correct_fields': correct_fields,
            'accuracy': (correct_fields / total_fields * 100) if total_fields > 0 else 0,
            'errors': errors
        }

    def validate_all(self) -> Dict:
        """
        Valida todos os documentos.

        Returns:
            Relatório completo de acurácia
        """
        results = {}
        total_fields_global = 0
        correct_fields_global = 0
        all_errors = []

        for pdf_name in self.ground_truth.keys():
            validation = self.validate_document(pdf_name)
            results[pdf_name] = validation

            if 'error' not in validation:
                total_fields_global += validation['total_fields']
                correct_fields_global += validation['correct_fields']

                # Adicionar erros à lista global
                for error in validation['errors']:
                    all_errors.append({
                        'pdf': pdf_name,
                        'field': error['field'],
                        'expected': error['expected'],
                        'actual': error['actual'],
                        'message': error['message']
                    })

        global_accuracy = (correct_fields_global / total_fields_global * 100) if total_fields_global > 0 else 0

        return {
            'documents': results,
            'summary': {
                'total_fields': total_fields_global,
                'correct_fields': correct_fields_global,
                'incorrect_fields': total_fields_global - correct_fields_global,
                'accuracy': global_accuracy
            },
            'all_errors': all_errors
        }

    def print_report(self, validation_results: Dict):
        """Imprime relatório formatado"""
        print("=" * 80)
        print("  RELATÓRIO DE ACURÁCIA - VALIDAÇÃO CAMPO-A-CAMPO")
        print("=" * 80)
        print()

        # Relatório por documento
        print("VALIDAÇÃO POR DOCUMENTO:")
        print("-" * 80)

        for pdf_name, doc_result in validation_results['documents'].items():
            if 'error' in doc_result:
                print(f"\n[ERRO] {pdf_name}")
                print(f"  {doc_result['error']}")
                continue

            accuracy = doc_result['accuracy']
            correct = doc_result['correct_fields']
            total = doc_result['total_fields']

            status = "[OK]" if accuracy == 100 else "[ERRO]"
            print(f"\n{status} {pdf_name}")
            print(f"  Acuracia: {accuracy:.1f}% ({correct}/{total} campos corretos)")

            if doc_result['errors']:
                for error in doc_result['errors']:
                    print(f"  [X] {error['field']}: {error['message']}")

        # Resumo global
        print()
        print("=" * 80)
        print("RESUMO GLOBAL:")
        print("=" * 80)

        summary = validation_results['summary']
        print(f"Total de campos: {summary['total_fields']}")
        print(f"Campos corretos: {summary['correct_fields']}")
        print(f"Campos incorretos: {summary['incorrect_fields']}")
        print(f"ACURACIA GLOBAL: {summary['accuracy']:.2f}%")

        # Lista de todos os erros
        if validation_results['all_errors']:
            print()
            print("=" * 80)
            print("ERROS ENCONTRADOS:")
            print("=" * 80)

            for error in validation_results['all_errors']:
                print(f"\n[ERRO] {error['pdf']} :: {error['field']}")
                print(f"  Esperado: {error['expected']}")
                print(f"  Extraido: {error['actual']}")
        else:
            print()
            print("[OK] NENHUM ERRO ENCONTRADO - 100% DE ACURACIA!")

        print()
        print("=" * 80)


def main():
    """Executa validação completa"""
    validator = AccuracyValidator()
    results = validator.validate_all()
    validator.print_report(results)

    # Retornar código de saída baseado na acurácia
    accuracy = results['summary']['accuracy']
    if accuracy == 100:
        exit(0)
    else:
        exit(1)


if __name__ == '__main__':
    main()
