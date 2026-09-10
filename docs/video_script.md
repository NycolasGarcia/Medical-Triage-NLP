# Roteiro do vídeo STAR (5 min)

Cinco minutos é curtíssimo: ~750 palavras faladas. Improvisar custa nota (R6, 15%).
Cronometrar em ensaio e cortar antes de gravar.

## Orçamento de tempo

| Bloco | Tempo | Conteúdo |
|---|---|---|
| Situation | 0:00–0:45 | Problema clínico: triagem lenta atrasa paciente crítico. Por que automatizar. |
| Task | 0:45–1:30 | Requisitos da fase: classificador NLP leve, API em container, CI/CD, Airflow, observabilidade, latência. |
| Action | 1:30–3:30 | Arquitetura, decisões (ADRs), custo FP/FN, otimização aplicada, como o monitoramento foi montado. |
| Result | 3:30–5:00 | Demo ao vivo: pipeline verde, dashboard com dados, números de latência antes/depois, lições aprendidas. |

## O que **mostrar** na tela (não só narrar)

1. CI verde no GitHub Actions.
2. DAG do Airflow com todas as tasks `success`.
3. `docker compose up` com os três serviços de pé.
4. Dashboard do Grafana **com dados** (rodar o load test antes de gravar).
5. Tabela de latência baseline vs. otimizado.

## Pontos que diferenciam (mencionar em Action/Result)

- Assimetria de custo: sub-triagem é o erro perigoso; a política de limiar foi
  enviesada para reduzi-la, com o trade-off medido.
- Limitação honesta: o rótulo de urgência é derivado (ADR-0001), não observado.
- Ganho de latência **medido** com protocolo (warm-up, N, percentis), não impressão.

## Erros comuns a evitar

- Gastar 2 min explicando o dataset e chegar em Result com 20 segundos.
- Mostrar código estático em vez do sistema rodando.
- Prometer validade clínica que o projeto não tem.

## Roteiro falado

### Situation (0:00–0:45)

<texto>

### Task (0:45–1:30)

<texto>

### Action (1:30–3:30)

<texto>

### Result (3:30–5:00)

<texto>
