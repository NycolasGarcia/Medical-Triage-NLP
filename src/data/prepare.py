"""Orquestra o pré-processamento: carrega, mapeia rótulo e deduplica (estágio DVC)."""

from pathlib import Path

import pandas as pd

from src.data.dedupe import dedupe_exact, dedupe_near
from src.data.labels import apply_urgency_mapping
from src.data.load import load_raw
from src.logging_config import configure_logging, get_logger

logger = get_logger(__name__)


def prepare(raw_dir: Path) -> pd.DataFrame:
    df = load_raw(raw_dir)
    df = apply_urgency_mapping(df)
    df = dedupe_exact(df)
    df = dedupe_near(df)
    return df


if __name__ == "__main__":
    configure_logging()
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    result = prepare(Path("data/raw"))
    result.to_csv(processed_dir / "deduped.csv", index=False)
    logger.info("preprocess_concluido", extra={"linhas": len(result)})
