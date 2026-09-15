<div align="center">

# Medical Triage NLP

Classificador de texto (NLP) leve para triagem de urgência de laudos médicos, servido via API REST com pipeline de CI/CD, orquestração de retreino e monitoramento

[Resultados](#resultados) | [Pipeline](#pipeline) | [Instalação](#instalação) | [Docker](#docker) | [Monitoramento](#monitoramento) | [API](#api-de-inferência) | [Documentação](#documentação) | [Roadmap](#roadmap)

Ferramentas:

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9+-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-3.16+-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)
![Airflow](https://img.shields.io/badge/Airflow-3.2+-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)
![DVC](https://img.shields.io/badge/DVC-3.x-945DD6?style=for-the-badge&logo=dvc&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-multi--stage-2496ED?style=for-the-badge&logo=docker&logoColor=white)

Detalhes:

[![CI](https://github.com/NycolasGarcia/Medical-Triage-NLP/actions/workflows/ci.yml/badge.svg)](https://github.com/NycolasGarcia/Medical-Triage-NLP/actions/workflows/ci.yml)
![Version](https://img.shields.io/badge/version-0.1.0-darkgrey?style=flat)
![Tests](https://img.shields.io/badge/tests-37%20passing-brightgreen?style=flat)
![Coverage](https://img.shields.io/badge/coverage-70%25-yellow?style=flat)
![Ruff](https://img.shields.io/badge/ruff-passing-brightgreen?style=flat)
![F1 Macro](https://img.shields.io/badge/F1--macro%20(teste)-0.728-blue?style=flat)
![Recall Urgente](https://img.shields.io/badge/recall%20urgente%20(teste)-0.769-blue?style=flat)

</div>

## Sobre o Projeto

Projeto da **Fase 3 do Tech Challenge** da Pós Tech em Machine Learning Engineering
(FIAP MLET). Um hospital de referência precisa de um sistema de triagem automática
de laudos médicos em texto, classificando a urgência em três faixas ordinais —
`normal < atenção < urgente` — para reduzir o tempo até o atendimento de casos
graves. O tema central da fase não é o modelo em si, e sim o **ciclo de vida em
produção**: pipeline CI/CD, orquestração de retreino, monitoramento e otimização
de latência.

> **Projeto em desenvolvimento incremental por fases** (F0–F7). O que este README
> descreve já está implementado e testado; o que ainda não existe é marcado como
> tal, não omitido. Progresso completo, checkpoints e evidências em
> [docs/PROGRESS.md](docs/PROGRESS.md).

## Dataset

**Medical Abstracts TC Corpus** ([GitHub `sebischair/Medical-Abstracts-TC-Corpus`](https://github.com/sebischair/Medical-Abstracts-TC-Corpus))
— abstracts médicos em **inglês**, classificados por sistema/condição (neoplasias,
doenças digestivas, do sistema nervoso, cardiovasculares, condições patológicas
gerais). 14.438 registros brutos → 11.225 após dedupe (exato + near-duplicate) →
8.980 treino / 2.245 teste, split estratificado com seed fixa.

O corpus **não** traz rótulo de urgência clínica — a faixa `normal/atenção/urgente`
é derivada por um mapeamento heurístico e didático, **não validado clinicamente**
([ADR-0001](docs/adr/0001-mapeamento-classes-urgencia.md)).

> **Idioma:** o texto de entrada esperado é **inglês** (idioma do dataset
> recomendado pelo enunciado). A documentação do projeto é em português, mas API,
> exemplos e demo usam inglês por decisão consciente — não é bug, ver
> [Model Card](docs/model_card.md) (limitação 2).
>
> Dataset não é versionado no git — baixado direto da fonte (sem credencial) via
> `dvc repro`. Dicionário completo em [docs/data_card.md](docs/data_card.md).

## Análise de Custo

Como as classes são ordinais, dois erros têm custo muito diferente: **sub-triagem**
(`urgente` classificado como `atenção`/`normal` — atraso no atendimento a paciente
crítico) e **sobre-triagem** (`normal` classificado acima — custa tempo de equipe,
não risco). O modelo campeão registra sub-triagem de 11,8% em validação cruzada
(vs. 32,9% do baseline Dummy) — quase 3× menos casos `urgente` rebaixados.

> A matriz de custo assimétrica explícita e o ajuste de limiar por classe
> (deliberadamente enviesado para reduzir sub-triagem) são trabalho de F6 —
> **planejado, não implementado ainda** (ADR-0005). Até lá, a decisão é o argmax
> padrão do `predict_proba`, sem política de limiar. Leitura completa em
> [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) e [docs/model_card.md](docs/model_card.md).

## Reprodutibilidade

Seed fixa (`42`) em dedupe/split (`src/data/split.py`), validação cruzada e todos os
candidatos (`src/models/factory.py`) — comparação de modelos reproduzida bit-a-bit
entre duas máquinas diferentes nesta sessão de desenvolvimento (mesmos valores de
F1-macro na precisão exibida).

## Resultados

Modelo em produção: **TF-IDF + Regressão Logística** — venceu entre 6 candidatos
comparados sob a mesma validação cruzada de 5 dobras
([ADR-0003](docs/adr/0003-escolha-modelo-base.md)).

<div align="center">

### Validação cruzada (F2) — todos os candidatos comparados

| Modelo | F1 macro | F1 weighted | Recall `urgente` | ROC-AUC OvR | Sub-triagem |
|---|---|---|---|---|---|
| DummyClassifier | 0,339 | 0,339 | 0,351 | 0,504 | 32,9% |
| **Regressão Logística (campeão)** | **0,731** | **0,733** | 0,796 | **0,877** | 11,8% |
| LinearSVC calibrado | 0,723 | 0,726 | 0,794 | 0,873 | 11,6% |
| LightGBM | 0,708 | 0,711 | 0,754 | 0,867 | 13,6% |
| Random Forest | 0,687 | 0,691 | 0,774 | 0,856 | 11,9% |
| Multinomial Naive Bayes | 0,675 | 0,679 | **0,863** | 0,863 | **6,9%** |

### Teste reservado — primeira avaliação real (nunca tocado desde F1)

| Métrica | CV (F2) | Teste reservado |
|---|---|---|
| F1 macro | 0,731 | 0,728 |
| ROC-AUC OvR | 0,877 | 0,878 |
| Recall `urgente` | 0,796 | 0,769 |

</div>

> Leitura honesta: Multinomial NB tem a menor sub-triagem de todos os candidatos
> reais (6,9%), à custa de mais sobre-triagem — não é o vencedor de F2 (F1-macro
> mais baixo do grupo), mas é o principal candidato a revisitar quando a matriz de
> custo de F6 existir. Diferença pequena entre CV e teste reservado (< 3 pontos em
> tudo) é bom sinal de generalização, não coincidência forçada.

## Pipeline

```mermaid
flowchart LR
    A["Medical Abstracts TC Corpus\n14.438 abstracts (GitHub)"] -->|dvc repro / DAG ingest| B["preprocess\nmapeamento ADR-0001 + dedupe"]
    B --> C["split\ntrain.csv / test.csv"]
    C --> D{{"6 candidatos\ncomparados em CV"}}
    D --> E["Regressão Logística\nvencedora (ADR-0003)"]
    C -->|"Airflow DAG\nretrain_triage_model"| TR["train + evaluate + register"]
    TR --> F["MLflow\ntracking + Model Registry"]
    TR --> G["model.joblib"]
    G --> H["FastAPI\nGET /health · POST /predict · GET /metrics"]
    H --> I["Cliente / Aplicação"]
    H -->|scrape 5s| PR["Prometheus"]
    PR --> GF["Grafana\ndashboard provisionado"]
```

## Stack

<div align="center">

| Camada | Tecnologia | Papel |
|---|---|---|
| Dados | pandas | Leitura, limpeza, dedupe (exato + near-duplicate) |
| Versionamento de dados | DVC ≥ 3.67 | Pipeline de 3 estágios (`dvc.yaml`), remote local |
| Vetorização | scikit-learn (TF-IDF) | Strategy trocável (`src/features/vectorize.py`) |
| Modelo em produção | scikit-learn ≥ 1.9 | Regressão Logística — vencedora honesta entre 6 candidatos |
| Candidatos comparados | scikit-learn + LightGBM | Dummy, LogReg, RandomForest, MultinomialNB, LightGBM, LinearSVC calibrado |
| Tracking + Registry | MLflow ≥ 3.16 | Params/métricas/artefatos por run; registro de versão do modelo |
| Orquestração | Apache Airflow ≥ 3.2 | DAG `retrain_triage_model`: ingest → preprocess → train → evaluate → register |
| API | FastAPI + Uvicorn, Pydantic | `/health`, `/predict`, `/metrics`, middleware de latência |
| Métricas | `prometheus_client` | Contadores/histograma expostos em `/metrics` |
| Monitoramento | Prometheus 2.53 + Grafana 11.1 | Scrape 5s + dashboard provisionado como código (4 painéis) |
| Validação de dados | pandera | Schema do dataset processado |
| Logging | JSON estruturado | Sem `print()` em nenhum módulo |
| Qualidade | ruff, pre-commit | Lint + mccabe (complexidade), zero erros |
| Testes | pytest, pytest-cov, httpx | 37 testes, 70% cobertura em `src/` |
| Container | Docker multi-stage + Compose | API + Prometheus + Grafana, usuário não-root, `HEALTHCHECK` nos 3 |

</div>

## Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/NycolasGarcia/Medical-Triage-NLP.git
cd Medical-Triage-NLP

# 2. Instalar dependências (uv)
uv sync

# 3. Configurar ambiente
cp .env.example .env

# 4. Baixar e processar o dataset (sem credencial — fonte pública)
uv run dvc repro

# 5. Treinar e persistir o modelo final
make train
```

## Quick Start

```bash
make lint            # ruff check
make test            # pytest (37 testes)

make run             # API com reload -> http://localhost:8000/docs
make train            # treina e persiste o modelo vencedor
make bench            # benchmark de latência (docs/LATENCY.md)

make stack-up         # API + Prometheus + Grafana -> http://localhost:3000
make load-test         # gera tráfego pra popular o dashboard
```

### Makefile

<div align="center">

| Comando | O que faz |
|---|---|
| `make setup` | `uv sync` + `pre-commit install` |
| `make lint` | `ruff check .` |
| `make test` | Suíte pytest completa |
| `make train` | Treina e persiste o modelo final (`src/models/train.py`) |
| `make run` | Sobe a API local com reload (`uvicorn`) |
| `make bench` | Benchmark de latência do `/predict` (`scripts/benchmark.py`) |
| `make stack-up` / `stack-down` | `docker compose up -d` / `down` — API + Prometheus + Grafana |
| `make load-test` | Gera tráfego contra a API (`scripts/load_test.py`) |

</div>

## Docker

```bash
docker build -t medical-triage-nlp .
docker run -d -p 8000:8000 medical-triage-nlp
curl localhost:8000/health   # ou: http://localhost:8000/docs
```

`Dockerfile` multi-stage (builder com `uv sync --no-dev` + runtime `python:3.11-slim`,
usuário não-root, `HEALTHCHECK` contra `/health`). Imagem atual: 1,03 GB — pesada
para TF-IDF+LogReg sozinho; achado registrado em
[docs/LATENCY.md](docs/LATENCY.md) (separar dependências de treino/serving é
trabalho planejado para F6). Latência medida dentro do container: **p50 2,65 ms
· p95 3,11 ms** (protocolo completo em `docs/LATENCY.md`).

## Monitoramento

```bash
make stack-up      # API + Prometheus + Grafana, docker-compose.yml
make load-test      # gera tráfego real pra popular o dashboard
```

<div align="center">

| Serviço | URL | Credenciais |
|---|---|---|
| API | http://localhost:8000/docs | — |
| Métricas | http://localhost:8000/metrics | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000/d/triagem-urgencia | admin / admin |

</div>

Datasource e dashboard **provisionados como código** (`monitoring/grafana/provisioning/`,
JSON commitado) — nada pra clicar manualmente. 4 painéis: total de requisições
(por rota/status), latência p50/p95, taxa de erro e distribuição de classes
preditas (métrica de negócio, base pra detectar drift). Print com dado real:

![Dashboard Grafana](docs/evidence/f5_grafana_dashboard_2026-09-15.png)

## MLflow e Model Registry

- Experimento: `triagem-urgencia`, backend `sqlite:///mlflow.db`. 6 candidatos
  comparados em F2 + runs de treino da DAG, todos rastreados com parâmetros, 9
  métricas e matriz de confusão como artefato.
- Modelo registrado no Model Registry (`triagem-urgencia`) a cada execução da DAG
  de retreino, com tag `elegivel_promocao` calculada pelo critério de ADR-0008
  (piso de F1-macro + não regressão de sub-triagem) — **sem promoção automática de
  stage**: a troca de `@production` continua decisão manual até a matriz de custo
  de ADR-0005 (F6) existir.

## Documentação

<div align="center">

| Documento | Conteúdo |
|---|---|
| [docs/model_card.md](docs/model_card.md) | Model Card: performance, limitações (incl. idioma), vieses, cenários de falha |
| [docs/data_card.md](docs/data_card.md) | Origem, licença, distribuição, mapeamento de rótulo do dataset |
| [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) | Tabela comparativa legível dos 6 candidatos e leitura dos resultados |
| [docs/LATENCY.md](docs/LATENCY.md) | Protocolo de benchmark, resultados e breakdown de onde o tempo é gasto |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Componentes, diagramas de fluxo de inferência e de treino |
| [docs/adr/](docs/adr/) | Architecture Decision Records: ADR-0001 a ADR-0009 |
| [docs/PROGRESS.md](docs/PROGRESS.md) | Log de checkpoints por fase, com evidências e veredito |

</div>

## Notebooks

<div align="center">

| Notebook | Conteúdo |
|---|---|
| [01_eda.ipynb](notebooks/01_eda.ipynb) | Volume, distribuição de classes, duplicatas, vocabulário, termos discriminativos por classe |

</div>

## API de Inferência

Modelo carregado uma única vez no `lifespan` do FastAPI (startup, não por
requisição). Middleware loga `request_id`, latência e classe predita por requisição.

<div align="center">

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/health` | Liveness check: `{"status": "ok"}` |
| `POST` | `/predict` | Recebe texto do laudo, retorna classe + probabilidades |
| `GET` | `/metrics` | Métricas Prometheus (requisições, latência, erros, classe predita) |
| `GET` | `/docs` | Swagger UI interativo (gerado automaticamente pelo FastAPI) |

</div>

**Testando via Swagger UI:** `make run`, abra `http://localhost:8000/docs`, expanda
`POST /predict`, **Try it out** e cole um payload abaixo (texto em **inglês** — ver
nota sobre idioma em [Dataset](#dataset)).

<details>
<summary><strong>Laudo urgente</strong> — choque cardiogênico → <code>"label": "urgente"</code> (66,5%)</summary>

```json
{
  "text": "Patient presents with acute myocardial infarction and cardiogenic shock, severe hemodynamic instability."
}
```

</details>

<details>
<summary><strong>Laudo normal</strong> — checkup de rotina → <code>"label": "normal"</code> (48,0%)</summary>

```json
{
  "text": "Routine follow-up examination, patient stable, no significant findings, general checkup."
}
```

</details>

## Estrutura do Projeto

```
medical-triage-nlp/
├── src/
│   ├── api/                # FastAPI: main, schemas, model_runtime
│   ├── data/                # load, labels, dedupe, split, prepare, schema
│   ├── features/             # TF-IDF (Strategy)
│   ├── models/                # factory, train, evaluate, experiments, tracking, promotion
│   ├── monitoring/             # metrics.py — instrumentação Prometheus
│   ├── config.py, logging_config.py
├── airflow/dags/              # retrain_dag.py — retrain_triage_model
├── tests/                     # smoke, schema, API, factory, train, evaluate, metrics, ...
├── notebooks/                 # 01_eda.ipynb
├── scripts/                   # benchmark.py, load_test.py
├── monitoring/                # prometheus.yml, grafana/provisioning/ (datasource + dashboard)
├── docs/                      # ADRs, cards, LATENCY, ARCHITECTURE, PROGRESS, evidence/
├── data/                      # raw/ processed/ — não versionado no git
├── models/                    # artefatos (git-ignored; versionados via MLflow)
├── Dockerfile                  # multi-stage (builder + runtime)
├── docker-compose.yml           # API + Prometheus + Grafana
├── dvc.yaml / dvc.lock          # pipeline de dados (3 estágios)
├── .github/workflows/ci.yml      # lint → test → build
└── pyproject.toml                # deps, ruff, pytest — single source of truth
```

## Roadmap

- [x] **Etapa 1 — Decisão Arquitetural e API Inicial**
  - [x] Estrutura de repo, `pyproject.toml` (uv), ruff + mccabe, logging estruturado, CI de lint
  - [x] Pipeline de dados reprodutível (DVC), ADR-0001 (mapeamento de rótulo), dedupe + split
  - [x] MLflow + 6 candidatos comparados em CV, ADR-0003 (escolha do modelo)
  - [x] API FastAPI (`/predict`, `/health`), Dockerfile multi-stage, latência baseline medida
  - [x] ADR-0002 (arquitetura de deploy: real-time, AWS ECS/Fargate teórico)
- [x] **Etapa 2 — CI/CD e Pipeline Automatizado**
  - [x] CI expandido: `lint` → `test` → `build`, verde no GitHub Actions, badge real no README
  - [x] Relatório de cobertura no CI
  - [x] DAG `retrain_triage_model` executada de ponta a ponta (5/5 tasks), registro no MLflow Model Registry
  - [x] RUNBOOK do Airflow completo + DAG parametrizada (`Param`) + ADR-0008 (critério de promoção)
- [x] **Etapa 3 — Monitoramento e Observabilidade**
  - [x] Instrumentação Prometheus (`/metrics`): requisições, latência, erros, classe predita
  - [x] `docker-compose.yml` (API + Prometheus + Grafana), os 3 serviços `healthy`
  - [x] Dashboard Grafana provisionado como código (4 painéis), gerador de carga, print com dado real
- [ ] **Etapa 4 — Otimização de Latência e Entrega**
  - [ ] Matriz de custo assimétrica + ajuste de limiar (ADR-0005), calibração de probabilidade
  - [ ] Export ONNX + benchmark comparativo, promoção do modelo no Registry (ADR-0008)
  - [ ] Model Card final, README final, vídeo STAR

Progresso completo (checkpoints, portões numéricos, evidências) em
[docs/PROGRESS.md](docs/PROGRESS.md).

## Contato

<div align="center">

| Plataforma | Link |
|---|---|
| <img src="https://skills.syvixor.com/api/icons?i=linkedin" width="30"> | [LinkedIn](https://www.linkedin.com/in/NycolasAGRGarcia/) |
| <img src="https://skills.syvixor.com/api/icons?i=github" width="30"> | [GitHub](https://github.com/NycolasGarcia) |
| <img src="https://skills.syvixor.com/api/icons?i=gmail" width="30"> | [Gmail](mailto:nycolasagrg.work@gmail.com) |
| <img src="https://skills.syvixor.com/api/icons?i=vercel" width="30"> | [Portfólio](https://dev-nycolas-garcia.vercel.app/) |

</div>
