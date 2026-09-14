"""Testa a Factory de modelos: cada candidato registrado deve construir e prever proba."""

import pytest
from sklearn.base import ClassifierMixin

from src.models.experiments import CANDIDATE_MODELS
from src.models.factory import build_model


@pytest.mark.parametrize("model_name", CANDIDATE_MODELS)
def test_build_model_retorna_classificador_treinavel(model_name):
    model = build_model(model_name)

    assert isinstance(model, ClassifierMixin)
    assert hasattr(model, "fit")
    assert hasattr(model, "predict_proba")


def test_build_model_nome_desconhecido_levanta_value_error():
    with pytest.raises(ValueError, match="Modelo desconhecido"):
        build_model("modelo_inexistente")
