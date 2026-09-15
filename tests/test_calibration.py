"""Testa as métricas de calibração (Brier multiclasse, ECE) e o fluxo por dobra
da caixa 6.2 — a lógica de bins do ECE é o ponto mais fácil de errar silenciosamente."""

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

from src.models.calibration import _brier_multiclass, _ece_binary, _fold_results

_LABELS = ["atencao", "normal", "urgente"]


def test_brier_multiclass_zero_quando_perfeito():
    y_true = ["urgente", "normal"]
    y_proba = np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    assert _brier_multiclass(y_true, y_proba, _LABELS) == pytest.approx(0.0)


def test_brier_multiclass_maximo_quando_totalmente_errado():
    y_true = ["urgente"]
    y_proba = np.array([[1.0, 0.0, 0.0]])  # previu "atencao" com certeza, era "urgente"
    # distância ao quadrado: (1-0)^2 + (0-0)^2 + (0-1)^2 = 2
    assert _brier_multiclass(y_true, y_proba, _LABELS) == pytest.approx(2.0)


def test_ece_zero_quando_confianca_bate_com_frequencia():
    # metade das amostras com prob 0.2 e 20% positivas; metade com prob 0.8 e 80% positivas
    y_true = np.array([0.0] * 8 + [1.0] * 2 + [0.0] * 2 + [1.0] * 8)
    y_prob = np.array([0.2] * 10 + [0.8] * 10)
    assert _ece_binary(y_true, y_prob, n_bins=10) == pytest.approx(0.0, abs=1e-9)


def test_ece_positivo_quando_desalinhado():
    # confiança sempre 0.9, mas nunca acerta
    y_true = np.zeros(10)
    y_prob = np.full(10, 0.9)
    assert _ece_binary(y_true, y_prob, n_bins=10) == pytest.approx(0.9)


@pytest.fixture
def tiny_dataset():
    # 20/classe: sobra amostra suficiente para os 2 splits estratificados aninhados
    # de _fold_results (treino externo -> fit/calib) sem violar o mínimo de 2
    # amostras por classe que o CalibratedClassifierCV exige mesmo com cv=2.
    rows = [
        (text, label)
        for label, texts in {
            "normal": [f"routine checkup stable patient number {i}" for i in range(20)],
            "atencao": [f"moderate concern requires monitoring case {i}" for i in range(20)],
            "urgente": [f"acute critical emergency shock patient {i}" for i in range(20)],
        }.items()
        for text in texts
    ]
    df = pd.DataFrame(rows, columns=["text", "urgency_label"])
    return df["text"], df["urgency_label"]


def test_fold_results_roda_as_3_variantes_sem_erro(tiny_dataset):
    X_text, y = tiny_dataset
    train_idx, val_idx = train_test_split(
        range(len(X_text)), test_size=0.2, random_state=42, stratify=y
    )
    results = _fold_results(X_text, y, train_idx, val_idx)
    assert set(results) == {"none", "sigmoid", "isotonic"}
    for r in results.values():
        assert 0.0 <= r["brier"] <= 2.0
        assert 0.0 <= r["ece_urgente"] <= 1.0
