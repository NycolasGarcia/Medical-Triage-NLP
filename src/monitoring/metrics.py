"""Métricas Prometheus da API: requisições, latência, erros e classe predita."""

from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter(
    "http_requests_total", "Total de requisições HTTP", ["method", "path", "status_code"]
)

REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds", "Duração da requisição HTTP em segundos", ["method", "path"]
)

ERRORS_TOTAL = Counter(
    "http_errors_total",
    "Total de requisições com status de erro (>=400)",
    ["method", "path", "status_code"],
)

PREDICTIONS_TOTAL = Counter(
    "predictions_total", "Total de predições por classe de urgência", ["label"]
)


def record_request(method: str, path: str, status_code: int, duration_seconds: float) -> None:
    """Registra uma requisição concluída nas métricas de contagem e latência."""
    REQUESTS_TOTAL.labels(method=method, path=path, status_code=status_code).inc()
    REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration_seconds)
    if status_code >= 400:
        ERRORS_TOTAL.labels(method=method, path=path, status_code=status_code).inc()


def record_prediction(label: str) -> None:
    """Registra a classe predita — base para detectar drift na distribuição."""
    PREDICTIONS_TOTAL.labels(label=label).inc()
