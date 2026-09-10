"""Configuração central do tracking MLflow (experimentos e runs)."""

import os

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")  # antes do import: silencia hint interno

import mlflow  # noqa: E402

from src.config import settings

EXPERIMENT_NAME = "triagem-urgencia"


def configure_tracking() -> None:
    """Aponta o MLflow para o backend SQLite local e seleciona o experimento."""
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)
