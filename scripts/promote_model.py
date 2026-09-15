"""Promove o modelo de produção no MLflow Registry (caixa 6.10) — reproduz, fora
da DAG, a mesma lógica da task `register` de `airflow/dags/retrain_dag.py`
(registro + tags de elegibilidade), mais o passo que a task não faz: trocar o
alias `@production`. Promoção continua decisão manual (ADR-0008/ADR-0010): sem
`--promote`, o script só registra a versão, avalia e reporta elegibilidade — a
troca do alias só acontece com o autor passando a flag explicitamente, mesmo
quando a versão é elegível.

Uso: `uv run python -m scripts.promote_model [--promote]` (usa o `model.joblib` +
`data/processed/test.csv` atuais; assume que `make train` já rodou).
"""

import argparse

import joblib
import mlflow

from src.config import settings
from src.logging_config import configure_logging, get_logger
from src.models.evaluate import evaluate_pipeline
from src.models.promotion import MODEL_NAME, get_production_mean_cost, meets_promotion_criteria
from src.models.tracking import configure_tracking

logger = get_logger(__name__)


def _latest_train_run_id(client: mlflow.MlflowClient) -> str:
    experiment = mlflow.get_experiment_by_name("triagem-urgencia")
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="tags.mlflow.runName = 'final_train_logreg'",
        order_by=["start_time DESC"],
        max_results=1,
    )
    if not runs:
        raise RuntimeError("Nenhum run 'final_train_logreg' encontrado — rode `make train` antes.")
    return runs[0].info.run_id


def promote(
    min_recall_urgente: float = 0.85, max_cost_increase: float = 0.10, promote_alias: bool = False
) -> dict:
    configure_tracking()
    client = mlflow.MlflowClient()

    pipeline = joblib.load(f"{settings.model_path}/model.joblib")
    evaluate_result = evaluate_pipeline(pipeline)

    run_id = _latest_train_run_id(client)
    model_uri = f"runs:/{run_id}/model"
    version = mlflow.register_model(model_uri, name=MODEL_NAME)
    v = version.version

    baseline_cost = get_production_mean_cost(client)
    elegivel = meets_promotion_criteria(
        evaluate_result["recall_urgente"],
        evaluate_result["mean_cost"],
        min_recall_urgente,
        max_cost_increase,
        baseline_cost,
    )
    client.set_model_version_tag(MODEL_NAME, v, "mean_cost", str(evaluate_result["mean_cost"]))
    client.set_model_version_tag(
        MODEL_NAME, v, "recall_urgente", str(evaluate_result["recall_urgente"])
    )
    client.set_model_version_tag(MODEL_NAME, v, "elegivel_promocao", str(elegivel))

    result = {
        "version": v,
        "recall_urgente": evaluate_result["recall_urgente"],
        "mean_cost": evaluate_result["mean_cost"],
        "baseline_mean_cost": baseline_cost,
        "elegivel_promocao": elegivel,
        "promovido": False,
    }
    logger.info(
        "versao_avaliada", extra={key: val for key, val in result.items() if key != "promovido"}
    )

    if elegivel and promote_alias:
        client.set_registered_model_alias(MODEL_NAME, "production", v)
        result["promovido"] = True
        logger.info("modelo_promovido", extra={"versao": v, "alias": "production"})
    elif elegivel:
        logger.info(
            "modelo_elegivel_nao_promovido",
            extra={"versao": v, "motivo": "elegível, mas --promote não foi passado"},
        )
    else:
        logger.info("modelo_nao_promovido", extra={"versao": v, "motivo": "não elegível"})

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-recall-urgente", type=float, default=0.85)
    parser.add_argument("--max-cost-increase", type=float, default=0.10)
    parser.add_argument(
        "--promote", action="store_true", help="Troca o alias @production se elegível."
    )
    args = parser.parse_args()

    configure_logging()
    promote(args.min_recall_urgente, args.max_cost_increase, args.promote)
