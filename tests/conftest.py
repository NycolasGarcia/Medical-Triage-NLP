"""Fixtures compartilhadas: dataset mínimo e isolamento do MLflow real em testes."""

from pathlib import Path

import pandas as pd
import pytest

from src.config import settings

_SAMPLE_TEXTS = [
    "sem sinais de isquemia aguda",
    "paciente estavel sem queixas",
    "dor toracica intensa com choque",
    "exame de rotina sem alteracoes",
    "quadro critico com instabilidade hemodinamica",
    "consulta de acompanhamento normal",
]
_SAMPLE_LABELS = ["atencao", "normal", "urgente", "normal", "urgente", "normal"]


@pytest.fixture
def sample_train_csv(tmp_path: Path) -> Path:
    """CSV pequeno com as 3 classes de urgência, para testes de pipeline ponta a ponta."""
    df = pd.DataFrame({"text": _SAMPLE_TEXTS, "urgency_label": _SAMPLE_LABELS})
    path = tmp_path / "train.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def isolated_mlflow(tmp_path: Path, monkeypatch):
    """Evita que testes gravem runs no `mlflow.db` real do projeto."""
    monkeypatch.setattr(settings, "mlflow_tracking_uri", f"sqlite:///{tmp_path}/mlflow_test.db")
