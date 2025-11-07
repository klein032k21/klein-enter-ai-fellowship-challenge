# -*- coding: utf-8 -*-
"""
Conversor de moedas USD -> BRL com cotacao em tempo real.
Usa AwesomeAPI para obter cotacao atualizada com cache de 1 hora.
"""
import requests
import time
from datetime import datetime

class CurrencyConverter:
    """
    Conversor de moedas com cache inteligente.
    ESTRATEGIA: Minimizar requests externos com cache de 1 hora.
    """

    def __init__(self, cache_duration=3600):
        """
        Inicializa o conversor.

        Args:
            cache_duration: Duracao do cache em segundos (padrao: 1 hora)
        """
        self.cache_duration = cache_duration
        self.cached_rate = None
        self.cache_timestamp = 0
        self.fallback_rate = 5.00  # Taxa fallback se API falhar
        self.api_url = 'https://economia.awesomeapi.com.br/last/USD-BRL'

    def get_usd_brl_rate(self):
        """
        Obtem a cotacao USD/BRL atual (com cache).

        Returns:
            float: Taxa de cambio USD -> BRL
        """
        # Verificar se cache ainda e valido
        current_time = time.time()
        if (current_time - self.cache_timestamp < self.cache_duration
            and self.cached_rate is not None):
            return self.cached_rate

        # Tentar buscar cotacao atualizada
        try:
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            data = response.json()

            # AwesomeAPI retorna formato: {"USDBRL": {"bid": "5.02", ...}}
            rate = float(data['USDBRL']['bid'])

            # Atualizar cache
            self.cached_rate = rate
            self.cache_timestamp = current_time

            return rate

        except Exception as e:
            # Se falhar, usar cache anterior se disponivel
            if self.cached_rate is not None:
                return self.cached_rate

            # Se nao tem cache, usar fallback
            return self.fallback_rate

    def usd_to_brl(self, usd_value):
        """
        Converte valor de USD para BRL.

        Args:
            usd_value: Valor em dolares

        Returns:
            float: Valor em reais
        """
        rate = self.get_usd_brl_rate()
        return usd_value * rate

    def format_dual_currency(self, usd_value):
        """
        Formata valor em USD e BRL para exibicao.

        Args:
            usd_value: Valor em dolares

        Returns:
            str: String formatada "$X.XXXXXX (R$ Y.YYYY)"
        """
        brl_value = self.usd_to_brl(usd_value)
        return f"${usd_value:.6f} (R$ {brl_value:.4f})"

    def get_exchange_info(self):
        """
        Retorna informacoes sobre a cotacao atual.

        Returns:
            dict: Informacoes de cotacao e timestamp
        """
        rate = self.get_usd_brl_rate()
        is_cached = (time.time() - self.cache_timestamp < self.cache_duration)

        return {
            "rate": rate,
            "is_cached": is_cached,
            "cache_age_seconds": int(time.time() - self.cache_timestamp) if self.cache_timestamp > 0 else 0,
            "timestamp": datetime.fromtimestamp(self.cache_timestamp).isoformat() if self.cache_timestamp > 0 else None
        }
