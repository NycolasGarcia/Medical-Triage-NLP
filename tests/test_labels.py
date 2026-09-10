"""Testa o mapeamento classe original -> urgência (ADR-0001)."""

import pandas as pd
import pytest

from src.data.labels import HeuristicUrgencyMapper, apply_urgency_mapping

EXPECTED = {
    "cardiovascular diseases": "urgente",
    "nervous system diseases": "urgente",
    "neoplasms": "atencao",
    "digestive system diseases": "atencao",
    "general pathological conditions": "normal",
}


@pytest.mark.parametrize(("original", "expected"), EXPECTED.items())
def test_mapeamento_por_classe(original, expected):
    assert HeuristicUrgencyMapper().map(original) == expected


def test_classe_desconhecida_levanta_erro():
    with pytest.raises(ValueError, match="desconhecida"):
        HeuristicUrgencyMapper().map("classe inexistente")


def test_apply_urgency_mapping_adiciona_coluna():
    df = pd.DataFrame({"original_label": list(EXPECTED.keys())})
    result = apply_urgency_mapping(df)
    assert list(result["urgency_label"]) == list(EXPECTED.values())
