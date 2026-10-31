import hashlib
import secrets
from datetime import datetime

from valutatrade_hub.core.exceptions import InsufficientFundsError


class User:
    def __init__(self, user_id, username, password, salt=None):
        self._user_id = user_id
        self._username = username
        self._salt = salt or self._generate_salt()
        self._hashed_password = self._hash_password(password)
        self._registration_date = datetime.now()

    @staticmethod
    def _generate_salt():
       
        return secrets.token_hex(4)

    def _hash_password(self, password):
        
        return hashlib.sha256((password + self._salt).encode()).hexdigest()


    def get_user_info(self):
        
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat(),
        }

    def change_password(self, new_password):
        
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов.")
        self._hashed_password = self._hash_password(new_password)

    def verify_password(self, password):
        
        return self._hash_password(password) == self._hashed_password

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if not value or not value.strip():
            raise ValueError("Имя не может быть пустым.")
        self._username = value

    @property
    def registration_date(self):
        return self._registration_date

    @property
    def hashed_password(self):
        return self._hashed_password

    @property
    def salt(self):
        return self._salt

class Wallet:
    def __init__(self, currency_code, balance=0.0):
        self._currency_code = currency_code
        self._balance = balance

    @property
    def balance(self):
        """Возвращает текущий баланс."""
        return self._balance

    @balance.setter
    def balance(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом.")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным.")
        self._balance = float(value)

    def deposit(self, amount):
        self._validate_amount(amount)
        self.balance = self._balance + amount

    def withdraw(self, amount):
        self._validate_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Недостаточно средств: доступно {self._balance:.2f} {self._currency_code}, " # noqa: E501
                f"требуется {amount:.2f} {self._currency_code}"
            )
        self.balance = self._balance - amount

    def get_balance_info(self):
        return {
            "currency_code": self._currency_code,
            "balance": self._balance,
        }    

    def _validate_amount(self, amount):
        if not isinstance(amount, (int, float)):
            raise ValueError("Сумма должна быть числом.")
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной.")

class Portfolio:
    def __init__(self, user):
        self._user = user
        self._wallets = {}  

    @property
    def user(self):
        return self._user

    @property
    def wallets(self):
        return self._wallets.copy()

    def add_currency(self, currency_code):
        if currency_code in self._wallets:
            raise ValueError(f'Кошелёк для {currency_code} уже существует.')
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code):
        if currency_code not in self._wallets:
            raise ValueError(f'Кошелёк для {currency_code} не найден.')
        return self._wallets[currency_code]

    def get_total_value(self, base_currency='USD'):
        exchange_rates = {
            "USD": 1.0,
            "EUR": 1.1,
            "BTC": 50000.0,
            "ETH": 3000.0,
        }

        total = 0.0
        for code, wallet in self._wallets.items():
            if code not in exchange_rates:
                raise ValueError(f'Курс для {code} не задан.')
            rate = exchange_rates[code]
            total += wallet.balance * rate
        return total      