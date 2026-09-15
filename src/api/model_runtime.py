"""Carregamento do modelo persistido — chamado uma vez no startup da API (ADR pendente F3)."""

from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline

from src.config import settings

# Versionamento formal via MLflow Registry entra em F6 (caixa 6.10); por ora é o
# identificador da representação vencedora de caixa 6.1 (ver docs/EXPERIMENTS.md).
MODEL_VERSION = "f6-logreg-negation-charngrams"


def load_pipeline() -> Pipeline:
    """Carrega o pipeline de representação + classificador persistido por `src.models.train`."""
    artifact_path = Path(settings.model_path) / "model.joblib"
    return joblib.load(artifact_path)
