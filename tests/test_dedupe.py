"""Testa deduplicação exata e por similaridade."""

import pandas as pd

from src.data.dedupe import dedupe_exact, dedupe_near


def test_dedupe_exact_remove_duplicata_normalizada():
    df = pd.DataFrame({"text": ["Abstract A", "  abstract a  ", "Abstract B"]})
    result = dedupe_exact(df)
    assert len(result) == 2
    assert list(result["text"]) == ["Abstract A", "Abstract B"]


def test_dedupe_near_remove_texto_quase_identico():
    df = pd.DataFrame(
        {
            "text": [
                "patient presents with acute chest pain and shortness of breath",
                "patient presents with acute chest pain and shortness of breath today",
                "completely unrelated abstract about a different medical condition entirely",
            ]
        }
    )
    result = dedupe_near(df, threshold=0.8)
    assert len(result) == 2
