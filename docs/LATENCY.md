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

## Otimizado (F6 — ONNX Runtime, caixa 6.6)

Medido em 2026-09-15, container `medical-triage-nlp:f6` (mesma imagem, mesmo
protocolo do baseline acima — só a variável `MODEL_BACKEND` muda entre as duas
medições, `sklearn` vs. `onnx`). "Original" aqui é o pipeline completo de F6
(representação 6.1 + calibração 6.2 + limiar 6.4) rodando via sklearn puro — não
o baseline de F3, que era um modelo mais simples e não é mais o que a API serve
por padrão. As 3 execuções de cada backend bateram entre si com folga (sklearn:
p95 entre 6,97 e 7,04 ms; ONNX: p95 entre 2,87 e 3,00 ms) — sem outlier de
execução isolada. Valores abaixo são da execução com o p95 mediano de cada lado.

| Métrica | Original (sklearn) | Otimizado (ONNX) | Variação |
|---|---|---|---|
| p50 (ms) | 6,47 | 2,57 | **-60,3%** |
| p95 (ms) | 7,01 | 2,92 | **-58,3%** |
| p99 (ms) | 7,18 | 3,10 | **-56,8%** |
| Tamanho do artefato | 2,4 MB (`model.joblib`) | 0,79 MB (`model.onnx` + calibrador) | -67% |
| Tamanho da imagem Docker | 1,03 GB (F3) → 696 MB (F6, mesma imagem serve os 2 backends) | | -32,4% |

**Ganho reportado: -58,3% no p95** (7,01 ms → 2,92 ms) — bem acima do que a leitura
"onde o tempo é gasto" (seção abaixo) fazia esperar como piso, porque o ONNX
**também** acelera a vetorização TF-IDF (não só a Regressão Logística) — a etapa
que dominava o tempo de processamento segundo aquela medição de F3.

**A redução de 32,4% no tamanho da imagem Docker não vem do ONNX** — vem de uma
correção separada, mas feita nesta mesma caixa: `mlflow`, `lightgbm` e `mord`
estavam na lista `dependencies` principal do `pyproject.toml` (usados só em
scripts de treino/experimentação, nunca por `src/api/`), inflando a imagem de
serving à toa — achado já registrado no baseline de F3 e explicitamente adiado
para F6 ("não esquecer ao reabrir F6"). Movidos para um grupo `training` separado
(mesmo padrão já usado para `orchestration`/Airflow em F4); `uv sync --no-dev` do
Dockerfile já os exclui automaticameante, confirmado simulando o comando exato do
Dockerfile numa venv limpa antes de reconstruir a imagem.

**Achado ao testar o backend ONNX em container (não local)**: o operador
`StringNormalizer` do onnxruntime (parte do `TfidfVectorizer` exportado) falha na
inicialização sem um locale UTF-8 instalado — a imagem `python:3.11-slim` não vem
com nenhum. Corrigido instalando `locales` + `locale-gen en_US.UTF-8` no
Dockerfile (ver `docs/adr/0004-tecnica-otimizacao-latencia.md` para o diagnóstico
completo). Não aparecia rodando a API local fora de container, porque o locale do
host já existia — só a validação em container real expôs o problema.

## Trade-off de qualidade do backend ONNX

**Não é otimização "de graça"** — a representação usada no backend ONNX é mais
simples que a vencedora de caixa 6.1 (só bigramas de palavra, sem char n-gramas
nem marcação de negação), porque o `skl2onnx` não converte nenhuma das duas
técnicas (ver ADR-0004 para o diagnóstico completo). Efeito medido em F1-macro
(CV, `docs/EXPERIMENTS.md`): 0,7338 (vencedora de 6.1, backend `sklearn`) vs.
0,7234 (backend `onnx`) — cerca de 1 ponto percentual.

**Como isso foi tratado**, em vez de simplesmente aceitar a perda:

1. **Duas variantes servíveis via flag** (`MODEL_BACKEND=sklearn|onnx`,
   `src/config.py`), não uma reescrita do pipeline de produção — `sklearn`
   continua sendo o padrão (melhor qualidade); `onnx` é opt-in para quem
   prioriza latência. Nenhum ganho de 6.1-6.4 foi descartado.
2. **Calibração isotônica preservada apesar da limitação do skl2onnx**:
   `CalibratedClassifierCV` também não converte para ONNX (exige entrada
   numérica, não uma pipeline de texto) — em vez de servir o backend ONNX sem
   calibração (perderia também o ganho de sub-triagem de caixa 6.2), foi
   implementado um calibrador isotônico one-vs-rest explícito
   (`src/optimization/calibrator.py`) que roda em Python **fora** do grafo ONNX,
   sobre a saída do `predict_proba` do runtime — o ONNX cuida da parte cara
   (vetorização + regressão logística), a calibração (barata, é só um lookup
   por classe) fica em Python.
3. **Decisão consciente registrada em ADR-0004**, não descoberta silenciosa: qual
   técnica foi sacrificada, por quê (limitação real do conversor, não escolha de
   qualidade), e o tamanho exato do custo (1 ponto de F1-macro), para o avaliador
   não precisar adivinhar.

## Paridade numérica

Teste `tests/test_onnx_parity.py`: tolerância declarada de **0,05 de diferença
absoluta por probabilidade**, sobre 100 amostras reais do conjunto de treino.
Medição de referência (fora do teste, 300 amostras): diferença média de 0,0024,
máxima de 0,0316 — dentro da tolerância com folga. Concordância de rótulo
(argmax) medida separadamente em 1.000 amostras: 99,4% (6 discordâncias, todas
em casos de probabilidade próxima do empate). Divergência existe porque o
`skl2onnx` reimplementa `TfidfVectorizer` com operações ONNX próprias — não é
bug, é o preço esperado de uma reimplementação independente do
tokenizador/normalização L2.

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
