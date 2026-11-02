"""Планировщик для регулярного обновления курсов."""
import logging
import time

from valutatrade_hub.infra.settings import SettingsLoader
from valutatrade_hub.parser_service.updater import RatesUpdater

logger = logging.getLogger(__name__)


def run_scheduler(updater: RatesUpdater):
    settings = SettingsLoader()
    interval = settings.RATES_TTL_SECONDS
    
    logger.info(f"Планировщик запущен. Интервал обновления: {interval} секунд.")
    
    try:
        while True:
            logger.info("Планировщик: запуск планового обновления курсов...")
            updater.run_update()
            
            logger.info(f"Планировщик: ожидание {interval} секунд до следующего запуска...") # noqa: E501
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Планировщик остановлен пользователем (Ctrl+C).")