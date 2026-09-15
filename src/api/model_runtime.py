"""Carregamento do modelo persistido — chamado uma vez no startup da API (ADR pendente F3).

Backend escolhido por `settings.model_backend` (caixa 6.9/ADR-0004): "sklearn"
(padrão) carrega o pipeline completo de 6.1-6.4; "onnx" carrega a variante mais
rápida de caixa 6.6 — representação mais simples, ver ADR-0004 para o porquê.
"""

from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline

from src.config import settings
from src.optimization.onnx_runtime import OnnxPipeline, load_onnx_pipeline

# Versionamento formal via MLflow Registry entra em F6 (caixa 6.10).
_MODEL_VERSIONS = {
    "sklearn": "f6-logreg-negation-charngrams",  # representação vencedora de 6.1
    "onnx": "f6-logreg-onnx-word-bigrams",  # representação compatível com skl2onnx
}
MODEL_VERSION = _MODEL_VERSIONS[settings.model_backend]


def load_pipeline() -> Pipeline | OnnxPipeline:
    """Carrega o pipeline do backend ativo (`settings.model_backend`)."""
    if settings.model_backend == "onnx":
        return load_onnx_pipeline(settings.model_path)
    artifact_path = Path(settings.model_path) / "model.joblib"
    return joblib.load(artifact_path)
