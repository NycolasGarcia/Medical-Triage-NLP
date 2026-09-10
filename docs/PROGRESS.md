# PROGRESS — log de checkpoints

Log **append-only**. Nunca reescrever entrada antiga; se algo mudou, nova entrada.
As caixas de tarefa vivem no plano de fases interno do projeto — aqui vai só o
snapshot numérico, as evidências e o veredito.

## Estado atual

| Campo | Valor |
|---|---|
| Fase atual | F3 — API, container e decisão arquitetural |
| Micro (fase) | 0% |
| Macro (rubrica coberta) | 12% |
| Último checkpoint | 2026-09-10 — F2 fechada 9/9, todos os hard requirements ok |
| Bloqueios | Nenhum conhecido |

## Progresso macro por fase

| Fase | Peso | Micro | Contribuição |
|---|---|---|---|
| F0 Scaffolding | 3 | 100% | 3.0 |
| F1 Dados e EDA | 4 | 100% | 4.0 |
| F2 Baselines | 5 | 100% | 5.0 |
| F3 API e container | 7 | 0% | 0.0 |
| F4 CI/CD e Airflow | 27 | 0% | 0.0 |
| F5 Monitoramento | 20 | 0% | 0.0 |
| F6 Modelo final e latência | 15 | 0% | 0.0 |
| F7 Consolidação e entrega | 19 | 0% | 0.0 |
| **Macro** | **100** | | **12.0%** |

---

## Checkpoints

<!-- Colar aqui o bloco CHECKPOINT a cada abertura e fechamento de fase. -->

### CHECKPOINT — F0 «Scaffolding e fundação» · abertura · 2026-09-08

HARD REQUIREMENTS DA FASE
- HR-0.1 instalação limpa funciona -> pendente
- HR-0.2 ruff sem erros -> pendente
- HR-0.3 CI verde no primeiro push -> pendente
- HR-0.4 estrutura de docs criada -> pendente

ESTADO
- Caixas da fase: 0/10 -> micro 0%
- Macro: 0%
- Rubrica tocada: R3 (parcial, 3%)

VEREDITO: em execução — F0 iniciada.

### CHECKPOINT — F0 «Scaffolding e fundação» · execução · 2026-09-08

HARD REQUIREMENTS DA FASE
- HR-0.1 instalação limpa funciona -> pendente
- HR-0.2 ruff sem erros -> pendente
- HR-0.3 CI verde no primeiro push -> pendente
- HR-0.4 estrutura de docs criada -> parcial (esqueleto de `docs/` já existia; falta ADR-0006/0007)

ESTADO
- Caixas da fase: 1/10 -> micro 10%
- Macro: 0.3%
- Rubrica tocada: R3 (parcial, 3%)

SITUAÇÃO
- Feito: `git` instalado (estava ausente no ambiente), repositório inicializado
  (branch `main`), `.gitignore` e `.dockerignore` para a stack ML/Docker, identidade
  git local configurada, commit `b829e0d`.
- Em andamento: nada no momento.
- Falta: 0.2 a 0.10.

VEREDITO: em execução — próxima caixa é 0.2 (`pyproject.toml` com gestor de
dependências, deps prod/dev separadas, lock commitado).

### CHECKPOINT — F0 «Scaffolding e fundação» · execução · 2026-09-08 (2)

ESTADO
- Caixas da fase: 2/10 -> micro 20%
- Macro: 0.6%
- Rubrica tocada: R3 (parcial, 3%)

SITUAÇÃO
- Feito: `uv` instalado (ausente no ambiente; binário ficou em
  `~/snap/code/261/.local/bin`, fora do PATH padrão de um terminal comum — ver
  `docs/RUNBOOK.md`); **ADR-0006 aceito** (uv como gestor de dependências);
  `pyproject.toml` criado com Python fixado em 3.11 (mais compatível com
  Airflow/ONNX/MLflow do que a 3.14 do sistema); grupo `dev` com ruff, pytest,
  pytest-cov, pre-commit; `uv.lock` gerado e commitado; `uv sync` e
  `uv run ruff check .` verdes.
- Em andamento: nada no momento.
- Falta: 0.3 a 0.10.

VEREDITO: em execução — próxima caixa é 0.3 (estrutura de pastas do projeto +
`src/config.py` + `.env.example`).

### CHECKPOINT — F0 «Scaffolding e fundação» · fechamento · 2026-09-08

HARD REQUIREMENTS DA FASE
- HR-0.1 instalação limpa funciona -> ok (evidência: `rm -rf .venv && uv sync` limpo,
  `ruff check .` e `pytest` verdes a partir do zero)
- HR-0.2 ruff sem erros -> ok (`uv run ruff check .` = All checks passed!)
- HR-0.3 CI verde no primeiro push -> **pendente** (repositório ainda não tem remote
  GitHub configurado; o workflow `.github/workflows/ci.yml` existe e roda localmente
  os mesmos comandos, mas nunca foi executado pelo Actions)
- HR-0.4 estrutura de docs criada -> ok (`docs/README.md`, `PROGRESS.md`,
  `ARCHITECTURE.md`, `adr/` com 0000 a 0002, 0006, 0007)

PORTÕES NUMÉRICOS

| Portão | Alvo | Medido | Status |
|---|---|---|---|
| `ruff check .` | 0 erros | 0 erros | ok |
| `pytest` (via `uv run`, `make` ausente no ambiente) | verde | 2/2 passou | ok |
| `uv sync` em ambiente limpo | OK | OK | ok |
| CI (GitHub Actions) | verde | não executado ainda | **não** |

ESTADO
- Caixas da fase: 10/10 -> micro 100%
- Macro: 3.0%
- Rubrica tocada: R3 (parcial, 3%)

SITUAÇÃO
- Feito: repositório, `.gitignore`/`.dockerignore`, `pyproject.toml` com uv
  (ADR-0006 aceito, Python 3.11), estrutura de pastas de `src/`,
  `src/config.py`, `.env.example`, `pre-commit` instalado e funcionando,
  `Makefile`, `src/logging_config.py` (JSON + `print()` banido via ruff T20),
  workflow de CI (lint), ADR-0007 aceito (DVC dispensado), smoke test verde.
- Bloqueios / decisões pendentes do autor: (1) repositório sem remote GitHub —
  HR-0.3 não pode ser fechada sem isso; (2) `docker` não instalado neste
  ambiente — não bloqueia F0, mas bloqueia F3/F5 adiante; (3) `make` não
  instalado neste ambiente — o `Makefile` existe e os comandos que ele chama
  foram verificados diretamente via `uv run`, mas `make <alvo>` em si não foi
  executado.
- Riscos observados: ambiente de desenvolvimento partiu sem `git`, `uv`, `make`
  nem `docker` pré-instalados — cada um precisou ser instalado manualmente
  nesta sessão; um ambiente novo (outra máquina) provavelmente repete o mesmo
  atrito.

VEREDITO: **PODE AVANÇAR para F1**, com exceção registrada em HR-0.3 — CI real
(execução no GitHub Actions) fica pendente até o repositório ter um remote e um
push. Não bloqueia o trabalho de F1 (dados/EDA), que é local. Precisa ser
resolvida antes do fechamento de F4 (CI/CD é 15% da rubrica) e idealmente antes
da entrega final.

### NOTA — 2026-09-09

`docker.io` + `docker-compose-v2` instalados e validados pelo autor
(`docker run --rm hello-world` completo: pull + run + output). Risco (2) da
situação registrada no checkpoint de fechamento de F0 está resolvido. Segue
pendente: (1) remote GitHub (HR-0.3) e (3) `make` não instalado neste ambiente.

### NOTA — 2026-09-09 (2)

HR-0.3 fechada. Durante a criação do remote, encontrado um repositório privado
pré-existente (`medical-triage-nlp`, criado 2026-09-07T22:06, 14 commits em 32
minutos) com histórico de progresso fabricado — mesmo padrão da documentação
interna do projeto, reconstituída no início desta sessão (ex.: commit alegando
"fecha F1" e "CI verde" sem trabalho real correspondente). Apagado pelo autor
após revisão.
Repositório público recriado do zero em
https://github.com/NycolasGarcia/Medical-Triage-NLP com o histórico real desta
sessão (15 commits). Push confirmado, workflow de CI executado no GitHub
Actions com sucesso (`completed / success`, 13s). HR-0.3 agora tem evidência
real, não apenas local.

Risco (1) resolvido. Segue pendente apenas (3): `make` não instalado neste
ambiente (Makefile correto, comandos verificados via `uv run` diretamente).

### NOTA — 2026-09-09 (3)

`make` instalado (`sudo apt-get install -y make`, GNU Make 4.4.1). `make lint`
e `make test` executados de ponta a ponta com sucesso pelo binário real (antes
só os comandos subjacentes via `uv run` tinham sido verificados). Os três
riscos de ambiente registrados no checkpoint de fechamento de F0 (`git`, `uv`,
`make`, `docker` ausentes) estão todos resolvidos.

### CHECKPOINT — F1 «Dados, EDA e contrato de dados» · abertura · 2026-09-09

HARD REQUIREMENTS DA FASE
- HR-1.0 NV-1 a NV-3 fechados -> pendente
- HR-1.1 ≥ 2.000 amostras com 3 classes -> pendente
- HR-1.2 mapeamento decidido em ADR aceito -> parcial (ADR-0001 aprovado pelo
  autor, status formal `proposto` até caixa 1.0 confirmar os dados reais)
- HR-1.3 dedupe antes do split -> pendente
- HR-1.4 schema validado por teste -> pendente

ESTADO
- Caixas da fase: 0/10 -> micro 0%
- Macro: 3% (herdado de F0)
- Rubrica tocada: R5 (parcial, 4%)

VEREDITO: em execução — próxima caixa é 1.0 (baixar o corpus, fechar NV-1 a
NV-3). Bloqueio conhecido: credencial da API do Kaggle ainda não configurada
neste ambiente — necessária para baixar o corpus.

### NOTA — 2026-09-09 (4)

Bloqueio da credencial Kaggle resolvido de outra forma: o corpus é baixado
direto da fonte canônica no GitHub (`sebischair/Medical-Abstracts-TC-Corpus`),
que não exige autenticação — o Kaggle era só um espelho. Documentação interna
do projeto corrigida no mesmo commit.

### CHECKPOINT — F1 «Dados, EDA e contrato de dados» · fechamento · 2026-09-09

HARD REQUIREMENTS DA FASE
- HR-1.0 NV-1 a NV-3 fechados -> ok (dados reais baixados e inspecionados; NV-6
  também fechado — vazamento grave no split original, descartado)
- HR-1.1 ≥ 2.000 amostras com 3 classes -> ok (11.225 após dedupe, 3 classes de
  urgência presentes, todas acima de 5%)
- HR-1.2 mapeamento decidido em ADR aceito -> ok (ADR-0001 aceito 2026-09-09,
  condição de confirmação dos dados satisfeita)
- HR-1.3 dedupe antes do split -> ok (estágio `preprocess` do `dvc.yaml` roda
  dedupe antes do estágio `split`)
- HR-1.4 schema validado por teste -> ok (`tests/test_schema.py`, 3 testes)

PORTÕES NUMÉRICOS

| Portão | Alvo | Medido | Status |
|---|---|---|---|
| Amostras (pós-dedupe) | ≥ 2.000 | 11.225 | ok |
| Classes presentes | 3 | 3 (`normal`/`atencao`/`urgente`) | ok |
| Menor classe | ≥ 5% | 31,7% (`normal`) | ok |
| Duplicatas quantificadas e removidas | sim | 3.211 exatas + 2 near-dup | ok |
| Seed fixa | sim | 42, checksum reproduzido igual | ok |
| Schema test | verde | 3/3 passou | ok |
| `ruff check .` | 0 erros | 0 erros | ok |
| `pytest` (suíte completa) | verde | 14/14 passou | ok |

ESTADO
- Caixas da fase: 10/10 -> micro 100%
- Macro: 7.0%
- Rubrica tocada: R5 (parcial, 4%)

SITUAÇÃO
- Feito: corpus baixado da fonte canônica (sem credencial Kaggle), NV-1/2/3/6
  fechados com evidência real, ADR-0001 aceito, `src/data/{load,labels,dedupe,
  split,prepare,schema}.py`, pipeline DVC completo (`download` -> `preprocess`
  -> `split`) reproduzível e versionado no remote local, notebook de EDA
  executado com achados reais, `data_card.md` completo, 14 testes verdes
  (labels, dedupe, schema, smoke).
- ADR-0009 (DVC dentro do escopo) materializado nesta fase, como previsto.
- Bloqueios / decisões pendentes do autor: nenhum conhecido.
- Riscos observados: nenhum novo. `test_schema.py` pula silenciosamente se
  `data/processed/*.csv` não existir — hoje o CI (F0/0.7) só roda lint, não
  testes, então isso ainda não foi exercitado em CI; ao expandir CI para rodar
  `pytest` em F4 (caixa 4.1), será preciso decidir como o pipeline de dados
  chega até lá (`dvc repro` no job, ou `dvc pull` a partir do remote).

VEREDITO: **PODE AVANÇAR para F2** — todos os hard requirements de F1 fechados,
nenhuma exceção pendente.

### CHECKPOINT — F2 «Baselines e experimentação» · abertura · 2026-09-09

HARD REQUIREMENTS DA FASE
- HR-2.1 ≥ 3 runs no MLflow -> pendente
- HR-2.2 ≥ 4 métricas por run -> pendente
- HR-2.3 todo candidato supera o Dummy -> pendente
- HR-2.4 primeira leitura de sub/sobre-triagem -> pendente

ESTADO
- Caixas da fase: 0/9 -> micro 0%
- Macro: 7% (herdado de F0+F1)
- Rubrica tocada: R1 (parcial, 5%)

VEREDITO: em execução — próxima caixa é 2.1 (MLflow local configurado).

### CHECKPOINT — F2 «Baselines e experimentação» · fechamento · 2026-09-10

HARD REQUIREMENTS DA FASE
- HR-2.1 ≥ 3 runs no MLflow -> ok (3 runs: dummy, logreg, random_forest;
  experimento `triagem-urgencia`, backend `sqlite:///mlflow.db`)
- HR-2.2 ≥ 4 métricas por run -> ok (9 métricas/run: f1_macro, f1_weighted,
  roc_auc_ovr, recall por classe (3), sub_triagem, sobre_triagem, acerto_exato)
- HR-2.3 todo candidato supera o Dummy -> ok (F1-macro: logreg 0,731 e
  random_forest 0,687, ambos > dummy 0,339)
- HR-2.4 primeira leitura de sub/sobre-triagem -> ok (dummy 32,9% sub-triagem ->
  logreg 11,8% -> random_forest 11,9%; nenhuma política de limiar ainda, F6)

PORTÕES NUMÉRICOS

| Portão | Alvo | Medido | Status |
|---|---|---|---|
| Runs no MLflow | ≥ 3 | 3 | ok |
| Métricas por run | ≥ 4 | 9 | ok |
| F1-macro candidato > Dummy | sim | 0,731 e 0,687 > 0,339 | ok |
| Seeds fixas | sim | 42 (split de CV e todos os modelos) | ok |
| `ruff check .` | 0 erros | 0 erros | ok |
| `pytest` | verde | 17/17 passou | ok |

ESTADO
- Caixas da fase: 9/9 -> micro 100%
- Macro: 12.0%
- Rubrica tocada: R1 (parcial, 5%)

SITUAÇÃO
- Feito: MLflow configurado com backend SQLite (o file-store legado foi
  descontinuado na versão instalada do MLflow — achado registrado, não estava
  previsto); `src/features/vectorize.py` (Strategy de vetorização),
  `src/models/factory.py` (Factory de modelos), `src/models/evaluate.py`
  (métricas + matriz de confusão + sub/sobre-triagem), `src/models/experiments.py`
  (orquestração da CV de 5 dobras), `docs/EXPERIMENTS.md` e rascunho de
  `docs/model_card.md` preenchidos com números reais. 3 novos testes
  (`tests/test_evaluate.py`).
- Bloqueios / decisões pendentes do autor: nenhum.
- Riscos observados: LinearSVC foi descartado como candidato adicional (não tem
  `predict_proba` nativo) em favor de Random Forest — registrado em
  `docs/EXPERIMENTS.md`, seção "Descartados e por quê". Calibração, ajuste de
  limiar e matriz de custo ficam inteiramente para F6 — os números de sub/sobre-
  triagem de F2 são linha de base sem intervenção, não uma política.

VEREDITO: **PODE AVANÇAR para F3** — todos os hard requirements de F2 fechados,
nenhuma exceção pendente.
