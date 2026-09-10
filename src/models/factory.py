"""Factory de modelos candidatos para o classificador de urgência."""

from collections.abc import Callable

from sklearn.base import ClassifierMixin
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

SEED = 42

_MODEL_BUILDERS: dict[str, Callable[[], ClassifierMixin]] = {
    "dummy": lambda: DummyClassifier(strategy="stratified", random_state=SEED),
    "logreg": lambda: LogisticRegression(max_iter=1000, random_state=SEED),
    "random_forest": lambda: RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=-1),
}


def build_model(name: str) -> ClassifierMixin:
    try:
        return _MODEL_BUILDERS[name]()
    except KeyError as exc:
        raise ValueError(f"Modelo desconhecido: {name!r}") from exc
