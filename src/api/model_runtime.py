"""Carregamento do modelo persistido — chamado uma vez no startup da API (ADR pendente F3)."""

from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline

from src.config import settings

# Versionamento formal via MLflow Registry entra em F6 (caixa 6.10); por ora é o
# identificador do vencedor de F2/ADR-0003.
MODEL_VERSION = "f2-logreg"


def load_pipeline() -> Pipeline:
    """Carrega o pipeline TF-IDF + classificador persistido por `src.models.train`."""
    artifact_path = Path(settings.model_path) / "model.joblib"
    return joblib.load(artifact_path)
