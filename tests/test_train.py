"""Smoke test (§13): o pipeline de treino roda ponta a ponta numa amostra pequena, sem erro."""

import joblib

from src.models.train import train_and_persist


def test_train_and_persist_roda_ponta_a_ponta(sample_train_csv, isolated_mlflow, tmp_path):
    result = train_and_persist(train_path=str(sample_train_csv), model_dir=str(tmp_path / "models"))

    assert result.artifact_path.exists()
    assert result.run_id
    pipeline = joblib.load(result.artifact_path)
    prediction = pipeline.predict(["sem sinais de dor toracica"])
    assert prediction[0] in {"normal", "atencao", "urgente"}
