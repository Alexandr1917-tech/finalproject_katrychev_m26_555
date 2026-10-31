class CurrencyNotFoundError(Exception):
    """Исключение, когда валюта с таким кодом не найдена."""
    pass


class InsufficientFundsError(Exception):
    """Исключение, когда на кошельке недостаточно средств."""
    pass


class ApiRequestError(Exception):
    """Исключение, когда внешний API (Parser Service) недоступен."""
    pass