"""Métricas de avaliação do classificador de urgência (F1 por classe, custo FP/FN)."""

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, recall_score, roc_auc_score

from src.data.labels import URGENCY_CLASSES
from src.models.cost import mean_cost
from src.models.threshold import select_label

_LABELS_SORTED = sorted(URGENCY_CLASSES)  # ordem que o sklearn usa em predict_proba
_URGENCY_RANK = {label: i for i, label in enumerate(URGENCY_CLASSES)}  # normal<atencao<urgente


def compute_metrics(y_true, y_pred, y_proba) -> dict[str, float]:
    """≥ 4 métricas: F1 macro/weighted, recall por classe e ROC-AUC one-vs-rest."""
    recalls = recall_score(
        y_true, y_pred, labels=list(URGENCY_CLASSES), average=None, zero_division=0
    )
    metrics = {
        "f1_macro": f1_score(y_true, y_pred, average="macro"),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
        "roc_auc_ovr": roc_auc_score(y_true, y_proba, labels=_LABELS_SORTED, multi_class="ovr"),
    }
    for label, recall in zip(URGENCY_CLASSES, recalls, strict=True):
        metrics[f"recall_{label}"] = recall
    return metrics


def confusion_matrix_3x3(y_true, y_pred) -> np.ndarray:
    """Matriz de confusão 3x3, na ordem normal/atencao/urgente."""
    return confusion_matrix(y_true, y_pred, labels=list(URGENCY_CLASSES))


def count_sub_over_triage(y_true, y_pred) -> dict[str, int]:
    """Sub-triagem: predito menos urgente que o real (o erro perigoso).
    Sobre-triagem: predito mais urgente que o real (caro, mas seguro)."""
    true_rank = np.array([_URGENCY_RANK[y] for y in y_true])
    pred_rank = np.array([_URGENCY_RANK[y] for y in y_pred])
    diff = pred_rank - true_rank
    return {
        "sub_triagem": int((diff < 0).sum()),
        "sobre_triagem": int((diff > 0).sum()),
        "acerto_exato": int((diff == 0).sum()),
    }


def evaluate_pipeline(pipeline, test_path: str = "data/processed/test.csv") -> dict[str, float]:
    """Avalia um pipeline treinado no teste reservado (nunca visto em CV/treino).

    Usa `select_label` (limiar cumulativo, caixa 6.4/ADR-0005) para decidir a
    classe, não `pipeline.predict()` — a API de produção não usa argmax puro
    (`src/api/main.py`), então avaliar com argmax mediria uma política diferente
    da que de fato é servida."""
    test = pd.read_csv(test_path)
    y_true = test["urgency_label"]
    y_proba = pipeline.predict_proba(test["text"])
    classes = list(pipeline.classes_)
    y_pred = [select_label(dict(zip(classes, row, strict=True))) for row in y_proba]
    metrics = compute_metrics(y_true, y_pred, y_proba)
    triage = count_sub_over_triage(y_true, y_pred)
    return {
        **metrics,
        **{f"triage_{k}": v for k, v in triage.items()},
        "mean_cost": mean_cost(y_true.to_numpy(), np.array(y_pred)),
    }
