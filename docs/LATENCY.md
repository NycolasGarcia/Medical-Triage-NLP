# Latência — protocolo e resultados

Latência é critério de nota (R1, 20%) e o ganho precisa ser **demonstrado com
números**, não afirmado.

## Protocolo de medição (fixar antes da primeira medida)

| Parâmetro | Valor |
|---|---|
| Ambiente | dentro do container, `docker run` local |
| Hardware | <CPU, RAM> |
| Requisições de warm-up (descartadas) | 100 |
| Amostras medidas (N) | >= 1000 |
| Concorrência | <1 ou N> |
| Payload | amostra real do conjunto de teste, comprimento mediano |
| Percentis reportados | p50, p95, p99 |
| Repetições | 3 execuções; reportar mediana dos p95 |

Regras: nunca reportar média sozinha (esconde cauda); nunca comparar medições feitas
com máquina em estados diferentes; sempre declarar N e warm-up.

## Baseline (F3 — modelo original)

| Métrica | Valor |
|---|---|
| p50 (ms) | |
| p95 (ms) | |
| p99 (ms) | |
| Throughput (req/s) | |
| Tamanho do artefato (MB) | |

## Otimizado (F6 — <ONNX / quantização>)

| Métrica | Baseline | Otimizado | Variação |
|---|---|---|---|
| p50 (ms) | | | |
| p95 (ms) | | | |
| p99 (ms) | | | |
| Throughput (req/s) | | | |
| Tamanho do artefato (MB) | | | |

**Ganho reportado:** <X>% no p95.

## Paridade numérica

Teste `tests/test_onnx_parity.py`: predições do modelo otimizado iguais às do original
em `<N>` amostras, tolerância `<valor>`. Divergências encontradas: `<n>`.

## Onde o tempo é gasto

| Etapa | ms (p50) | % |
|---|---|---|
| Vetorização | | |
| Inferência | | |
| Serialização da resposta | | |

<Se a vetorização dominar, otimizar só o modelo rende pouco — registrar essa leitura.>
