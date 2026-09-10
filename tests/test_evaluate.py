"""Testa as métricas de avaliação, com foco na contagem de sub/sobre-triagem."""

import numpy as np

from src.models.evaluate import compute_metrics, confusion_matrix_3x3, count_sub_over_triage


def test_count_sub_over_triage():
    y_true = ["urgente", "normal", "atencao", "urgente"]
    y_pred = ["atencao", "normal", "urgente", "urgente"]

    result = count_sub_over_triage(y_true, y_pred)

    assert result == {"sub_triagem": 1, "sobre_triagem": 1, "acerto_exato": 2}


def test_confusion_matrix_3x3_shape_e_ordem():
    y_true = ["normal", "atencao", "urgente"]
    y_pred = ["normal", "atencao", "urgente"]

    matrix = confusion_matrix_3x3(y_true, y_pred)

    assert matrix.shape == (3, 3)
    assert np.array_equal(matrix, np.eye(3, dtype=int))


def test_compute_metrics_retorna_ao_menos_quatro_metricas():
    y_true = ["normal", "atencao", "urgente", "normal", "atencao", "urgente"]
    y_pred = ["normal", "atencao", "urgente", "atencao", "atencao", "urgente"]
    # colunas em ordem alfabetica (atencao, normal, urgente), como o sklearn espera
    y_proba = np.array(
        [
            [0.2, 0.7, 0.1],
            [0.8, 0.1, 0.1],
            [0.1, 0.1, 0.8],
            [0.7, 0.2, 0.1],
            [0.8, 0.1, 0.1],
            [0.1, 0.1, 0.8],
        ]
    )

    metrics = compute_metrics(y_true, y_pred, y_proba)

    assert len(metrics) >= 4
    assert 0.0 <= metrics["f1_macro"] <= 1.0
    assert metrics["recall_urgente"] == 1.0
