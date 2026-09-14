"""Benchmark de latência do `/predict` (protocolo em `docs/LATENCY.md`).

Uso: `uv run python -m scripts.benchmark [--base-url URL] [--n N] [--warmup N]`
Requer a API já rodando (local ou em container) no `--base-url` informado.
"""

import argparse
import logging
import statistics
import time

import httpx
import pandas as pd

from src.logging_config import configure_logging, get_logger

logger = get_logger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)  # silencia 1 linha por request

WARMUP_DEFAULT = 100
N_DEFAULT = 1000
REPETITIONS = 3


def _median_length_payload(test_csv: str = "data/processed/test.csv") -> str:
    """Escolhe, do conjunto de teste, o texto com comprimento mais próximo da mediana."""
    df = pd.read_csv(test_csv)
    lengths = df["text"].str.len()
    median_idx = (lengths - lengths.median()).abs().idxmin()
    return df.loc[median_idx, "text"]


def _time_requests(client: httpx.Client, url: str, payload: dict, n: int) -> list[float]:
    latencies = []
    for _ in range(n):
        start = time.perf_counter()
        client.post(url, json=payload)
        latencies.append((time.perf_counter() - start) * 1000)
    return latencies


def _percentiles(latencies: list[float]) -> dict[str, float]:
    sorted_lat = sorted(latencies)
    return {
        "p50": sorted_lat[int(len(sorted_lat) * 0.50)],
        "p95": sorted_lat[int(len(sorted_lat) * 0.95)],
        "p99": sorted_lat[int(len(sorted_lat) * 0.99)],
    }


def run_benchmark(base_url: str, n: int, warmup: int) -> None:
    payload = {"text": _median_length_payload()}
    url = f"{base_url}/predict"

    with httpx.Client(timeout=30.0) as client:
        _time_requests(client, url, payload, warmup)

        runs = [_percentiles(_time_requests(client, url, payload, n)) for _ in range(REPETITIONS)]

    p95_values = [run["p95"] for run in runs]
    median_run = runs[p95_values.index(statistics.median(p95_values))]

    for i, run in enumerate(runs, start=1):
        logger.info("execucao_benchmark", extra={"execucao": i, **run})
    logger.info(
        "benchmark_concluido",
        extra={
            "n": n,
            "warmup": warmup,
            "repeticoes": REPETITIONS,
            "p95_mediano": statistics.median(p95_values),
            **median_run,
        },
    )


if __name__ == "__main__":
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--n", type=int, default=N_DEFAULT)
    parser.add_argument("--warmup", type=int, default=WARMUP_DEFAULT)
    args = parser.parse_args()
    run_benchmark(args.base_url, args.n, args.warmup)
