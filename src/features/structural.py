"""Features estruturais/estatísticas do texto (§10.6) — não sobre o *conteúdo*
lexical (isso é TF-IDF/léxico), mas sobre a *forma* do laudo, como proxy de
complexidade do caso:

- `n_tokens`: laudos mais longos tendem a descrever mais achados/comorbidades.
- `numeric_density`: fração de tokens com dígito — proxy de valores de exame
  (sinais vitais, resultados de laboratório) citados no texto.
- `punct_density`: pontuação por token — proxy de enumeração de múltiplos
  achados (`fever, tachycardia, hypotension`) num único laudo.
"""

import re

from sklearn.base import BaseEstimator, TransformerMixin

_TOKEN_RE = re.compile(r"\S+")
_DIGIT_RE = re.compile(r"\d")
_PUNCT_RE = re.compile(r"[.,;:!?]")


def _structural_row(text: str) -> list[float]:
    tokens = _TOKEN_RE.findall(text)
    n_tokens = len(tokens) or 1
    n_numeric = sum(1 for tok in tokens if _DIGIT_RE.search(tok))
    n_punct = len(_PUNCT_RE.findall(text))
    return [float(len(tokens)), n_numeric / n_tokens, n_punct / n_tokens]


class StructuralFeatures(BaseEstimator, TransformerMixin):
    """Produz 3 colunas numéricas por documento: `n_tokens`, `numeric_density`,
    `punct_density`."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [_structural_row(text) for text in X]

    def get_feature_names_out(self, input_features=None):
        return ["n_tokens", "numeric_density", "punct_density"]
