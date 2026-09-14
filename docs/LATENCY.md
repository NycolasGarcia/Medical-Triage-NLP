# Latência — protocolo e resultados

Latência é critério de nota (R1, 20%) e o ganho precisa ser **demonstrado com
números**, não afirmado.

## Protocolo de medição (fixar antes da primeira medida)

| Parâmetro | Valor |
|---|---|
| Ambiente | dentro do container, `docker run` local (`medical-triage-nlp:f3`) |
| Hardware | Intel Core i5-9400F @ 2.90GHz, 6 vCPUs, 15 GiB RAM |
| Requisições de warm-up (descartadas) | 100 |
| Amostras medidas (N) | 1000 |
| Concorrência | 1 (cliente único, sequencial — sem paralelismo nesta rodada) |
| Payload | amostra real do conjunto de teste, comprimento mediano (`scripts/benchmark.py`) |
| Percentis reportados | p50, p95, p99 |
| Repetições | 3 execuções; reportar mediana dos p95 |

Regras: nunca reportar média sozinha (esconde cauda); nunca comparar medições feitas
com máquina em estados diferentes; sempre declarar N e warm-up.

Script: `uv run python -m scripts.benchmark --base-url http://127.0.0.1:<porta> --n 1000 --warmup 100`.

## Baseline (F3 — modelo original)

Medido em 2026-09-14, container `medical-triage-nlp:f3` publicado em `127.0.0.1:8126`.
As 3 execuções bateram entre si com folga (p95 entre 3,05 e 3,18 ms) — sem outlier
de execução isolada. Valores abaixo são da execução com o p95 mediano.

| Métrica | Valor |
|---|---|
| p50 (ms) | 2,65 |
| p95 (ms) | 3,11 |
| p99 (ms) | 3,30 |
| `/health` (média de 10 chamadas) | 1,66 ms — bem abaixo do portão de 50 ms |
| Throughput (req/s, concorrência 1) | ~369 |
| Tamanho do artefato (`model.joblib`) | 1,2 MB |
| Tamanho da imagem Docker (`docker images`) | 1,03 GB |

**Observação sobre o tamanho da imagem:** não é o "imagem enxuta" que se esperaria de
um modelo TF-IDF + Regressão Logística sozinho. A camada de dependências
(`.venv` copiado do builder) responde por ~646 MB do total. Causa: o pipeline
completo (baixar dataset → notebooks → treinar com MLflow → persistir
`model.joblib`) roda **antes** do container existir — a API só faz `joblib.load()`
no startup e nunca importa `mlflow` — mas `pyproject.toml` ainda declara `mlflow`
e `lightgbm` (dependências de treino) na mesma lista `dependencies` usada pelo
`uv sync --no-dev` do Dockerfile, então elas entram na imagem de serving sem
necessidade. **Decisão do autor (2026-09-14): adiar a separação treino/serving
para F6** (caixa 6.1/6.6, mesma fase que trata otimização de latência formalmente)
em vez de mexer agora — F3 já cumpre o portão ("medido e registrado", sem alvo
numérico). Não esquecer ao reabrir F6.

## Otimizado (F6 — <ONNX / quantização>)

| Métrica | Baseline | Otimizado | Variação |
|---|---|---|---|
| p50 (ms) | | | |
| p95 (ms) | | | |
| p99 (ms) | | | |
| Throughput (req/s) | | | |
| Tamanho do artefato (MB) | | | |

**Ganho reportado:** <X>% no p95.

## Paridade numérica

Teste `tests/test_onnx_parity.py`: predições do modelo otimizado iguais às do original
em `<N>` amostras, tolerância `<valor>`. Divergências encontradas: `<n>`.

## Onde o tempo é gasto

Medido isolando cada etapa diretamente sobre o pipeline persistido (fora da API,
sem rede/ASGI/serialização HTTP), 500 repetições, mesmo payload do benchmark
principal. Soma das 3 etapas (~0,74 ms) é bem menor que o p50 do benchmark via
HTTP (~2,65 ms) — a diferença é overhead de rede/ASGI/Starlette em si, não do
pipeline de ML.

| Etapa | ms (p50) | % |
|---|---|---|
| Vetorização (TF-IDF) | 0,544 | 73,7% |
| Inferência (Regressão Logística) | 0,188 | 25,4% |
| Serialização da resposta (dict + JSON) | 0,007 | 0,9% |

A vetorização domina (quase 3/4 do tempo de processamento) — otimizar só o
classificador (ex.: trocar Regressão Logística por algo mais rápido) renderia
pouco. Se a otimização de F6 (ONNX) não tocar a vetorização TF-IDF, o ganho
esperado no p95 fim-a-fim é limitado por essa proporção — registrar essa leitura
como expectativa antes de medir o otimizado.
