"""Testa a lógica de busca de limiar (caixa 6.4) sobre um DataFrame sintético de
probabilidades — sem rodar CV real, só a extração do limiar que cumpre a meta."""

import pandas as pd

from src.models.threshold_search import (
    _recall_urgente,
    _search_threshold_atencao,
    _search_threshold_urgente,
)


def _pooled(rows: list[tuple[float, float, float, str]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["normal", "atencao", "urgente", "y_true"])


def test_recall_urgente_conta_so_os_positivos_reais():
    pooled = _pooled(
        [
            (0.1, 0.1, 0.8, "urgente"),  # >= 0.5, captura
            (0.1, 0.5, 0.4, "urgente"),  # < 0.5, perde
            (0.9, 0.05, 0.05, "normal"),  # não conta pro denominador
        ]
    )
    assert _recall_urgente(pooled, threshold_urgente=0.5) == 0.5


def test_search_threshold_urgente_escolhe_o_maior_que_cumpre_a_meta():
    # metade dos urgentes reais tem P(urgente) alto, metade tem P(urgente) baixo:
    # só limiares <= 0.3 capturam os dois e cumprem recall >= 1.0
    rows = [(0.0, 0.0, 0.9, "urgente")] * 5 + [(0.0, 0.7, 0.3, "urgente")] * 5
    pooled = _pooled(rows)
    threshold = _search_threshold_urgente(pooled)
    assert threshold == 0.3  # maior valor da grade que ainda cumpre recall == 1.0


def test_search_threshold_atencao_minimiza_custo():
    # todos os "atencao" reais têm P(atencao)+P(urgente) = 0.2; threshold_urgente
    # alto o bastante para nunca prever urgente aqui, isolando o efeito do 2º limiar
    rows = [(0.8, 0.15, 0.05, "atencao")] * 5 + [(0.95, 0.03, 0.02, "normal")] * 5
    pooled = _pooled(rows)
    threshold = _search_threshold_atencao(pooled, threshold_urgente=0.9)
    # limiar <= 0.20 classifica os "atencao" reais corretamente (custo 0 nesses);
    # limiar mais alto perde-os para "normal" (sub-triagem, custo 5) — deve escolher <= 0.20
    assert threshold <= 0.20
