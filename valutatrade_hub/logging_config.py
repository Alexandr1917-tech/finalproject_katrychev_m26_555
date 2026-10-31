import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_level=logging.INFO):
    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handler = RotatingFileHandler(
        "logs/actions.log",
        maxBytes=1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger("valutatrade")
    logger.setLevel(log_level)
    logger.addHandler(handler)
    
    return logger


logger = setup_logging()