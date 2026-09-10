"""Smoke test trivial: o pacote importa e a configuração básica carrega sem erro."""

import logging

from src.config import settings
from src.logging_config import get_logger


def test_settings_carrega_com_valores_padrao():
    assert settings.api_port == 8000
    assert settings.environment == "development"


def test_get_logger_retorna_logger():
    logger = get_logger("smoke")
    assert isinstance(logger, logging.Logger)
