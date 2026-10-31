from abc import ABC, abstractmethod

from valutatrade_hub.core.exceptions import CurrencyNotFoundError


class Currency(ABC):

    def __init__(self, name: str, code: str):
        # Валидация (инварианты)
        if not name or not name.strip():
            raise ValueError("Название валюты не может быть пустым.")
        
        code = code.strip().upper()
        if not (2 <= len(code) <= 5):
            raise ValueError("Код валюты должен состоять из 2–5 символов.")
        
        self.name = name
        self.code = code

    @abstractmethod
    def get_display_info(self) -> str:
        pass

class FiatCurrency(Currency):

    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        if not issuing_country or not issuing_country.strip():
            raise ValueError("Страна/зона эмиссии не может быть пустой.")
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):

    def __init__(self, name: str, code: str, algorithm: str, market_cap: float):
        super().__init__(name, code)
        if not algorithm or not algorithm.strip():
            raise ValueError("Алгоритм не может быть пустым.")
        if market_cap < 0:
            raise ValueError("Рыночная капитализация не может быть отрицательной.")
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"    # noqa: E501

_CURRENCIES = {
    "USD": FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 4.5e11),
}


def get_currency(code: str) -> Currency:
    code = code.strip().upper()
    if code not in _CURRENCIES:
        raise CurrencyNotFoundError(f"Валюта с кодом '{code}' не найдена.")
    return _CURRENCIES[code]    