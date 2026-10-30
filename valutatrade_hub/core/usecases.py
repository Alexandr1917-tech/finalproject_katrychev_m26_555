import hashlib
from datetime import datetime, timedelta

from valutatrade_hub.core.models import User
from valutatrade_hub.core.utils import (
    META_FILE,
    PORTFOLIO_FILE,
    load_json,
    load_portfolio,
    load_rates,
    load_session,
    save_json,
    save_rates,
    save_session,
)

USER_ID = 1


def register_user(username, password):
    if not username or not username.strip():
        raise ValueError("Имя пользователя не может быть пустым.")
    if len(password) < 4:
        raise ValueError("Пароль должен быть не короче 4 символов.")

    users = load_json(META_FILE, default=[])
    if any(u["username"] == username for u in users):
        raise ValueError(f"Имя пользователя '{username}' уже занято")

    user_id = max([u["user_id"] for u in users], default=0) + 1
    user = User(user_id, username, password)

    user_dict = {
        "user_id": user.user_id,
        "username": user.username,
        "hashed_password": user.hashed_password,
        "salt": user.salt,
        "registration_date": user.registration_date.isoformat(),
    }
    users.append(user_dict)
    save_json(META_FILE, users)

    portfolios = load_json(PORTFOLIO_FILE, default=[])
    portfolios.append({"user_id": user_id, "wallets": {}})
    save_json(PORTFOLIO_FILE, portfolios)

    return user

def login_user(username, password):
    users = load_json(META_FILE, default=[])
    user_data = next((u for u in users if u["username"] == username), None)

    if user_data is None:
        raise ValueError(f"Пользователь '{username}' не найден")

    salt = user_data["salt"]
    hashed_input = hashlib.sha256((password + salt).encode()).hexdigest()
    if hashed_input != user_data["hashed_password"]:
        raise ValueError("Неверный пароль")

    save_session(user_data["user_id"])
    return user_data["user_id"], user_data["username"]

def get_portfolio_info(base_currency="USD"):
    user_id = load_session()
    if user_id is None:
        raise ValueError("Сначала выполните login")

    exchange_rates = {
        "USD": 1.0,
        "EUR": 1.1,
        "BTC": 50000.0,
        "ETH": 3000.0,
    }
    if base_currency not in exchange_rates:
        raise ValueError(f"Неизвестная базовая валюта '{base_currency}'")

    portfolio = load_portfolio(user_id)
    if portfolio is None or not portfolio.get("wallets"):
        return None

    base_rate = exchange_rates[base_currency]
    items = []
    total = 0.0

    for code, wallet_data in portfolio["wallets"].items():
        balance = wallet_data["balance"]
        rate = exchange_rates[code]
        value_in_base = (balance * rate) / base_rate
        items.append({
            "currency_code": code,
            "balance": balance,
            "value_in_base": value_in_base,
        })
        total += value_in_base

    return {
        "user_id": user_id,
        "base_currency": base_currency,
        "items": items,
        "total": total,
    }

def buy_currency(currency_code, amount, base_currency="USD"):
    user_id = load_session()
    if user_id is None:
        raise ValueError("Сначала выполните login")

    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    if not currency_code or not currency_code.strip():
        raise ValueError("Код валюты не может быть пустым")
    currency_code = currency_code.upper()

    exchange_rates = {
        "USD": 1.0,
        "EUR": 1.1,
        "BTC": 50000.0,
        "ETH": 3000.0,
    }
    if currency_code not in exchange_rates:
        raise ValueError(f"Не удалось получить курс для {currency_code}->{base_currency}") # noqa: E501

    portfolios = load_json(PORTFOLIO_FILE, default=[])
    portfolio = next((p for p in portfolios if p["user_id"] == user_id), None)
    if portfolio is None:
        portfolio = {"user_id": user_id, "wallets": {}}
        portfolios.append(portfolio)

    wallets = portfolio["wallets"]
    old_balance = wallets.get(currency_code, {}).get("balance", 0.0)
    new_balance = old_balance + amount
    wallets[currency_code] = {"balance": new_balance}

    save_json(PORTFOLIO_FILE, portfolios)

    rate = exchange_rates[currency_code]
    cost = amount * rate

    return {
        "currency_code": currency_code,
        "amount": amount,
        "old_balance": old_balance,
        "new_balance": new_balance,
        "rate": rate,
        "cost": cost,
        "base_currency": base_currency,
    }

DEFAULT_RATES = {
    "USD": 1.0,
    "EUR": 1.1,
    "BTC": 59337.21,
    "ETH": 3720.00,
}

def get_rate(from_currency, to_currency):
    if not from_currency or not from_currency.strip():
        raise ValueError("Код исходной валюты не может быть пустым")
    if not to_currency or not to_currency.strip():
        raise ValueError("Код целевой валюты не может быть пустым")

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    pair_key = f"{from_currency}_{to_currency}"
    reverse_key = f"{to_currency}_{from_currency}"

    rates = load_rates()

    if pair_key in rates:
        cached = rates[pair_key]
        updated_at = datetime.fromisoformat(cached["updated_at"])
        if datetime.now() - updated_at < timedelta(minutes=5):
            return {
                "rate": cached["rate"],
                "updated_at": cached["updated_at"],
                "reverse_rate": rates.get(reverse_key, {}).get("rate"),
            }

    if from_currency not in DEFAULT_RATES or to_currency not in DEFAULT_RATES:
        raise ValueError(f"Курс {from_currency}->{to_currency} недоступен. Повторите попытку позже.") # noqa: E501

    rate = DEFAULT_RATES[from_currency] / DEFAULT_RATES[to_currency]

    now = datetime.now()
    rates[pair_key] = {
        "rate": rate,
        "updated_at": now.isoformat(),
    }
    rates[reverse_key] = {
        "rate": 1.0 / rate if rate != 0 else 0.0,
        "updated_at": now.isoformat(),
    }
    rates["source"] = "ParserService"
    rates["last_refresh"] = now.isoformat()

    save_rates(rates)

    return {
        "rate": rate,
        "updated_at": now.isoformat(),
        "reverse_rate": rates[reverse_key]["rate"],
    }