"""Testa as métricas Prometheus (§13): contagem, latência e classe predita."""

from prometheus_client import generate_latest

from src.monitoring.metrics import record_prediction, record_request


def _metric_value(name: str, **labels) -> float | None:
    label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
    prefix = f"{name}{{{label_str}}} "
    for line in generate_latest().decode().splitlines():
        if line.startswith(prefix):
            return float(line.removeprefix(prefix))
    return None


def test_record_request_incrementa_contagem_e_latencia():
    before = (
        _metric_value("http_requests_total", method="GET", path="/test-metrics", status_code="200")
        or 0.0
    )

    record_request("GET", "/test-metrics", 200, 0.01)

    after = _metric_value(
        "http_requests_total", method="GET", path="/test-metrics", status_code="200"
    )
    assert after == before + 1.0


def test_record_request_status_erro_incrementa_errors_total():
    before = (
        _metric_value(
            "http_errors_total", method="POST", path="/test-metrics-erro", status_code="422"
        )
        or 0.0
    )

    record_request("POST", "/test-metrics-erro", 422, 0.01)

    after = _metric_value(
        "http_errors_total", method="POST", path="/test-metrics-erro", status_code="422"
    )
    assert after == before + 1.0


def test_record_prediction_incrementa_classe():
    before = _metric_value("predictions_total", label="normal") or 0.0

    record_prediction("normal")

    after = _metric_value("predictions_total", label="normal")
    assert after == before + 1.0
