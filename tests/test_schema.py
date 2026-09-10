"""Valida o schema do dataset processado (train/test) gerado pelo pipeline de dados."""

from pathlib import Path

import pandas as pd
import pandera.pandas as pa
import pytest

from src.data.schema import ProcessedDatasetSchema

PROCESSED_DIR = Path("data/processed")
FILES_ESPERADOS = ("train.csv", "test.csv")


@pytest.mark.parametrize("filename", FILES_ESPERADOS)
def test_processed_file_segue_o_schema(filename):
    path = PROCESSED_DIR / filename
    if not path.exists():
        pytest.skip(f"{path} não existe — rode `dvc repro` antes de testar o schema")
    df = pd.read_csv(path)
    ProcessedDatasetSchema.validate(df)


def test_schema_rejeita_urgency_label_invalido():
    df = pd.DataFrame(
        {
            "condition_label": [1],
            "text": ["abstract de teste"],
            "original_label": ["neoplasms"],
            "urgency_label": ["nao_e_uma_classe_valida"],
        }
    )
    with pytest.raises(pa.errors.SchemaError):
        ProcessedDatasetSchema.validate(df)
