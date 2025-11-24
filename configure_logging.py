import os.path
import logging
import logging.config
import uuid
from datetime import datetime
import structlog
from config import settings
from contextlib import asynccontextmanager
import contextvars
from typing import Dict, Any, Optional


CENSOR_FIELDS = [
    "password",
    "username",
    "ipAddress",
    "Authorization",
    "API_KEY",
    "X-API-KEY"
]

LARGE_FIELDS = [
    "document",
    "file_content",
    "file",
    "base64_content"
]

execution_context: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar("execution_context", default={})

class CensoringFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        for field in CENSOR_FIELDS:
            if field in record.getMessage():
                record.msg = record.getMessage().replace(record.args.get(field, ""), "****")
        return True


def inject_context(logger, method_name, event_dict):
    context = execution_context.get()
    if context:
        event_dict.update(context)

    return event_dict


def configure_logging(config_settings):

    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        inject_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.processors.JSONRenderer()
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    loggers = {
        "": {
            "level": config_settings.LOG_LEVEL if hasattr(config_settings, "LOG_LEVEL") else "INFO",
            "handlers": ["console", "json_file"],
            "filters": ["censoring_filter"]
        },
    }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "censoring_filter": {
                    "()": CensoringFilter,
                },
            },
            "formatters": {
                "standard": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(
                        colors=True
                    ),
                    "foreign_pre_chain": shared_processors,
                },
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                    "foreign_pre_chain": shared_processors
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "filters": ["censoring_filter"],
                },
                "json_file": {
                    "class": "logging.FileHandler",
                    "filename": os.path.join(config_settings.LOGGING_PATH, config_settings.LOGGING_FILE),
                    "formatter": "json",
                    "filters": ["censoring_filter"],
                },
            },
            "loggers": loggers,
        }
    )