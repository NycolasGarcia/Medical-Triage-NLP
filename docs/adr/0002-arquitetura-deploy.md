# ADR-0002 — Arquitetura de deploy: batch vs. real-time

- **Status:** aceito
- **Data:** 2026-09-14
- **Fase:** F3
- **Decisor:** Nycolas Garcia

## Contexto

O TC3 (Etapa 1) exige analisar qual estratégia de deploy em nuvem seria ideal para o
cenário de triagem hospitalar — batch ou real-time — e documentar a análise no README.
Nesta fase **não há implementação em nuvem**: a entrega é a análise fundamentada e a
API local em container (já funcional, ver `docs/LATENCY.md`).

O cenário clínico impõe a restrição principal: triagem existe para reduzir tempo até
o atendimento. Latência de resposta compete diretamente com o valor do produto — um
laudo `urgente` que espera numa fila de processamento em lote perde exatamente o
propósito do sistema.

Evidência disponível para decidir, que não existia quando o ADR foi proposto: o
benchmark de F3 (`docs/LATENCY.md`) mede p50 de 2,65 ms e p95 de 3,11 ms para o
modelo servindo dentro do container, com `/health` em 1,66 ms. Real-time não é uma
aposta arriscada de latência — está medido e sobra folga enorme.

## Decisão

**Real-time, via serviço containerizado sempre ativo (não serverless/on-demand).**
A API (já implementada em F3: FastAPI + Uvicorn, modelo carregado no startup) recebe
o laudo e responde a classificação síncrona, na mesma requisição.

Nuvem-alvo teórica: **AWS**, usando **ECS/Fargate** atrás de um Application Load
Balancer, com auto scaling por número de requisições/CPU. Justificativa da escolha
de serviço (não é a única opção viável, mas é a mais coerente com o que já existe):

- O `Dockerfile` multi-stage já produzido em F3 é a unidade de deploy — ECS/Fargate
  consome imagem de container diretamente, sem reescrever a aplicação.
- **Lambda (serverless) foi descartado deliberadamente**, mesmo sendo mais barato em
  baixo volume: cold start de container Lambda (ainda mais com as dependências
  pesadas de ML do projeto — ver observação de tamanho de imagem em `LATENCY.md`)
  pode chegar a segundos, o que é inaceitável num fluxo que hoje responde em
  milissegundos. Um serviço "sempre ativo" preserva a latência medida; serverless
  trocaria uma vitória já conquistada por economia de custo em um cenário onde custo
  não é a restrição citada no enunciado — latência é.
- Modelo é servido a partir do artefato baked na imagem (mesma estratégia de F3). Uma
  evolução natural, fora do escopo desta fase, é o container buscar a versão
  `Production` do MLflow Registry no startup em vez de tê-la embutida — isso é
  decisão de F6/ADR-0008 (critério de promoção), não desta.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| Batch (job periódico) | Custo menor; throughput alto; simples de escalar horizontalmente | Laudo espera a próxima janela de processamento — inaceitável para `urgente`; não existe leitura de "urgência" que sobreviva a um atraso de minutos/horas por design | Contradiz o propósito central do sistema (triagem **rápida**); descartado sem ambiguidade |
| **Real-time via serviço containerizado (ECS/Fargate) — ESCOLHIDA** | Resposta imediata (medido: p95 3,11 ms); reaproveita o Dockerfile/API já prontos; auto scaling gerenciado; sem cold start relevante | Custo de disponibilidade contínua (instância sempre ativa, mesmo ocioso) | — (é a decisão) |
| Real-time via serverless (AWS Lambda + container image) | Custo por invocação, zero custo ocioso; escala a zero | Cold start de container com dependências de ML pesadas (~1 GB, ver `LATENCY.md`) pode levar segundos — destrói exatamente a garantia de latência que o projeto acabou de medir e validar | Risco de latência inaceitável no pior caso (primeira requisição após período ocioso), justo no cenário onde isso mais importa (urgência clínica) |
| Híbrido (real-time para triagem + reprocessamento em lote para auditoria/retreino) | Cobre a urgência com real-time e ainda aproveita lote para tarefas que toleram atraso (ex.: retreino, análise agregada) | Mais superfície operacional (duas trilhas de deploy) | Fora de escopo em F3 — mas **não descartado**: o retreino (F4, Airflow) já é essencialmente essa segunda trilha em lote, então o sistema como um todo **já é híbrido** na prática, só que a trilha de lote é para retreino, não para servir triagem |

## Consequências

**Positivas**

- Decisão de arquitetura de deploy fechada com evidência de latência real, não
  suposição — o portão do enunciado ("análise fundamentada") tem número por trás.
- Nenhuma mudança de código necessária para migrar do `docker run` local (F3) para
  ECS/Fargate: a unidade de deploy (imagem Docker) já é a mesma.
- A rejeição de serverless fica documentada com o motivo técnico específico (cold
  start vs. imagem pesada de ML), não como preferência genérica — reduz a chance de
  a decisão ser questionada sem contexto por um avaliador.

**Negativas / dívidas aceitas**

- Custo de infraestrutura sempre ativa é maior que serverless em cenários de baixo
  volume — aceito conscientemente, já que o enunciado não pede otimização de custo
  de nuvem, pede latência.
- A "nuvem-alvo teórica" é só análise textual — nada disso é implementado nesta fase
  nem em nenhuma outra do TC3 (§1 do CLAUDE.md: sem entrega de deploy em nuvem).
- O tamanho da imagem (1,03 GB, ver `LATENCY.md`) é o principal fator de risco desta
  decisão — imagens grandes pesam mais mesmo em serviço sempre ativo (tempo de
  deploy, transferência de rede). Reforça, e não enfraquece, a decisão de adiar a
  separação de dependências treino/serving para F6: o benefício se estende também a
  este cenário teórico de nuvem.

## Como revisitar

Se o volume de laudos ficar muito acima do previsto (justificando custo de
serverless com cold start amortizado), ou se o p95 de latência medido em produção
exceder o orçamento definido em `LATENCY.md`, ou se a imagem for enxugada o
suficiente (F6) para tornar cold start de Lambda desprezível — qualquer um desses
sinais reabre a comparação real-time vs. serverless.
