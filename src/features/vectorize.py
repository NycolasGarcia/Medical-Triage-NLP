"""Estratégias de vetorização de texto (Strategy) — TF-IDF hoje, outras se necessário.

`TfidfStrategy` é a representação **congelada de F2** (espelhada em
`docs/EXPERIMENTS.md`) — não editar, é o que gerou os números já publicados.
`RepresentationConfig`/`build_representation` (F6, caixa 6.1) é onde a
representação é de fato tunada; a vencedora vira a nova `build_pipeline()` de
`src/models/train.py` ao final da caixa, não esta classe.
"""

from dataclasses import dataclass
from typing import Protocol

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import StandardScaler

from src.features.lexicon import SeverityLexiconCounter
from src.features.negation import mark_negation
from src.features.structural import StructuralFeatures


class VectorizerStrategy(Protocol):
    def build(self) -> TfidfVectorizer:
        """Constrói o vetorizador configurado pela estratégia."""
        ...


class TfidfStrategy:
    """TF-IDF simples para os baselines de F2. Tuning de hiperparâmetros fica para F6."""

    def __init__(self, max_features: int = 20000) -> None:
        self.max_features = max_features

    def build(self) -> TfidfVectorizer:
        """Constrói o TfidfVectorizer com o `max_features` configurado."""
        # stop_words=None (padrão): negadores clínicos ("não", "sem") não são removidos.
        return TfidfVectorizer(max_features=self.max_features)


@dataclass(frozen=True)
class RepresentationConfig:
    """Um ponto no espaço de busca da caixa 6.1. `word_ngram_range=(1, 2)` é a
    correção de baseline (§10.6/ADR-0003 já decidiam bigramas para dar contexto
    à negação; nunca tinha sido implementado) — não é um dos 4 candidatos, é
    parte de toda config, inclusive a baseline."""

    name: str
    negation: bool = False
    severity_lexicon: bool = False
    structural: bool = False
    char_ngrams: bool = False
    word_ngram_range: tuple[int, int] = (1, 2)
    max_features: int = 20000


def build_representation(config: RepresentationConfig) -> FeatureUnion:
    """Monta a `FeatureUnion` das colunas ativadas em `config`. O branch de
    palavras é sempre incluído; o preprocessador muda para `mark_negation`
    quando `negation=True` — as demais colunas recebem texto cru de propósito
    (ver docstring de `SeverityLexiconCounter` sobre o risco de interação)."""
    branches: list[tuple[str, object]] = [
        (
            "word_tfidf",
            TfidfVectorizer(
                max_features=config.max_features,
                ngram_range=config.word_ngram_range,
                preprocessor=mark_negation if config.negation else None,
            ),
        )
    ]
    if config.severity_lexicon:
        branches.append(("severity", SeverityLexiconCounter()))
    if config.structural:
        branches.append(
            ("structural", Pipeline([("raw", StructuralFeatures()), ("scale", StandardScaler())]))
        )
    if config.char_ngrams:
        branches.append(
            (
                "char_tfidf",
                TfidfVectorizer(
                    analyzer="char_wb", ngram_range=(3, 5), max_features=config.max_features
                ),
            )
        )
    return FeatureUnion(branches)


# Vencedora da busca gulosa de caixa 6.1 (12 runs, MLflow experimento
# `triagem-urgencia`, prefixo `f6_repr_*`): char n-gramas + marcação de negação
# sobre a base de bigramas. F1-macro CV 0,7338 vs. 0,731 do baseline de F2
# (unigramas) e 0,7234 do baseline corrigido só com bigramas — léxico de
# severidade e features estruturais não bateram o incremental em nenhuma
# rodada; classificador ordinal (`mord`) teve F1-macro 0,566, descartado.
# Ver `docs/EXPERIMENTS.md` para a tabela completa e `docs/PROGRESS.md` F6.
PRODUCTION_REPRESENTATION = RepresentationConfig(
    name="f6_negation_char_ngrams", negation=True, char_ngrams=True
)
