"""Critério de elegibilidade de promoção do modelo (ADR-0008, atualizado em F6).

Critério original (F4) usava piso de F1-macro — fazia sentido antes de F6, quando
F1-macro ainda era a métrica de seleção. A partir da caixa 6.4/ADR-0005, o projeto
troca F1-macro por custo/recall de `urgente` deliberadamente (limiar cumulativo
enviesado contra sub-triagem) — um piso de F1-macro teria **bloqueado** o próprio
modelo que ADR-0005 decidiu servir (F1-macro caiu de 0,73 para ~0,52 no teste, de
propósito). Critério trocado para refletir o que o projeto de fato otimiza agora.
"""

import mlflow

MODEL_NAME = "triagem-urgencia"


def get_production_mean_cost(client: mlflow.MlflowClient) -> float | None:
    """Custo médio (matriz de §7) da versão atualmente em produção, se existir."""
    try:
        version = client.get_model_version_by_alias(MODEL_NAME, "production")
    except mlflow.exceptions.MlflowException:
        return None
    tag = version.tags.get("mean_cost")
    return float(tag) if tag is not None else None


def meets_promotion_criteria(
    recall_urgente: float,
    mean_cost: float,
    min_recall_urgente: float,
    max_cost_increase: float,
    baseline_mean_cost: float | None,
) -> bool:
    """ADR-0008 (F6): piso de recall de `urgente` (§14) + não regredir custo
    médio (matriz de §7) além do limite."""
    meets_recall = recall_urgente >= min_recall_urgente
    meets_regression = (
        baseline_mean_cost is None or mean_cost <= baseline_mean_cost + max_cost_increase
    )
    return meets_recall and meets_regression
