# docs/ — índice

Ponto de entrada da documentação. Toda leitura de contexto do projeto passa por
aqui. Se um documento novo for criado, adicionar à tabela.

| Arquivo | O que é | Atualizar quando |
|---|---|---|
| `PROGRESS.md` | Log append-only de checkpoints por fase | Abertura e fechamento de toda fase |
| `ARCHITECTURE.md` | Componentes, portas, fluxos de request e de treino | Componente entra ou sai |
| `adr/` | Decisões arquiteturais (contexto, alternativas, consequências) | Nova decisão cara de reverter |
| `data_card.md` | Origem, volume, distribuição e limitações do dataset | Dataset ou mapeamento muda |
| `EXPERIMENTS.md` | Tabela comparativa legível dos runs do MLflow | Novo modelo relevante |
| `LATENCY.md` | Protocolo de benchmark e resultados antes/depois | Cada medição |
| `error_analysis.md` | Análise qualitativa dos erros do modelo | Cada rodada de erro |
| `RUNBOOK.md` | Como subir e operar a stack local | Comando muda |
| `model_card.md` | Performance, limitações, vieses, uso pretendido | Antes da entrega |
| `video_script.md` | Roteiro STAR cronometrado | Até gravar |

Evidências (prints de dashboard, logs de DAG) vão em `docs/evidence/`.
