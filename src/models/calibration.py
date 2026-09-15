"""Caixa 6.2 — calibração de probabilidade sobre a representação vencedora de 6.1.

§7 é explícito: "sem calibrar, ajustar limiar é chute com aparência de método" — esta
caixa mede se as probabilidades já são bem-calibradas (Regressão Logística costuma
ser razoável nisso) ou se Platt/isotônica melhoram antes da caixa 6.4 mexer em limiar.

Protocolo: para cada dobra externa (5, seed 42, igual às demais caixas de F2/F6),
separa uma fatia de calibração (20%, estratificada) do próprio treino da dobra — o
pipeline (representação + LogReg) é ajustado só no restante (80%), e a calibração
(Platt/isotônica) é ajustada só na fatia separada, via `cv="prefit"`. Evita o custo
de reajustar o pipeline inteiro (TF-IDF + char n-grama) váras vezes por dobra, que
seria o preço do `cv` k-fold embutido do `CalibratedClassifierCV`.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from src.data.labels import URGENCY_CLASSES
from src.features.vectorize import PRODUCTION_REPRESENTATION, build_representation
from src.logging_config import configure_logging, get_logger
from src.models.evaluate import compute_metrics, count_sub_over_triage
from src.models.tracking import configure_tracking

logger = get_logger(__name__)

SEED = 42
N_SPLITS = 5
CALIB_HOLDOUT_FRACTION = 0.2
METHODS = ("none", "sigmoid", "isotonic")
_LABELS_SORTED = sorted(URGENCY_CLASSES)
_URGENTE_IDX = _LABELS_SORTED.index("urgente")


def _build_base_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("features", build_representation(PRODUCTION_REPRESENTATION)),
            ("clf", LogisticRegression(max_iter=1000, random_state=SEED)),
        ]
    )


def _brier_multiclass(y_true: np.ndarray, y_proba: np.ndarray, labels: list[str]) -> float:
    """Extensão multiclasse do Brier score: distância euclidiana ao quadrado entre a
    probabilidade prevista e o one-hot da classe real, média sobre as amostras."""
    y_onehot = np.array([[1.0 if label == cls else 0.0 for cls in labels] for label in y_true])
    return float(np.mean(np.sum((y_proba - y_onehot) ** 2, axis=1)))


def _ece_binary(y_true_binary: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Expected Calibration Error: diferença ponderada entre confiança média prevista
    e frequência real observada, por faixa de probabilidade."""
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    n = len(y_true_binary)
    ece = 0.0
    for lo, hi in zip(bin_edges[:-1], bin_edges[1:], strict=True):
        mask = (y_prob >= lo) & (y_prob < hi) if hi < 1.0 else (y_prob >= lo) & (y_prob <= hi)
        if not mask.any():
            continue
        bin_confidence = y_prob[mask].mean()
        bin_accuracy = y_true_binary[mask].mean()
        ece += (mask.sum() / n) * abs(bin_accuracy - bin_confidence)
    return float(ece)


def _evaluate_method(estimator, X_val: pd.Series, y_val: pd.Series) -> dict:
    y_pred = estimator.predict(X_val)
    y_proba = estimator.predict_proba(X_val)
    metrics = compute_metrics(y_val, y_pred, y_proba)
    triage = count_sub_over_triage(y_val, y_pred)
    brier = _brier_multiclass(y_val.to_numpy(), y_proba, _LABELS_SORTED)
    urgente_true = (y_val.to_numpy() == "urgente").astype(float)
    urgente_proba = y_proba[:, _URGENTE_IDX]
    ece_urgente = _ece_binary(urgente_true, urgente_proba)
    return {
        "metrics": metrics,
        "triage": triage,
        "brier": brier,
        "ece_urgente": ece_urgente,
        "urgente_true": urgente_true,
        "urgente_proba": urgente_proba,
    }


def _fold_results(X_text: pd.Series, y: pd.Series, train_idx, val_idx) -> dict[str, dict]:
    X_train_full, y_train_full = X_text.iloc[train_idx], y.iloc[train_idx]
    X_val, y_val = X_text.iloc[val_idx], y.iloc[val_idx]

    X_fit, X_calib, y_fit, y_calib = train_test_split(
        X_train_full,
        y_train_full,
        test_size=CALIB_HOLDOUT_FRACTION,
        random_state=SEED,
        stratify=y_train_full,
    )

    base = _build_base_pipeline()
    base.fit(X_fit, y_fit)

    results = {"none": _evaluate_method(base, X_val, y_val)}
    for method in ("sigmoid", "isotonic"):
        # FrozenEstimator (sklearn >= 1.6) substitui o antigo cv="prefit": impede que
        # CalibratedClassifierCV reajuste o pipeline já treinado em `X_fit`/`y_fit`.
        # `cv=2` (mínimo aceito): como o estimador está congelado, `fit()` por dobra
        # é no-op — o valor de `cv` só satisfaz a validação de amostras mínimas por
        # classe da API, não muda a substância (nenhum refit real acontece).
        calibrated = CalibratedClassifierCV(estimator=FrozenEstimator(base), method=method, cv=2)
        calibrated.fit(X_calib, y_calib)
        results[method] = _evaluate_method(calibrated, X_val, y_val)
    return results


def _log_run(method: str, summary: dict) -> None:
    with mlflow.start_run(run_name=f"f6_calib_{method}"):
        mlflow.log_params(
            {
                "calibration_method": method,
                "calib_holdout_fraction": CALIB_HOLDOUT_FRACTION,
                "seed": SEED,
                "n_splits": N_SPLITS,
            }
        )
        mlflow.log_metrics(summary["metrics"])
        mlflow.log_metrics({f"triage_{k}": v for k, v in summary["triage"].items()})
        mlflow.log_metric("brier_multiclass", summary["brier"])
        mlflow.log_metric("ece_urgente", summary["ece_urgente"])


def _plot_reliability_curve(summary: dict[str, dict], output_path: Path) -> None:
    """Curva de calibração (reliability diagram) one-vs-rest da classe `urgente`,
    sobrepondo as 3 variantes — artefato exigido pela caixa 6.2."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey", label="calibração perfeita")
    for method, style in zip(METHODS, ("o-", "s-", "^-"), strict=True):
        frac_pos, mean_pred = calibration_curve(
            summary[method]["urgente_true"], summary[method]["urgente_proba"], n_bins=10
        )
        brier, ece = summary[method]["brier"], summary[method]["ece_urgente"]
        label = f"{method} (Brier {brier:.4f}, ECE {ece:.4f})"
        ax.plot(mean_pred, frac_pos, style, label=label)
    ax.set_xlabel("Probabilidade prevista (classe urgente, one-vs-rest)")
    ax.set_ylabel("Fração observada positiva")
    ax.set_title("Curva de calibração — caixa 6.2")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def run_calibration_search() -> dict[str, dict]:
    configure_tracking()
    train = pd.read_csv("data/processed/train.csv")
    X_text, y = train["text"], train["urgency_label"]
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)

    pooled: dict[str, dict[str, list]] = {
        m: {"metrics": [], "triage": [], "brier": [], "urgente_true": [], "urgente_proba": []}
        for m in METHODS
    }
    for train_idx, val_idx in skf.split(X_text, y):
        fold_results = _fold_results(X_text, y, train_idx, val_idx)
        for method, r in fold_results.items():
            pooled[method]["metrics"].append(r["metrics"])
            pooled[method]["triage"].append(r["triage"])
            pooled[method]["brier"].append(r["brier"])
            pooled[method]["urgente_true"].append(r["urgente_true"])
            pooled[method]["urgente_proba"].append(r["urgente_proba"])

    summary = {}
    for method in METHODS:
        avg_metrics = {
            k: float(np.mean([m[k] for m in pooled[method]["metrics"]]))
            for k in pooled[method]["metrics"][0]
        }
        triage_total = {
            k: sum(t[k] for t in pooled[method]["triage"]) for k in pooled[method]["triage"][0]
        }
        urgente_true_all = np.concatenate(pooled[method]["urgente_true"])
        urgente_proba_all = np.concatenate(pooled[method]["urgente_proba"])
        summary[method] = {
            "metrics": avg_metrics,
            "triage": triage_total,
            "brier": float(np.mean(pooled[method]["brier"])),
            "ece_urgente": _ece_binary(urgente_true_all, urgente_proba_all),
            "urgente_true": urgente_true_all,
            "urgente_proba": urgente_proba_all,
        }
        _log_run(method, summary[method])
        logger.info(
            "calibracao_avaliada",
            extra={
                "method": method,
                "f1_macro": summary[method]["metrics"]["f1_macro"],
                "brier": summary[method]["brier"],
                "ece_urgente": summary[method]["ece_urgente"],
            },
        )

    plot_path = Path("docs/evidence/f6_calibration_curve_2026-09-15.png")
    _plot_reliability_curve(summary, plot_path)
    with mlflow.start_run(run_name="f6_calibration_curve_artifact"):
        mlflow.log_artifact(str(plot_path))
    logger.info("curva_calibracao_salva", extra={"path": str(plot_path)})

    return summary


if __name__ == "__main__":
    configure_logging()
    run_calibration_search()
