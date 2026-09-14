"""DAG de retreino: ingest -> preprocess -> train -> evaluate -> register.

Cada task chama funções já existentes em `src/` (nenhuma lógica de negócio
vive aqui, só orquestração — ver §12 do CLAUDE.md). Registra uma nova versão
do modelo no MLflow Model Registry a cada execução; **não promove** a
Staging/Production automaticamente — o critério de promoção é decisão de
ADR-0008 (F6), fora do escopo desta DAG.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pendulum
from airflow.sdk import dag, task

# Airflow importa este arquivo diretamente (não via `python -m`), então o
# pacote `src` do projeto não entra em sys.path por padrão — as tasks abaixo
# fazem `from src...` dentro do corpo da função, depois deste bootstrap rodar.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dag(
    dag_id="retrain_triage_model",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["triagem-urgencia", "retreino"],
)
def retrain_triage_model():
    """Pipeline de retreino do classificador de urgência de laudos médicos."""

    @task()
    def ingest() -> None:
        from src.data.load import download_raw

        download_raw(PROJECT_ROOT / "data" / "raw")

    @task()
    def preprocess() -> dict:
        from src.data.prepare import prepare
        from src.data.split import stratified_split

        processed_dir = PROJECT_ROOT / "data" / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)

        deduped = prepare(PROJECT_ROOT / "data" / "raw")
        deduped.to_csv(processed_dir / "deduped.csv", index=False)

        train_df, test_df = stratified_split(deduped)
        train_df.to_csv(processed_dir / "train.csv", index=False)
        test_df.to_csv(processed_dir / "test.csv", index=False)
        return {"train_rows": len(train_df), "test_rows": len(test_df)}

    @task()
    def train() -> dict:
        from src.models.train import train_and_persist

        result = train_and_persist()
        return {"artifact_path": str(result.artifact_path), "run_id": result.run_id}

    @task()
    def evaluate(train_result: dict) -> dict:
        import joblib
        import mlflow

        from src.models.evaluate import evaluate_pipeline
        from src.models.tracking import configure_tracking

        pipeline = joblib.load(train_result["artifact_path"])
        metrics = evaluate_pipeline(pipeline)

        configure_tracking()
        with mlflow.start_run(run_id=train_result["run_id"]):
            mlflow.log_metrics({f"test_{k}": v for k, v in metrics.items()})
        return metrics

    @task()
    def register(train_result: dict, evaluate_result: dict) -> dict:
        import mlflow

        from src.models.tracking import configure_tracking

        configure_tracking()
        model_uri = f"runs:/{train_result['run_id']}/model"
        version = mlflow.register_model(model_uri, name="triagem-urgencia")
        return {
            "registered_version": version.version,
            "f1_macro_teste": evaluate_result["f1_macro"],
        }

    ingest_task = ingest()
    preprocess_task = preprocess()
    train_task = train()
    evaluate_task = evaluate(train_task)
    register(train_task, evaluate_task)

    ingest_task >> preprocess_task >> train_task


retrain_triage_model()
