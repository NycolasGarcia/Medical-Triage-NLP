# ADR-0002 — Arquitetura de deploy: batch vs. real-time

- **Status:** proposto
- **Data:** AAAA-MM-DD
- **Fase:** F3
- **Decisor:** Nycolas Garcia

## Contexto

O TC3 (Etapa 1) exige analisar qual estratégia de deploy em nuvem seria ideal para o
cenário de triagem hospitalar — batch ou real-time — e documentar a análise no README.
Nesta fase **não há implementação em nuvem**: a entrega é a análise fundamentada e a
API local em container.

O cenário clínico impõe a restrição principal: triagem existe para reduzir tempo até
o atendimento. Latência de resposta compete diretamente com o valor do produto.

## Decisão

<Preencher em F3: real-time via serviço containerizado, ou híbrido, e nuvem-alvo teórica.>

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| Batch (job periódico) | Custo menor; throughput alto | Laudo espera a próxima janela — inaceitável para urgência | |
| Real-time (API sob demanda) | Resposta imediata; encaixa no fluxo de triagem | Custo de disponibilidade contínua | |
| Híbrido (real-time + reprocessamento em lote) | Cobre urgência e reprocessa histórico | Mais superfície operacional | |

## Consequências

**Positivas**

-

**Negativas / dívidas aceitas**

-

## Como revisitar

Se o volume de laudos ficar muito acima do previsto, ou se o p95 de latência exceder
o orçamento definido em `LATENCY.md`.
