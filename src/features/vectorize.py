"""Estratégias de vetorização de texto (Strategy) — TF-IDF hoje, outras se necessário."""

from typing import Protocol

from sklearn.feature_extraction.text import TfidfVectorizer


class VectorizerStrategy(Protocol):
    def build(self) -> TfidfVectorizer: ...


class TfidfStrategy:
    """TF-IDF simples para os baselines de F2. Tuning de hiperparâmetros fica para F6."""

    def __init__(self, max_features: int = 20000) -> None:
        self.max_features = max_features

    def build(self) -> TfidfVectorizer:
        # stop_words=None (padrão): negadores clínicos ("não", "sem") não são removidos.
        return TfidfVectorizer(max_features=self.max_features)
