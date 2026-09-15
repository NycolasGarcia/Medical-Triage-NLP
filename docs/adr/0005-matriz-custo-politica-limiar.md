# ADR-0005 — Matriz de custo e política de limiar

- **Status:** aceito
- **Data:** 2026-09-15
- **Fase:** F6
- **Decisor:** Nycolas Garcia

## Contexto

§7 do CLAUDE.md trata os dois erros de triagem como qualitativamente diferentes:
**sub-triagem** (`urgente` classificado como `atenção`/`normal`) é o erro perigoso —
atraso no atendimento a paciente crítico; **sobre-triagem** (`normal` classificado
como `atenção`/`urgente`) é caro (tempo de equipe), mas seguro. Um classificador
otimizado só para F1-macro/accuracy trata os dois erros como equivalentes, o que é
errado para este domínio.

Duas decisões numéricas ficaram em aberto desde o planejamento (§14) e foram
fechadas com o autor em 2026-09-15, antes desta caixa:

1. **Matriz de custo**: sub-triagem de 1 nível = 5, de 2 níveis = 15; sobre-triagem
   de 1 nível = 1, de 2 níveis = 2. Mantida a proposta original após pesquisa de
   precedente (padrão ACS-COT de triagem de trauma: sub-triagem < 5%, sobre-triagem
   tolerada 25–50% — confirma que custo escalado pela distância ordinal é padrão de
   literatura).
2. **Alvo de recall de `urgente`**: 0,90 — entre o baseline do ESI humano (≈0,893) e
   o padrão ACS-COT de trauma puro (≥0,95).

Faltava transformar essas duas decisões em código: uma regra de decisão real que a
API usa, não só um número em documentação.

## Decisão

A API usa uma **regra de limiar cumulativo**, não argmax puro, sobre as
probabilidades calibradas (isotônica, caixa 6.2, ADR implícito em
`docs/EXPERIMENTS.md`): prediz `urgente` se `P(urgente) ≥ 0,31`; senão prediz
`atenção` se `P(atenção) + P(urgente) ≥ 0,09`; senão `normal`. Implementado em
`src/models/threshold.py` (`select_label`), usado por `src/api/main.py` no lugar do
`max(probabilities)` anterior.

Os dois limiares vêm de uma busca em duas etapas (`src/models/threshold_search.py`),
sobre probabilidades calibradas *out-of-fold* de 5 dobras (nunca as mesmas amostras
usadas para ajustar representação/calibração — sem vazamento):

1. `THRESHOLD_URGENTE`: maior valor que ainda cumpre `recall_urgente ≥ 0,90`
   (minimiza sobre-triagem desnecessária entre os candidatos que cumprem a meta).
2. `THRESHOLD_ATENCAO`: com o primeiro já fixado, o valor que minimiza o custo médio
   da matriz de custo (`src/models/cost.py`) — não é escolhido para otimizar uma
   métrica de qualidade, é escolhido para minimizar custo real do domínio.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| Argmax puro (limiar implícito de 1/3 por classe) | Simples, já era o comportamento da API até 6.4 | Trata sub- e sobre-triagem como equivalentes — exatamente o que §7 diz que está errado neste domínio | Descartada: é o baseline contra o qual a política de limiar é comparada, não uma opção real |
| Regra de decisão bayesiana de custo mínimo (escolher a classe que minimiza custo esperado dado `P(classe)` e a matriz inteira) | Mais "correta" teoricamente — usa a matriz de custo completa em vez de só dois limiares escalares | Menos legível como "limiar por classe" (o que a caixa 6.4 pede explicitamente); mais difícil de explicar/auditar no vídeo e no Model Card | Preterida em favor da regra de limiar cumulativo, mais simples de justificar e já suficiente para bater a meta de recall com folga de custo |
| Grade 2D completa (`THRESHOLD_URGENTE` × `THRESHOLD_ATENCAO` simultâneos) | Garantidamente ótimo global, sem o viés de uma busca em duas etapas | ~55×90 combinações vs. ~55+90 da busca em duas etapas; `THRESHOLD_URGENTE` não depende de `THRESHOLD_ATENCAO` (decide sozinho quem vira `urgente`), então a busca em duas etapas já encontra o mesmo ótimo para o primeiro limiar, só não garante o ótimo conjunto | Custo computacional maior sem ganho de qualidade esperado, dada a independência do primeiro limiar |

## Consequências

**Positivas**

- Meta de recall de `urgente` atingida: 0,9026 (CV, out-of-fold pooled, 8.980
  amostras) — acima do alvo de 0,90. No teste reservado (2.245 amostras, nunca
  tocado na busca): 0,8803 — abaixo do CV por variância amostral de um conjunto
  menor, não contradição; registrado com transparência, não escondido.
- Custo médio caiu quase pela metade: 1,1747 (argmax) → 0,6449 (CV) / 1,290 → 0,672
  (teste reservado) — **-45% a -48%**, medido nos dois conjuntos.
- Sub-triagem caiu de 9,3% para 3,4% (CV) / de 10,3% para 4,3% (teste reservado).

**Negativas / dívidas aceitas**

- Sobre-triagem quase dobrou: 17,1% → 33,4% (CV) / 15,9% → 32,6% (teste reservado).
  Aceito deliberadamente — é o "erro caro, mas seguro" que §7 permite trocar por
  menos sub-triagem.
- Acurácia bruta (acerto exato) caiu de 73,6% para 63,1% (CV). Não é o critério de
  otimização desta política — F1-macro/accuracy já foram os critérios de 6.1; a
  partir de 6.2/6.4 o critério é custo explícito, que é o que a rubrica (R1) e o
  domínio clínico pedem.
- `THRESHOLD_ATENCAO = 0,09` é baixo — quase qualquer sinal de `atenção` ou
  `urgente` já tira a predição de `normal`. É o que a busca encontrou como
  ótimo de custo, não um valor arbitrário, mas vale registrar como possível alvo de
  reavaliação se a leitura qualitativa de erros (caixa 6.5) mostrar volume
  desproporcional de sobre-triagem sem padrão claro.
- **Achado mais forte desta caixa, não previsto antes de rodar**: o recall da
  classe `normal` desaba de 0,5449 (argmax) para **0,0435** no teste reservado — o
  modelo praticamente para de prever `normal` (31 de 712 casos reais de `normal`).
  Matematicamente correto dado o custo assimétrico (sub-triagem normal→atenção custa
  só 1, sub-triagem atenção/urgente→normal custa 5-15 — o ótimo de custo empurra
  quase tudo para pelo menos `atenção`), mas é uma mudança de caráter do sistema,
  não só um número: ele deixa de ser um classificador 3-vias equilibrado e vira, na
  prática, um filtro "isto claramente NÃO é normal?". Se isso for operacionalmente
  inviável (equipe sobrecarregada de falsos `atenção`), o ajuste correto é reabrir a
  matriz de custo (tornar sub-triagem normal→atenção mais barata ainda, ou
  sobre-triagem mais cara), não o código do limiar. Prioridade alta para a leitura
  qualitativa de erros da caixa 6.5.

## Como revisitar

Reabrir se: a leitura qualitativa de erros (caixa 6.5) mostrar um padrão sistemático
de sobre-triagem que pareça ruído em vez de custo aceitável; o dataset mudar
(§0.1, migração para rótulo de urgência real); ou o autor decidir que 33% de
sobre-triagem é operacionalmente inviável mesmo sendo o ótimo de custo sob os pesos
atuais — nesse caso, o ajuste correto é a matriz de custo (§14), não o código do
limiar, já que o limiar só implementa fielmente o que a matriz pede.
