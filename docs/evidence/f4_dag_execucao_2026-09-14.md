# Evidência de execução — DAG `retrain_triage_model` (F4, caixas 4.5–4.7)

Execução real contra o stack Airflow 3.2.2 local (`airflow standalone`), não
`airflow dags test` (achado registrado em `docs/PROGRESS.md`: `dags test`
tem um bug interno nesta versão — `AttributeError: 'State' object has no
attribute 'svcs_registry'` — contornado disparando via `dags trigger` contra
o scheduler real).

- **DAG run:** `manual__2026-09-14T12:42:31.738819+00:00`
- **Resultado:** `success`, todas as 5 tasks `success`, ~41s de ponta a ponta

## Estado de cada task

```
dag_id               | task_id    | state   | start_date                       | end_date
=====================+============+=========+==================================+=================================
retrain_triage_model | ingest     | success | 2026-09-14T12:42:33.119312+00:00 | 2026-09-14T12:42:35.670134+00:00
retrain_triage_model | preprocess | success | 2026-09-14T12:42:36.395710+00:00 | 2026-09-14T12:42:42.747656+00:00
retrain_triage_model | train      | success | 2026-09-14T12:42:43.669461+00:00 | 2026-09-14T12:43:05.717583+00:00
retrain_triage_model | evaluate   | success | 2026-09-14T12:43:06.395459+00:00 | 2026-09-14T12:43:09.940792+00:00
retrain_triage_model | register   | success | 2026-09-14T12:43:10.555103+00:00 | 2026-09-14T12:43:12.679085+00:00
```

## Log de aplicação por task (extraído do log real, ruído do Airflow removido)

```
=== TASK: ingest ===
raw_file_already_present (x3 — CSVs já baixados por execução anterior nesta sessão)
Done. Returned value was: None

=== TASK: preprocess ===
dedupe_exato
dedupe_near
Done. Returned value was: {'train_rows': 8980, 'test_rows': 2245}

=== TASK: train ===
modelo_persistido
Done. Returned value was: {'artifact_path': 'models/current/model.joblib', 'run_id': '5d28e4ad064549ddbc77a99f9c1e2332'}

=== TASK: evaluate ===
Done. Returned value was: {'f1_macro': 0.7281147873940977, 'f1_weighted': 0.7306730415230924,
'roc_auc_ovr': 0.8783571386099639, 'recall_normal': 0.6067415730337079,
'recall_atencao': 0.8101604278074866, 'recall_urgente': 0.7694267515923567,
'triage_sub_triagem': 296, 'triage_sobre_triagem': 307, 'triage_acerto_exato': 1642}

=== TASK: register ===
Done. Returned value was: {'registered_version': 1, 'f1_macro_teste': 0.7281147873940977}
```

## Achado científico: primeira avaliação real no teste reservado

O conjunto de teste (`data/processed/test.csv`, 2.245 linhas) ficou **reservado e
nunca tocado** desde F1 — só a comparação de F2 (validação cruzada sobre o treino)
existia até agora. Esta é a primeira leitura real de generalização:

| Métrica | CV (F2, `EXPERIMENTS.md`) | Teste reservado (esta execução) |
|---|---|---|
| F1 macro | 0,731 | 0,728 |
| ROC-AUC OvR | 0,877 | 0,878 |
| Recall `urgente` | 0,796 | 0,769 |

Diferença pequena (< 3 pontos em tudo) — bom sinal de que a CV de F2 não estava
otimista demais e o modelo generaliza para dado nunca visto. Sub-triagem no teste:
296/2.245 = 13,2% (um pouco acima do 11,8% medido em CV — dentro do esperado por
ser uma amostra diferente, não motivo de alarme).

## Confirmação no MLflow Model Registry

```
versao 1  run_id 5d28e4ad064549ddbc77a99f9c1e2332  status READY
```

Modelo registrado como `triagem-urgencia`, versão 1, vinculado ao run de treino
(mesmo run recebeu as métricas de teste via `evaluate`, prefixo `test_*`).
**Sem promoção de stage** (Staging/Production) — critério de promoção é decisão
de ADR-0008 (F6), fora do escopo de F4.
