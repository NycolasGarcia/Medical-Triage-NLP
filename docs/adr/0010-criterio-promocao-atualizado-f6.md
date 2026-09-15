# ADR-0010 — Critério de promoção atualizado (recall + custo, não F1-macro)

- **Status:** aceito
- **Data:** 2026-09-15
- **Fase:** F6
- **Decisor:** Nycolas Garcia

## Contexto

ADR-0008 (F4) já previa este momento explicitamente: "Quando ADR-0005 (matriz de
custo assimétrica, F6) for aceito: substituir o piso de F1-macro isolado pelo
custo total ponderado... este ADR fica supersedido nesse momento, não editado."
ADR-0005 foi aceito na caixa 6.4 — este ADR cumpre o que aquele já prometia.

Motivo prático, não só cumprimento de promessa: o piso de `min_f1_macro=0,70` de
ADR-0008 **bloquearia o próprio modelo que ADR-0005 decidiu servir**. A política de
limiar de caixa 6.4 troca F1-macro por recall de `urgente`/custo de propósito
(§7) — o modelo de produção mede F1-macro 0,523 no teste reservado (era 0,728
antes do limiar tunado), abaixo do piso antigo. Promover com o critério antigo
teria barrado a decisão que o projeto acabou de tomar deliberadamente em ADR-0005.

## Decisão

Critério de `elegivel_promocao` (task `register` da DAG,
`src/models/promotion.py`) passa de **F1-macro + sub-triagem** para **recall de
`urgente` + custo médio**:

- `recall_urgente` no teste reservado ≥ `min_recall_urgente` (parâmetro da DAG,
  default **0,85** — abaixo do alvo de CV de 0,90/ADR-0005, mas o teste reservado é
  4x menor que o conjunto de CV, com variância amostral esperada — medição real
  deu 0,8803; piso com folga, não a mesma casa decimal do alvo).
- Sem regressão de custo médio acima de `max_cost_increase` (parâmetro, default
  **+0,10**) frente à versão atualmente em produção (`mean_cost`, matriz de §7,
  `src/models/cost.py`).

Estratégia geral de ADR-0008 (gate humano, não promoção automática; task
`register` calcula e loga elegibilidade, mudar o alias `@production` continua
decisão do autor) **não muda** — só o critério numérico. Por isso este ADR
supersede especificamente a seção de critério de ADR-0008, não o documento
inteiro; a decisão de manter a promoção manual permanece válida e não é
reafirmada aqui por já estar registrada lá.

Achado colateral ao implementar: `src/models/evaluate.py::evaluate_pipeline`
(usada pela task `evaluate` da DAG) media as métricas com `pipeline.predict()`
(argmax puro) — **não** com a regra de limiar cumulativo que a API de produção
de fato usa (`select_label`, caixa 6.4). Corrigido para usar `select_label`, senão
a DAG avaliaria e decidiria elegibilidade com uma política diferente da servida.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| Manter o piso de F1-macro, só relaxar o valor (ex.: 0,50) | Muda menos código | F1-macro não é mais a métrica que o projeto otimiza desde 6.3/6.4 — manteria um critério desalinhado do que a matriz de custo de fato pede, só com um número diferente | Resolveria o sintoma (modelo bloqueado), não a causa (métrica errada) |
| Custo total ponderado (soma), não custo médio | Já cotado em ADR-0008 como opção | Depende do N de amostras — não comparável entre execuções com tamanhos de teste diferentes (ex. se o dataset crescer) | `mean_cost` (já usado em toda a caixa 6.3/6.4) é comparável entre execuções por construção |
| Promoção automática (sem gate humano) agora que a matriz de custo existe | ADR-0008 cotava isso como possível "quando ADR-0005 existir" | Domínio de triagem hospitalar — trocar o modelo em produção sem revisão humana é risco desproporcional ao ganho de conveniência, mesmo com critério objetivo | Critério objetivo não elimina a necessidade de julgamento humano antes de um modelo clínico entrar em produção |

## Consequências

**Positivas**

- Critério de promoção alinhado com o que o projeto de fato otimiza desde 6.3/6.4
  — não bloqueia mais o próprio modelo que ADR-0005 decidiu servir.
- Achado da task `evaluate` usando argmax em vez do limiar real corrigido —
  `elegivel_promocao` agora reflete a política de decisão realmente servida.
- Parâmetros da DAG (`min_recall_urgente`, `max_cost_increase`) continuam
  ajustáveis por execução, sem tocar código — mesma ergonomia de ADR-0008.

**Negativas / dívidas aceitas**

- `min_recall_urgente=0,85` é `PROPOSTO` (minha escolha, com a folga justificada
  acima) — não uma re-derivação formal, sujeito a revisão sem cerimônia.
- Testes antigos de `tests/test_promotion.py` reescritos para a nova assinatura —
  não há mais cobertura direta do critério antigo (aceitável, o critério antigo
  está descontinuado, não é código morto para manter testado).

## Como revisitar

Reabrir se: a matriz de custo de ADR-0005 mudar (§14) — o `mean_cost` usado aqui
deriva diretamente dela; ou se o autor decidir automatizar a promoção — a
mudança seria localizada na task `register` (trocar o log de elegibilidade pela
troca de fato do alias), não redesenho deste critério.
