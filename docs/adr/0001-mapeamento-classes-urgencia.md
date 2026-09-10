# ADR-0001 — Mapeamento de classes do corpus para faixas de urgência

- **Status:** aceito
- **Data:** AAAA-MM-DD
- **Fase:** F1
- **Decisor:** Nycolas Garcia

## Contexto

O enunciado do TC3 pede classificação de urgência (`normal` / `atenção` / `urgente`)
de laudos médicos. O dataset escolhido — Medical Abstracts TC Corpus (Kaggle) — **não
contém rótulo de urgência**: rotula por sistema/condição (neoplasias, doenças
digestivas, do sistema nervoso, cardiovasculares, condições patológicas gerais).

É preciso derivar o alvo de urgência a partir das classes existentes, sem fingir que
o resultado tem validade clínica.

## Decisão

**Aprovado pelo autor em 2026-09-08**, condicionado à reconfirmação das classes
reais do corpus. **Condição satisfeita em 2026-09-09** (caixa 1.0, NV-1/NV-2/NV-3):
as 5 classes e a ausência de coluna de urgência foram confirmadas com os CSVs
reais — a tabela abaixo se aplica sem alteração.

| Classe original | Faixa de urgência | Justificativa |
|---|---|---|
| Cardiovascular | `urgente` | Infarto, AVC — tempo-crítico clássico |
| Sistema nervoso | `urgente` | AVC, convulsão, meningite — tempo-crítico |
| Neoplasias | `atenção` | Sério, mas raramente emergência do mesmo dia — janela de investigação/tratamento |
| Doenças digestivas | `atenção` | Varia de leve a abdome agudo; em média menos tempo-crítico que cardíaco/neuro |
| Condições patológicas gerais | `normal` | Categoria geral/catch-all, presumivelmente mais rotineira |

O mapeamento é **heurístico e didático**, criado para viabilizar o exercício
acadêmico. Não é validado clinicamente e não deve ser usado como referência médica.
Esta ressalva é replicada no `data_card.md`, no `model_card.md` e no README.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| Buscar dataset com urgência real (ex. triagem de PS anotada) | Validade do alvo | Escassez de dataset público; risco de prazo | |
| MIMIC-III | Realismo clínico | Exige credenciamento PhysioNet/CITI; tempo | Descartado com o autor |
| Rotulação manual de amostra | Alvo mais defensável | Custo de tempo alto; sem expertise clínica | |
| Mapeamento heurístico documentado | Viável no prazo; transparente | Alvo é proxy, não urgência real | **Escolhida**, com ressalva explícita |

## Consequências

**Positivas**

- Viabiliza o pipeline completo dentro do prazo da fase.
- A limitação declarada demonstra maturidade — é conteúdo de Model Card, não defeito escondido.

**Negativas / dívidas aceitas**

- As métricas medem aderência ao mapeamento, não urgência clínica real.
- Qualquer leitura de "performance clínica" seria enganosa e deve ser evitada no vídeo e no README.

## Como revisitar

Se surgir dataset com rótulo de urgência real, o contrato (`text` + `urgency_label`)
já é compatível: troca-se a fonte e refaz-se F1–F2.
