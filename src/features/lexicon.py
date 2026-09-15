"""Léxico de severidade clínica (inglês — idioma do dataset e da API, ver
`docs/model_card.md`). Conta termos de alta e baixa gravidade como sinal
numérico extra além do TF-IDF de palavras — hipótese: um laudo com `acute`,
`shock`, `critical` carrega urgência mesmo se essas palavras isoladas não
dominarem o vocabulário mais frequente.

Consciente de negação por construção (usa `negation_flags` de `src.features.negation`,
não texto já marcado) — `denies acute distress` não deve contar como termo de alta
severidade presente.
"""

from sklearn.base import BaseEstimator, TransformerMixin

from src.features.negation import negation_flags

HIGH_SEVERITY_TERMS = frozenset(
    {
        "acute",
        "severe",
        "critical",
        "emergent",
        "emergency",
        "shock",
        "massive",
        "fulminant",
        "refractory",
        "unstable",
        "deteriorating",
        "arrest",
        "hemorrhage",
        "hemorrhagic",
        "collapse",
        "life-threatening",
        "rupture",
        "ruptured",
        "malignant",
        "metastatic",
        "progressive",
        "respiratory failure",
    }
)

LOW_SEVERITY_TERMS = frozenset(
    {
        "mild",
        "stable",
        "chronic",
        "resolved",
        "improving",
        "routine",
        "benign",
        "asymptomatic",
        "well-controlled",
        "unremarkable",
        "follow-up",
        "minimal",
    }
)


def _count_terms(tokens_with_flags: list[tuple[str, bool]], terms: frozenset[str]) -> int:
    return sum(1 for token, negated in tokens_with_flags if not negated and token in terms)


class SeverityLexiconCounter(BaseEstimator, TransformerMixin):
    """Produz 2 colunas por documento: contagem de termos de alta e de baixa
    severidade, ambas descontando termos dentro de escopo de negação."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        rows = []
        for text in X:
            flags = negation_flags(text)
            rows.append(
                [_count_terms(flags, HIGH_SEVERITY_TERMS), _count_terms(flags, LOW_SEVERITY_TERMS)]
            )
        return rows

    def get_feature_names_out(self, input_features=None):
        return ["severity_high_count", "severity_low_count"]
