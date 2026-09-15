"""Testa o calibrador isotônico manual (caminho ONNX, caixa 6.6)."""

import numpy as np

from src.optimization.calibrator import OneVsRestIsotonicCalibrator


def test_linhas_somam_1():
    rng = np.random.default_rng(42)
    raw = rng.dirichlet([1, 1, 1], size=50)
    y_true = rng.choice(["a", "b", "c"], size=50)
    calibrator = OneVsRestIsotonicCalibrator().fit(raw, y_true, ["a", "b", "c"])
    calibrated = calibrator.transform(raw)
    assert np.allclose(calibrated.sum(axis=1), 1.0)


def test_score_alto_da_classe_correta_gera_probabilidade_calibrada_alta():
    # classe "a" sempre tem o maior score bruto quando y_true == "a"
    raw = np.array(
        [
            [0.9, 0.05, 0.05],
            [0.85, 0.1, 0.05],
            [0.1, 0.85, 0.05],
            [0.05, 0.9, 0.05],
            [0.05, 0.05, 0.9],
            [0.1, 0.05, 0.85],
        ]
    )
    y_true = np.array(["a", "a", "b", "b", "c", "c"])
    calibrator = OneVsRestIsotonicCalibrator().fit(raw, y_true, ["a", "b", "c"])
    calibrated = calibrator.transform(raw)
    for i, label in enumerate(y_true):
        idx = ["a", "b", "c"].index(label)
        assert calibrated[i, idx] == calibrated[i].max()


def test_protege_contra_divisao_por_zero_quando_soma_da_linha_e_zero():
    calibrator = OneVsRestIsotonicCalibrator()
    calibrator.classes_ = ["a", "b", "c"]

    class _ZeroCalibrator:
        def predict(self, x):
            return np.zeros_like(x)

    calibrator.calibrators_ = {label: _ZeroCalibrator() for label in calibrator.classes_}
    calibrated = calibrator.transform(np.array([[0.5, 0.3, 0.2]]))
    assert not np.isnan(calibrated).any()
    assert calibrated.tolist() == [[0.0, 0.0, 0.0]]
