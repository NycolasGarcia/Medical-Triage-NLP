"""Caixa 6.4 — busca dos limiares de `src/models/threshold.py`.

Protocolo: 5 dobras externas (seed 42, igual às demais caixas de F6) — em cada
uma, separa a fatia de calibração (mesmo protocolo de 6.2/6.3), ajusta
representação (6.1) + LogReg no restante, calibra isotônica na fatia separada, e
usa as probabilidades calibradas da dobra de validação (nunca vistas no ajuste)
para a busca de limiar. Probabilidades das 5 dobras são concatenadas ("out-of-fold
pooling") antes da busca em grade — evita ajustar limiar com viés otimista de dados
já vistos no treino/calibração.

Busca em duas etapas, não uma grade 2D completa: primeiro `THRESHOLD_URGENTE` (só
ele decide quem vira `urgente`, independente do limiar de `atenção`) — maior valor
que ainda cumpre `recall_urgente >= RECALL_URGENTE_TARGET`; depois `THRESHOLD_ATENCAO`
com o primeiro já fixado, minimizando custo médio (`src/models/cost.py`).
"""

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from src.features.vectorize import PRODUCTION_REPRESENTATION, build_representation
from src.logging_config import configure_logging, get_logger
from src.models.cost import mean_cost
from src.models.evaluate import count_sub_over_triage
from src.models.factory import build_model
from src.models.threshold import RECALL_URGENTE_TARGET, select_label
from src.models.tracking import configure_tracking

logger = get_logger(__name__)

SEED = 42
N_SPLITS = 5
CALIB_HOLDOUT_FRACTION = 0.2
_URGENTE_GRID = np.round(np.arange(0.05, 0.61, 0.01), 2)
_ATENCAO_GRID = np.round(np.arange(0.05, 0.96, 0.01), 2)


def _build_base_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("features", build_representation(PRODUCTION_REPRESENTATION)),
            ("clf", build_model("logreg")),
        ]
    )


def _fold_out_of_fold_proba(X_text: pd.Series, y: pd.Series, train_idx, val_idx) -> pd.DataFrame:
    X_train_full, y_train_full = X_text.iloc[train_idx], y.iloc[train_idx]
    X_val, y_val = X_text.iloc[val_idx], y.iloc[val_idx]

    X_fit, X_calib, y_fit, y_calib = train_test_split(
        X_train_full,
        y_train_full,
        test_size=CALIB_HOLDOUT_FRACTION,
        random_state=SEED,
        stratify=y_train_full,
    )
    base = _build_base_pipeline()
    base.fit(X_fit, y_fit)
    calibrated = CalibratedClassifierCV(estimator=FrozenEstimator(base), method="isotonic", cv=2)
    calibrated.fit(X_calib, y_calib)

    proba = calibrated.predict_proba(X_val)
    df = pd.DataFrame(proba, columns=calibrated.classes_)
    df["y_true"] = y_val.to_numpy()
    return df


def _collect_out_of_fold_proba() -> pd.DataFrame:
    train = pd.read_csv("data/processed/train.csv")
    X_text, y = train["text"], train["urgency_label"]
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
    parts = [_fold_out_of_fold_proba(X_text, y, tr, val) for tr, val in skf.split(X_text, y)]
    return pd.concat(parts, ignore_index=True)


def _recall_urgente(pooled: pd.DataFrame, threshold_urgente: float) -> float:
    predicted_urgente = pooled["urgente"] >= threshold_urgente
    true_urgente = pooled["y_true"] == "urgente"
    if true_urgente.sum() == 0:
        return 0.0
    return float((predicted_urgente & true_urgente).sum() / true_urgente.sum())


def _recall_urgente_from_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    true_urgente = y_true == "urgente"
    if true_urgente.sum() == 0:
        return 0.0
    return float(((y_pred == "urgente") & true_urgente).sum() / true_urgente.sum())


def _search_threshold_urgente(pooled: pd.DataFrame) -> float:
    """Maior `THRESHOLD_URGENTE` que ainda cumpre o piso de recall — minimiza
    sobre-triagem desnecessária entre os candidatos que cumprem a meta."""
    candidates = [t for t in _URGENTE_GRID if _recall_urgente(pooled, t) >= RECALL_URGENTE_TARGET]
    if not candidates:
        logger.info("piso_de_recall_inalcancavel_na_grade", extra={"menor_testado": 0.05})
        return float(_URGENTE_GRID.min())
    return float(max(candidates))


def _search_threshold_atencao(pooled: pd.DataFrame, threshold_urgente: float) -> float:
    y_true = pooled["y_true"].to_numpy()
    best_threshold, best_cost = _ATENCAO_GRID[0], float("inf")
    for t_atencao in _ATENCAO_GRID:
        y_pred = [
            select_label(row, threshold_urgente, t_atencao)
            for row in pooled[["normal", "atencao", "urgente"]].to_dict("records")
        ]
        cost = mean_cost(y_true, y_pred)
        if cost < best_cost:
            best_threshold, best_cost = t_atencao, cost
    return float(best_threshold)


def run_threshold_search() -> dict:
    configure_tracking()
    pooled = _collect_out_of_fold_proba()

    threshold_urgente = _search_threshold_urgente(pooled)
    threshold_atencao = _search_threshold_atencao(pooled, threshold_urgente)

    y_true = pooled["y_true"].to_numpy()
    y_pred_tuned = [
        select_label(row, threshold_urgente, threshold_atencao)
        for row in pooled[["normal", "atencao", "urgente"]].to_dict("records")
    ]
    y_pred_argmax = pooled[["normal", "atencao", "urgente"]].idxmax(axis=1).to_numpy()

    result = {
        "threshold_urgente": threshold_urgente,
        "threshold_atencao": threshold_atencao,
        "tuned": {
            "recall_urgente": _recall_urgente(pooled, threshold_urgente),
            "mean_cost": mean_cost(y_true, y_pred_tuned),
            "triage": count_sub_over_triage(y_true, y_pred_tuned),
        },
        "argmax": {
            "recall_urgente": _recall_urgente_from_predictions(y_true, y_pred_argmax),
            "mean_cost": mean_cost(y_true, y_pred_argmax),
            "triage": count_sub_over_triage(y_true, y_pred_argmax),
        },
    }
    logger.info("busca_limiar_concluida", extra=result)
    return result


if __name__ == "__main__":
    configure_logging()
    run_threshold_search()
