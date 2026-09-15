"""Testa o critério de elegibilidade de promoção (ADR-0008, atualizado em F6:
recall de `urgente` + custo médio no lugar do antigo piso de F1-macro)."""

from src.models.promotion import meets_promotion_criteria


def test_elegivel_quando_recall_acima_do_piso_e_sem_baseline():
    assert meets_promotion_criteria(0.90, 0.65, 0.85, 0.10, None) is True


def test_nao_elegivel_quando_recall_abaixo_do_piso():
    assert meets_promotion_criteria(0.80, 0.65, 0.85, 0.10, None) is False


def test_nao_elegivel_quando_custo_regride_alem_do_limite():
    assert meets_promotion_criteria(0.90, 0.90, 0.85, 0.10, 0.65) is False


def test_elegivel_quando_custo_dentro_do_limite_de_regressao():
    assert meets_promotion_criteria(0.90, 0.70, 0.85, 0.10, 0.65) is True
