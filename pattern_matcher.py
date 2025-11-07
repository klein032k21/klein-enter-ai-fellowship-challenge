# -*- coding: utf-8 -*-
"""
Pattern Matcher Local - Extração de campos estruturados com regex.
ESTRATÉGIA: Reduzir carga do LLM extraindo dados óbvios localmente.
FASE 2: Pattern matching agressivo para campos estruturados.
"""
import re
from typing import Dict, Any, Optional, List

class PatternMatcher:
    """
    Extrai campos estruturados usando regex antes de chamar LLM.
    """

    def __init__(self):
        # Padrões compilados para performance
        self.patterns = {
            'cpf': re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'),
            'cnpj': re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b'),
            'cep': re.compile(r'\b\d{5}-?\d{3}\b'),
            'telefone': re.compile(r'\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'data_br': re.compile(r'\b\d{2}/\d{2}/\d{4}\b'),
            'inscricao': re.compile(r'\b\d{5,6}\b'),  # Números de 5-6 dígitos
            'valor_monetario': re.compile(r'R?\$?\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?'),
        }

    def extract_structured_fields(self, text: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """
        Extrai campos estruturados do texto usando regex.

        Args:
            text: Texto extraído do PDF
            schema: Schema de extração (field_name -> description)

        Returns:
            dict: Campos extraídos {field_name: value ou None}
        """
        extracted = {}

        for field_name, description in schema.items():
            value = self._match_field(field_name, description, text)
            if value:
                extracted[field_name] = value

        return extracted

    def _match_field(self, field_name: str, description: str, text: str) -> Optional[str]:
        """
        Tenta encontrar valor para um campo específico COM VALIDAÇÃO DE CONTEXTO.

        Args:
            field_name: Nome do campo
            description: Descrição do campo
            text: Texto do documento

        Returns:
            str ou None: Valor encontrado ou None
        """
        # Mapear nome do campo para padrão
        field_lower = field_name.lower()
        desc_lower = description.lower()

        # CPF
        if 'cpf' in field_lower or 'cpf' in desc_lower:
            match = self.patterns['cpf'].search(text)
            if match:
                return self._clean_cpf(match.group())

        # CNPJ
        if 'cnpj' in field_lower or 'cnpj' in desc_lower:
            match = self.patterns['cnpj'].search(text)
            if match:
                return self._clean_cnpj(match.group())

        # CEP - NÃO extrair para telefone!
        if 'cep' in field_lower or 'cep' in desc_lower:
            match = self.patterns['cep'].search(text)
            if match:
                return self._clean_cep(match.group())

        # Telefone - VALIDAR que não é CEP
        if 'telefone' in field_lower or 'telefone' in desc_lower or 'fone' in field_lower:
            match = self.patterns['telefone'].search(text)
            if match:
                value = match.group().strip()
                # Validar: telefone tem 10-11 dígitos, CEP tem 8
                digits_only = re.sub(r'\D', '', value)
                if len(digits_only) >= 10:  # Telefone válido
                    return value
                # Se tem 8 dígitos, é CEP, não telefone!
                return None

        # Email
        if 'email' in field_lower or 'e-mail' in field_lower:
            match = self.patterns['email'].search(text)
            if match:
                return match.group().lower()

        # Data - FASE 2: extrair PRIMEIRA data (LLM escolherá a correta se houver múltiplas)
        if 'data' in field_lower or 'vencimento' in desc_lower or 'referencia' in desc_lower:
            match = self.patterns['data_br'].search(text)
            if match:
                return match.group()

        # Quantidade/Total de parcelas - FASE 2: buscar número com contexto
        if 'parcela' in field_lower or 'quantidade' in field_lower or 'total_de' in field_lower:
            number = self.extract_number_in_context(text, ['parcela', 'total', 'quantidade', 'saldo'], field_name)
            if number:
                return number

        # Inscrição (número de 5-6 dígitos) - SEM CONTEXTO DE CEP
        if 'inscricao' in field_lower or 'inscrição' in field_lower:
            # Buscar número de 5-6 dígitos que NÃO seja CEP
            for match in self.patterns['inscricao'].finditer(text):
                value = match.group()
                # Verificar contexto: não deve estar perto de "CEP" ou endereço
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].lower()
                if 'cep' not in context and 'endereco' not in context and 'endereço' not in context:
                    return value
            return None

        # Valor monetário
        if 'valor' in field_lower or 'parcela' in field_lower or 'preco' in field_lower or 'preço' in field_lower:
            match = self.patterns['valor_monetario'].search(text)
            if match:
                return match.group().strip()

        return None

    def _clean_cpf(self, cpf: str) -> str:
        """Remove formatação do CPF"""
        digits = re.sub(r'\D', '', cpf)
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

    def _clean_cnpj(self, cnpj: str) -> str:
        """Remove formatação do CNPJ"""
        digits = re.sub(r'\D', '', cnpj)
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"

    def _clean_cep(self, cep: str) -> str:
        """Remove formatação do CEP"""
        digits = re.sub(r'\D', '', cep)
        return f"{digits[:5]}-{digits[5:]}"

    def get_extraction_confidence(self, extracted: Dict[str, Any], schema: Dict[str, str]) -> float:
        """
        Calcula confiança da extração local.

        Args:
            extracted: Campos extraídos
            schema: Schema completo

        Returns:
            float: Percentual de campos encontrados (0.0 a 1.0)
        """
        if not schema:
            return 0.0

        found = sum(1 for v in extracted.values() if v is not None)
        total = len(schema)

        return found / total

    def extract_all_dates(self, text: str) -> List[str]:
        """
        Extrai TODAS as datas do documento (não apenas a primeira).
        ESTRATÉGIA FASE 2: LLM escolhe qual data é qual campo.

        Args:
            text: Texto do documento

        Returns:
            list: Lista de datas encontradas (formato dd/mm/yyyy)
        """
        matches = self.patterns['data_br'].findall(text)
        # Remover duplicatas mantendo ordem
        seen = set()
        unique_dates = []
        for date in matches:
            if date not in seen:
                seen.add(date)
                unique_dates.append(date)
        return unique_dates

    def extract_number_in_context(self, text: str, keywords: List[str], field_name: str) -> Optional[str]:
        """
        Extrai número (2-3 dígitos) próximo a keywords específicas.
        ESTRATÉGIA FASE 2: Capturar "96 parcelas", "total: 96", etc.

        Args:
            text: Texto do documento
            keywords: Palavras-chave para buscar contexto ['total', 'parcela']
            field_name: Nome do campo (para debug)

        Returns:
            str ou None: Número encontrado ou None
        """
        # Buscar padrão: keyword + número ou número + keyword (janela de 30 chars)
        pattern = r'\b\d{1,3}\b'

        for match in re.finditer(pattern, text):
            number = match.group()

            # Verificar contexto ao redor (50 chars antes e depois)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].lower()

            # Validar que NÃO é CEP, telefone ou data
            if re.search(r'\d{5}-?\d{3}', context):  # CEP
                continue
            if re.search(r'\d{2}/\d{2}/\d{4}', context):  # Data
                continue

            # Verificar se alguma keyword está presente
            if any(keyword.lower() in context for keyword in keywords):
                return number

        return None
