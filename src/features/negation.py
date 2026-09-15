"""Marcação de escopo de negação, estilo NegEx — para o laudo clínico não perder
sentido quando `sem sinais de choque` vira, sem marcação, indistinguível de
`sinais de choque` (§10.6, armadilha 1).

Escopo simplificado: da palavra-gatilho até a próxima pontuação (ou fim do texto),
limitado a `MAX_SCOPE_TOKENS` para não marcar a frase inteira em textos sem
pontuação. Suficiente para capturar `denies chest pain` ou `no signs of shock`
sem depender de um parser de dependência sintática — fora do escopo de um
modelo leve (R1).
"""

import re

from sklearn.base import BaseEstimator, TransformerMixin

NEGATION_CUES = frozenset(
    {
        "no",
        "not",
        "without",
        "never",
        "none",
        "denies",
        "denied",
        "denying",
        "negative",
        "absence",
        "absent",
        "ruled",
        "unremarkable",
        "free",
        "lack",
        "lacking",
        "resolved",
    }
)

MAX_SCOPE_TOKENS = 5
_PUNCT_RE = re.compile(r"[.,;:!?]$")
_TOKEN_RE = re.compile(r"\S+")


def negation_flags(text: str) -> list[tuple[str, bool]]:
    """Tokeniza e marca cada token com se está no escopo de uma negação.

    Extraído como função própria (não só `mark_negation`) para que outros
    consumidores — o léxico de severidade, por exemplo — possam decidir por si
    se um termo está negado, **sem** depender de já terem recebido texto
    passado por `mark_negation`. Evita o risco de interação identificado antes
    de implementar: se o léxico contasse `severe` em `severe_NEG`, a contagem
    de severidade ficaria invertida silenciosamente.
    """
    tokens = _TOKEN_RE.findall(text.lower())
    flags = []
    scope_remaining = 0
    for token in tokens:
        bare = token.strip(".,;:!?")
        flags.append((bare, scope_remaining > 0))
        if scope_remaining > 0:
            scope_remaining -= 1
        if bare in NEGATION_CUES:
            scope_remaining = MAX_SCOPE_TOKENS
        if _PUNCT_RE.search(token):
            scope_remaining = 0
    return flags


def mark_negation(text: str) -> str:
    """Sufixa `_NEG` nos tokens dentro do escopo de uma palavra-gatilho de negação."""
    return " ".join(f"{tok}_NEG" if negated else tok for tok, negated in negation_flags(text))


class NegationMarker(BaseEstimator, TransformerMixin):
    """Wrapper sklearn de `mark_negation`, para compor em `Pipeline`/`FeatureUnion`."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [mark_negation(text) for text in X]
