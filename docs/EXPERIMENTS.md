# Experimentos

Espelho legível dos runs do MLflow — o avaliador não vai abrir seu tracking server.
Atualizar a cada modelo relevante (F2 e F6).

| # | Run id | Modelo | Representação | F1 macro | F1 weighted | Recall `urgente` | ROC-AUC OvR | Sub-triagem % | Latência p95 (ms) | Observação |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `eff1b453` | DummyClassifier (stratified) | — | 0,339 | 0,339 | 0,351 | 0,504 | 32,9% | não medida (F3) | baseline mínimo — ~aleatório, como esperado |
| 2 | `0dd51d0c` | Regressão Logística | TF-IDF (1,1), max_features=20000 | **0,731** | 0,733 | **0,796** | **0,877** | **11,8%** | não medida (F3) | melhor F1-macro e menor sub-triagem dos três |
| 3 | `85cf2652` | Random Forest (200 árvores) | TF-IDF (1,1), max_features=20000 | 0,687 | 0,691 | 0,774 | 0,856 | 11,9% | não medida (F3) | levemente abaixo da LogReg em tudo, mais lento pra treinar |

## Protocolo

- Validação cruzada estratificada, `k = 5`, seed `42`.
- Métricas reportadas são a **média das 5 dobras sobre o treino** (`data/processed/train.csv`,
  8.980 amostras) — o teste (`data/processed/test.csv`, 2.245 amostras) fica reservado,
  nunca tocado nesta fase.
- Sub-triagem % = proporção das 8.980 predições (soma das 5 dobras de validação) em
  que o modelo previu uma faixa de urgência **menos grave** que a real.
- Todo run registra no MLflow: parâmetros (`model`, `n_splits`, `seed`), as 9 métricas
  (6 de qualidade + 3 de contagem sub/sobre-triagem/acerto exato) e a matriz de
  confusão 3×3 como artefato CSV.

## Leitura dos resultados

Regressão Logística venceu em **todas** as métricas medidas, com folga suficiente pra
não ser ruído de CV: F1-macro 0,731 vs. 0,687 do Random Forest (diferença de ~4,4
pontos) e 0,339 do Dummy. Mais relevante que o F1 agregado neste domínio: **sub-triagem
caiu de 32,9% (Dummy) para 11,8% (LogReg)** — quase 3× menos casos `urgente` sendo
rebaixados para `atenção`/`normal`. Random Forest fica muito próximo da LogReg em
sub-triagem (11,9%), mas perde em toda métrica de qualidade e é o candidato mais caro
de treinar entre os dois — não há indício ainda (F2 não mede latência de inferência)
de que valha o candidato adicional além de comprovar que "não-linear" não ajudou aqui.

Nenhum ajuste de limiar ou calibração foi feito nesta fase (isso é F6, ADR-0005) — os
números de sub-triagem acima são com o limiar padrão de decisão de cada modelo (maior
probabilidade), não uma política deliberada de reduzir sub-triagem.

## Descartados e por quê

| Modelo | Motivo do descarte |
|---|---|
| LinearSVC | Não produz `predict_proba` nativamente (precisaria de calibração extra para ROC-AUC/PR-AUC) — Random Forest já cobre o requisito de "≥ 1 candidato adicional" sem essa complicação em F2 |
