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
