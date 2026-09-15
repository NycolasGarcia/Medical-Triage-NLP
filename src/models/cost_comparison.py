"""Caixa 6.3 — usa a matriz de custo (`src/models/cost.py`) para revisitar a escolha
de modelo, como o ADR-0003 já previa ("Como revisitar"): comparar Regressão
Logística contra Multinomial NB (menor sub-triagem de F2) sob custo explícito, agora
com a representação vencedora de 6.1 e a calibração isotônica de 6.2 aplicadas aos
dois candidatos igualmente — a comparação original de F2 usava TF-IDF simples, não
a representação atual, então não seria uma comparação justa reaproveitar aquele
resultado.
"""

import mlflow
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from src.features.vectorize import PRODUCTION_REPRESENTATION, build_representation
from src.logging_config import configure_logging, get_logger
from src.models.cost import mean_cost
from src.models.evaluate import compute_metrics, count_sub_over_triage
from src.models.factory import build_model
from src.models.tracking import configure_tracking

logger = get_logger(__name__)

SEED = 42
N_SPLITS = 5
CALIB_HOLDOUT_FRACTION = 0.2
CANDIDATES = ("logreg", "multinomial_nb")


def _build_base_pipeline(model_name: str) -> Pipeline:
    return Pipeline(
        [
            ("features", build_representation(PRODUCTION_REPRESENTATION)),
            ("clf", build_model(model_name)),
        ]
    )


def _fold_result(model_name: str, X_text, y, train_idx, val_idx) -> dict:
    X_train_full, y_train_full = X_text.iloc[train_idx], y.iloc[train_idx]
    X_val, y_val = X_text.iloc[val_idx], y.iloc[val_idx]

    X_fit, X_calib, y_fit, y_calib = train_test_split(
        X_train_full,
        y_train_full,
        test_size=CALIB_HOLDOUT_FRACTION,
        random_state=SEED,
        stratify=y_train_full,
    )
    base = _build_base_pipeline(model_name)
    base.fit(X_fit, y_fit)
    calibrated = CalibratedClassifierCV(estimator=FrozenEstimator(base), method="isotonic", cv=2)
    calibrated.fit(X_calib, y_calib)

    y_pred = calibrated.predict(X_val)
    y_proba = calibrated.predict_proba(X_val)
    metrics = compute_metrics(y_val, y_pred, y_proba)
    triage = count_sub_over_triage(y_val, y_pred)
    cost = mean_cost(y_val.to_numpy(), y_pred)
    return {"metrics": metrics, "triage": triage, "mean_cost": cost}


def _log_run(model_name: str, summary: dict) -> None:
    with mlflow.start_run(run_name=f"f6_cost_{model_name}"):
        mlflow.log_params({"model": model_name, "calibration": "isotonic", "seed": SEED})
        mlflow.log_metrics(summary["metrics"])
        mlflow.log_metrics({f"triage_{k}": v for k, v in summary["triage"].items()})
        mlflow.log_metric("mean_cost", summary["mean_cost"])


def run_cost_comparison() -> dict[str, dict]:
    configure_tracking()
    train = pd.read_csv("data/processed/train.csv")
    X_text, y = train["text"], train["urgency_label"]
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)

    summary = {}
    for model_name in CANDIDATES:
        fold_results = [
            _fold_result(model_name, X_text, y, tr, val) for tr, val in skf.split(X_text, y)
        ]
        avg_metrics = {
            k: float(np.mean([r["metrics"][k] for r in fold_results]))
            for k in fold_results[0]["metrics"]
        }
        triage_total = {
            k: sum(r["triage"][k] for r in fold_results) for k in fold_results[0]["triage"]
        }
        avg_cost = float(np.mean([r["mean_cost"] for r in fold_results]))
        summary[model_name] = {
            "metrics": avg_metrics,
            "triage": triage_total,
            "mean_cost": avg_cost,
        }
        _log_run(model_name, summary[model_name])
        logger.info(
            "comparacao_custo_avaliada",
            extra={
                "model": model_name,
                "f1_macro": avg_metrics["f1_macro"],
                "mean_cost": avg_cost,
                "recall_urgente": avg_metrics["recall_urgente"],
            },
        )
    return summary


if __name__ == "__main__":
    configure_logging()
    run_cost_comparison()
