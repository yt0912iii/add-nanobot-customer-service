"""Structlog configuration for the application"""

import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog
from structlog.types import EventDict, Processor

from config import settings

# Paths to exclude from traceback (keep only app code)
_EXC_SKIP_PATH_PARTS = ("site-packages", ".venv", "lib/python")


def _format_exc_app_frames_only(exc_info: tuple) -> str:
    """Format exception traceback keeping only frames from app code (exclude site-packages/.venv)."""
    typ, val, tb = exc_info
    if tb is None:
        return "".join(traceback.format_exception_only(typ, val))
    extracted = traceback.extract_tb(tb)
    kept = [f for f in extracted if not any(skip in f.filename for skip in _EXC_SKIP_PATH_PARTS)]
    if not kept:
        kept = extracted[-1:]  # keep at least the last frame
    lines = traceback.format_list(kept) + traceback.format_exception_only(typ, val)
    return "".join(lines)


def filter_exc_info_app_frames(_: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
    """Replace full exc_info with a short traceback (app frames only). Removes exc_info from event."""
    exc_info = event_dict.pop("exc_info", None)
    if exc_info is None or exc_info is False:
        return event_dict
    if exc_info is True:
        exc_info = sys.exc_info()
    if not isinstance(exc_info, tuple) or len(exc_info) != 3:
        return event_dict
    event_dict["exception"] = _format_exc_app_frames_only(exc_info)
    return event_dict


def configure_logging() -> None:
    """Configure structlog with ProcessorFormatter for clean JSON output

    Architecture: Shared processors transform events, then ProcessorFormatter
    renders them differently per handler (JSON for files/prod, Console for dev).
    This avoids mixing text prefixes with JSON output.
    """

    # Shared processors: transform but don't render (rendering happens in formatters)
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Short traceback: only app frames (exclude site-packages/.venv)
    shared_processors.append(filter_exc_info_app_frames)

    structlog.configure(
        processors=shared_processors
        + [
            # Wrap for ProcessorFormatter to handle rendering per handler
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    root_logger.handlers.clear()

    # ProcessorFormatter: defer rendering to avoid "text prefix + JSON" problem
    json_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )

    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(
            colors=sys.stderr.isatty(),
            pad_event=30,
            sort_keys=False,
        ),
        foreign_pre_chain=shared_processors,
    )

    # Console: human-readable in dev, JSON in prod (for CloudWatch/ELK/Loki)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    if settings.ENVIRONMENT == "local":
        console_handler.setFormatter(console_formatter)
    else:
        console_handler.setFormatter(json_formatter)

    root_logger.addHandler(console_handler)

    # File handlers: for traditional deployments (VMs). Disable in containers.
    
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    app_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=settings.LOG_ROTATION_BYTES,
        backupCount=settings.LOG_RETENTION_COUNT,
        encoding="utf-8",
    )
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(json_formatter)
    root_logger.addHandler(app_handler)

    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=settings.LOG_ROTATION_BYTES,
        backupCount=settings.LOG_RETENTION_COUNT,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    root_logger.addHandler(error_handler)

    # Suppress verbose third-party logs (access logs, HTTP client internals)
    noisy_loggers = [
        "granian.access",
        # "granian.error",
        "httpx",
        "httpcore",
        "openai",
        "anthropic",
        "urllib3",
        "grpc._cython.cygrpc",
        "watchfiles.main",  # Hot reload file watcher
        "python_multipart",
        "langchain_milvus.vectorstores.milvus",
        "neo4j",
        "hpack",
        "pymongo",
        "authlib",
    ]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    # TODO: 未來思考有沒有更好過濾 third-party logs的方法
    logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
