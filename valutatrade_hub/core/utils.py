import json
import os

META_FILE = "data/users.json"
PORTFOLIO_FILE = "data/portfolios.json"


def load_json(filepath, default=None):
    if not os.path.exists(filepath):
        return default if default is not None else {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return default if default is not None else {}


def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

SESSION_FILE = "data/session.json"


def save_session(user_id):
    save_json(SESSION_FILE, {"user_id": user_id})


def load_session():
    data = load_json(SESSION_FILE, default={})
    return data.get("user_id")


def clear_session():
    save_json(SESSION_FILE, {})        

def load_portfolio(user_id):
    portfolios = load_json(PORTFOLIO_FILE, default=[])
    for p in portfolios:
        if p["user_id"] == user_id:
            return p
    return None    

RATES_FILE = "data/rates.json"


def load_rates():
    return load_json(RATES_FILE, default={})


def save_rates(rates):
    save_json(RATES_FILE, rates)