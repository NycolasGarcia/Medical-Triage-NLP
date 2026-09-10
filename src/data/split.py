"""Split estratificado do dataset processado, com seed fixa e reprodutível."""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.logging_config import configure_logging, get_logger

logger = get_logger(__name__)

SEED = 42
TEST_SIZE = 0.2


def stratified_split(
    df: pd.DataFrame, label_col: str = "urgency_label", test_size: float = TEST_SIZE
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split treino/teste estratificado por `label_col`, com seed fixa (reprodutível)."""
    train_df, test_df = train_test_split(
        df, test_size=test_size, stratify=df[label_col], random_state=SEED
    )
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


if __name__ == "__main__":
    configure_logging()
    processed_dir = Path("data/processed")

    deduped = pd.read_csv(processed_dir / "deduped.csv")
    train_df, test_df = stratified_split(deduped)
    train_df.to_csv(processed_dir / "train.csv", index=False)
    test_df.to_csv(processed_dir / "test.csv", index=False)
    logger.info("split_concluido", extra={"train": len(train_df), "test": len(test_df)})
