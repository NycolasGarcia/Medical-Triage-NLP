# PROGRESS — log de checkpoints

Log **append-only**. Nunca reescrever entrada antiga; se algo mudou, nova entrada.
As caixas de tarefa vivem no plano de fases interno do projeto — aqui vai só o
snapshot numérico, as evidências e o veredito.

## Estado atual

| Campo | Valor |
|---|---|
| Fase atual | F4 — CI/CD e orquestração |
| Micro (fase) | 0% |
| Macro (rubrica coberta) | 19,0% |
| Último checkpoint | 2026-09-14 — F3 fechada 10/10, todos os hard requirements ok |
| Bloqueios | Nenhum conhecido |

## Progresso macro por fase

| Fase | Peso | Micro | Contribuição |
|---|---|---|---|
| F0 Scaffolding | 3 | 100% | 3.0 |
| F1 Dados e EDA | 4 | 100% | 4.0 |
| F2 Baselines | 5 | 100% | 5.0 |
| F3 API e container | 7 | 100% | 7.0 |
| F4 CI/CD e Airflow | 27 | 0% | 0.0 |
| F5 Monitoramento | 20 | 0% | 0.0 |
| F6 Modelo final e latência | 15 | 0% | 0.0 |
| F7 Consolidação e entrega | 19 | 0% | 0.0 |
| **Macro** | **100** | | **19.0%** |

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
