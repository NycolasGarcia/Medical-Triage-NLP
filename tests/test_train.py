"""Smoke test (§13): o pipeline de treino roda ponta a ponta numa amostra pequena, sem erro."""

from pathlib import Path

import joblib
import pandas as pd

from src.config import settings
from src.models.train import train_and_persist

_SAMPLE_TEXTS = [
    "sem sinais de isquemia aguda",
    "paciente estavel sem queixas",
    "dor toracica intensa com choque",
    "exame de rotina sem alteracoes",
    "quadro critico com instabilidade hemodinamica",
    "consulta de acompanhamento normal",
]
_SAMPLE_LABELS = ["atencao", "normal", "urgente", "normal", "urgente", "normal"]


def _write_sample_train_csv(tmp_path: Path) -> Path:
    df = pd.DataFrame({"text": _SAMPLE_TEXTS, "urgency_label": _SAMPLE_LABELS})
    path = tmp_path / "train.csv"
    df.to_csv(path, index=False)
    return path


def test_train_and_persist_roda_ponta_a_ponta(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "mlflow_tracking_uri", f"sqlite:///{tmp_path}/mlflow_test.db")
    train_path = _write_sample_train_csv(tmp_path)

    artifact_path = train_and_persist(
        train_path=str(train_path), model_dir=str(tmp_path / "models")
    )

    assert artifact_path.exists()
    pipeline = joblib.load(artifact_path)
    prediction = pipeline.predict(["sem sinais de dor toracica"])
    assert prediction[0] in {"normal", "atencao", "urgente"}
