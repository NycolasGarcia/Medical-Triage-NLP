"""Deduplicação de texto: exata e por similaridade (near-duplicate)."""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from src.logging_config import get_logger

logger = get_logger(__name__)


def dedupe_exact(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    """Remove duplicatas exatas (texto normalizado por strip+lower), mantendo a 1ª ocorrência."""
    normalized = df[text_col].str.strip().str.lower()
    is_dup = normalized.duplicated()
    logger.info(
        "dedupe_exato", extra={"removidas": int(is_dup.sum()), "restantes": int((~is_dup).sum())}
    )
    return df.loc[~is_dup].reset_index(drop=True)


def dedupe_near(df: pd.DataFrame, text_col: str = "text", threshold: float = 0.9) -> pd.DataFrame:
    """Remove near-duplicates por similaridade de cosseno (TF-IDF) acima do limiar.

    Assume que `dedupe_exact` já rodou. Para cada par de vizinhos mais próximos acima
    do limiar, mantém o de menor índice — não resolve transitividade em grupos de 3+
    (aceitável aqui: o EDA mostrou que near-dup remanescente após dedupe exato é raro).
    """
    vec = TfidfVectorizer(max_features=20000)
    X = vec.fit_transform(df[text_col])
    nn = NearestNeighbors(n_neighbors=2, metric="cosine", algorithm="brute", n_jobs=-1)
    dist, idx = nn.fit(X).kneighbors(X)
    similarity, neighbor = 1 - dist[:, 1], idx[:, 1]

    to_drop: set[int] = set()
    for i, (sim, j) in enumerate(zip(similarity, neighbor, strict=True)):
        if sim >= threshold and i not in to_drop and j not in to_drop:
            to_drop.add(max(i, j))

    restantes = len(df) - len(to_drop)
    logger.info("dedupe_near", extra={"removidas": len(to_drop), "restantes": restantes})
    return df.drop(df.index[list(to_drop)]).reset_index(drop=True)
