"""Mapeamento de classes originais do corpus para faixas de urgência (ADR-0001).

Heurístico e didático, sem validação clínica — ver limitações em `docs/model_card.md`
e `docs/data_card.md`.
"""

from typing import Protocol

import pandas as pd

URGENCY_CLASSES = ("normal", "atencao", "urgente")


class UrgencyMappingStrategy(Protocol):
    def map(self, original_label: str) -> str: ...


class HeuristicUrgencyMapper:
    """Mapeamento aprovado em ADR-0001: cardiovascular/nervoso -> urgente,
    neoplasias/digestivo -> atenção, geral -> normal."""

    _MAPPING = {
        "cardiovascular diseases": "urgente",
        "nervous system diseases": "urgente",
        "neoplasms": "atencao",
        "digestive system diseases": "atencao",
        "general pathological conditions": "normal",
    }

    def map(self, original_label: str) -> str:
        try:
            return self._MAPPING[original_label]
        except KeyError as exc:
            raise ValueError(f"Classe original desconhecida: {original_label!r}") from exc


def apply_urgency_mapping(
    df: pd.DataFrame, strategy: UrgencyMappingStrategy | None = None
) -> pd.DataFrame:
    """Adiciona a coluna `urgency_label` a partir de `original_label`."""
    strategy = strategy or HeuristicUrgencyMapper()
    result = df.copy()
    result["urgency_label"] = result["original_label"].map(strategy.map)
    return result
