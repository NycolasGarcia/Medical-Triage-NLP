"""Gera carga contra a API pra popular o dashboard do Grafana (docs/RUNBOOK.md).

Uso: `uv run python -m scripts.load_test [--base-url URL] [--requests N] [--concurrency N]`
"""

import argparse
import concurrent.futures
import random

import httpx
import pandas as pd

from src.logging_config import configure_logging, get_logger

logger = get_logger(__name__)

N_DEFAULT = 500
CONCURRENCY_DEFAULT = 10


def _sample_texts(test_csv: str = "data/processed/test.csv", n: int = 50) -> list[str]:
    """Amostra textos reais do teste — carga realista, não string fixa repetida."""
    df = pd.read_csv(test_csv)
    return df["text"].sample(n=min(n, len(df)), random_state=42).tolist()


def _fire(base_url: str, text: str) -> int:
    with httpx.Client(timeout=10.0) as client:
        if random.random() < 0.02:
            response = client.get(f"{base_url}/health")
        else:
            response = client.post(f"{base_url}/predict", json={"text": text})
    return response.status_code


def run_load_test(base_url: str, n_requests: int, concurrency: int) -> None:
    texts = _sample_texts()
    payloads = [random.choice(texts) for _ in range(n_requests)]

    statuses: list[int] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(_fire, base_url, text) for text in payloads]
        for future in concurrent.futures.as_completed(futures):
            statuses.append(future.result())

    ok = sum(1 for s in statuses if s == 200)
    logger.info(
        "load_test_concluido",
        extra={"requests": n_requests, "concurrency": concurrency, "status_200": ok},
    )


if __name__ == "__main__":
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--requests", type=int, default=N_DEFAULT)
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY_DEFAULT)
    args = parser.parse_args()
    run_load_test(args.base_url, args.requests, args.concurrency)
