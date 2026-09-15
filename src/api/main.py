"""Aplicação FastAPI de triagem de urgência: `/predict` e `/health`."""

import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.api.model_runtime import MODEL_VERSION, load_pipeline
from src.api.schemas import HealthResponse, PredictRequest, PredictResponse
from src.logging_config import configure_logging, get_logger
from src.monitoring.metrics import record_prediction, record_request

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Carrega o modelo uma única vez no startup — não por requisição (decisão de F3)."""
    configure_logging()
    app.state.pipeline = load_pipeline()
    logger.info("modelo_carregado", extra={"model_version": MODEL_VERSION})
    yield


app = FastAPI(title="Triagem de Urgência", lifespan=lifespan)


@app.middleware("http")
async def log_requisicao(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Mede latência por requisição e loga id, rota, status e classe predita (se houver)."""
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    record_request(request.method, request.url.path, response.status_code, duration)
    logger.info(
        "requisicao",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "status_code": response.status_code,
            "latencia_ms": round(duration * 1000, 2),
            "classe_predita": getattr(request.state, "predicted_label", None),
        },
    )
    return response


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict", response_model=PredictResponse)
def predict(body: PredictRequest, request: Request) -> PredictResponse:
    pipeline = request.app.state.pipeline
    proba = pipeline.predict_proba([body.text])[0]
    probabilities = {label: float(p) for label, p in zip(pipeline.classes_, proba, strict=True)}
    label = max(probabilities, key=probabilities.get)
    request.state.predicted_label = label
    record_prediction(label)
    return PredictResponse(label=label, probabilities=probabilities, model_version=MODEL_VERSION)
