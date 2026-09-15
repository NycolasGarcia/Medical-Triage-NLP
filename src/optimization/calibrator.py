"""Calibração isotônica one-vs-rest implementada explicitamente (não via
`CalibratedClassifierCV`) — necessário porque o caminho ONNX (caixa 6.6) não pode
usar `CalibratedClassifierCV` (o conversor do skl2onnx só aceita entrada numérica,
não uma pipeline de texto encadeada). A lógica é a mesma que o sklearn usa
internamente para calibração multiclasse (um `IsotonicRegression` por classe,
seguido de renormalização para somar 1) — só explícita em vez de escondida atrás
de uma API que não é exportável.

**Diferença deliberada do `CalibratedClassifierCV` do sklearn**: por padrão, o
sklearn calibra sobre `decision_function` (margem bruta antes do softmax) quando o
estimador oferece os dois métodos — confirmado empiricamente nesta sessão comparando
os dois (`decision_function` bateu byte a byte com a referência; `predict_proba` não,
diferença de até 0,23 na probabilidade calibrada). Esta classe calibra sobre
`predict_proba`, não `decision_function`, porque é isso que sai do runtime ONNX (o
grafo exportado expõe probabilidades, não os escores brutos do classificador linear)
— ver `docs/adr/0004-tecnica-otimizacao-latencia.md`. Escolha consciente, consistente
do fit ao serving (o calibrador é sempre ajustado e aplicado sobre o mesmo tipo de
escore), não uma tentativa de replicar exatamente a calibração do pipeline sklearn
de 6.2 — são modelos diferentes (representações diferentes), calibrações
independentes."""

import numpy as np
from sklearn.isotonic import IsotonicRegression


class OneVsRestIsotonicCalibrator:
    """Calibra `predict_proba` bruto de um classificador multiclasse: um
    `IsotonicRegression` por classe (rótulo real == classe vs. resto), depois
    renormaliza para as probabilidades calibradas somarem 1 por amostra."""

    def __init__(self) -> None:
        self.classes_: list[str] = []
        self.calibrators_: dict[str, IsotonicRegression] = {}

    def fit(
        self, y_proba_raw: np.ndarray, y_true: np.ndarray, classes: list[str]
    ) -> "OneVsRestIsotonicCalibrator":
        self.classes_ = list(classes)
        self.calibrators_ = {}
        for i, cls in enumerate(self.classes_):
            calibrator = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
            calibrator.fit(y_proba_raw[:, i], (y_true == cls).astype(float))
            self.calibrators_[cls] = calibrator
        return self

    def transform(self, y_proba_raw: np.ndarray) -> np.ndarray:
        calibrated = np.column_stack(
            [
                self.calibrators_[cls].predict(y_proba_raw[:, i])
                for i, cls in enumerate(self.classes_)
            ]
        )
        row_sums = calibrated.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0  # evita divisão por zero se as 3 calibrações derem 0
        return calibrated / row_sums
