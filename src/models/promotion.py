"""Critério de elegibilidade de promoção do modelo (ADR-0008)."""

import mlflow

MODEL_NAME = "triagem-urgencia"


def get_production_sub_triagem_rate(client: mlflow.MlflowClient) -> float | None:
    """Taxa de sub-triagem da versão atualmente em produção, se existir."""
    try:
        version = client.get_model_version_by_alias(MODEL_NAME, "production")
    except mlflow.exceptions.MlflowException:
        return None
    tag = version.tags.get("sub_triagem_rate")
    return float(tag) if tag is not None else None


def meets_promotion_criteria(
    f1_macro: float,
    sub_triagem_rate: float,
    min_f1_macro: float,
    max_sub_triagem_increase: float,
    baseline_sub_triagem_rate: float | None,
) -> bool:
    """ADR-0008: piso de F1-macro + não regredir sub-triagem além do limite."""
    meets_f1 = f1_macro >= min_f1_macro
    meets_regression = (
        baseline_sub_triagem_rate is None
        or sub_triagem_rate <= baseline_sub_triagem_rate + max_sub_triagem_increase
    )
    return meets_f1 and meets_regression
