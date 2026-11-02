"""Операции чтения/записи exchange_rates.json."""
import json
import os
import tempfile
from datetime import datetime, timezone

EXCHANGE_RATES_FILE = "data/exchange_rates.json"


def load_exchange_rates():
    if not os.path.exists(EXCHANGE_RATES_FILE):
        return []
    try:
        with open(EXCHANGE_RATES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_exchange_rates(records):
    os.makedirs("data", exist_ok=True)

    fd, temp_path = tempfile.mkstemp(dir="data", suffix=".json.tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, EXCHANGE_RATES_FILE)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise

def _make_id(from_code, to_code, timestamp_iso):
    return f"{from_code.upper()}_{to_code.upper()}_{timestamp_iso}"


def add_rate_record(from_code, to_code, rate, source, meta=None):
    from_code = from_code.strip().upper()
    to_code = to_code.strip().upper()

    if not (2 <= len(from_code) <= 5) or not (2 <= len(to_code) <= 5):
        raise ValueError("Коды валют должны быть от 2 до 5 символов.")

    if not isinstance(rate, (int, float)):
        raise ValueError(f"Курс должен быть числом, получено: {type(rate).__name__}")

    
    timestamp_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record_id = _make_id(from_code, to_code, timestamp_iso)

    records = load_exchange_rates()

    if any(r.get("id") == record_id for r in records):
        return None 

    record = {
        "id": record_id,
        "from_currency": from_code,
        "to_currency": to_code,
        "rate": rate,
        "timestamp": timestamp_iso,
        "source": source,
        "meta": meta or {},
    }

    records.append(record)
    save_exchange_rates(records)
    return record    