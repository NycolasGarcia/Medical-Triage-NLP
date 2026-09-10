# Runbook — operação local

Como subir, operar e diagnosticar a stack. Base do README final.

## Pré-requisitos

- Docker + Docker Compose
- Python 3.11 e `uv` (ADR-0006)
- Portas livres: 8000 (API), 9090 (Prometheus), 3000 (Grafana), 8080 (Airflow), 5000 (MLflow)

## Setup

```bash
uv python install 3.11   # se ainda não tiver essa versão
make setup                # uv sync — instala dependências a partir do lock
cp .env.example .env
make lint                 # ruff
make test                 # pytest
```

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
make train          # treino local, registra run no MLflow
```

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

## Gerar carga (para popular o dashboard)

```bash
python scripts/load_test.py --requests 500 --concurrency 10
```

Sem carga o dashboard fica vazio e a evidência da rubrica R2 não existe.

## Benchmark de latência

```bash
make bench          # segue o protocolo de docs/LATENCY.md
```

## Airflow

```bash
# subir
<comando>
# listar DAGs (valida import)
airflow dags list
# disparar manualmente
airflow dags trigger retrain_triage_model
```

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `port is already allocated` | Porta ocupada por outro serviço | `docker ps`, parar o conflitante ou remapear no compose |
| Target `DOWN` no Prometheus | Nome de serviço errado no `prometheus.yml` | Usar o nome do serviço do compose, não `localhost` |
| Dashboard vazio | Sem tráfego | Rodar `scripts/load_test.py` |
| Grafana sem datasource | Provisionamento não montado | Conferir volume de `monitoring/grafana/provisioning/` |
| DAG não aparece | Erro de import | `airflow dags list-import-errors` |
| Modelo não carrega na API | Caminho/versão do artefato | Conferir `.env` e o artefato em `models/` |

## Parar tudo

```bash
make stack-down
```
