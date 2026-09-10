"""Métricas de avaliação do classificador de urgência (F1 por classe, custo FP/FN)."""

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, recall_score, roc_auc_score

from src.data.labels import URGENCY_CLASSES

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
