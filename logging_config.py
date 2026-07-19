import json
import logging
import logging.config
import os
import sys
from pathlib import Path

SERVICE_NAME = os.getenv("SERVICE_NAME", "app")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.getenv("LOG_FILE", f"{SERVICE_NAME}.log")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "service": getattr(record, "service", None),
            "logger": record.name,
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        return json.dumps(log_record, ensure_ascii=False)


class ServiceNameFilter(logging.Filter):
    def filter(self, record):
        record.service = SERVICE_NAME
        return True


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "service_name": {
            "()": ServiceNameFilter,
        },
    },
    "formatters": {
        "standard": {
            # "format": "%(asctime)s | %(levelname)s | %(service)s | %(module)s | %(name)s | %(pathname)s | %(filename)s | %(lineno)d | %(message)s | %(funcName)s",
            "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        },
        "json": {
            "()": JsonFormatter,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
            "filters": ["service_name"],
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filters": ["service_name"],
            "filename": "",  # заполним при setup_logging
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console", "file"],
    },
}


def setup_logging():
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    LOGGING_CONFIG["handlers"]["file"]["filename"] = str(log_dir / LOG_FILE)

    logging.config.dictConfig(LOGGING_CONFIG)
