"""Основной модуль обновления курсов (сбор, сохранение, кэш)."""
import json
import logging
import os
import tempfile
from datetime import datetime, timezone

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.storage import add_rate_record

logger = logging.getLogger(__name__)

RATES_CACHE_FILE = "data/rates.json"


class RatesUpdater:
    def __init__(self, clients, storage_module):

        self.clients = clients
        self.storage = storage_module

    def run_update(self):
        logger.info("Начало обновления курсов...")

        all_rates = {}
        sources_meta = {}

        for client in self.clients:
            client_name = client.__class__.__name__
            logger.info(f"Запрос к {client_name}...")
            
            try:
                rates = client.fetch_rates()
                all_rates.update(rates)
                sources_meta[client_name] = "ok"
                logger.info(f"Успешно получено {len(rates)} курсов от {client_name}.")
                
            except ApiRequestError as e:
                sources_meta[client_name] = f"error: {e}"
                logger.error(f"Ошибка при запросе к {client_name}: {e}")
                continue

        if not all_rates:
            logger.error("Не удалось получить ни одного курса. Сохранение отменено.")
            return {}

        added_count = 0
        for pair, rate in all_rates.items():
            if "_" in pair:
                from_code, to_code = pair.split("_", 1)
            else:
                from_code, to_code = pair, "USD"

            source = "CoinGecko" if from_code in ("BTC", "ETH", "SOL") else "ExchangeRate-API" # noqa: E501
            meta = {"meta": sources_meta.get(source)}

            record = add_rate_record(
                from_code=from_code,
                to_code=to_code,
                rate=rate,
                source=source,
                meta=meta,
            )
            if record:
                added_count += 1

        logger.info(f"В журнал добавлено новых записей: {added_count}")

        os.makedirs("data", exist_ok=True)
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        cache_data = {
            "pairs": {},
            "last_refresh": now_iso,
        }

        for pair, rate in all_rates.items():
            source = "CoinGecko" if pair.split("_")[0] in ("BTC", "ETH", "SOL") else "ExchangeRate-API" # noqa: E501
            cache_data["pairs"][pair] = {
                "rate": rate,
                "updated_at": now_iso,
                "source": source,
            }

        fd, temp_path = tempfile.mkstemp(dir="data", suffix=".json.tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, RATES_CACHE_FILE)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

        logger.info(f"Кэш {RATES_CACHE_FILE} обновлён. Курсов в кэше: {len(cache_data['pairs'])}") # noqa: E501
        logger.info("Обновление курсов завершено.")

        return {
            "added_records": added_count,
            "total_rates": len(all_rates),
            "timestamp": now_iso,
        }