# Experimentos

Espelho legível dos runs do MLflow — o avaliador não vai abrir seu tracking server.
Atualizar a cada modelo relevante (F2 e F6).

| # | Run id | Modelo | Representação | F1 macro | F1 weighted | Recall `urgente` | ROC-AUC OvR | Sub-triagem % | Sobre-triagem % | Latência p95 (ms) | Observação |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `54c1815e` | DummyClassifier (stratified) | — | 0,339 | 0,339 | 0,351 | 0,504 | 32,9% | 33,2% | não medida (F3) | baseline mínimo — ~aleatório, como esperado |
| 2 | `ed2e5ded` | Regressão Logística | TF-IDF (1,1), max_features=20000 | **0,731** | 0,733 | 0,796 | **0,877** | 11,8% | 14,6% | não medida (F3) | melhor F1-macro e ROC-AUC dos seis — **candidato a servir** |
| 3 | `e2fdf3db` | Random Forest (200 árvores) | TF-IDF (1,1), max_features=20000 | 0,687 | 0,691 | 0,774 | 0,856 | 11,9% | 18,2% | não medida (F3) | abaixo da LogReg em tudo, mais lento pra treinar |
| 4 | `b09a0535` | Multinomial Naive Bayes | TF-IDF (1,1), max_features=20000 | 0,675 | 0,679 | 0,863 | 0,863 | **6,9%** | 22,8% | não medida (F3) | pior F1-macro do grupo, mas **menor sub-triagem de todos** — ver leitura abaixo |
| 5 | `2ed5914e` | LightGBM (100 árvores) | TF-IDF (1,1), max_features=20000 | 0,708 | 0,711 | 0,754 | 0,867 | 13,6% | 15,2% | não medida (F3) | pior sub-triagem do grupo, exceto o Dummy |
| 6 | `8aa8c496` | LinearSVC calibrado (sigmoide) | TF-IDF (1,1), max_features=20000 | 0,723 | 0,726 | 0,794 | 0,873 | 11,6% | 15,5% | não medida (F3) | segundo melhor F1-macro; calibração viabilizou probabilidade |

## Protocolo

- Validação cruzada estratificada, `k = 5`, seed `42`.
- Métricas reportadas são a **média das 5 dobras sobre o treino** (`data/processed/train.csv`,
  8.980 amostras) — o teste (`data/processed/test.csv`, 2.245 amostras) fica reservado,
  nunca tocado nesta fase.
- Sub-triagem % / Sobre-triagem % = proporção das 8.980 predições (soma das 5 dobras
  de validação) em que o modelo previu, respectivamente, uma faixa de urgência **menos**
  ou **mais** grave que a real.
- Todo run registra no MLflow: parâmetros (`model`, `n_splits`, `seed`), as 9 métricas
  (6 de qualidade + 3 de contagem sub/sobre-triagem/acerto exato) e a matriz de
  confusão 3×3 como artefato CSV.
- Os candidatos 4–6 (Multinomial NB, LightGBM, LinearSVC calibrado) foram adicionados
  numa segunda rodada, ainda em F2, **antes** de persistir modelo para F3 — decisão
  registrada em ADR-0003: comparar modelo é escopo de F2 (R1), não de F3 (API/container),
  e trocar de modelo depois de montar a API custaria retrabalho de infraestrutura.
- Reprodutibilidade: os 3 candidatos originais (dummy/logreg/random_forest) foram
  re-treinados nesta rodada, em máquina diferente da que gerou os números publicados
  antes — os valores de F1-macro bateram na precisão exibida (3 casas), confirmando
  que o pipeline (seed, split, vetorização) é reprodutível entre ambientes.

## Leitura dos resultados

Regressão Logística segue vencedora em **todas** as métricas de qualidade agregada
(F1-macro, F1-weighted, ROC-AUC) mesmo depois de ampliar a comparação de 3 para 6
candidatos. O segundo colocado em F1-macro é o LinearSVC calibrado (0,723 vs. 0,731,
diferença de menos de 1 ponto) — confirma que o SVM linear já era competitivo em F2,
só faltava `predict_proba` (motivo do descarte original, ver tabela abaixo).

**Achado mais relevante da rodada, para além do ranking de F1-macro:** Multinomial NB
tem a **menor sub-triagem de todos os candidatos reais** (6,9%, contra 11,6–13,6% dos
demais) — quase metade da LogReg. Ele consegue isso à custa da maior sobre-triagem do
grupo (22,8%): o modelo erra "para o lado seguro" com muito mais frequência. Isso **não**
o torna o vencedor de F2 — F2 ainda não tem matriz de custo nem política de limiar
formalizada (isso é F6/ADR-0005), e seu F1-macro (0,675) é o pior do grupo de candidatos
reais. Mas é um sinal empírico forte demais para descartar: fica registrado em ADR-0003
como o principal candidato a revisitar quando a matriz de custo assimétrica entrar em
jogo — sob uma política que penalize sub-triagem pesadamente, o ranking pode inverter.

LightGBM (não-linear, gradient boosting sobre TF-IDF) não superou nenhum dos lineares
em nenhuma métrica — repete o padrão já visto com Random Forest: não-linearidade não
ajudou nesta representação de texto. Fica descartado como modelo a servir, mas não
como técnica (ver nota técnica abaixo sobre a escolha da biblioteca).

Nenhum ajuste de limiar ou calibração de decisão foi feito nesta fase (isso é F6,
ADR-0005) — os números de sub/sobre-triagem acima são com o limiar padrão de decisão
de cada modelo (maior probabilidade), não uma política deliberada de reduzir sub-triagem.

## Descartados e por quê

Decisão de modelo final, alternativas fora do escopo desta fase (embeddings
pré-treinados/fine-tuning de transformer, classificador ordinal) e a análise completa
de trade-offs estão em **`docs/adr/0003-escolha-modelo-base.md`** — este documento é
o espelho legível dos runs, a justificativa fica no ADR.

| Item | Motivo do descarte |
|---|---|
| LinearSVC (F2, primeira rodada) | Não produzia `predict_proba` nativamente — resolvido nesta rodada com `CalibratedClassifierCV` (candidato 6); a hipótese de que era competitivo se confirmou (0,723 F1-macro) |
| `HistGradientBoostingClassifier` (sklearn) | Não aceita matriz esparsa — exigiria densificar TF-IDF (8.980×20.000 ≈ 1,4 GB por dobra), incompatível com o requisito de modelo leve. Ver ADR-0003 |
| XGBoost | `uv add xgboost` instalou ~326 MB de dependências CUDA/NCCL (`nvidia-nccl-cu12`) mesmo para uso 100% CPU — contradiz a leveza exigida por R1. Substituído por LightGBM (3,3 MB, sem dependência de GPU). Ver ADR-0003 |

## F6 — Tuning de representação (caixa 6.1)

Busca gulosa incremental em vez de fatorial completo (2⁴ = 16 combinações) — decisão
do autor de 2026-09-15 (`docs/PROGRESS.md`): baseline → cada candidato isolado contra
o baseline → incorpora o vencedor da rodada, testa os restantes em cima → repete até
não haver ganho → checagem cirúrgica do 2º colocado do round 1 combinado à config
final → classificador ordinal (`mord`) como eixo separado, testado só por cima da
representação vencedora. Orçamento máximo ~13 runs; parou em **12** (a rodada 3 não
trouxe ganho, sem precisar da rodada 4).

Classificador fixo em Regressão Logística (vencedora de F2) em todos os runs, exceto
o último (eixo ordinal). Mesma CV de 5 dobras, seed 42, sobre `data/processed/train.csv`
(8.980 amostras) — igual ao protocolo de F2.

| Run | Config | F1 macro | F1 weighted | ROC-AUC OvR | Recall `urgente` | Sub-triagem % | Sobre-triagem % |
|---|---|---|---|---|---|---|---|
| `f6_repr_baseline` | bigramas (1,2), sem técnica extra | 0,7234 | 0,7260 | 0,8758 | 0,7855 | 12,2% | 15,0% |
| `f6_repr_r1_negation` | + marcação de negação (isolada) | 0,7211 | 0,7237 | 0,8754 | 0,7826 | 12,2% | 15,1% |
| `f6_repr_r1_severity_lexicon` | + léxico de severidade (isolado) | 0,7213 | 0,7239 | 0,8754 | 0,7833 | 12,2% | 15,1% |
| `f6_repr_r1_structural` | + features estruturais (isolado) | 0,7221 | 0,7246 | 0,8754 | 0,7769 | 12,5% | 14,8% |
| `f6_repr_r1_char_ngrams` | + char n-gramas (3,5) (isolado) — **vencedor round 1** | 0,7331 | 0,7356 | 0,8822 | 0,7915 | 11,9% | 14,3% |
| `f6_repr_r2_negation` | char_ngrams + negação — **vencedor round 2 e da busca** | **0,7338** | **0,7363** | **0,8822** | 0,7915 | 11,9% | 14,2% |
| `f6_repr_r2_severity_lexicon` | char_ngrams + léxico | 0,7322 | 0,7347 | 0,8820 | 0,7896 | 12,0% | 14,3% |
| `f6_repr_r2_structural` | char_ngrams + estruturais | 0,7325 | 0,7350 | 0,8819 | 0,7896 | 12,0% | 14,3% |
| `f6_repr_r3_severity_lexicon` | char_ngrams + negação + léxico | 0,7325 | 0,7350 | 0,8820 | 0,7925 | 11,9% | 14,4% |
| `f6_repr_r3_structural` | char_ngrams + negação + estruturais | 0,7327 | 0,7352 | 0,8819 | 0,7887 | 12,1% | 14,2% |
| `f6_repr_surgical_check` | idêntico ao round 3 (`structural` combinado à config final) | 0,7327 | 0,7352 | 0,8819 | 0,7887 | 12,1% | 14,2% |
| `f6_repr_ordinal_mord` | vencedora + `mord.LogisticAT` em vez de LogReg | 0,5663 | 0,5694 | 0,7580 | 0,5544 | **21,6%** | 21,2% |

### Leitura dos resultados

**A correção do gap de §10.6 (bigramas nunca implementados em F2) sozinha piora o
baseline**: 0,7234 contra 0,731 do TF-IDF unigrama original — achado relevante que
não estava previsto. Bigramas isolados adicionam ruído dimensional sem contexto
suficiente para compensar. Só voltam a valer a pena **combinados** com char n-gramas.

**Char n-gramas (3,5) é a técnica isolada mais forte de longe** (0,7331 no round 1,
contra 0,721-0,722 das outras três) — captura variação morfológica/subtoken
(prefixos como `hyper-`/`hypo-`, sufixos `-itis`/`-oma`) que nem unigrama nem
bigrama de palavra alcançam. Consistente com a literatura de classificação de texto
biomédico.

**Marcação de negação só ajuda depois do char n-grama**, não sozinha (round 1: 0,7211,
pior que o próprio baseline) — evidência direta do risco de interação identificado
antes de rodar: o ganho de marcar `shock_NEG` só aparece quando o char n-grama já
captura submorfemas que se beneficiam de tokens distintos para a forma negada vs.
afirmada. Testar via busca gulosa incremental (em vez de assumir o ganho isolado)
capturou exatamente esse efeito.

**Léxico de severidade e features estruturais nunca venceram uma rodada** — nem
isolados, nem combinados. Hipótese: o léxico de 34 termos é pequeno demais frente a
um vocabulário TF-IDF de até 20k+20k dimensões para mover a agulha, e as 3 features
estruturais (contagem de tokens, densidade numérica, densidade de pontuação) são
fracamente correlacionadas com urgência clínica real (mais um proxy plausível na
teoria do que um sinal forte na prática, o que já era a dúvida original antes de
implementar). Ambas ficam descartadas da representação de produção — código
mantido em `src/features/lexicon.py` e `src/features/structural.py` (testado,
reaproveitável se uma revisão futura do léxico mudar o resultado), mas fora do
`PRODUCTION_REPRESENTATION` de `src/features/vectorize.py`.

**Checagem cirúrgica não trouxe combinação nova**: o 2º colocado do round 1 fora da
config final era `structural` — mas essa exata combinação (`char_ngrams + negação +
structural`) já tinha sido testada no round 3 como candidata perdedora. O resultado
bateu byte a byte com `f6_repr_r3_structural` (mesma seed, pipeline determinístico),
o que confirma reprodutibilidade em vez de descobrir algo novo — artefato de haver
só 4 candidatos, não falha do protocolo.

**Classificador ordinal (`mord.LogisticAT`) teve o pior resultado de toda a
bateria**, inclusive abaixo do Dummy de F2 em recall de `urgente` (0,554 contra 0,351
do Dummy — pior que aleatório nessa métrica específica) e mais que dobrou a
sub-triagem (21,6% contra ~12% dos candidatos de Regressão Logística). Hipótese mais
provável: a regularização L2 padrão do `mord` (`alpha=1.0`) não foi pensada para
~40 mil dimensões esparsas herdadas do char n-grama — não é evidência de que
classificação ordinal não presta para o problema, é evidência de que os
hiperparâmetros padrão não servem nesta representação de alta dimensão. Fica
registrado como técnica testada e descartada nesta rodada (não hipótese, fato
validado — diferença do que constava em ADR-0003), sem impedir uma futura reavaliação
com regularização mais forte, se o tempo do projeto permitir.

### Decisão

`PRODUCTION_REPRESENTATION` (`src/features/vectorize.py`): bigramas de palavra (1,2)
+ char n-gramas (3,5) + marcação de negação, Regressão Logística. `src/models/train.py`
atualizado para usar essa representação no artefato servido pela API. Ganho de
F1-macro sobre o TF-IDF original de F2: **+0,0028** (0,731 → 0,7338) — modesto, mas
real e medido em CV, não em uma única leitura de teste.

## F6 — Calibração de probabilidade (caixa 6.2)

§7 é explícito: calibrar **antes** de ajustar limiar (caixa 6.4), senão o ajuste é
"chute com aparência de método". Protocolo: 5 dobras externas (seed 42, igual às
demais caixas) — em cada uma, separa 20% do treino da dobra como fatia de calibração
(estratificada), ajusta representação vencedora de 6.1 + LogReg só no restante (80%),
calibra (Platt/sigmoide ou isotônica) só na fatia separada via `FrozenEstimator`
(sklearn ≥ 1.6 — substitui o antigo `cv="prefit"`, removido nesta versão do sklearn).
Compara contra a mesma pipeline **sem** recalibrar ("none").

| Método | F1 macro | F1 weighted | ROC-AUC OvR | Recall `urgente` | Brier multiclasse | ECE `urgente` | Sub-triagem % | Sobre-triagem % |
|---|---|---|---|---|---|---|---|---|
| `none` (sem recalibrar) | 0,7297 | 0,7322 | 0,8793 | 0,7858 | 0,3798 | 0,0417 | 12,1% | 14,4% |
| `sigmoid` (Platt) | 0,7288 | 0,7316 | 0,8811 | 0,8109 | 0,3746 | 0,0351 | 10,3% | 16,0% |
| `isotonic` — **vencedora** | 0,7235 | 0,7266 | 0,8795 | **0,8154** | **0,3744** | **0,0184** | **9,3%** | 17,1% |

Curva de calibração (reliability diagram, classe `urgente` one-vs-rest, 3 métodos
sobrepostos): `docs/evidence/f6_calibration_curve_2026-09-15.png`.

Nota sobre o F1-macro de `none` aqui (0,7297) ser um pouco menor que o da caixa 6.1
(0,7338, mesma config de representação): a diferença é o próprio protocolo desta
caixa — aqui o pipeline treina só nos 80% de cada dobra (20% vira fatia de
calibração), enquanto em 6.1 treinava nos 100% da dobra. Queda esperada, não é
regressão da representação.

### Leitura dos resultados

**Calibração isolada, sem qualquer ajuste de limiar, já reduz sub-triagem de forma
mensurável**: 12,1% (`none`) → 10,3% (`sigmoid`) → **9,3%** (`isotonic`) — quase 3
pontos percentuais só de recalibrar as probabilidades, antes da caixa 6.4 sequer
existir. Recall de `urgente` sobe na mesma direção (0,786 → 0,815). Isso acontece
porque a calibração é ajustada por classe (one-vs-rest) e pode mudar a ordem relativa
das probabilidades entre classes para uma mesma amostra — não é uma transformação
cosmética que preserva o argmax, como pareceria à primeira vista.

**Isotônica vence em toda métrica de calibração** (menor Brier, muito menor ECE — menos
da metade do Platt) **e também no efeito colateral que mais importa para o projeto**
(menor sub-triagem, maior recall de `urgente`), ao custo de uma queda pequena de
F1-macro (0,7297 → 0,7235, -0,0062) e mais sobre-triagem (14,4% → 17,1%). Consistente
com a troca que o próprio §7 descreve como aceitável: sobre-triagem é "cara, mas
segura"; sub-triagem é o erro perigoso. Isotônica normalmente precisa de mais dados
que Platt para não sobreajustar (~1.400+ amostras por fatia de calibração aqui,
folga confortável acima do problema clássico de isotônica com poucos dados).

### Decisão

Isotônica (`CALIBRATION_METHOD = "isotonic"` em `src/models/train.py`) entra na
produção: `train_and_persist()` agora separa 20% do treino como fatia de calibração
(`CALIB_HOLDOUT_FRACTION`, estratificada, seed 42) antes de persistir o artefato —
`model.joblib` passa a ser um `CalibratedClassifierCV` envolvendo a representação
vencedora de 6.1, não mais o pipeline cru. Ajuste de limiar (caixa 6.4) parte desta
calibração, não da probabilidade não-calibrada.
