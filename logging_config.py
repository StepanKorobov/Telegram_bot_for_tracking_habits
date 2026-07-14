import logging
import logging.config
import os
import sys

SERVICE_NAME = os.getenv("SERVICE_NAME", "app")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


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
            "format": "%(asctime)s | %(levelname)s | %(service)s | %(name)s | %(lineno)d | %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "standard",
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
