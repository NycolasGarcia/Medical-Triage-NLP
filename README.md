# Medical Triage NLP

Sistema de triagem automática de urgência de laudos médicos em texto: um
classificador de texto (NLP) leve, servido via API REST em container, com pipeline
de CI/CD, orquestração de retreino e monitoramento — o foco do projeto é o ciclo de
vida do modelo em produção, não só o modelo em si.

## Contexto

Um hospital de referência precisa classificar a urgência de um laudo médico em três
faixas ordinais — `normal < atenção < urgente` — a partir do texto livre. O corpus
usado para treino (Medical Abstracts TC Corpus) não traz rótulo de urgência
clinicamente validado; a faixa é derivada por um mapeamento heurístico e didático
(ver `docs/adr/0001-mapeamento-classes-urgencia.md` e `docs/model_card.md`), não uma
recomendação clínica.

## Arquitetura de deploy

Decisão completa em `docs/adr/0002-arquitetura-deploy.md`; resumo:

**Real-time**, via serviço containerizado sempre ativo — não batch, não serverless.
Um laudo `urgente` que espera numa fila de processamento em lote perde o próprio
propósito do sistema, e a latência medida (p95 de 3,11 ms dentro do container, ver
`docs/LATENCY.md`) já comprova que real-time é viável sem custo de engenharia extra.

Nuvem-alvo teórica (análise textual, não implementada nesta fase): **AWS ECS/Fargate**
atrás de um Application Load Balancer. Serverless (Lambda) foi avaliado e descartado
deliberadamente — não por preferência genérica, mas porque o cold start de um
container com as dependências de ML do projeto (imagem de ~1 GB) pode levar segundos,
destruindo exatamente a garantia de latência que o projeto mede e valida.

Diagramas de fluxo de inferência e de treino: `docs/ARCHITECTURE.md`.

## Status do projeto

Em desenvolvimento incremental por fases (F0–F7); progresso, checkpoints e evidências
em `docs/PROGRESS.md`. Setup, execução e resultados finais de latência entram no
README à medida que as fases avançam — a versão completa é entregável de F7.
