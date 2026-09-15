"""Fixtures compartilhadas: dataset mínimo e isolamento do MLflow real em testes."""

from pathlib import Path

import pandas as pd
import pytest

from src.config import settings

_BASE_PHRASES = {
    "atencao": "sem sinais de isquemia aguda, caso {i} sob observação",
    "normal": "paciente estavel sem queixas, consulta de rotina {i}",
    "urgente": "dor toracica intensa com choque, quadro critico {i}",
}
# 10 por classe: mínimo para o split estratificado de calibração (caixa 6.2,
# CALIB_HOLDOUT_FRACTION=0.2) conseguir >= 2 amostras por classe na fatia de
# calibração sem lançar ValueError do CalibratedClassifierCV.
_SAMPLE_TEXTS = [phrase.format(i=i) for phrase in _BASE_PHRASES.values() for i in range(10)]
_SAMPLE_LABELS = [label for label in _BASE_PHRASES for _ in range(10)]


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
