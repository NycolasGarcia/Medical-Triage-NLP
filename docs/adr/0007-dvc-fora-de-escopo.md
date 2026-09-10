# ADR-0007 — DVC fora do escopo desta fase

- **Status:** supersedido por ADR-0009
- **Data:** 2026-09-08
- **Fase:** F0
- **Decisor:** Nycolas Garcia

## Contexto

DVC é herança recomendada de TC1/TC2 para versionamento de dataset, mas **não é
critério de nota no TC3** — diferente de MLflow (tracking + Model Registry), que
segue obrigatório. O projeto é individual, com oito fases planejadas e prazo
apertado; toda dependência adicional (aqui, um remote de armazenamento a manter e
sincronizar) compete por tempo com os critérios que de fato valem nota.

## Decisão

**Dispensar DVC nesta fase.** Rastreabilidade do dataset fica garantida por outros
meios já obrigatórios: seed fixa de split, `docs/data_card.md` com origem,
volume e hash do dataset processado, e MLflow registrando qual versão de dados
gerou cada run (parâmetro/tag do experimento).

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| DVC com remote local | Versionamento real de dados, `dvc.yaml` documenta o pipeline | Mais uma ferramenta a configurar, manter e explicar no vídeo, sem valer nota | Custo de setup não se paga no orçamento de tempo do projeto |
| DVC com remote em nuvem | Mesmo benefício + backup fora da máquina | Exige credenciais de storage externo, escopo que o TC3 explicitamente não pede | Adiciona superfície de configuração para um critério que não é avaliado |
| Hash do dataset processado registrado manualmente (decisão adotada) | Zero dependência nova; rastreabilidade suficiente para reprodutibilidade acadêmica | Não versiona binários de dados, só identifica qual versão foi usada | É o nível de rigor que o benefício (rastreabilidade) justifica aqui |

## Consequências

**Positivas**

- Nenhuma dependência, credencial ou remote adicional para manter durante o projeto.
- Tempo redirecionado para fases que valem nota, em especial F4/F5 (45% da rubrica).

**Negativas / dívidas aceitas**

- Sem DVC, não há diff versionado de arquivos de dados nem rollback automático
  para uma versão anterior do dataset — se o dataset mudar, a rastreabilidade
  depende de disciplina manual (hash + `data_card.md` atualizados no mesmo commit).

## Como revisitar

Se o dataset precisar de mais de uma versão significativa ao longo do projeto (ex.:
reprocessamento que muda distribuição de classes), ou se sobrar tempo real após F4/F5
fechadas, reabrir esta decisão com um novo ADR e introduzir DVC retroativamente.
