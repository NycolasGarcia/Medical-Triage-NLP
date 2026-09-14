"""Logging estruturado central do projeto. Nenhum módulo deve usar print()."""

import json
import logging
import sys
from datetime import UTC, datetime

from src.config import settings

_STANDARD_RECORD_ATTRS = frozenset(logging.LogRecord("", 0, "", 0, "", (), None).__dict__)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        """Serializa o LogRecord em uma linha JSON (timestamp, nível, logger, mensagem, extras)."""
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = {k: v for k, v in record.__dict__.items() if k not in _STANDARD_RECORD_ATTRS}
        payload.update(extra)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging() -> None:
    """Configura o logger raiz para emitir JSON estruturado em stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level)


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger nomeado, já sob a configuração central."""
    return logging.getLogger(name)
