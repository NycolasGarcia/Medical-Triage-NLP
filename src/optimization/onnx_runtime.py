"""Runtime de inferência via ONNX (caixa 6.6/6.9). Interface compatível com
`predict_proba`/`predict`/`classes_` do sklearn — o resto da API
(`src/api/model_runtime.py`, `src/api/main.py`) não precisa saber qual backend
está ativo."""

from pathlib import Path

import joblib
import numpy as np
import onnxruntime as ort

from src.data.labels import URGENCY_CLASSES
from src.optimization.calibrator import OneVsRestIsotonicCalibrator


class OnnxPipeline:
    """Sessão ONNX Runtime + calibrador isotônico, com a mesma interface pública
    (`classes_`, `predict`, `predict_proba`) que o `Pipeline` sklearn servido pelo
    outro backend."""

    def __init__(
        self, session: ort.InferenceSession, calibrator: OneVsRestIsotonicCalibrator
    ) -> None:
        self._session = session
        self._calibrator = calibrator
        self._input_name = session.get_inputs()[0].name
        self.classes_ = np.array(sorted(URGENCY_CLASSES))

    def predict_proba(self, texts) -> np.ndarray:
        text_array = np.array([[t] for t in texts], dtype=object)
        _, proba_maps = self._session.run(None, {self._input_name: text_array})
        raw = np.array([[row[label] for label in self.classes_] for row in proba_maps])
        return self._calibrator.transform(raw)

    def predict(self, texts) -> np.ndarray:
        proba = self.predict_proba(texts)
        return self.classes_[np.argmax(proba, axis=1)]


def load_onnx_pipeline(model_dir: str) -> OnnxPipeline:
    """Carrega o `.onnx` + o calibrador persistidos por `onnx_export.py`."""
    model_dir_path = Path(model_dir)
    session = ort.InferenceSession(str(model_dir_path / "model.onnx"))
    calibrator = joblib.load(model_dir_path / "onnx_calibrator.joblib")
    return OnnxPipeline(session, calibrator)
