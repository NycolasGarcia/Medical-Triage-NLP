"""Download e carregamento do Medical Abstracts TC Corpus."""

from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd

from src.logging_config import configure_logging, get_logger

logger = get_logger(__name__)

RAW_BASE_URL = "https://raw.githubusercontent.com/sebischair/Medical-Abstracts-TC-Corpus/main"
RAW_FILES = ("medical_tc_labels.csv", "medical_tc_train.csv", "medical_tc_test.csv")


def download_raw(dest_dir: Path) -> None:
    """Baixa os CSVs do corpus para dest_dir, pulando os que já existem."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filename in RAW_FILES:
        target = dest_dir / filename
        if target.exists():
            logger.info("raw_file_already_present", extra={"file": filename})
            continue
        urlretrieve(f"{RAW_BASE_URL}/{filename}", target)
        logger.info("raw_file_downloaded", extra={"file": filename})


def load_raw(raw_dir: Path) -> pd.DataFrame:
    """Carrega train+test concatenados, com o nome da classe original.

    O split treino/teste original do corpus tem vazamento (ver `docs/data_card.md`:
    988 abstracts duplicados entre train/test com `condition_label` divergente em
    100% dos casos) e não é usado como referência — os dados voltam concatenados
    para dedupe e split próprios no pipeline (caixas 1.5/1.6).
    """
    labels = pd.read_csv(raw_dir / "medical_tc_labels.csv")
    train = pd.read_csv(raw_dir / "medical_tc_train.csv")
    test = pd.read_csv(raw_dir / "medical_tc_test.csv")

    combined = pd.concat([train, test], ignore_index=True)
    combined = combined.merge(labels, on="condition_label", how="left")
    return combined.rename(columns={"medical_abstract": "text", "condition_name": "original_label"})


if __name__ == "__main__":
    configure_logging()
    raw_dir = Path("data/raw")
    download_raw(raw_dir)
    df = load_raw(raw_dir)
    logger.info("dataset_carregado", extra={"linhas": len(df), "colunas": list(df.columns)})
