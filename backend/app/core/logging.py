
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from backend.app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings with structured data.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string.
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Include detailed exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include extra attributes passed in extra={}
        # Filter out standard LogRecord attributes to avoid clutter
        # This is a basic filter, might need tuning
        standard_attrs = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())
        for key, value in record.__dict__.items():
            if key not in standard_attrs and key not in ["message", "asctime"]:
                log_data[key] = value

        return json.dumps(log_data)


def setup_logging() -> None:
    """
    Configure the root logger and other loggers to use JSON format.
    """
    settings = get_settings()
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplication (e.g. from uvicorn's default config)
    root_logger.handlers = []
    root_logger.addHandler(handler)

    # Configure Uvicorn loggers to use our handler
    # access logs might be redundant if we have structured request logging middleware
    # but for now, let's just structure them.
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.addHandler(handler)
        logger.propagate = False  # Prevent double logging if root logger also catches it

