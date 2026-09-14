"""Testes de contrato da API (§13): health, predict válido e payload inválido."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.config import settings
from src.models.train import train_and_persist


@pytest.fixture
def client(sample_train_csv, isolated_mlflow, tmp_path, monkeypatch):
    model_dir = tmp_path / "models"
    train_and_persist(train_path=str(sample_train_csv), model_dir=str(model_dir))
    monkeypatch.setattr(settings, "model_path", str(model_dir))
    with TestClient(app) as test_client:
        yield test_client


def test_health_retorna_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_retorna_uma_das_tres_classes(client):
    response = client.post("/predict", json={"text": "sem sinais de isquemia aguda"})
    assert response.status_code == 200
    body = response.json()
    assert body["label"] in {"normal", "atencao", "urgente"}
    assert abs(sum(body["probabilities"].values()) - 1.0) < 1e-6


def test_predict_payload_invalido_retorna_422(client):
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 422
