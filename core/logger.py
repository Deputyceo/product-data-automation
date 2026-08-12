import logging
from datetime import datetime
from pathlib import Path
import sys

from config import LOGS_DIR, LOG_FORMAT, LOG_DATE_FORMAT


class AppLogger:
    """Provide application loggers with local file and console handlers."""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str = "ProductDataAutomation") -> logging.Logger:
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        log_filename = f"{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file_path = LOGS_DIR / log_filename

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        cls._loggers[name] = logger
        return logger
