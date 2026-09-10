"""Schema pandera do dataset processado (pós dedupe + mapeamento de rótulo)."""

import pandera.pandas as pa
from pandera.typing import Series

from src.data.labels import URGENCY_CLASSES

ORIGINAL_LABELS = (
    "neoplasms",
    "digestive system diseases",
    "nervous system diseases",
    "cardiovascular diseases",
    "general pathological conditions",
)


class ProcessedDatasetSchema(pa.DataFrameModel):
    condition_label: Series[int] = pa.Field(isin=[1, 2, 3, 4, 5])
    text: Series[str] = pa.Field(str_length={"min_value": 1})
    original_label: Series[str] = pa.Field(isin=ORIGINAL_LABELS)
    urgency_label: Series[str] = pa.Field(isin=list(URGENCY_CLASSES))

    class Config:
        strict = True
        coerce = True
