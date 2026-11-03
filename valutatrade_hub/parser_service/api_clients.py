"""Клиенты для работы с внешними API (CoinGecko и ExchangeRate-API)."""
from abc import ABC, abstractmethod

import requests

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import config


class BaseApiClient(ABC):
    """Абстрактный базовый класс для всех API-клиентов."""
    
    @abstractmethod
    def fetch_rates(self) -> dict:
        """Получает курсы валют из внешнего источника и возвращает их в стандартном формате."""  # noqa: E501
        pass


class CoinGeckoClient(BaseApiClient):
    """Клиент для получения курсов криптовалют с CoinGecko."""

    def fetch_rates(self) -> dict:
        """Запрашивает курсы криптовалют к USD и возвращает словарь вида {'BTC_USD': 59000}.""" # noqa: E501
        ids = ",".join(config.CRYPTO_ID_MAP.values())
        params = {
            "ids": ids,
            "vs_currencies": "usd",
        }

        try:
            response = requests.get(
                config.COINGECKO_URL, 
                params=params, 
                timeout=config.REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                raise ApiRequestError(
                    f"CoinGecko API вернул статус {response.status_code}: {response.text}" # noqa: E501
                )
                
            data = response.json()
            
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка сети при запросе к CoinGecko: {e}") from e
        except ValueError as e:
            raise ApiRequestError(f"Ошибка парсинга JSON от CoinGecko: {e}") from e

        result = {}
        for ticker, cg_id in config.CRYPTO_ID_MAP.items():
            if cg_id in data and "usd" in data[cg_id]:
                result[f"{ticker}_USD"] = data[cg_id]["usd"]

        return result    


class ExchangeRateApiClient(BaseApiClient):
    """Клиент для получения курсов фиатных валют с ExchangeRate-API."""

    def fetch_rates(self) -> dict:
        """Запрашивает курсы фиатных валют к USD и возвращает словарь вида {'EUR_USD': 1.08}.""" # noqa: E501
        if not config.EXCHANGE_RATE_API_KEY:
            return {"EUR_USD": 1.08, "RUB_USD": 0.01, "GBP_USD": 1.27}

        url = (
            f"{config.EXCHANGE_RATE_URL}/"
            f"{config.EXCHANGE_RATE_API_KEY}/latest/USD"
        )
        
        try:
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            
            if response.status_code != 200:
                raise ApiRequestError(
                    f"ExchangeRate API вернул статус {response.status_code}: {response.text}" # noqa: E501
                )
                
            data = response.json()
            
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка сети при запросе к ExchangeRate: {e}") from e
        except ValueError as e:
            raise ApiRequestError(f"Ошибка парсинга JSON от ExchangeRate: {e}") from e

        rates = data.get("conversion_rates", {})
        result = {}
        
        for code in config.FIAT_CURRENCIES:
            if code in rates:
                result[f"{code}_USD"] = rates[code]

        return result