# Runbook — operação local

Como subir, operar e diagnosticar a stack. Base do README final.

## Pré-requisitos

- Docker + Docker Compose
- Python 3.11 e `uv` (ADR-0006)
- Portas livres: 8000 (API), 9090 (Prometheus), 3000 (Grafana), 8080 (Airflow), 5000 (MLflow)

## Setup

```bash
uv python install 3.11   # se ainda não tiver essa versão
make setup                # uv sync --group training — instala dependências a partir do lock
cp .env.example .env
make lint                 # ruff
make test                 # pytest
```

`mlflow`/`lightgbm`/`mord` ficam num grupo de dependência separado (`training`,
mesmo padrão do `orchestration` do Airflow) — usados só em scripts de
treino/experimentação, nunca pela API. `make setup` já inclui o grupo; a imagem
Docker (`uv sync --no-dev`) não — ver ADR-0004.

Se `uv: comando não encontrado`: instalar com
`wget -qO- https://astral.sh/uv/install.sh | sh` (ou `curl -LsSf ... | sh` se
`curl` estiver disponível) e depois `source $HOME/.local/bin/env` (ou o caminho
de instalação impresso pelo instalador — pode variar em ambientes com `$HOME`
não padrão, ex. containers/snaps) para adicionar `uv` ao `PATH` da sessão atual;
adicionar essa linha ao `.bashrc`/`.zshrc` para persistir entre sessões.

## Dados (DVC)

O remote configurado (`local-storage`) aponta para uma pasta **fora do
repositório**, irmã dele (`../medical-triage-nlp-dvc-storage`). Em uma máquina
nova, criar essa pasta antes de rodar `dvc pull`/`dvc repro`:

```bash
mkdir -p ../medical-triage-nlp-dvc-storage
```

Ou reconfigurar o remote para outro caminho: `dvc remote modify local-storage url <caminho>`.

## Treinar o modelo

```bash
make train          # treino local, registra run no MLflow (backend sklearn)
make train-onnx     # exporta a variante ONNX (caixa 6.6/ADR-0004)
```

## Alternar o backend de inferência (caixa 6.9/ADR-0004)

```bash
MODEL_BACKEND=sklearn make run    # padrão — pipeline completo de 6.1-6.4, melhor qualidade
MODEL_BACKEND=onnx make run       # mais rápido (~-58% no p95), representação mais simples
```

Em container: variável de ambiente `MODEL_BACKEND` no `docker run`/`docker-compose.yml`.
Os dois artefatos (`model.joblib` e `model.onnx`+`onnx_calibrator.joblib`) precisam
existir em `models/current/` antes — `make train && make train-onnx` gera os dois.
Ver `docs/LATENCY.md` para os números completos e `docs/adr/0004-tecnica-
otimizacao-latencia.md` para o porquê da diferença de qualidade entre os backends.

## Subir a stack de monitoramento

```bash
make stack-up       # docker compose up -d (API + Prometheus + Grafana)
```

| Serviço | URL | Credenciais |
|---|---|---|
| API | http://localhost:8000/docs | — |
| Métricas | http://localhost:8000/metrics | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / admin (trocar) |

Verificar que o Prometheus enxerga a API: Status -> Targets, alvo `api` deve estar `UP`.

Dashboard já vem provisionado (datasource + JSON em `monitoring/grafana/`,
sem clicar em nada) — abrir `http://localhost:3000/d/triagem-urgencia`.
Evidência com dado real: `docs/evidence/f5_grafana_dashboard_2026-09-15.png`.

## Gerar carga (para popular o dashboard)

```bash
make load-test                                    # defaults: 500 requisições, concorrência 10
uv run python -m scripts.load_test --requests 500 --concurrency 10   # com flags
```

Sem carga o dashboard fica vazio e a evidência da rubrica R2 não existe. O
script amostra textos reais de `data/processed/test.csv` (não uma string fixa
repetida) e dispara ~2% das chamadas contra `/health` — tráfego mais realista
pro gráfico de "Total de requisições" mostrar mais de uma série.

## Benchmark de latência

```bash
make bench          # segue o protocolo de docs/LATENCY.md, mede o backend ativo
```

Para comparar os dois backends (como em `docs/LATENCY.md`): subir o container com
`MODEL_BACKEND=sklearn`, rodar `uv run python -m scripts.benchmark --base-url
<url> --n 1000 --warmup 100`, repetir com `MODEL_BACKEND=onnx`.

## Airflow

Airflow **3.2.2** fica num grupo de dependência separado (`orchestration`),
não no `uv sync` padrão — evita que o builder do Dockerfile da API
(`uv sync --no-dev`) instale o orquestrador inteiro na imagem de serving
(achado de F4, ver `docs/LATENCY.md`).

```bash
# instalar (uma vez, ou sempre que o lock mudar)
uv sync --group orchestration

# variáveis de ambiente da sessão (todo comando airflow abaixo precisa delas)
export AIRFLOW_HOME="$(pwd)/airflow"
export AIRFLOW__CORE__LOAD_EXAMPLES=False   # sem isso, polui dags list com DAGs de exemplo

# primeira vez só: cria o banco de metadados (sqlite local, git-ignorado)
uv run airflow db migrate

# subir o stack completo (scheduler + triggerer + dag-processor + api-server)
uv run airflow standalone
```

`airflow standalone` fica em foreground e imprime a senha do usuário `admin`
no log (`Simple auth manager | Password for user 'admin': ...`) — UI em
`http://localhost:8080`. Em outro terminal (mesmas variáveis de ambiente):

```bash
# listar DAGs (valida import, sem erro esperado)
uv run airflow dags list

# a primeira execução precisa destravar o pause automático
uv run airflow dags unpause retrain_triage_model

# disparar manualmente
uv run airflow dags trigger retrain_triage_model

# acompanhar (substituir pelo run_id retornado pelo trigger)
uv run airflow tasks states-for-dag-run retrain_triage_model <run_id>
```

**`airflow dags test retrain_triage_model` não funciona nesta versão** —
bug conhecido do supervisor de execução interno (`AttributeError: 'State'
object has no attribute 'svcs_registry'`), falha antes até de rodar a
primeira task. Usar sempre `standalone` + `dags trigger` (caminho real de
execução, já validado ponta a ponta — evidência em
`docs/evidence/f4_dag_execucao_2026-09-14.md`).

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `port is already allocated` | Porta ocupada por outro serviço | `docker ps`, parar o conflitante ou remapear no compose |
| Target `DOWN` no Prometheus | Nome de serviço errado no `prometheus.yml` | Usar o nome do serviço do compose, não `localhost` |
| Dashboard vazio | Sem tráfego | Rodar `scripts/load_test.py` |
| Grafana sem datasource | Provisionamento não montado | Conferir volume de `monitoring/grafana/provisioning/` |
| DAG não aparece | Erro de import | `airflow dags list-import-errors` |
| `dags list` quebra com `TimetableNotRegistered` | Banco de metadados tem DAGs de exemplo de uma execução anterior com `load_examples` ligado | `rm airflow/airflow.db*` + `airflow db migrate` com `AIRFLOW__CORE__LOAD_EXAMPLES=False` já exportado |
| `airflow dags test` falha com `svcs_registry` | Bug do supervisor de execução no Airflow 3.2.2 | Não usar `dags test` — `airflow standalone` + `dags trigger` (ver seção Airflow) |
| Modelo não carrega na API | Caminho/versão do artefato | Conferir `.env` e o artefato em `models/` |
| `MODEL_BACKEND=onnx` falha no startup com erro de `StringNormalizer`/locale | Imagem sem locale UTF-8 instalado (`python:3.11-slim`) | Já corrigido no `Dockerfile` (`locales` + `locale-gen en_US.UTF-8`, ADR-0004); se usar outra base image, replicar |
| `MODEL_BACKEND=onnx` falha com `FileNotFoundError` em `model.onnx` | Artefato ONNX nunca foi exportado | `make train-onnx` antes de subir com esse backend |

## Parar tudo

```bash
make stack-down
```
