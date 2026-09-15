# Evidência — revalidação da DAG após ADR-0010 (caixa 7.4/7.7)

O código da task `register` mudou na caixa 6.10 (critério de promoção:
`recall_urgente`/`mean_cost` no lugar de `f1_macro`/`sub_triagem_rate`) — só
tinha sido validado por import/sintaxe até este ponto, não por execução real.
Executado de ponta a ponta antes da auditoria final de F7.

## Execução

- **Ambiente:** `airflow standalone` local, `AIRFLOW_HOME` configurado,
  `AIRFLOW__CORE__LOAD_EXAMPLES=False`. Scheduler, triggerer, dag-processor e
  api-server todos `healthy` via `/api/v2/monitor/health`.
- **`airflow dags list-import-errors`**: nenhum erro.
- **Run:** `manual__2026-09-15T23:17:41.159763+00:00`, disparada via
  `airflow dags trigger retrain_triage_model`.

| Task | Estado | Início | Fim |
|---|---|---|---|
| `ingest` | `success` | 23:17:42 | 23:17:46 |
| `preprocess` | `success` | 23:17:47 | 23:17:59 |
| `train` | `success` | 23:18:00 | 23:21:42 |
| `evaluate` | `success` | 23:21:42 | 23:21:50 |
| `register` | `success` | 23:21:51 | 23:21:53 |

## Resultado da task `register` (log real)

```
Returned value was: {'registered_version': 6, 'recall_urgente_teste': 0.8802547770700637,
'mean_cost_teste': 0.6717, 'elegivel_promocao': True}
```

Confirma que o critério de ADR-0010 (`min_recall_urgente=0,85`,
`max_cost_increase=0,10`, sem baseline de custo anterior registrado nesta
execução isolada) funciona corretamente na execução real via Airflow, não só
em teste unitário isolado (`tests/test_promotion.py`).

## Nota sobre a versão registrada

Versão **6** ficou registrada com a tag `elegivel_promocao=True`, mas o alias
`@production` **não foi trocado** por esta execução — a DAG só calcula e loga
elegibilidade (ADR-0008/ADR-0010: gate humano, não promoção automática). A
versão em produção continua sendo a **5**, promovida manualmente em caixa 6.10
via `scripts/promote_model.py --promote`. Comportamento esperado, não
divergência.
