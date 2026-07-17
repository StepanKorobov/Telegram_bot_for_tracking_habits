import logging
import logging.config
import os
import sys
import json

SERVICE_NAME = os.getenv("SERVICE_NAME", "app")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


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
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
            "filters": ["service_name"],
        },
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console"],
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
