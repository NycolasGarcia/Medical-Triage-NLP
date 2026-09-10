"""Orquestra os experimentos de baseline: validação cruzada, métricas e MLflow."""

import tempfile
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from src.data.labels import URGENCY_CLASSES
from src.features.vectorize import TfidfStrategy
from src.logging_config import configure_logging, get_logger
from src.models.evaluate import compute_metrics, confusion_matrix_3x3, count_sub_over_triage
from src.models.factory import build_model
from src.models.tracking import configure_tracking

logger = get_logger(__name__)

SEED = 42
N_SPLITS = 5
CANDIDATE_MODELS = ("dummy", "logreg", "random_forest")


def _evaluate_fold(model_name: str, X_text: pd.Series, y: pd.Series, train_idx, val_idx):
    vec = TfidfStrategy().build()
    X_train = vec.fit_transform(X_text.iloc[train_idx])
    X_val = vec.transform(X_text.iloc[val_idx])
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

    model = build_model(model_name)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)

    metrics = compute_metrics(y_val, y_pred, y_proba)
    confusion = confusion_matrix_3x3(y_val, y_pred)
    triage = count_sub_over_triage(y_val, y_pred)
    return metrics, confusion, triage


def _run_cv(model_name: str, X_text: pd.Series, y: pd.Series) -> dict:
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
    fold_results = [
        _evaluate_fold(model_name, X_text, y, tr, val) for tr, val in skf.split(X_text, y)
    ]
    metrics_list, confusions, triages = zip(*fold_results, strict=True)

    avg_metrics = {k: float(np.mean([m[k] for m in metrics_list])) for k in metrics_list[0]}
    confusion_total = np.sum(confusions, axis=0)
    triage_total = {k: sum(t[k] for t in triages) for k in triages[0]}
    return {"metrics": avg_metrics, "confusion_matrix": confusion_total, "triage": triage_total}


def _log_confusion_matrix(matrix: np.ndarray) -> None:
    df = pd.DataFrame(matrix, index=list(URGENCY_CLASSES), columns=list(URGENCY_CLASSES))
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "confusion_matrix.csv"
        df.to_csv(path)
        mlflow.log_artifact(str(path))


def _log_run(model_name: str, result: dict) -> None:
    with mlflow.start_run(run_name=model_name):
        mlflow.log_param("model", model_name)
        mlflow.log_param("n_splits", N_SPLITS)
        mlflow.log_param("seed", SEED)
        mlflow.log_metrics(result["metrics"])
        mlflow.log_metrics({f"triage_{k}": v for k, v in result["triage"].items()})
        _log_confusion_matrix(result["confusion_matrix"])


def run_all_experiments() -> dict[str, dict]:
    configure_tracking()
    train = pd.read_csv("data/processed/train.csv")
    X_text, y = train["text"], train["urgency_label"]

    results = {}
    for model_name in CANDIDATE_MODELS:
        result = _run_cv(model_name, X_text, y)
        _log_run(model_name, result)
        results[model_name] = result
        logger.info("experimento_concluido", extra={"modelo": model_name, **result["metrics"]})
    return results


if __name__ == "__main__":
    configure_logging()
    run_all_experiments()
