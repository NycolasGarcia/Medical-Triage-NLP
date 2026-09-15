"""Testa a lógica de suporte da busca de representação (caixa 6.1) — em especial
o reordenamento de colunas de probabilidade do classificador ordinal, o ponto mais
fácil de acertar silenciosamente errado (ver docstring de `_reorder_ordinal_proba`)."""

import numpy as np
import pandas as pd
import pytest

from src.features.vectorize import RepresentationConfig
from src.models.representation_tuning import _reorder_ordinal_proba, run_cv

# 10 amostras por classe — mínimo para caber em 5 dobras estratificadas sem erro.
_SAMPLE_TEXTS = {
    "normal": [f"routine checkup stable patient number {i}" for i in range(10)],
    "atencao": [f"moderate concern requires monitoring case {i}" for i in range(10)],
    "urgente": [f"acute critical emergency shock patient {i}" for i in range(10)],
}


@pytest.fixture
def tiny_dataset():
    rows = [(text, label) for label, texts in _SAMPLE_TEXTS.items() for text in texts]
    df = pd.DataFrame(rows, columns=["text", "urgency_label"])
    return df["text"], df["urgency_label"]


def test_reorder_ordinal_proba_alinha_com_ordem_alfabetica():
    # classes_ do mord em ordem ordinal: 0=normal, 1=atencao, 2=urgente
    y_proba = np.array([[0.7, 0.2, 0.1]])  # colunas: normal, atencao, urgente
    reordered = _reorder_ordinal_proba(y_proba, classes_=np.array([0, 1, 2]))
    # saída deve estar em ordem alfabética: atencao, normal, urgente
    assert reordered.tolist() == [[0.2, 0.7, 0.1]]


def test_run_cv_baseline_roda_sem_erro(tiny_dataset):
    X_text, y = tiny_dataset
    result = run_cv(RepresentationConfig(name="smoke"), X_text, y)
    assert "f1_macro" in result["metrics"]
    assert set(result["triage"]) == {"sub_triagem", "sobre_triagem", "acerto_exato"}


def test_run_cv_ordinal_roda_sem_erro(tiny_dataset):
    X_text, y = tiny_dataset
    result = run_cv(RepresentationConfig(name="smoke_ordinal"), X_text, y, ordinal=True)
    assert 0.0 <= result["metrics"]["f1_macro"] <= 1.0
