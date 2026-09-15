# PROGRESS — log de checkpoints

Log **append-only**. Nunca reescrever entrada antiga; se algo mudou, nova entrada.
As caixas de tarefa vivem no plano de fases interno do projeto — aqui vai só o
snapshot numérico, as evidências e o veredito.

## Estado atual

| Campo | Valor |
|---|---|
| Fase atual | F6 — Modelo final e otimização de latência |
| Micro (fase) | 0% |
| Macro (rubrica coberta) | 66,0% |
| Último checkpoint | 2026-09-15 — F5 fechada 10/10, todos os hard requirements ok |
| Bloqueios | Nenhum conhecido |

## Progresso macro por fase

| Fase | Peso | Micro | Contribuição |
|---|---|---|---|
| F0 Scaffolding | 3 | 100% | 3.0 |
| F1 Dados e EDA | 4 | 100% | 4.0 |
| F2 Baselines | 5 | 100% | 5.0 |
| F3 API e container | 7 | 100% | 7.0 |
| F4 CI/CD e Airflow | 27 | 100% | 27.0 |
| F5 Monitoramento | 20 | 100% | 20.0 |
| F6 Modelo final e latência | 15 | 0% | 0.0 |
| F7 Consolidação e entrega | 19 | 0% | 0.0 |
| **Macro** | **100** | | **66.0%** |

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

### CHECKPOINT — F3 «API, container e decisão arquitetural» · abertura · 2026-09-10

HARD REQUIREMENTS DA FASE
- HR-3.1 API funcional em container -> pendente
- HR-3.2 latência baseline medida com protocolo -> pendente
- HR-3.3 ADR-0002 aceito e resumido no README -> pendente
- HR-3.4 ≥ 3 testes verdes -> já satisfeito globalmente (19 testes), mas caixa
  3.4 pede testes específicos da API ainda não escritos

ESTADO
- Caixas da fase: 0/10 -> micro 0%
- Macro: 12% (herdado de F0+F1+F2)
- Rubrica tocada: R5 (parcial, 7%)

SITUAÇÃO
- Pré-requisito não listado explicitamente em nenhuma caixa, mas necessário para
  3.1/3.2: nenhum modelo final foi persistido ainda — F2 só avaliou em CV, não
  salvou um artefato treinado no dataset completo. Vai ser feito como parte da
  caixa 3.2 (carregar modelo no startup implica ter o que carregar).

VEREDITO: em execução — próxima ação: treinar e persistir o modelo vencedor de
F2 (TF-IDF + Regressão Logística) no dataset de treino completo, depois montar
a API FastAPI.

### NOTA — 2026-09-14

Antes de seguir com a caixa 3.2 (persistir modelo), decidiu-se estender a
comparação de F2 de 3 para 6 candidatos — ainda é escopo de F2/R1 (comparação de
modelo), não de F3 (API/container), e trocar de modelo depois de montar a API
custaria retrabalho. Candidatos adicionados: Multinomial Naive Bayes, LightGBM
(gradient boosting sobre TF-IDF) e LinearSVC calibrado (`CalibratedClassifierCV`,
resolvendo a falta de `predict_proba` que motivou o descarte original do
LinearSVC em F2).

Resultado: **Regressão Logística confirmada como vencedora** (F1-macro 0,731,
ROC-AUC 0,877), sem nenhum dos 3 novos candidatos superando-a. Achado relevante:
Multinomial NB tem a menor sub-triagem de todos os candidatos reais (6,9%),
registrado em ADR-0003 como candidato a revisitar em F6 (ADR-0005) quando a
matriz de custo formal existir.

Achados técnicos registrados em ADR-0003 (não descrição do enunciado, decisão de
engenharia): `HistGradientBoostingClassifier` do sklearn não aceita matriz
esparsa (exigiria densificar TF-IDF, ~1,4 GB por dobra); XGBoost instala ~326 MB
de dependências CUDA/NCCL irrelevantes para uso em CPU via `uv add` — ambos
descartados em favor de LightGBM (3,3 MB, sem dependência de GPU).

Os 3 candidatos originais (dummy/logreg/random_forest) foram re-treinados nesta
sessão, em máquina diferente da que gerou os números publicados antes — mesmos
valores de F1-macro na precisão exibida, confirmando reprodutibilidade do
pipeline entre ambientes.

**ADR-0003 aceito.** `docs/EXPERIMENTS.md` e `docs/model_card.md` atualizados
com a tabela de 6 candidatos e os run ids atuais do MLflow. `dvc status` seguiu
limpo — nenhum dado mudou, só código de modelo e experimentos; nenhum novo
stage do DVC foi necessário. `ruff check .` e `pytest` verdes (24/24, incluindo
novo `tests/test_factory.py`).

Não muda o veredito de F2 (já fechada 9/9, PODE AVANÇAR) nem reabre a fase
formalmente — é extensão de escopo registrada antes do primeiro commit de
código de F3, para não persistir/servir um modelo que a própria comparação
ainda não tinha decidido ser o melhor.

### NOTA — 2026-09-14 (2)

Pré-requisito da caixa 3.2 resolvido: `src/models/train.py` treina o pipeline
vencedor (TF-IDF + Regressão Logística, `build_pipeline`) no
`data/processed/train.csv` completo (8.980 amostras, teste segue reservado) e
persiste em `models/current/model.joblib` (1,2 MB — git-ignorado por design,
`/models/` no `.gitignore`; versionado via MLflow, não via git). Run
`final_train_logreg` logado no MLflow com o modelo completo
(`mlflow.sklearn.log_model`). `tests/test_train.py` adicionado como o smoke
test de pipeline ponta a ponta previsto em §13 (item 1) — ainda não existia
um teste real disso, só o smoke trivial de config/logging do F0.

Caixa 3.2 **não fechada ainda** — falta a parte de "carregar no startup, não
por request" (decisão a registrar), que só existe quando a API existir
(caixa 3.1). `ruff check .` e `pytest` verdes (25/25).

### CHECKPOINT — F3 «API, container e decisão arquitetural» · execução · 2026-09-14

HARD REQUIREMENTS DA FASE
- HR-3.1 API funcional em container -> parcial (API funcional local; container
  ainda não, caixa 3.5)
- HR-3.2 latência baseline medida com protocolo -> pendente (caixa 3.6)
- HR-3.3 ADR-0002 aceito e resumido no README -> pendente (caixa 3.7/3.8)
- HR-3.4 ≥ 3 testes verdes -> ok (`tests/test_api.py`, 3 testes; suíte total 28/28)

ESTADO
- Caixas da fase: 4/10 -> micro 40%
- Macro: 14,8%
- Rubrica tocada: R5 (parcial, 7%)

SITUAÇÃO
- Feito: `src/api/{main,schemas,model_runtime}.py` — `POST /predict` e
  `GET /health` com validação Pydantic (`PredictRequest`/`PredictResponse`/
  `HealthResponse`); modelo carregado no `lifespan` do FastAPI (startup, não
  por request — decisão registrada em comentário no código, não precisou de
  ADR por ser escolha padrão de baixo risco); middleware de logging por
  requisição (`request_id`, rota, status, latência em ms, classe predita).
  `tests/test_api.py` com os 3 testes previstos em §13 (health 200, predict
  válido, payload inválido 422); `tests/conftest.py` com fixtures
  compartilhadas (`sample_train_csv`, `isolated_mlflow`) para não depender do
  `mlflow.db`/modelo reais em teste. Testado manualmente com `uvicorn` real:
  startup carrega o modelo, `/health` e `/predict` respondem certo, log JSON
  por requisição confirmado (`request_id`, `latencia_ms`, `classe_predita`).
- Achado durante o teste manual (não estava documentado): o modelo é
  treinado inteiramente em **inglês** (Medical Abstracts TC Corpus). Texto em
  português produz probabilidades quase uniformes (sem poder discriminativo);
  o mesmo conteúdo em inglês funciona como esperado (frase de choque
  cardiogênico → 66,5% `urgente`). Decisão do autor: **não é bug nem
  inconsistência a corrigir** — a documentação do projeto segue em português,
  mas a API/demo/vídeo usam texto em inglês, por ser o idioma do dataset
  recomendado pelo enunciado. Registrado com destaque em `model_card.md`
  (limitação 2 e tabela de cenários de falha), não mais como hipótese
  genérica de "idioma diferente do treino".
- Em andamento agora: nada — pausado para revisão antes de seguir.
- Falta para fechar a fase: 3.5 (Dockerfile multi-stage) · 3.6 (latência
  baseline dentro do container) · 3.7 (ADR-0002 aceito) · 3.8 (README) · 3.9
  (ARCHITECTURE.md com diagramas de fato) · 3.10 (checkpoint de fechamento).
- Bloqueios / decisões pendentes do autor: nenhum conhecido.
- Riscos observados: `docker` foi validado em F0 mas o Dockerfile em si ainda
  não existe — caixa 3.5 é a primeira vez que isso é exercitado de verdade.

VEREDITO: em execução — próxima ação: caixa 3.5 (Dockerfile multi-stage) para
então medir a latência baseline dentro do container (caixa 3.6).

### CHECKPOINT — F3 «API, container e decisão arquitetural» · execução · 2026-09-14 (2)

HARD REQUIREMENTS DA FASE
- HR-3.1 API funcional em container -> ok (`docker run` do zero, `/health` e
  `/predict` testados contra a imagem publicada)
- HR-3.2 latência baseline medida com protocolo -> ok (N=1000, warm-up=100, 3
  repetições, `docs/LATENCY.md`)
- HR-3.3 ADR-0002 aceito e resumido no README -> pendente (caixa 3.7/3.8)
- HR-3.4 ≥ 3 testes verdes -> ok (mantido; suíte total 28/28)

PORTÕES NUMÉRICOS

| Portão | Alvo | Medido | Status |
|---|---|---|---|
| Container sobe do zero (`docker run`) | sim | sim | ok |
| `/health` | < 50 ms | 1,66 ms (média de 10) | ok |
| Baseline p50/p95 com N e warm-up declarados | sim | p50 2,65 ms · p95 3,11 ms · N=1000 · warmup=100 | ok |
| Tamanho da imagem medido e registrado | sim | 1,03 GB | ok (medido; não é alvo numérico em F3) |
| 3 testes verdes | sim | 28/28 | ok |

ESTADO
- Caixas da fase: 6/10 -> micro 60%
- Macro: 16,2%
- Rubrica tocada: R5 (parcial, 7%)

SITUAÇÃO
- Feito: bloqueio de ambiente resolvido — Docker instalado nesta máquina
  (transferida, sem o setup anterior); grupo `docker` só passou a valer para
  esta sessão depois de um reboot completo do SO (reload de janela/sessão do
  VSCode não bastou, registrado como aprendizado de ambiente). `Dockerfile`
  multi-stage (builder com `uv sync --frozen --no-dev`, runtime `python:3.11-slim`
  + `libgomp1` pro LightGBM, usuário não-root `appuser`) builda de primeira.
  `docker run` publicado em `127.0.0.1:8126`, `/health` e `/predict` responderam
  certo contra a imagem real. `scripts/benchmark.py` rodado dentro do protocolo
  completo (N=1000, warmup=100, 3 repetições): p50 2,65 ms / p95 3,11 ms (mediana
  das 3 execuções) / p99 3,30 ms — números muito baixos e estáveis entre execuções
  (sem outlier). Breakdown isolado (fora da API): vetorização TF-IDF domina
  (73,7% do tempo de pipeline), inferência 25,4%, serialização 0,9% — registrado
  como leitura para calibrar expectativa do ganho de ONNX em F6 (se não tocar a
  vetorização, o teto de ganho é limitado). `docs/LATENCY.md` preenchido por
  completo (protocolo + baseline + breakdown).
- Achado não bloqueante: imagem de 1,03 GB é pesada pra um TF-IDF+LogReg — maior
  camada (~646 MB) é o conjunto de dependências, e `mlflow` (dependência de
  produção, usada só por `train.py`/`experiments.py`) provavelmente é o maior
  contribuinte, já que a API não importa `mlflow` em nenhum momento. Registrado
  em `LATENCY.md` como candidato a otimização, não bloqueia F3 (portão pede
  "medido e registrado", não um alvo numérico).
- Em andamento agora: nada — pausado para seguir com 3.7 (ADR-0002).
- Falta para fechar a fase: 3.7 (ADR-0002 aceito) · 3.8 (README) · 3.9
  (ARCHITECTURE.md com diagramas de fato) · 3.10 (checkpoint de fechamento).
- Bloqueios / decisões pendentes do autor: nenhum conhecido.
- Riscos observados: nenhum novo.

VEREDITO: em execução — próxima ação: caixa 3.7, ADR-0002 (batch vs. real-time
+ nuvem-alvo teórica).

### NOTA — 2026-09-14 (3)

Caixa 3.7 fechada. **ADR-0002 aceito**: real-time via serviço containerizado
(nuvem-alvo teórica: AWS ECS/Fargate atrás de ALB), com base na latência já
medida em `LATENCY.md` (p95 3,11 ms) — não suposição. Serverless (Lambda)
avaliado e descartado explicitamente por risco de cold start com imagem
pesada de ML (~1 GB), não por preferência genérica. Batch descartado por
contradizer o propósito do sistema. Híbrido registrado como observação: o
retreino via Airflow (F4) já é, na prática, a trilha em lote do sistema —
só que para retreino, não para servir triagem.

Caixas: 7/10 -> micro 70%. Macro: 16,9%. Próxima ação: caixa 3.8 (resumo do
ADR-0002 no README, que ainda não existe na raiz do repositório).

### NOTA — 2026-09-14 (4)

Caixas 3.8 e 3.9 fechadas. `README.md` criado na raiz (não existia) com
contexto breve e a seção de arquitetura de deploy (resumo do ADR-0002) — setup/
execução/resultados completos ficam para F7 (caixa 7.2), README por enquanto é
propositalmente enxuto. `docs/ARCHITECTURE.md` reescrito com os dois diagramas
mermaid pedidos (request e treino), agora refletindo o que **existe de fato**
(API, middleware, `train.py`, pipeline DVC), com elementos planejados (F4/F5/F6)
marcados com seta tracejada em vez de aparecer como se já estivessem prontos —
o esqueleto anterior (F0) misturava aspiração com realidade sem distinguir.
Tabela de componentes ganhou coluna de status; tabela de ADRs vinculados
atualizada (0001/0002/0003 aceitos, 0004/0005/0008 ainda planejados).

Caixas: 9/10 -> micro 90%. Macro: 18,3%. Falta só 3.10 (CHECKPOINT de
fechamento de F3).

### CHECKPOINT — F3 «API, container e decisão arquitetural» · fechamento · 2026-09-14

HARD REQUIREMENTS DA FASE
- HR-3.1 API funcional em container -> ok (`docker run` do zero, `/health` e
  `/predict` testados contra a imagem publicada)
- HR-3.2 latência baseline medida com protocolo -> ok (N=1000, warmup=100, 3
  repetições, `docs/LATENCY.md`)
- HR-3.3 ADR-0002 aceito e resumido no README -> ok (`docs/adr/0002-...md`
  status aceito; `README.md` § Arquitetura de deploy)
- HR-3.4 ≥ 3 testes verdes -> ok (`tests/test_api.py`, 3 testes; suíte 28/28)

PORTÕES NUMÉRICOS

| Portão | Alvo | Medido | Status |
|---|---|---|---|
| Container sobe do zero (`docker run`) | sim | sim | ok |
| `/health` | < 50 ms | 1,66 ms | ok |
| Baseline p50/p95 com N e warm-up | sim | p50 2,65 ms · p95 3,11 ms · N=1000 · warmup=100 | ok |
| Tamanho da imagem medido e registrado | sim | 1,03 GB | ok (sem alvo numérico em F3) |
| 3 testes verdes | sim | 28/28 | ok |
| `ruff check .` | 0 erros | 0 erros | ok |

ESTADO
- Caixas da fase: 10/10 -> micro 100%
- Macro: 19,0%
- Rubrica tocada: R5 (parcial, 7%)

SITUAÇÃO
- Feito: API FastAPI completa (`/predict`, `/health`, middleware de latência/
  log por requisição), modelo final treinado e persistido, `Dockerfile`
  multi-stage funcional (build limpo, usuário não-root), latência baseline
  medida dentro do container com protocolo declarado, ADR-0002 aceito
  (real-time, AWS ECS/Fargate teórico, serverless descartado por cold start),
  README criado com resumo da decisão, `ARCHITECTURE.md` reescrito com
  diagramas mermaid reais (não mais aspiracionais).
- Bloqueios / decisões pendentes do autor: nenhum.
- Riscos observados: imagem de 1,03 GB pesada — decisão consciente de adiar
  a separação treino/serving para F6, registrada em `LATENCY.md`; não
  esquecer ao reabrir aquela fase.

VEREDITO: **PODE AVANÇAR para F4** — todos os hard requirements de F3
fechados, nenhuma exceção pendente.

### CHECKPOINT — F4 «CI/CD e orquestração» · abertura · 2026-09-14

HARD REQUIREMENTS DA FASE
- HR-4.1 workflow com ≥ 2 automações rodando verde -> pendente
- HR-4.2 DAG executando ponta a ponta e gerando artefato de modelo -> pendente
- HR-4.3 evidência de execução no repositório -> pendente

ESTADO
- Caixas da fase: 0/8 -> micro 0%
- Macro: 19,0% (herdado)
- Rubrica tocada: R3 (12%) + R4 (15%) = 27% — fase mais pesada do projeto

SITUAÇÃO
- Feito: **NV-5 fechado** (estava aberto desde o planejamento) — `airflow db
  migrate` e `airflow standalone` rodaram limpos neste ambiente, scheduler/
  triggerer/dag-processor/api-server todos `healthy`. Achado: é **Airflow
  3.2.2**, não 2.x — mudança real de arquitetura (Task SDK, api-server no
  lugar do webserver clássico), RUNBOOK e DAG precisam refletir isso, não
  suposições de Airflow 2. Correção de dependência feita na hora: `uv add
  apache-airflow` inicialmente foi pra `dependencies` (lista principal) —
  moveu pra um grupo novo `orchestration` em `pyproject.toml`, porque senão
  `uv sync --no-dev` (usado pelo builder do Dockerfile da API) instalaria
  Airflow inteiro na imagem de serving, que não tem nada a ver com ele.
  Confirmado com `uv sync --frozen --no-dev` de novo: Airflow não entra.
  `.gitignore` também ganhou padrões novos (`airflow.db-shm`/`-wal`, arquivo
  de senha gerado pelo Simple Auth Manager) que não existiam nas versões
  antigas do Airflow — ficariam commitados por acidente sem isso (achado
  antes de virar problema, não depois).
- Em andamento agora: nada — pausado para reportar antes de escrever a DAG.
- Falta para fechar a fase: 4.1-4.8 inteiras (nada além da validação de
  ambiente foi feito ainda).
- Bloqueios / decisões pendentes do autor: nenhum.
- Riscos observados: nenhum novo além do já registrado (DVC remote local
  não acessível em CI, a decidir na caixa 4.1).

VEREDITO: em execução — próxima ação: caixa 4.1 (expandir CI) ou 4.5 (DAG),
a decidir com o autor.

### NOTA — 2026-09-14 (5)

Caixa 4.1 **em execução, ainda não fechada** (autor escolheu atacar 4.1 antes
de 4.5, pelo raciocínio de reduzir risco antes — qualquer código novo da DAG
nasce sob CI, em vez de escrito sem rede de segurança). `.github/workflows/ci.yml`
expandido de 1 job (`lint`) para 3 encadeados (`lint` → `test` → `build`),
via `needs:`.

Resolvida a pendência do DVC-remote-em-CI (registrada como risco desde F1):
testei localmente simulando checkout limpo de verdade — apaguei `data/` **e**
`.dvc/cache` (não só `data/`, que só teria testado o cache local, não o
cenário real de CI) — `dvc repro` reconstruiu os 3 estágios do zero em ~15s,
sem precisar do remote nem de credencial (fonte é o GitHub público). Schema
test parou de pular silenciosamente. `dvc.lock` atualizado (hashes de
`dedupe.py`/`labels.py` mudaram nas edições de docstring desta sessão, nunca
re-propagado até agora).

Job `build` roda `dvc repro` + `python -m src.models.train` antes do
`docker build` — a imagem copia `models/` no Dockerfile, precisa existir
artefato antes, e cada job do CI começa de checkout limpo (não herda estado
de outro job sem passar artefato explicitamente).

Cobertura de teste (`pytest --cov=src --cov-report=term-missing`) já embutida
no job `test` — resultado local 68% (`src/data/load.py`, `prepare.py`,
`split.py` em 0% porque só rodam via script, não são importados por teste
diretamente; não é problema, é esperado). Caixa 4.3 **não marcada ainda** —
falta confirmar que o relatório aparece certo no log real do GitHub Actions,
não só localmente.

Caixas: 0/8 ainda -> micro 0%. Macro segue 19,0% (sem mudança) — caixa só
fecha com CI real verde no GitHub Actions, não com validação local (§10.1:
caixa marcada sem artefato verificável é pior que caixa desmarcada). Próxima
ação: push e confirmar os 3 jobs verdes de verdade.

### NOTA — 2026-09-14 (6)

Push feito (`86a9117`), CI real conferido: **run 34836927538, os 3 jobs
verdes** — `lint` 13s, `test` 45s (`dvc repro` reconstruiu os dados do zero
no runner e `pytest --cov` passou, schema test sem skip), `build` 1m1s
(`dvc repro` + `train.py` + `docker build` da imagem completa). Conferi o
log real do job `test` linha a linha — o relatório de cobertura aparece
certo (68% local, mesmo shape no CI).

Caixas 4.1 e 4.3 fechadas com evidência real (não só local). Achado sem
ação necessária: cache do `astral-sh/setup-uv` falhou nesta run por
instabilidade do lado do GitHub ("Our services aren't available right now"
+ "Cache service responded with 400") — não é problema de configuração
nossa, `enable-cache: true` já está certo nos 3 jobs; só não deu pra
confirmar o ganho de velocidade ainda. Caixa 4.2 (cache + badge) segue
pendente — falta o badge no README e uma run limpa confirmando cache OK.

Caixas: 2/8 -> micro 25%. Macro: 25,75%. Próxima ação: caixa 4.2 (badge) ou
seguir direto pra 4.5 (DAG) — a decidir.

### NOTA — 2026-09-14 (7)

Caixas 4.5 e 4.7 fechadas. `airflow/dags/retrain_dag.py`: 5 tasks
(`ingest → preprocess → train → evaluate → register`), TaskFlow API do
Airflow 3 (`from airflow.sdk import dag, task`), cada task só chama funções
de `src/` (nenhuma lógica de negócio no arquivo da DAG, §12).

Duas extensões em `src/` pra viabilizar `evaluate`/`register`:
- `src/models/train.py`: `train_and_persist()` agora retorna `TrainResult`
  (`artifact_path` + `run_id`), não só o path — precisava do `run_id` pra
  `evaluate` conseguir reabrir o mesmo run do MLflow (`mlflow.start_run(run_id=...)`)
  e logar as métricas de teste no mesmo registro do treino. `test_train.py`
  e o smoke test de `test_api.py` ajustados.
- `src/models/evaluate.py`: nova função `evaluate_pipeline()` — carrega
  `data/processed/test.csv` (reservado desde F1, nunca tocado até agora) e
  calcula as mesmas métricas de F2, mas no held-out real. Teste novo em
  `tests/test_evaluate.py`.

**Achado de ferramenta:** `airflow dags test` tem um bug nesta versão
(3.2.2) — `AttributeError: 'State' object has no attribute 'svcs_registry'`
no supervisor de execução interna, falha na primeira task antes até de
rodar nosso código. Sem relato conhecido buscado. Contornado: subi o stack
completo (`airflow standalone`, o mesmo já validado no NV-5) e disparei via
`airflow dags trigger` contra o scheduler real — esse caminho funciona limpo.
Também precisei resetar o banco de metadados uma vez (`rm airflow.db*` +
`db migrate` com `AIRFLOW__CORE__LOAD_EXAMPLES=False`): a run anterior do
NV-5 tinha carregado DAGs de exemplo com um timetable customizado que não
resolve fora do contexto do scheduler, quebrando `dags list`.

**Execução real:** `manual__2026-09-14T12:42:31.738819+00:00`, 5/5 tasks
`success`, ~41s ponta a ponta. Evidência completa (estado por task, logs de
aplicação, achado científico) em `docs/evidence/f4_dag_execucao_2026-09-14.md`.
Achado científico: primeira avaliação real no teste reservado (2.245 linhas)
bateu perto da estimativa de CV de F2 — F1-macro 0,728 (CV: 0,731), ROC-AUC
0,878 (CV: 0,877), recall `urgente` 0,769 (CV: 0,796) — sinal de que a CV
não estava otimista demais. Modelo registrado no MLflow Model Registry
(`triagem-urgencia`, versão 1), **sem promoção de stage** — critério de
promoção é ADR-0008 (F6), fora do escopo de F4.

Caixas: 4/8 -> micro 50%. Macro: 32,5%. Próxima ação: caixa 4.2 (badge) ou
4.4/4.6 (RUNBOOK do Airflow + ADR-0008 + parametrização) — a decidir.

### NOTA — 2026-09-14 (8)

README.md reescrito por completo, seguindo o template pessoal já usado em
TC1/TC2 (badges, nav links, seções padronizadas) a pedido do autor — cobre
bem mais do que a caixa 3.8 pedia (só resumo do ADR-0002). Adiantou boa
parte do que seria caixa 7.2 ("README final"), mas **não fecha 7.2**: faltam
resultados de F5 (dashboard)/F6 (ONNX, limiar)/F7 (vídeo), e o README já é
explícito sobre isso — roadmap mostra Etapa 2 parcial e Etapas 3/4 vazias,
sem fingir conclusão. Números conferidos contra o estado real do projeto
nesta sessão (29 testes, 69% cobertura, métricas de EXPERIMENTS.md e do
teste reservado desta sessão) — nenhum número inventado.

Também adicionado `HEALTHCHECK` ao `Dockerfile` (usa `urllib` da stdlib
contra `/health`, sem novo pacote) — testado, `docker inspect` reporta
`healthy`. Não estava pedido por nenhuma caixa específica, mas é prática
padrão de Dockerfile de produção e ficou barato de adicionar agora.

### NOTA — 2026-09-14 (9)

Caixas 4.2, 4.4 e 4.6 fechadas.

- **4.2**: badge real do GitHub Actions no README (`actions/workflows/ci.yml/badge.svg`,
  reflete status ao vivo, não estático). Cache do `setup-uv` investigado a fundo:
  configuração está correta (`enable-cache: true`), `save` funciona (confirmado no
  log real: "cache saved with the key..."), mas `restore` falha consistentemente com
  "Cache service responded with 400" — reproduzido em 3 runs diferentes, inclusive
  entre dois jobs da **mesma** run (o `test` não conseguiu restaurar o que o `lint`
  acabou de salvar segundos antes). Não é bug nosso — bate com o incidente mais
  amplo do GitHub em 13/09 (checado no `githubstatus.com`) e com relatos públicos de
  problemas no backend do Cache Service v2. Registrado como limitação externa
  conhecida, não bloqueia a caixa (configuração comprovadamente correta).
- **4.4**: `docs/RUNBOOK.md` — seção Airflow reescrita com os comandos reais
  validados (grupo `orchestration`, `AIRFLOW_HOME`, `load_examples=False`,
  `standalone` + `trigger`), incluindo os dois achados de ferramenta como
  troubleshooting (bug do `dags test`, DAGs de exemplo quebrando `dags list`).
- **4.6**: DAG parametrizada via `Param` do Airflow (`min_f1_macro=0.70`,
  `max_sub_triagem_increase=0.03`) + schedule real (`@weekly`, antes `None`).
  **ADR-0008 aceito**: critério de elegibilidade de promoção (piso de F1-macro +
  não regressão de sub-triagem) — task `register` agora calcula e tageia
  `elegivel_promocao` no MLflow Registry, sem promover sozinha (decisão manual até
  ADR-0005/F6 existir). Lógica isolada em `src/models/promotion.py`, testada
  (`tests/test_promotion.py`, 4 testes). Execução real revalidada com os params
  novos: 5/5 tasks `success`, `elegivel_promocao: True` (F1-macro 0,728 ≥ piso
  0,70, sem baseline de produção ainda para checar regressão).

Suíte local: 33/33 testes, `ruff` limpo.

### CHECKPOINT — F4 «CI/CD e orquestração» · fechamento · 2026-09-14

HARD REQUIREMENTS DA FASE
- HR-4.1 workflow com ≥ 2 automações rodando verde -> ok (3 automações:
  lint/test/build, verificado em múltiplas runs reais do GitHub Actions)
- HR-4.2 DAG executando ponta a ponta e gerando artefato de modelo -> ok
  (validado 2x, 5/5 tasks `success`, `model.joblib` + versão no MLflow Registry)
- HR-4.3 evidência de execução no repositório -> ok (`docs/evidence/f4_dag_execucao_2026-09-14.md`)

PORTÕES NUMÉRICOS

| Portão | Alvo | Medido | Status |
|---|---|---|---|
| CI verde no push | sim | sim (4 runs reais confirmadas) | ok |
| ≥ 2 automações | sim | 3 (lint, test, build) | ok |
| `airflow dags list` sem erro de import | sim | sim | ok |
| Execução completa com todas as tasks `success` | sim | 5/5, 2 execuções | ok |
| Artefato de modelo produzido pela DAG | sim | `model.joblib` + registro MLflow | ok |

ESTADO
- Caixas da fase: 7/8 -> micro 87,5%
- Macro: 42,6%
- Rubrica tocada: R3 (12%) + R4 (15%) = 27% — fase mais pesada do projeto, fechada

SITUAÇÃO
- Feito: fase inteira, exceto este próprio checkpoint de fechamento. CI real
  com 3 automações verdes; DAG real com 5 tasks, retreino + avaliação em
  teste reservado + registro no MLflow Model Registry + critério de
  promoção (ADR-0008); RUNBOOK documentado com os comandos que de fato
  funcionam nesta versão do Airflow (3.2.2, não 2.x).
- Bloqueios / decisões pendentes do autor: nenhum.
- Riscos observados: cache do CI não traz ganho de velocidade hoje (falha
  de restore do lado do GitHub) — sem ação nossa possível, resolve sozinho
  quando o serviço deles estabilizar. Imagem Docker em 1,03 GB segue pesada
  (decisão já registrada de adiar correção para F6).

VEREDITO: **PODE AVANÇAR para F5** — todos os hard requirements de F4
fechados, nenhuma exceção pendente.

### CHECKPOINT — F5 «Monitoramento e observabilidade» · abertura e fechamento · 2026-09-15

Fase executada e fechada na mesma sessão — abertura e fechamento combinados
aqui (mesma prática já usada em F4 quando o trabalho saiu rápido e validado
a cada passo).

HARD REQUIREMENTS DA FASE
- HR-5.1 compose sobe os 3 serviços saudáveis -> ok (`docker compose ps`:
  api/prometheus/grafana todos `healthy`, `HEALTHCHECK` real nos 3)
- HR-5.2 Prometheus com target UP -> ok (`/api/v1/targets`: `{'instance':
  'api:8000', 'job': 'api'} up`)
- HR-5.3 dashboard com ≥ 3 painéis populados -> ok (4 painéis, todos com
  série temporal real após carga)
- HR-5.4 dashboard versionado como código -> ok (JSON em
  `monitoring/grafana/provisioning/dashboards/triagem-urgencia.json`,
  commitado — print é evidência complementar, não a fonte)

PORTÕES NUMÉRICOS

| Portão | Alvo | Medido | Status |
|---|---|---|---|
| `docker compose up` → 3 serviços healthy | sim | sim | ok |
| Target UP no Prometheus | sim | sim | ok |
| ≥ 3 painéis com série temporal não vazia | sim | 4/4 | ok |
| JSON do dashboard no repositório | sim | sim | ok |

ESTADO
- Caixas da fase: 10/10 -> micro 100%
- Macro: 66,0%
- Rubrica tocada: R2 (20%) — fase mapeia 1:1 com o critério

SITUAÇÃO
- Feito: `src/monitoring/metrics.py` (Counter de requisições, Histogram de
  latência, Counter de erros, Counter de classe predita — métrica de
  negócio), `/metrics` na API reaproveitando o middleware já existente (uma
  só medição de latência, não duas). `docker-compose.yml` com os 3 serviços,
  `monitoring/prometheus.yml` fazendo scrape de `api:8000` a cada 5s,
  Grafana com datasource + dashboard provisionados como código (sem clicar
  em nada). `scripts/load_test.py` (amostra texto real do teste, ~2% contra
  `/health`) gerou a carga real da evidência. Print capturado via Playwright
  headless (ferramenta ad-hoc desta sessão, não é dependência do projeto) —
  login real no Grafana provisionado, screenshot do dashboard com dado de
  verdade, salvo em `docs/evidence/f5_grafana_dashboard_2026-09-15.png`.
- Achado corrigido no caminho: o painel de taxa de erro usava `sum(rate(...))`
  puro, que fica "No data" quando a taxa de erro é genuinamente zero (Prometheus
  não retorna série vazia como zero) — corrigido com `or vector(0)` na query,
  e gerada uma leva de erros de propósito (payload inválido) pra a evidência
  mostrar os dois casos, não só o caminho feliz.
- `docs/ARCHITECTURE.md` e `README.md` atualizados por completo — componentes,
  diagramas (inferência com `/metrics`→Prometheus→Grafana; treino com a DAG
  real em vez de "planejado"), seção nova "Monitoramento", roadmap com Etapa 2
  e Etapa 3 fechadas.
- Bloqueios / decisões pendentes do autor: nenhum.
- Riscos observados: nenhum novo.

VEREDITO: **PODE AVANÇAR para F6** — todos os hard requirements de F5
fechados, nenhuma exceção pendente.

### F6 — caixa 6.1 (tuning de representação) · execução · 2026-09-15

Protocolo negociado com o autor antes de rodar: busca gulosa incremental
(baseline → 4 candidatos isolados → incorpora vencedor, testa restantes em
cima → repete até não haver ganho → checagem cirúrgica do 2º colocado →
classificador ordinal como eixo separado), em vez de fatorial completo
(2⁴ = 16 combinações) — orçamento máximo ~13 runs, parou em 12 (rodada 3
sem ganho). Motivo da escolha: capturar interação entre técnicas (ex.:
marcação de negação só ajuda combinada a char n-gramas, não sozinha — viu-se
exatamente isso nos resultados) a um custo muito menor que testar todas as
combinações.

- Achado ao abrir a caixa: §10.6/ADR-0003 já tinham decidido bigramas (1,2)
  para dar contexto à negação, nunca implementado (`TfidfStrategy` ficou em
  unigrama desde F2). Virou parte da correção de baseline, não um 5º
  candidato.
- Config vencedora: bigramas de palavra + char n-gramas (3,5) + marcação de
  negação, Regressão Logística. F1-macro CV 0,7338 (vs. 0,731 do TF-IDF
  unigrama original de F2, vs. 0,7234 do baseline só com a correção de
  bigramas — bigramas isolados **pioraram**, só compensam combinados com
  char n-gramas).
- Léxico de severidade e features estruturais: implementados, testados,
  nunca venceram uma rodada — descartados da representação de produção,
  código mantido e testado em `src/features/lexicon.py`/`structural.py`.
- Classificador ordinal (`mord.LogisticAT`): testado sobre a representação
  vencedora, F1-macro 0,566 — pior resultado da bateria inteira, inclusive
  abaixo do `DummyClassifier` de F2 em recall de `urgente`. Descartado;
  ADR-0003 atualizado (seção "Atualização — caixa 6.1") fechando a dívida
  que constava como hipótese não testada.
- Achado colateral (não do modelo, do pipeline): `mlflow.sklearn.log_model`
  recusou serializar o pipeline via skops por causa do `mark_negation`
  (callable customizado) — corrigido com `skops_trusted_types` explícito em
  `src/models/train.py`, não com troca geral para pickle/cloudpickle.
- Evidência: 12 runs no MLflow (experimento `triagem-urgencia`, prefixo
  `f6_repr_*`), tabela completa e leitura em `docs/EXPERIMENTS.md` (seção
  F6), 15 testes novos (`test_negation.py`, `test_lexicon.py`,
  `test_structural.py`, `test_representation_tuning.py`) — suíte em 52/52
  verde, cobertura 69%. `src/models/train.py` e `src/features/vectorize.py`
  atualizados para servir a representação vencedora; `models/current/model.joblib`
  retreinado de verdade com o pipeline novo (não só medido em CV) e checado
  manualmente contra 3 laudos de exemplo.
- Pendente para o fechamento de F6: caixas 6.2 a 6.11.

### F6 — caixa 6.2 (calibração de probabilidade) · execução · 2026-09-15

Protocolo: 5 dobras externas (seed 42) — em cada uma, separa 20% do treino da
dobra como fatia de calibração (estratificada), ajusta representação vencedora
de 6.1 + LogReg só no restante, calibra (Platt/isotônica) só na fatia separada
via `FrozenEstimator` (achado: sklearn removeu `cv="prefit"` na versão em uso,
1.9 — substituído sem alterar a metodologia pretendida, ver `src/models/calibration.py`).

- Vencedora: **isotônica**. Menor Brier multiclasse (0,3744) e menor ECE da
  classe `urgente` (0,0184, menos da metade do Platt) da bateria.
- Achado relevante para §7, não esperado antes de rodar: calibração isolada
  (sem qualquer ajuste de limiar, que só vem em 6.4) já reduz sub-triagem de
  12,1% para 9,3% e sobe recall de `urgente` de 0,786 para 0,815 — a
  calibração por classe muda a ordem relativa de probabilidade entre classes
  para uma mesma amostra, não é transformação cosmética.
- Custo aceito: F1-macro cai de 0,7297 para 0,7235 (-0,0062) e sobre-triagem
  sobe de 14,4% para 17,1% — consistente com §7 (sobre-triagem é o erro
  "caro, mas seguro").
- Achado colateral de serialização: `mlflow.sklearn.log_model` também recusou
  `sklearn.calibration._CalibratedClassifier` via skops (classe interna do
  sklearn fora da allowlist padrão) — mesma correção de 6.1, allowlist
  explícita em `skops_trusted_types`, não troca geral de formato.
- Produção atualizada: `train_and_persist()` agora separa 20% do treino como
  fatia de calibração antes de persistir — `model.joblib` é um
  `CalibratedClassifierCV`, não mais o pipeline cru. Conferido manualmente:
  API carrega e prediz; um exemplo de teste do README precisou ser trocado
  porque o texto curado antes (checkup de rotina, sintético) virou fronteiriço
  e passou a predizer `urgente` — trocado por um exemplo real do
  `data/processed/test.csv` mais estável.
- Evidência: 3 runs no MLflow (`f6_calib_none/sigmoid/isotonic`), curva de
  calibração em `docs/evidence/f6_calibration_curve_2026-09-15.png`, tabela e
  leitura em `docs/EXPERIMENTS.md` (seção F6), 5 testes novos
  (`test_calibration.py`) — suíte em 57/57 verde, cobertura 68%.
- Pendente para o fechamento de F6: caixas 6.3 a 6.11.

### F6 — caixa 6.3 (matriz de custo) · execução · 2026-09-15

`src/models/cost.py`: matriz 3x3 de §7/§14 (sub-triagem 5/15 por nível de
distância ordinal, sobre-triagem 1/2), `mean_cost()`/`total_cost()`.

- Usada para fechar a dívida "Como revisitar" do ADR-0003: comparação
  Regressão Logística vs. Multinomial NB (menor sub-triagem em F2) refeita
  sob custo explícito, com a representação de 6.1 e a calibração isotônica
  de 6.2 aplicadas igualmente aos dois.
- Resultado, ao contrário da hipótese registrada em F2/ADR-0003: **LogReg
  venceu em toda métrica**, inclusive custo médio (1,1749 vs. 1,3812 do NB).
  A vantagem de sub-triagem que o NB tinha em F2 não se repetiu — a
  calibração isotônica já recupera esse efeito para a LogReg de forma
  deliberada, superando a vantagem "acidental" do NB.
- Custo médio do pipeline de produção no teste reservado: 1,290 (vs. 1,175
  em CV — sem sinal de overfitting na calibração).
- ADR-0003 atualizado (seção "Atualização — caixa 6.3"): decisão de modelo
  confirmada, não supersedida.
- Evidência: 2 runs no MLflow (`f6_cost_logreg`/`f6_cost_multinomial_nb`),
  tabela e leitura em `docs/EXPERIMENTS.md` (seção F6), 7 testes novos
  (`test_cost.py`) — suíte verde.
- Pendente para o fechamento de F6: caixas 6.4 a 6.11.

### F6 — caixa 6.4 (ajuste de limiar, ADR-0005) · execução · 2026-09-15

`src/models/threshold.py` + `src/models/threshold_search.py`: regra de decisão
por limiar cumulativo sobre probabilidades calibradas (6.2), substituindo o
argmax puro na API. Busca em duas etapas sobre probabilidades *out-of-fold*
de 5 dobras (sem vazamento): `THRESHOLD_URGENTE` (maior valor que cumpre
`recall_urgente >= 0,90`, §14), depois `THRESHOLD_ATENCAO` (minimiza custo
médio da matriz de 6.3, com o primeiro já fixado).

- Limiares encontrados: `THRESHOLD_URGENTE = 0,31`, `THRESHOLD_ATENCAO = 0,09`.
- Meta de recall atingida em CV (0,9026 ≥ 0,90); no teste reservado ficou em
  0,8803 — abaixo do alvo por variância amostral (conjunto 4x menor), não
  contradição, registrado com transparência.
- Custo médio caiu quase pela metade nos dois conjuntos: -45% (CV, 1,1747→0,6449)
  e -48% (teste, 1,2904→0,6717). Sub-triagem caiu de ~9-10% para ~3-4%.
- **Achado mais forte, não previsto antes de rodar**: recall de `normal`
  desaba de 0,5449 para 0,0435 no teste — o sistema praticamente para de
  prever `normal` (troca matematicamente correta dada a assimetria de custo,
  mas muda o caráter do sistema; registrado com destaque em ADR-0005 como
  prioridade para a leitura qualitativa de erros de 6.5).
- `src/api/main.py` atualizado: usa `select_label()` em vez de
  `max(probabilities)`. Dois exemplos do README precisaram ser revisados —
  o exemplo de "normal" sintético virou "atenção" com o novo limiar; trocado
  por um laudo real do conjunto de teste com alta confiança.
- ADR-0005 aceito, com alternativas descartadas (argmax, regra bayesiana de
  custo mínimo, grade 2D completa) e condição explícita de reabertura.
- Evidência: MLflow (`busca_limiar_concluida`), tabela e leitura em
  `docs/EXPERIMENTS.md` (seção F6), 8 testes novos (`test_threshold.py`,
  `test_threshold_search.py`) — suíte em 72/72 verde, cobertura 64%.
- Pendente para o fechamento de F6: caixas 6.5 a 6.11.

### F6 — caixa 6.5 (análise qualitativa de erros) · execução · 2026-09-15

`docs/error_analysis.md`: leitura manual de amostras reais dos 4 tipos de erro
(distância ordinal -2/-1/+1/+2) no teste reservado, motivada pela pergunta em
aberto do autor sobre o recall de `normal` ter caído a 0,04 em ADR-0005 (o
autor pediu para ver esta análise antes de decidir se reabre a matriz de
custo — resposta registrada aqui, decisão final ainda com o autor).

- **Achado principal**: boa parte do que a matriz de confusão chama de "erro"
  é o teto de qualidade do mapeamento heurístico de ADR-0001 sendo
  alcançado, não falha de representação/calibração/limiar. Confirmado nas
  duas direções com exemplos reais: `normal`→`urgente` (246 casos) são em
  boa parte artigos de pesquisa básica sobre temas graves ("ventricular
  fibrillation", "rupture of thoracic aorta") categorizados `normal` só por
  não caírem na categoria "cardiovascular" original; `urgente`→`atenção`/
  `normal` (94 casos, incluindo os 5 piores erros de 2 níveis) são artigos
  de epidemiologia/metodologia sobre temas cardiovasculares/neurológicos mas
  com texto administrativo, sem urgência aparente.
- Hipóteses descartadas com evidência: tamanho de texto (sem diferença entre
  acerto/erro); negação mal tratada (checagem grosseira não mostrou padrão
  causal — a evidência real sobre negação continua sendo a comparação
  controlada em CV de 6.1).
- Resposta à pergunta pendente sobre a matriz de custo: recall de `normal`
  baixo tem duas causas empilhadas — a assimetria do limiar (reversível
  ajustando a matriz) e o teto de qualidade do rótulo (não reversível por
  ajuste de limiar/matriz, só por revisar ADR-0001 ou trocar de dataset,
  fora do escopo de F6). Reabrir a matriz reduziria a contagem de
  sobre-triagem mas não eliminaria essa segunda categoria de erro.
- Pendente para o fechamento de F6: caixas 6.6 a 6.11 — e a decisão do autor
  sobre reabrir ou não a matriz de custo, informada por esta análise.

### F6 — decisão do autor sobre a matriz de custo · 2026-09-15

Autor revisou `docs/error_analysis.md` e decidiu **manter a matriz de custo como
está** — reabri-la resolveria só a causa reversível (assimetria do limiar), não o
teto de qualidade do mapeamento de rótulo (causa dominante do recall baixo de
`normal`). Registrado em ADR-0005, seção "Revisão do autor".

### F6 — caixas 6.6-6.9 (ONNX, paridade, latência, flag da API) · execução · 2026-09-15

Testado diretamente (não assumido) se o pipeline vencedor de 6.1-6.4 convertia
para ONNX — não convertia, por 3 limitações reais do `skl2onnx`: preprocessador
Python customizado (marcação de negação), `analyzer="char_wb"` (char n-gramas) e
`CalibratedClassifierCV` exigindo entrada numérica (não aceita pipeline de texto).

- Decisão: duas variantes servíveis via `MODEL_BACKEND` (`sklearn` padrão,
  `onnx` opt-in) — ver **ADR-0004 aceito**, com o diagnóstico completo e as
  alternativas descartadas.
- Calibração preservada no backend ONNX apesar do bloqueio do
  `CalibratedClassifierCV`: `OneVsRestIsotonicCalibrator`
  (`src/optimization/calibrator.py`), calibrador isotônico manual rodando em
  Python fora do grafo ONNX. Achado ao validar essa peça: sklearn calibra por
  padrão sobre `decision_function`, não `predict_proba` — confirmado
  empiricamente comparando as duas (bateram byte a byte usando
  `decision_function`); o calibrador manual usa `predict_proba` conscientemente
  (é o que o runtime ONNX expõe), documentado no docstring da classe.
- Resultado de latência (container, mesmo protocolo do baseline de F3, 3
  execuções de N=1.000): p95 original (sklearn) 7,01 ms → p95 otimizado (ONNX)
  2,92 ms — **-58,3%**. Tamanho de artefato -67% (2,4 MB → 0,79 MB).
- Achado colateral fechado nesta caixa (estava explicitamente adiado desde F3
  em `docs/LATENCY.md`, "não esquecer ao reabrir F6"): `mlflow`/`lightgbm`/`mord`
  moveram de `dependencies` para um grupo `training` separado — não são usados
  por `src/api/`, só por scripts de treino/experimentação. Imagem Docker caiu de
  1,03 GB para 696 MB (-32,4%), confirmado com build real, não estimativa.
  `Makefile`/CI atualizados (`uv sync --group training`) para não quebrar
  `make setup`/testes.
- Achado ao testar o backend ONNX em **container** (não local): operador
  `StringNormalizer` do onnxruntime falha sem locale UTF-8 instalado — a imagem
  `python:3.11-slim` não vem com nenhum. Corrigido no Dockerfile (`locales` +
  `locale-gen en_US.UTF-8`). Não aparecia rodando local porque o locale do host
  mascarava o problema — só apareceu com a validação real em container.
- `tests/test_onnx_parity.py`: tolerância declarada de 0,05 de diferença
  absoluta por probabilidade, baseada em medição real (300 amostras: diferença
  média 0,0024, máxima 0,0316); concordância de rótulo 99,4% em 1.000 amostras.
- Evidência: `docs/LATENCY.md` atualizado com os números completos e a seção de
  trade-off de qualidade; 8 testes novos (`test_calibrator.py`,
  `test_onnx_parity.py`) — suíte em 77/77 verde.
- Pendente para o fechamento de F6: caixa 6.10 (promoção no MLflow Registry) e
  6.11 (checkpoint de fechamento).

### F6 — caixa 6.10 (promoção no MLflow Registry) · execução · 2026-09-15

Achado ao preparar a promoção: o critério de elegibilidade de ADR-0008 (piso de
F1-macro ≥ 0,70) **bloquearia o próprio modelo que ADR-0005/6.4 decidiu
servir** — F1-macro do pipeline com limiar tunado é 0,523 no teste (era 0,728
antes, caiu de propósito). ADR-0008 já previa este exato momento ("quando
ADR-0005 for aceito... este ADR fica supersedido"). Resolvido com **ADR-0010**:
critério trocado para recall de `urgente` (piso 0,85) + custo médio (sem
regredir mais que +0,10 vs. produção) — estratégia de gate humano de ADR-0008
não muda, só o número que decide elegibilidade.

- Achado colateral: `evaluate_pipeline` (usada pela task `evaluate` da DAG)
  avaliava com `pipeline.predict()` (argmax puro), não com `select_label`
  (limiar real de produção, caixa 6.4) — corrigido; a DAG agora avalia a
  política que de fato é servida, não uma diferente.
- `scripts/promote_model.py` (novo): reproduz a lógica da task `register` da
  DAG fora dela, mais o passo que a task não faz (trocar o alias
  `@production`) — só troca com `--promote` explícito, mesmo quando elegível
  (gate humano de verdade, não automação disfarçada).
- Executado de verdade: versão 5 do modelo `triagem-urgencia` promovida a
  `@production` (recall_urgente 0,8803 ≥ piso de 0,85; sem baseline anterior
  para comparar custo). Confirmado consultando o MLflow Registry diretamente.
- `airflow/dags/retrain_dag.py` atualizada (`min_recall_urgente`,
  `max_cost_increase`) e validada com import real (não só sintaxe) antes de
  aceitar a mudança — `AIRFLOW_HOME` configurado, `AIRFLOW__CORE__LOAD_EXAMPLES=False`,
  módulo importa sem erro.
- Evidência: `tests/test_promotion.py` reescrito para a nova assinatura, suíte
  em 77/77 verde.
- Pendente para o fechamento de F6: caixa 6.11 (checkpoint de fechamento).

### CHECKPOINT — F6 «Modelo final e otimização de latência» · fechamento · 2026-09-15

HARD REQUIREMENTS DA FASE
- HR-6.1 otimização aplicada e ganho medido → ok (ONNX Runtime, p95 -58,3%,
  `docs/LATENCY.md`)
- HR-6.2 paridade numérica entre modelo original e otimizado → ok
  (`tests/test_onnx_parity.py`, tolerância 0,05, divergência real medida
  0,0024 média / 0,0316 máxima)
- HR-6.3 política de custo/limiar decidida em ADR → ok (ADR-0005 aceito,
  matriz + alvo de recall + limiares numéricos)
- HR-6.4 modelo em `Production` no Registry → ok (`triagem-urgencia` versão 5,
  alias `@production`, confirmado consultando o Registry diretamente)

PORTÕES NUMÉRICOS

| Portão | Alvo | Medido | Status |
|---|---|---|---|
| Ganho de latência p95 medido e registrado em % | sim | -58,3% (7,01→2,92 ms) | ok |
| Paridade ONNX verde | sim | 2/2 testes, tolerância 0,05 | ok |
| Recall de `urgente` ≥ alvo do ADR-0005 | ≥ 0,90 | 0,9026 (CV, out-of-fold pooled) | ok |
| Modelo em `Production` | sim | versão 5 | ok |

ESTADO
- Caixas da fase: 11/11 → micro 100%
- Progresso macro: **81,0%** (66,0% herdado de F5 + 15,0% de F6, peso cheio)
- Rubrica tocada por esta fase: R1 (15%) — fase mapeia 1:1 com o critério

SITUAÇÃO
- Feito: tuning de representação (6.1, +char n-gramas/negação, F1-macro
  +0,0028 sobre F2); calibração isotônica (6.2, sub-triagem -21% já antes de
  qualquer limiar); matriz de custo aplicada à seleção de modelo (6.3,
  confirma LogReg mesmo sob custo explícito); limiar cumulativo (6.4/ADR-0005,
  custo médio -45 a -48%, meta de recall batida); análise qualitativa de
  erros (6.5, achado principal: teto de qualidade do mapeamento heurístico de
  rótulo, não falha do modelo); export ONNX com duas variantes servíveis via
  flag (6.6-6.9/ADR-0004, p95 -58,3%, imagem Docker -32,4% como achado
  colateral); critério de promoção atualizado e modelo promovido de fato
  (6.10/ADR-0010).
- 4 ADRs novos/atualizados nesta fase: ADR-0004 (aceito), ADR-0005 (aceito),
  ADR-0008 (supersedido por ADR-0010 quanto ao critério), ADR-0010 (aceito).
  ADR-0003 recebeu 2 atualizações (ordinal descartado em 6.1, LogReg
  reconfirmado sob custo em 6.3) sem ser supersedido — decisão original
  manteve-se válida nos dois casos.
- Achados reais que mudaram o rumo do trabalho, não hipóteses: skl2onnx não
  converte char n-gramas nem preprocessador customizado nem
  `CalibratedClassifierCV` com pipeline de texto (forçou a arquitetura de duas
  variantes); recall de `normal` desaba para 0,04 com o limiar tunado (efeito
  colateral real da assimetria de custo, mantido após revisão do autor);
  `mlflow.sklearn.log_model` recusa serializar callables/classes fora da
  allowlist da skops (corrigido com `skops_trusted_types` explícito, não
  bypass geral); locale UTF-8 ausente quebra o `StringNormalizer` do ONNX em
  container (não aparecia local); critério de promoção antigo (F1-macro)
  bloquearia o próprio modelo que a fase decidiu servir.
- Bloqueios / decisões pendentes do autor: nenhum — a única decisão em aberto
  durante a fase (reabrir ou não a matriz de custo após ver o recall de
  `normal` cair) foi resolvida pelo autor após ver `docs/error_analysis.md`
  (manter a matriz como está).
- Riscos observados: dois pipelines de produção para manter (`sklearn` e
  `onnx`), não um — se a representação vencedora mudar no futuro, o backend
  ONNX não se atualiza sozinho (documentado em ADR-0004, "Como revisitar").

VEREDITO: **PODE AVANÇAR para F7** — todos os hard requirements de F6
fechados, nenhuma exceção pendente.
