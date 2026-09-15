"""Caixa 6.1 — tuning de representação em validação cruzada.

Protocolo aprovado pelo autor (2026-09-15, ver `docs/PROGRESS.md`): busca gulosa
incremental em vez de fatorial completo (2^4 = 16 combinações). Baseline (já com
a correção de bigramas de §10.6) -> cada candidato isolado contra o baseline ->
incorpora o vencedor, testa os restantes em cima -> repete até não haver ganho ->
checagem cirúrgica do 2º colocado do primeiro round combinado à config final ->
classificador ordinal (`mord`) como eixo separado, testado só por cima da
representação vencedora, contra Regressão Logística na mesma representação.
Orçamento máximo: ~13 runs (4 + 3 + 2 + 1 no pior caso da busca gulosa + 1
checagem cirúrgica + 1 eixo ordinal); para de crescer assim que uma rodada não
melhora nada.
"""

from dataclasses import replace

import mlflow
import mord
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline

from src.data.labels import URGENCY_CLASSES
from src.features.vectorize import RepresentationConfig, build_representation
from src.logging_config import configure_logging, get_logger
from src.models.evaluate import compute_metrics, count_sub_over_triage
from src.models.tracking import configure_tracking

logger = get_logger(__name__)

SEED = 42
N_SPLITS = 5
CANDIDATE_FLAGS = ("negation", "severity_lexicon", "structural", "char_ngrams")

_URGENCY_RANK = {label: i for i, label in enumerate(URGENCY_CLASSES)}
_RANK_TO_LABEL = {i: label for label, i in _URGENCY_RANK.items()}
_LABELS_SORTED = sorted(URGENCY_CLASSES)


def _build_pipeline(config: RepresentationConfig, ordinal: bool) -> Pipeline:
    clf = mord.LogisticAT() if ordinal else LogisticRegression(max_iter=1000, random_state=SEED)
    return Pipeline([("features", build_representation(config)), ("clf", clf)])


def _reorder_ordinal_proba(y_proba: np.ndarray, classes_: np.ndarray) -> np.ndarray:
    """`classes_` do `mord` vem em ordem ordinal (0,1,2); `compute_metrics` espera
    colunas na ordem alfabética de `URGENCY_CLASSES` (mesma convenção do sklearn
    com rótulo string, ver `evaluate.py`). Reordena antes de repassar."""
    col_labels = [_RANK_TO_LABEL[c] for c in classes_]
    order = [col_labels.index(label) for label in _LABELS_SORTED]
    return y_proba[:, order]


def _evaluate_fold(config: RepresentationConfig, ordinal: bool, X_text, y, train_idx, val_idx):
    pipeline = _build_pipeline(config, ordinal)
    X_train, X_val = X_text.iloc[train_idx], X_text.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

    y_train_fit = y_train.map(_URGENCY_RANK) if ordinal else y_train
    pipeline.fit(X_train, y_train_fit)

    y_proba = pipeline.predict_proba(X_val)
    if ordinal:
        y_pred = pd.Series(pipeline.predict(X_val)).map(_RANK_TO_LABEL).to_numpy()
        y_proba = _reorder_ordinal_proba(y_proba, pipeline.named_steps["clf"].classes_)
    else:
        y_pred = pipeline.predict(X_val)

    metrics = compute_metrics(y_val, y_pred, y_proba)
    triage = count_sub_over_triage(y_val, y_pred)
    return metrics, triage


def run_cv(
    config: RepresentationConfig, X_text: pd.Series, y: pd.Series, ordinal: bool = False
) -> dict:
    """CV de 5 dobras, mesmo seed do F2, para uma config de representação."""
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
    fold_results = [
        _evaluate_fold(config, ordinal, X_text, y, tr, val) for tr, val in skf.split(X_text, y)
    ]
    metrics_list, triages = zip(*fold_results, strict=True)
    avg_metrics = {k: float(np.mean([m[k] for m in metrics_list])) for k in metrics_list[0]}
    triage_total = {k: sum(t[k] for t in triages) for k in triages[0]}
    return {"metrics": avg_metrics, "triage": triage_total}


def _log_run(run_name: str, config: RepresentationConfig, ordinal: bool, result: dict) -> None:
    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(
            {
                "negation": config.negation,
                "severity_lexicon": config.severity_lexicon,
                "structural": config.structural,
                "char_ngrams": config.char_ngrams,
                "word_ngram_range": str(config.word_ngram_range),
                "clf": "mord_logistic_at" if ordinal else "logreg",
                "seed": SEED,
                "n_splits": N_SPLITS,
            }
        )
        mlflow.log_metrics(result["metrics"])
        mlflow.log_metrics({f"triage_{k}": v for k, v in result["triage"].items()})


def _run_and_log(
    run_name: str, config: RepresentationConfig, X_text, y, ordinal: bool = False
) -> dict:
    result = run_cv(config, X_text, y, ordinal=ordinal)
    _log_run(run_name, config, ordinal, result)
    logger.info(
        "run_representacao_concluida",
        extra={"run": run_name, "f1_macro": result["metrics"]["f1_macro"]},
    )
    return result


def _greedy_search(
    X_text, y
) -> tuple[RepresentationConfig, float, dict[str, dict], dict[str, float]]:
    """Retorna (config vencedora, F1-macro da vencedora, resultados por run,
    F1-macro de cada candidato isolado no round 1 — usado depois pela checagem
    cirúrgica)."""
    all_results: dict[str, dict] = {}

    current_config = RepresentationConfig(name="baseline")
    baseline_result = _run_and_log("f6_repr_baseline", current_config, X_text, y)
    all_results["baseline"] = baseline_result
    current_score = baseline_result["metrics"]["f1_macro"]

    remaining = list(CANDIDATE_FLAGS)
    first_round_scores: dict[str, float] = {}
    round_n = 1

    while remaining:
        round_scores: dict[str, tuple[RepresentationConfig, dict]] = {}
        for flag in remaining:
            candidate_config = replace(
                current_config, name=f"{current_config.name}+{flag}", **{flag: True}
            )
            result = _run_and_log(f"f6_repr_r{round_n}_{flag}", candidate_config, X_text, y)
            round_scores[flag] = (candidate_config, result)
            all_results[f"r{round_n}_{flag}"] = result
            if round_n == 1:
                first_round_scores[flag] = result["metrics"]["f1_macro"]

        best_flag = max(round_scores, key=lambda f: round_scores[f][1]["metrics"]["f1_macro"])
        best_config, best_result = round_scores[best_flag]
        best_score = best_result["metrics"]["f1_macro"]

        if best_score <= current_score:
            logger.info(
                "busca_gulosa_parou", extra={"round": round_n, "melhor_sem_ganho": best_flag}
            )
            break

        current_config, current_score = best_config, best_score
        remaining = [f for f in remaining if f != best_flag]
        round_n += 1

    return current_config, current_score, all_results, first_round_scores


def run_representation_search() -> dict:
    """Executa a busca gulosa completa + checagem cirúrgica + eixo ordinal.
    Loga cada run no MLflow; devolve um resumo para consulta/documentação."""
    configure_tracking()
    train = pd.read_csv("data/processed/train.csv")
    X_text, y = train["text"], train["urgency_label"]

    winner_config, winner_score, all_results, first_round_scores = _greedy_search(X_text, y)

    # Checagem cirúrgica: 2º colocado do round 1 combinado à config final vencedora,
    # mesmo que a busca gulosa não tenha passado por essa combinação.
    active_flags = {f for f in CANDIDATE_FLAGS if getattr(winner_config, f)}
    remaining_from_r1 = [f for f in first_round_scores if f not in active_flags]
    if remaining_from_r1:
        runner_up = max(remaining_from_r1, key=lambda f: first_round_scores[f])
        surgical_config = replace(
            winner_config, name=f"{winner_config.name}+{runner_up}_surgical", **{runner_up: True}
        )
        surgical_result = _run_and_log("f6_repr_surgical_check", surgical_config, X_text, y)
        all_results["surgical_check"] = surgical_result
        surgical_score = surgical_result["metrics"]["f1_macro"]
        if surgical_score > winner_score:
            winner_config, winner_score = surgical_config, surgical_score

    # Eixo separado: classificador ordinal (mord) sobre a representação vencedora.
    ordinal_result = _run_and_log("f6_repr_ordinal_mord", winner_config, X_text, y, ordinal=True)
    all_results["ordinal_mord"] = ordinal_result

    logger.info(
        "busca_representacao_concluida",
        extra={
            "config_vencedora": winner_config.name,
            "f1_macro_vencedora": winner_score,
            "total_runs": len(all_results),
        },
    )
    return {"winner_config": winner_config, "winner_score": winner_score, "results": all_results}


if __name__ == "__main__":
    configure_logging()
    run_representation_search()
