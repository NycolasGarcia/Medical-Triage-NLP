"""Factory de modelos candidatos para o classificador de urgência."""

from collections.abc import Callable

from lightgbm import LGBMClassifier
from sklearn.base import ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

SEED = 42

_MODEL_BUILDERS: dict[str, Callable[[], ClassifierMixin]] = {
    "dummy": lambda: DummyClassifier(strategy="stratified", random_state=SEED),
    "logreg": lambda: LogisticRegression(max_iter=1000, random_state=SEED),
    "random_forest": lambda: RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=-1),
    "multinomial_nb": lambda: MultinomialNB(),
    "lightgbm": lambda: LGBMClassifier(random_state=SEED, verbosity=-1),
    # LinearSVC não tem predict_proba nativo (motivo do descarte em F2/EXPERIMENTS.md);
    # CalibratedClassifierCV adiciona calibração sigmoide (Platt) para viabilizar como candidato.
    "linear_svc_calibrated": lambda: CalibratedClassifierCV(
        LinearSVC(random_state=SEED), method="sigmoid"
    ),
}


def build_model(name: str) -> ClassifierMixin:
    """Constrói o classificador de `_MODEL_BUILDERS`; levanta ValueError se desconhecido."""
    try:
        return _MODEL_BUILDERS[name]()
    except KeyError as exc:
        raise ValueError(f"Modelo desconhecido: {name!r}") from exc
