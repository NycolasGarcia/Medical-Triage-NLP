"""Caixa 6.6 — exporta uma variante ONNX do modelo, para inferência mais rápida
via ONNX Runtime (`src/optimization/onnx_runtime.py`, servida atrás de uma flag
em `src/api/model_runtime.py`, caixa 6.9).

Representação **diferente** da vencedora de caixa 6.1 (`PRODUCTION_REPRESENTATION`,
`src/features/vectorize.py`): só bigramas de palavra, sem char n-gramas nem
marcação de negação. Não é escolha de qualidade, é limitação real do `skl2onnx`
descoberta ao tentar exportar o pipeline completo — ver `docs/adr/0004-tecnica-
otimizacao-latencia.md` para o diagnóstico e a decisão de manter as duas variantes
servíveis (`ONNX_REPRESENTATION` aqui é exatamente `f6_repr_baseline` de
`docs/EXPERIMENTS.md`, F1-macro 0,7234 já medido em CV — não remedido aqui).

Calibração isotônica própria (`src/optimization/calibrator.py`), não
`CalibratedClassifierCV` — pelo mesmo motivo: não converte para ONNX.
"""

from pathlib import Path

import joblib
import mlflow
import pandas as pd
from skl2onnx import to_onnx
from skl2onnx.common.data_types import StringTensorType
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.config import settings
from src.features.vectorize import RepresentationConfig, build_representation
from src.logging_config import configure_logging, get_logger
from src.models.tracking import configure_tracking
from src.optimization.calibrator import OneVsRestIsotonicCalibrator

logger = get_logger(__name__)

SEED = 42
CALIB_HOLDOUT_FRACTION = 0.2
ONNX_REPRESENTATION = RepresentationConfig(name="onnx_word_bigrams")


def build_onnx_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("features", build_representation(ONNX_REPRESENTATION)),
            ("clf", LogisticRegression(max_iter=1000, random_state=SEED)),
        ]
    )


def export_onnx_model(
    train_path: str = "data/processed/train.csv",
    output_dir: str = settings.model_path,
) -> dict:
    """Treina + calibra (calibrador manual, one-vs-rest isotônico) + exporta a
    variante ONNX. Retorna os caminhos dos dois artefatos persistidos (o `.onnx`
    e o calibrador — precisam andar juntos, o runtime carrega os dois)."""
    train = pd.read_csv(train_path)
    X_fit, X_calib, y_fit, y_calib = train_test_split(
        train["text"],
        train["urgency_label"],
        test_size=CALIB_HOLDOUT_FRACTION,
        random_state=SEED,
        stratify=train["urgency_label"],
    )

    pipeline = build_onnx_pipeline()
    pipeline.fit(X_fit, y_fit)

    calibrator = OneVsRestIsotonicCalibrator().fit(
        pipeline.predict_proba(X_calib), y_calib.to_numpy(), list(pipeline.classes_)
    )

    onnx_model = to_onnx(pipeline, initial_types=[("text", StringTensorType([None, 1]))])

    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    onnx_path = output_dir_path / "model.onnx"
    calibrator_path = output_dir_path / "onnx_calibrator.joblib"
    onnx_path.write_bytes(onnx_model.SerializeToString())
    joblib.dump(calibrator, calibrator_path)

    configure_tracking()
    with mlflow.start_run(run_name="f6_onnx_export"):
        mlflow.log_params(
            {
                "representation": ONNX_REPRESENTATION.name,
                "seed": SEED,
                "calib_holdout_fraction": CALIB_HOLDOUT_FRACTION,
                "n_samples_fit": len(X_fit),
            }
        )
        mlflow.log_artifact(str(onnx_path))

    logger.info(
        "modelo_onnx_exportado",
        extra={"onnx_path": str(onnx_path), "calibrator_path": str(calibrator_path)},
    )
    return {"onnx_path": onnx_path, "calibrator_path": calibrator_path}


if __name__ == "__main__":
    configure_logging()
    export_onnx_model()
