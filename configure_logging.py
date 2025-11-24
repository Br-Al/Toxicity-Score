import os.path
import logging
import logging.config
import structlog
import contextvars
from typing import Dict, Any, Optional


execution_context: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar("execution_context", default={})

def inject_context(logger, method_name, event_dict):
    context = execution_context.get()
    if context:
        event_dict.update(context)

    return event_dict

def configure_logging(config_settings, additional_processors: Optional[list] = None):
    shared_processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        inject_context,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
    ]
    if additional_processors:
        shared_processors.extend(additional_processors)
    structlog_only_processors = [
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    ]

    structlog.configure(
        processors=shared_processors + structlog_only_processors,
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    loggers = {
        "": {
            "level": config_settings.LOG_LEVEL if hasattr(config_settings, "LOG_LEVEL") else "INFO",
            "handlers": ["console", "json_file"]
        },
    }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "plain_console": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(
                        sort_keys=True,
                        pad_event=40,
                        colors=True,
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
                    "formatter": "plain_console",
                },
                "json_file": {
                    "class": "logging.handlers.WatchedFileHandler",
                    "filename": os.path.join(config_settings.LOGGING_PATH, config_settings.LOGGING_FILE),
                    "formatter": "json",
                },
            },
            "loggers": loggers,
        }
    )


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    logger_name = name if name else __name__

    return structlog.get_logger(logger_name)