"""Matriz de custo assimétrica (§7, decidida em §14/CLAUDE.md, formalizada em
ADR-0005): sub-triagem custa muito mais que sobre-triagem, e escala com a
distância ordinal do erro — errar `urgente` por `normal` é pior que errar por
`atenção`.

| Real \\ Previsto | normal | atenção | urgente |
|---|---|---|---|
| normal  | 0  | 1  | 2  |
| atenção | 5  | 0  | 1  |
| urgente | 15 | 5  | 0  |

Custo 0 na diagonal (acerto). Abaixo da diagonal (sub-triagem, previsto menos
urgente que o real): 5 por nível, 15 para os 2 níveis — o erro perigoso.
Acima da diagonal (sobre-triagem, previsto mais urgente que o real): 1-2 por
nível — caro (tempo de equipe), mas seguro.
"""

import numpy as np
import pandas as pd

from src.data.labels import URGENCY_CLASSES

_URGENCY_RANK = {label: i for i, label in enumerate(URGENCY_CLASSES)}

# [distância sub-triagem 1, distância sub-triagem 2] e [sobre-triagem 1, sobre-triagem 2]
_SUB_TRIAGEM_COST = {1: 5.0, 2: 15.0}
_SOBRE_TRIAGEM_COST = {1: 1.0, 2: 2.0}


def _cost_for_distance(distance: int) -> float:
    """`distance = rank(previsto) - rank(real)`: negativo é sub-triagem, positivo
    é sobre-triagem, zero é acerto."""
    if distance == 0:
        return 0.0
    if distance < 0:
        return _SUB_TRIAGEM_COST[-distance]
    return _SOBRE_TRIAGEM_COST[distance]


def cost_matrix() -> pd.DataFrame:
    """Matriz 3x3 (real x previsto), na ordem normal/atenção/urgente."""
    labels = list(URGENCY_CLASSES)
    matrix = np.array(
        [
            [_cost_for_distance(_URGENCY_RANK[pred] - _URGENCY_RANK[true]) for pred in labels]
            for true in labels
        ]
    )
    return pd.DataFrame(matrix, index=labels, columns=labels)


def sample_costs(y_true, y_pred) -> np.ndarray:
    """Custo de cada predição individual, na ordem de `y_true`/`y_pred`."""
    true_rank = np.array([_URGENCY_RANK[label] for label in y_true])
    pred_rank = np.array([_URGENCY_RANK[label] for label in y_pred])
    distances = pred_rank - true_rank
    return np.array([_cost_for_distance(int(d)) for d in distances])


def total_cost(y_true, y_pred) -> float:
    """Soma dos custos — comparável entre modelos só com o mesmo N de amostras."""
    return float(sample_costs(y_true, y_pred).sum())


def mean_cost(y_true, y_pred) -> float:
    """Custo médio por amostra — comparável entre conjuntos de tamanhos diferentes,
    é a métrica a usar para comparar modelos/dobras de CV."""
    return float(sample_costs(y_true, y_pred).mean())
