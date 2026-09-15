"""Treina o modelo final (vencedor de F2, ADR-0003) e persiste o artefato para servir."""

from dataclasses import dataclass
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.config import settings
from src.features.vectorize import PRODUCTION_REPRESENTATION, build_representation
from src.logging_config import configure_logging, get_logger
from src.models.factory import build_model
from src.models.tracking import configure_tracking

logger = get_logger(__name__)

FINAL_MODEL_NAME = "logreg"  # vencedor de F2 entre 6 candidatos comparados — ver ADR-0003
# Vencedora da caixa 6.2 (ver docs/EXPERIMENTS.md, seção F6): isotônica teve o menor
# Brier e ECE da bateria e, como efeito colateral relevante para §7, reduziu
# sub-triagem de 12,1% para 9,3% mesmo antes do ajuste de limiar de caixa 6.4.
CALIBRATION_METHOD = "isotonic"
CALIB_HOLDOUT_FRACTION = 0.2
SEED = 42


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


def _fit_calibrated(X: pd.Series, y: pd.Series) -> CalibratedClassifierCV:
    """Separa uma fatia de calibração (20%, estratificada) do treino, ajusta a
    representação + LogReg só no restante e calibra (isotônica, vencedora da
    caixa 6.2) só na fatia separada — mesmo protocolo de `src/models/calibration.py`,
    aplicado uma vez sobre todo o treino disponível em vez de em CV."""
    X_fit, X_calib, y_fit, y_calib = train_test_split(
        X, y, test_size=CALIB_HOLDOUT_FRACTION, random_state=SEED, stratify=y
    )
    pipeline = build_pipeline()
    pipeline.fit(X_fit, y_fit)

    calibrated = CalibratedClassifierCV(
        estimator=FrozenEstimator(pipeline), method=CALIBRATION_METHOD, cv=2
    )
    calibrated.fit(X_calib, y_calib)
    return calibrated


def train_and_persist(
    train_path: str = "data/processed/train.csv",
    model_dir: str = settings.model_path,
) -> TrainResult:
    """Treina no dataset de treino completo (teste segue reservado) e salva o artefato,
    já calibrado (caixa 6.2) — 20% do treino vira fatia de calibração, não entra no
    ajuste da representação/classificador."""
    train = pd.read_csv(train_path)
    calibrated_pipeline = _fit_calibrated(train["text"], train["urgency_label"])

    artifact_path = Path(model_dir) / "model.joblib"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(calibrated_pipeline, artifact_path)

    configure_tracking()
    with mlflow.start_run(run_name="final_train_logreg") as run:
        mlflow.log_params(
            {
                "model": FINAL_MODEL_NAME,
                "n_samples": len(train),
                "adr": "0003",
                "calibration_method": CALIBRATION_METHOD,
                "calib_holdout_fraction": CALIB_HOLDOUT_FRACTION,
            }
        )
        # skops (serialização padrão do mlflow.sklearn) recusa por padrão qualquer
        # tipo fora da allowlist embutida dela: `mark_negation` (caixa 6.1) é nossa
        # própria função; `_CalibratedClassifier` (caixa 6.2) é interno do sklearn,
        # só não está na allowlist padrão da skops por ser uma classe privada pouco
        # comum. Confiança explícita nos dois, não um bypass geral de segurança.
        mlflow.sklearn.log_model(
            calibrated_pipeline,
            name="model",
            skops_trusted_types=[
                "src.features.negation.mark_negation",
                "sklearn.calibration._CalibratedClassifier",
            ],
        )
        run_id = run.info.run_id

    logger.info("modelo_persistido", extra={"path": str(artifact_path), "n_samples": len(train)})
    return TrainResult(artifact_path=artifact_path, run_id=run_id)


if __name__ == "__main__":
    configure_logging()
    train_and_persist()
