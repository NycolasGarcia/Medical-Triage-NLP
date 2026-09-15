# ADR-0003 — Escolha do modelo base de classificação de texto

- **Status:** aceito
- **Data:** 2026-09-14
- **Fase:** F2
- **Decisor:** Nycolas Garcia

## Contexto

O enunciado do TC3 (Bibliotecas Requeridas) permite "Scikit-Learn ou framework de
preferência" para o modelo base — não obriga Scikit-Learn, só o sugere como default.
O critério R1 (20% da nota) exige um "modelo funcional de NLP" com "conversão/otimização
(ex.: ONNX) bem-sucedida e melhoria de latência demonstrada" — ou seja, o modelo
escolhido precisa ser leve o bastante para caber no orçamento de latência de F3/F6 e
exportável para ONNX, não apenas ter a melhor métrica de qualidade isolada.

F2 já havia comparado 3 candidatos (`DummyClassifier`, Regressão Logística, Random
Forest) com a Regressão Logística vencendo por margem clara (`docs/EXPERIMENTS.md`).
Antes de persistir esse modelo e começar a construir a API/Docker em F3, a comparação
foi deliberadamente estendida com mais 3 candidatos estruturalmente relevantes para
classificação ordinal de texto curto — o mesmo formato de problema da literatura de
análise de sentimento (previsão de nota/polaridade), que também é multiclasse ordinal
sobre texto curto. Fazer isso agora, ainda em F2, evita o custo de trocar de modelo
depois de já ter investido em API/Docker/monitoramento em torno de um candidato que
não é o melhor disponível.

## Decisão

Manter a **Regressão Logística (TF-IDF unigramas, `max_features=20000`)** como modelo
base a ser persistido e servido a partir de F3. Ela venceu em F1-macro (0,731) e
ROC-AUC one-vs-rest (0,877) entre os 6 candidatos avaliados, com sub-triagem competitiva
(11,8%, sem diferença prática frente aos outros lineares). Nenhum dos 3 candidatos
adicionados nesta rodada superou a Regressão Logística nas métricas agregadas.

Dois caminhos foram avaliados e **descartados nesta fase** (não do projeto inteiro):
classificador ordinal (`mord`) e embeddings clínicos pré-treinados/fine-tuning de
transformer — ver alternativas 7 e 8 abaixo.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| `DummyClassifier` (stratified) | Referência de piso, custo zero | Sem capacidade preditiva real | Não é candidato, é piso de comparação (F2, caixa 2.2) |
| **Regressão Logística (TF-IDF) — ESCOLHIDA** | Melhor F1-macro (0,731) e ROC-AUC (0,877) do grupo; leve (poucos MB); interpretável (coeficiente por n-grama); caminho direto para ONNX via `skl2onnx` | Linear — não captura interação entre termos | — (é a decisão) |
| Random Forest (200 árvores) | Não-linear, robusto a outliers | F1-macro 4,4 pontos abaixo da LogReg; mais lento para treinar; artefato maior para exportar/servir | Perde em toda métrica de qualidade sem compensar em sub-triagem |
| Multinomial Naive Bayes | Treino quase instantâneo; **menor sub-triagem de todos os candidatos reais** (6,9%, quase metade da LogReg) | F1-macro mais baixo do grupo (0,675); atinge a sub-triagem baixa às custas de sobre-triagem alta (22,8%) — ainda sem matriz de custo formal | Promissor para a política de limiar de F6 (ver ADR-0005), mas escolher modelo base por sub-triagem isolada antes da matriz de custo existir seria otimizar uma métrica sem o framework que a torna comparável às demais. Registrado como candidato forte a revisitar em F6 |
| LightGBM (gradient boosting sobre TF-IDF) | Não-linear, geralmente forte em texto esparso, exporta para ONNX via `onnxmltools` | F1-macro (0,708) e ROC-AUC (0,867) abaixo dos dois lineares líderes; pior sub-triagem do grupo, exceto o Dummy (13,6%) | Não superou os lineares neste dataset — repete o padrão do Random Forest: não-linearidade não ajudou aqui |
| LinearSVC + `CalibratedClassifierCV` (sigmoide) | Segundo melhor F1-macro (0,723) e ROC-AUC (0,873) — confirma que o LinearSVC já era competitivo em F2, só faltava `predict_proba` | Calibração adiciona CV aninhada (mais tempo de treino); ainda perde para a LogReg em toda métrica | Muito próximo da LogReg, mas não supera em nenhuma métrica — sem motivo para trocar |
| Classificador ordinal (`mord.LogisticAT`/`LogisticIT`) | Explora nativamente a ordem `normal < atencao < urgente`; conversa diretamente com a matriz de custo assimétrica planejada em ADR-0005 | Dependência nova fora do stack atual (`mord` não é mantido tão ativamente quanto scikit-learn); caminho de exportação ONNX não validado; testar exigiria decidir modelo e política de limiar ao mesmo tempo | **Adiado para F6**, não descartado — o ganho teórico é real, mas F2 é escopo de "comparar modelo" e F6 é escopo de "custo/limiar"; misturar as duas decisões nesta fase confundiria qual delas explica o resultado |
| Embeddings clínicos pré-treinados + classificador raso, ou fine-tuning de transformer (BioBERT/PubMedBERT/ClinicalBERT) | Maior teto de qualidade potencial; estado da arte em NLP clínico | Contradiz diretamente R1 ("modelo leve" é o próprio critério de nota, não um detalhe de implementação); artefato de centenas de MB a alguns GB, contra poucos MB do TF-IDF+LogReg; exige runtime pesado (`torch`/`transformers`) no container de inferência; ONNX e otimização de latência ficam ordens de magnitude mais caras de demonstrar dentro do orçamento da fase; sem indício de que a qualidade adicional seja necessária — a LogReg já atinge recall de `urgente` de 0,796 | **Descartado nesta fase** por violar a restrição central do projeto antes mesmo de qualquer teste. Não há cenário em que o ganho de qualidade hipotético justifique abrir mão do requisito de leveza que é avaliado explicitamente (R1) |

### Nota técnica: por que LightGBM e não `HistGradientBoostingClassifier` (sklearn) ou XGBoost

A primeira tentativa de testar gradient boosting foi com `HistGradientBoostingClassifier`
do próprio scikit-learn (zero dependência nova). Falhou: o estimador **não aceita
matriz esparsa** nesta versão do sklearn (1.9.0) — exigiria densificar a matriz TF-IDF
(8.980 linhas × 20.000 colunas ≈ 1,4 GB por dobra de CV), o que é incompatível com o
princípio de modelo leve do projeto.

A segunda tentativa foi XGBoost. `uv add xgboost` resolveu e instalou **326 MB** de
`nvidia-nccl-cu12` (biblioteca de comunicação multi-GPU) junto com o pacote, mesmo o
uso aqui sendo inteiramente em CPU — o wheel padrão do XGBoost para Linux traz essa
dependência de GPU mesmo quando não é usada. Isso inflaria a imagem Docker de forma
desproporcional ao ganho (que nem se confirmou nos resultados) e contradiz a leveza
exigida por R1. Removido (`uv remove xgboost`) antes de virar dívida técnica.

LightGBM (`lightgbm==4.7.0`, ~3,3 MB, sem dependência de GPU) suporta matriz esparsa
nativamente e foi o que de fato rodou a comparação. Fica registrado que a rejeição do
XGBoost é sobre a dependência instalada, não sobre a qualidade do modelo em si — se uma
necessidade futura justificar reavaliar XGBoost, existe a variante `xgboost-cpu` no
PyPI (sem CUDA) a considerar primeiro.

## Consequências

**Positivas**

- Decisão de modelo base fechada e documentada antes de investir em API/Docker (F3) —
  evita retrabalho de infraestrutura em torno de um candidato subótimo.
- Bateria reproduzida nesta sessão, em máquina diferente da que gerou os números
  publicados anteriormente: os 3 candidatos originais bateram os mesmos valores de
  F1-macro na precisão exibida — validação de reprodutibilidade do pipeline "de
  graça", sem esforço extra.
- Achado do Multinomial NB (menor sub-triagem do grupo) já registrado para reaproveitar
  em F6 (ADR-0005), sem precisar redescobrir depois.
- Nenhuma dependência pesada ou de GPU entrou no projeto — XGBoost foi testado e
  descartado antes de virar dívida técnica no `pyproject.toml`/imagem Docker.

**Negativas / dívidas aceitas**

- Classificador ordinal (`mord`) não foi de fato testado, só avaliado em tese — é
  hipótese registrada para F6, não fato validado; não pode ser citado como "testamos e
  X" até lá.
- `lightgbm` entra como dependência de produção permanente mesmo perdendo a comparação
  — aceito porque é leve (3,3 MB) e mantém a bateria de 6 candidatos reproduzível; se
  não for reaproveitado em F6, considerar removê-lo então.

## Como revisitar

Quando a matriz de custo assimétrica entrar em vigor (F6, ADR-0005) e sub-triagem
passar a ser o critério dominante de seleção (não só F1-macro), reabrir esta decisão e
comparar a Regressão Logística com limiar ajustado contra o Multinomial NB com limiar
ajustado — o NB pode virar vencedor sob uma política de custo explícita, mesmo perdendo
em F1-macro cru. Se isso acontecer, este ADR é supersedido, não editado.

## Atualização — caixa 6.1 (F6, 2026-09-15)

A dívida aceita "classificador ordinal (`mord`) não foi de fato testado, só avaliado
em tese" está fechada — não muda a decisão deste ADR (Regressão Logística segue como
classificador de produção), por isso não abre ADR novo, só fecha o item em aberto.

Testado (`mord.LogisticAT`) sobre a representação vencedora de caixa 6.1 (bigramas +
char n-gramas + marcação de negação): F1-macro 0,566, recall de `urgente` 0,554 —
pior resultado de toda a bateria de F6, inclusive abaixo do `DummyClassifier` de F2
em recall de `urgente`. Hipótese mais provável (não confirmada): regularização L2
padrão do `mord` (`alpha=1.0`) mal calibrada para as ~40 mil dimensões esparsas da
representação vencedora — não é evidência de que classificação ordinal não serve
para o problema, é evidência de que os hiperparâmetros padrão não servem nesta
representação de alta dimensão. Ver `docs/EXPERIMENTS.md`, seção F6, para a tabela
completa e a leitura dos 12 runs.
