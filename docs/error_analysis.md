# Análise qualitativa de erros

> Caixa 6.5 (§7: "ler os laudos errados e achar o padrão"). Base: predições do
> pipeline de produção (representação 6.1 + calibração isotônica 6.2 + limiar
> cumulativo 6.4, `THRESHOLD_URGENTE=0,31`/`THRESHOLD_ATENCAO=0,09`) no **teste
> reservado** (2.245 amostras, nunca tocado em nenhuma busca de F2/F6).

## Matriz de confusão (contagem absoluta)

| Real \\ Previsto | normal | atenção | urgente |
|---|---|---|---|
| **normal** (712) | 31 | 435 | 246 |
| **atenção** (748) | 2 | 695 | 51 |
| **urgente** (785) | 5 | 89 | 691 |

Por distância ordinal do erro:

| Distância | Significado | N |
|---|---|---|
| -2 | sub-triagem de 2 níveis (`urgente`→`normal`) — o pior erro possível | **5** |
| -1 | sub-triagem de 1 nível | 91 |
| +1 | sobre-triagem de 1 nível | 486 |
| +2 | sobre-triagem de 2 níveis (`normal`→`urgente`) | 246 |

## Padrão dominante: o mapeamento heurístico, não o modelo

Lendo os textos das duas maiores classes de erro (`normal`→`urgente`, 246 casos, e
`urgente`→`atenção`/`normal`, 94 casos), o padrão é consistente e não é sutil: o
corpus original classifica por **assunto do artigo** (neoplasias, cardiovascular,
digestivo, sistema nervoso, "condições patológicas gerais"), não por **urgência do
caso descrito** — e ADR-0001 mapeia essa categoria de assunto para urgência
(cardiovascular/nervoso → `urgente`). Essas duas coisas divergem sistematicamente:

**`normal`→`urgente` (246 casos)**: majoritariamente artigos de pesquisa básica ou
metodologia — sobre mecanismo fisiológico, técnica de imagem, ou série de casos —
que usam vocabulário clinicamente alarmante mesmo tratando de um tema classificado
como "condição patológica geral" (logo `normal` no mapeamento). Exemplos reais do
teste: *"Role of calcium... in the initiation and maintenance of **ventricular
fibrillation**"*, *"**Rupture** of thoracic aorta caused by blunt trauma... Shock
Trauma [Center]"*, *"Effects of endotracheal suctioning... in **critically ill**
adults"*. O modelo lê "ventricular fibrillation", "rupture", "shock", "critically
ill" e reage corretamente ao léxico — o rótulo de referência é que classifica esses
artigos como `normal` por não caírem na categoria "cardiovascular" original do
corpus, não porque o conteúdo seja calmo.

**`urgente`→`atenção`/`normal` (94 casos, inclusive os 5 piores erros de 2
níveis)**: o inverso — artigos de epidemiologia, metodologia ou acompanhamento
rotineiro que *são* categorizados como cardiovascular/nervoso (logo `urgente` no
mapeamento), mas cujo texto é administrativo/descritivo, sem urgência aparente.
Exemplos reais: *"Outcome of pregnancies experienced during residency"* (estudo de
cohort sobre residência médica, não sobre um caso urgente), *"The efficacy of
suction drains after **routine** total joint arthroplasty"*, *"Etiology and
pathophysiology of pyelonephritis"* (revisão de mecanismo, não caso agudo). Aqui o
modelo também está lendo o texto corretamente — só que o texto de um artigo de
metodologia sobre um tema cardiovascular não soa urgente, e não deveria soar.

**Leitura**: boa parte do que a matriz de confusão chama de "erro" é, na prática,
o **teto de qualidade do mapeamento heurístico de ADR-0001** sendo alcançado, não
uma falha de representação/calibração/limiar. Já era a limitação documentada desde
F1 ("mapeamento heurístico e didático, não validado clinicamente") — esta caixa
mostra *concretamente* como e onde essa limitação aparece, algo que só a leitura
dos textos revela, não as métricas agregadas.

## Hipóteses descartadas

- **Tamanho do texto**: sem diferença relevante entre acertos e erros (média de
  1.247 caracteres nos acertos vs. 1.198 nos erros) — texto curto não é fator.
- **Negação mal tratada**: checagem grosseira (presença de "no"/"not"/"without" etc.
  em qualquer parte do texto) apareceu em 51/94 dos erros de sub-triagem residual —
  não é evidência de causa, é só a taxa-base de essas palavras comuns aparecerem em
  qualquer abstract de +1.000 caracteres. A evidência real sobre negação é a
  comparação controlada em CV da caixa 6.1 (marcação de negação melhorou o F1-macro
  quando combinada a char n-gramas) — esta análise qualitativa não contradiz aquilo.

## O que isto implica para a decisão pendente (recall de `normal` = 0,04)

O achado de ADR-0005 (recall de `normal` caiu de 0,54 para 0,04 com o limiar
tunado) tem **duas causas empilhadas**, não uma só:

1. A assimetria da matriz de custo (5-15 vs. 1-2) empurra o limiar de decisão para
   raramente prever `normal` — efeito **do limiar**, reversível ajustando a matriz.
2. Uma fração real dos textos rotulados `normal` (artigos de pesquisa básica sobre
   temas graves, ver acima) **contém vocabulário genuinamente alarmante** — efeito
   **do mapeamento de rótulo**, não reversível ajustando o limiar.

Reabrir a matriz de custo (tornar sub-triagem `normal`→`atenção` mais barata, ou
sobre-triagem mais cara) reduziria a contagem de sobre-triagem e provavelmente
recuperaria parte do recall de `normal` — mas **não elimina** a categoria de erro
descrita acima, porque essa categoria não é sobre o limiar, é sobre o texto
realmente conter linguagem de alta severidade. Ajustar a matriz atacaria o sintoma
mensurável (recall de `normal` baixo), não a causa (rótulo de referência que não
reflete urgência real do texto em ~10% dos casos, pela leitura desta amostra).

## Recomendação

Não é chamada desta caixa decidir a matriz de custo (isso é o autor, registrado em
§14/ADR-0005) — mas a evidência aqui aponta que **qualquer novo valor de matriz
ainda vai esbarrar neste teto de ~10% de casos com vocabulário incoerente com o
rótulo heurístico**. Se o objetivo for reduzir sobre-triagem sem abrir mão do
recall de `urgente`, o ganho maior não está em re-tunar o limiar, e sim em uma
melhoria de rótulo (fora do escopo de F6: exigiria revisar ADR-0001 ou trocar de
dataset por um com urgência real, ambos fora do prazo do projeto) — ou aceitar o
teto como limitação documentada do projeto acadêmico, registrada no Model Card
(F7).
