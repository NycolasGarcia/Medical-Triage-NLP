"""Treina o modelo final (vencedor de F2, ADR-0003) e persiste o artefato para servir."""

from dataclasses import dataclass
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.pipeline import Pipeline

from src.config import settings
from src.features.vectorize import PRODUCTION_REPRESENTATION, build_representation
from src.logging_config import configure_logging, get_logger
from src.models.factory import build_model
from src.models.tracking import configure_tracking

logger = get_logger(__name__)

FINAL_MODEL_NAME = "logreg"  # vencedor de F2 entre 6 candidatos comparados — ver ADR-0003


@dataclass
class TrainResult:
    artifact_path: Path
    run_id: str


def build_pipeline() -> Pipeline:
    """Representação + classificador num único artefato exportável. Representação
    é a vencedora da caixa 6.1 (`PRODUCTION_REPRESENTATION`, ver `vectorize.py`)."""
    return Pipeline(
        [
            ("features", build_representation(PRODUCTION_REPRESENTATION)),
            ("clf", build_model(FINAL_MODEL_NAME)),
        ]
    )


def train_and_persist(
    train_path: str = "data/processed/train.csv",
    model_dir: str = settings.model_path,
) -> TrainResult:
    """Treina no dataset de treino completo (teste segue reservado) e salva o artefato."""
    train = pd.read_csv(train_path)
    pipeline = build_pipeline()
    pipeline.fit(train["text"], train["urgency_label"])

    artifact_path = Path(model_dir) / "model.joblib"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, artifact_path)

    configure_tracking()
    with mlflow.start_run(run_name="final_train_logreg") as run:
        mlflow.log_params({"model": FINAL_MODEL_NAME, "n_samples": len(train), "adr": "0003"})
        # skops (serialização padrão do mlflow.sklearn) recusa por padrão qualquer
        # callable que não seja de uma lib conhecida — `mark_negation` (caixa 6.1)
        # é nossa própria função, determinística e sem I/O; confiança explícita,
        # não um bypass geral de segurança (achado ao rodar os testes desta caixa).
        mlflow.sklearn.log_model(
            pipeline, name="model", skops_trusted_types=["src.features.negation.mark_negation"]
        )
        run_id = run.info.run_id

    logger.info("modelo_persistido", extra={"path": str(artifact_path), "n_samples": len(train)})
    return TrainResult(artifact_path=artifact_path, run_id=run_id)


if __name__ == "__main__":
    configure_logging()
    train_and_persist()
