"""Testa o critério de elegibilidade de promoção (ADR-0008)."""

from src.models.promotion import meets_promotion_criteria


def test_elegivel_quando_f1_acima_do_piso_e_sem_baseline():
    assert meets_promotion_criteria(0.73, 0.12, 0.70, 0.03, None) is True


def test_nao_elegivel_quando_f1_abaixo_do_piso():
    assert meets_promotion_criteria(0.65, 0.10, 0.70, 0.03, None) is False


def test_nao_elegivel_quando_sub_triagem_regride_alem_do_limite():
    assert meets_promotion_criteria(0.75, 0.20, 0.70, 0.03, 0.10) is False


def test_elegivel_quando_sub_triagem_dentro_do_limite_de_regressao():
    assert meets_promotion_criteria(0.75, 0.12, 0.70, 0.03, 0.10) is True
