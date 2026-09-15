"""Testa a matriz de custo assimétrica (§7/§14/ADR-0005) — cada célula da matriz
e o comportamento agregado de total_cost/mean_cost."""

import pytest

from src.models.cost import cost_matrix, mean_cost, sample_costs, total_cost


def test_matriz_tem_zero_na_diagonal():
    matrix = cost_matrix()
    for label in matrix.index:
        assert matrix.loc[label, label] == 0.0


def test_sub_triagem_custa_5_por_nivel_e_15_para_dois_niveis():
    matrix = cost_matrix()
    assert matrix.loc["atencao", "normal"] == 5.0  # sub-triagem de 1 nível
    assert matrix.loc["urgente", "atencao"] == 5.0  # sub-triagem de 1 nível
    assert matrix.loc["urgente", "normal"] == 15.0  # sub-triagem de 2 níveis


def test_sobre_triagem_custa_1_ou_2():
    matrix = cost_matrix()
    assert matrix.loc["normal", "atencao"] == 1.0  # sobre-triagem de 1 nível
    assert matrix.loc["atencao", "urgente"] == 1.0  # sobre-triagem de 1 nível
    assert matrix.loc["normal", "urgente"] == 2.0  # sobre-triagem de 2 níveis


def test_sub_triagem_custa_mais_que_sobre_triagem_na_mesma_distancia():
    matrix = cost_matrix()
    assert matrix.loc["urgente", "atencao"] > matrix.loc["normal", "atencao"]
    assert matrix.loc["urgente", "normal"] > matrix.loc["normal", "urgente"]


def test_sample_costs_bate_com_a_matriz():
    y_true = ["urgente", "urgente", "normal", "atencao"]
    y_pred = ["normal", "urgente", "atencao", "urgente"]
    costs = sample_costs(y_true, y_pred)
    assert costs.tolist() == [15.0, 0.0, 1.0, 1.0]


def test_total_e_mean_cost():
    y_true = ["urgente", "normal"]
    y_pred = ["normal", "normal"]
    assert total_cost(y_true, y_pred) == pytest.approx(15.0)
    assert mean_cost(y_true, y_pred) == pytest.approx(7.5)


def test_acerto_perfeito_custa_zero():
    y_true = ["normal", "atencao", "urgente"]
    assert total_cost(y_true, y_true) == 0.0
    assert mean_cost(y_true, y_true) == 0.0
