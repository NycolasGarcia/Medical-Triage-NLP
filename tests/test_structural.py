"""Testa as features estruturais (contagem de tokens, densidade numérica/pontuação)."""

from src.features.structural import StructuralFeatures


def test_conta_tokens():
    rows = StructuralFeatures().transform(["patient with fever and cough"])
    assert rows[0][0] == 5.0


def test_densidade_numerica():
    rows = StructuralFeatures().transform(["bp 120 90 hr 88"])
    n_tokens, numeric_density, _ = rows[0]
    assert n_tokens == 5.0
    assert numeric_density == 3 / 5


def test_densidade_pontuacao():
    rows = StructuralFeatures().transform(["fever, chills, and nausea."])
    n_tokens, _, punct_density = rows[0]
    assert n_tokens == 4.0  # "fever," "chills," "and" "nausea."
    assert punct_density == 3 / 4  # 2 vírgulas + 1 ponto, sobre 4 tokens


def test_get_feature_names_out():
    names = StructuralFeatures().get_feature_names_out()
    assert names == ["n_tokens", "numeric_density", "punct_density"]
