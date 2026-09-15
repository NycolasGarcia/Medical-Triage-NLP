# ADR-0008 — Estratégia de retreino e critério de promoção do modelo

- **Status:** supersedido por ADR-0010 (critério de promoção; estratégia geral de
  gate humano continua vigente)
- **Data:** 2026-09-14
- **Fase:** F4
- **Decisor:** Nycolas Garcia

## Contexto

A DAG `retrain_triage_model` (F4, caixa 4.5) já treina, avalia no teste reservado e
**registra** uma nova versão no MLflow Model Registry a cada execução — mas não
decide sozinha se essa versão deveria assumir produção. Sem um critério objetivo, a
promoção vira "só uso a versão mais recente porque é a mais recente", que é
exatamente o tipo de decisão sem lastro que o projeto vem evitando (§0.1 do
CLAUDE.md).

Restrição real desta fase: a matriz de custo assimétrica formal (sub-triagem vs.
sobre-triagem com pesos numéricos) é trabalho de F6/ADR-0005, ainda não existe. Um
critério de promoção **não pode fingir** que essa matriz já existe — mas também não
pode ficar sem critério nenhum até F6, senão a DAG de retreino registra versões que
ninguém nunca vai promover, o que esvazia o propósito de retreinar.

## Decisão

**Promoção não automática nesta fase — gate humano com critério objetivo
documentado, não promoção livre nem promoção cega.**

A task `register` da DAG calcula e loga se a versão nova **atinge o piso mínimo**
(não decide promover sozinha):

- `f1_macro` no teste reservado ≥ `min_f1_macro` (parâmetro da DAG, default **0,70**
  — referência: campeão atual mede 0,728 em teste reservado, Dummy mede 0,339; o piso
  dá margem contra ruído de retreino sem travar em uma casa decimal).
- Sem regressão de sub-triagem acima de `max_sub_triagem_increase` (parâmetro,
  default **+3 pontos percentuais**) frente à versão atualmente em produção.

Se os dois critérios passam, a versão fica marcada `elegivel_promocao: true` no log
da task e numa tag do run MLflow — a promoção de fato (mudar o alias `@production`
no Registry) continua **manual**, decisão do autor, até a matriz de custo de F6
existir para automatizar com confiança.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| Promoção automática sempre que uma versão nova treina | Zero fricção operacional | Sem matriz de custo formal, "melhor F1" pode esconder piora de sub-triagem (o erro que mais importa, §7) — promoveria modelo pior por métrica errada | Arriscado demais para domínio de triagem hospitalar antes de F6 existir |
| Promoção manual sem critério objetivo | Simples de implementar (não implementa nada) | Não é verificável nem reproduzível — vira "confiar no autor", exatamente o oposto do que os portões numéricos do projeto (§10.4) tentam evitar | Contradiz a disciplina de checkpoint com evidência já estabelecida no projeto |
| **Gate humano com critério objetivo (piso de F1 + não-regressão de sub-triagem) — ESCOLHIDA** | Promoção continua decisão humana (seguro), mas a decisão tem número por trás, não "achismo"; parâmetros configuráveis por execução da DAG, sem editar código | Piso de 0,70 é `PROPOSTO` (minha construção, não do enunciado) — pode se mostrar errado e precisar ajuste | Melhor equilíbrio disponível nesta fase entre segurança e verificabilidade |
| Promoção automática só depois de ADR-0005 (matriz de custo) existir | Evita construir critério provisório que pode ser descartado | Deixa a DAG de retreino sem propósito prático até F6 — registra versões que nunca viram nada | Adiar até F6 é pior que ter um piso provisório documentado como tal |

## Consequências

**Positivas**

- A DAG de retreino agora tem um sinal acionável (`elegivel_promocao`), não só um
  registro passivo de versão — cada execução responde "essa versão presta pra
  virar produção?", não só "treinei de novo".
- Critério parametrizado (`min_f1_macro`, `max_sub_triagem_increase`) via `Param` da
  DAG — ajustável por execução (ex.: relaxar o piso numa run de teste) sem tocar
  código, e documentado num único lugar em vez de espalhado em comentário.
- Base pronta para a promoção **automática** de F6, quando a matriz de custo de
  ADR-0005 existir: trocar o piso de F1-macro isolado pelo custo total ponderado é
  mudança localizada nesta mesma task, não redesenho.

**Negativas / dívidas aceitas**

- O piso de 0,70 é heurístico, não derivado de nenhuma análise de custo — aceito
  conscientemente como `PROPOSTO`, sujeito a revisão sem cerimônia.
- Promoção continua manual — não fecha sozinha o HR-4.2/portão de "DAG que
  produz artefato de modelo pronto pra uso" no sentido mais forte (versão em
  produção automaticamente); fecha no sentido documentado: artefato registrado e
  avaliado, decisão de produção é do autor.

## Como revisitar

Quando ADR-0005 (matriz de custo assimétrica, F6) for aceito: substituir o piso de
F1-macro isolado pelo custo total ponderado (sub-triagem × peso alto + sobre-triagem
× peso baixo) como critério de `elegivel_promocao`, e decidir se a promoção passa a
ser automática quando o critério é atingido — este ADR fica supersedido nesse
momento, não editado.
