# ADR-0009 — DVC dentro do escopo (supersede ADR-0007)

- **Status:** aceito
- **Data:** 2026-09-08
- **Fase:** F0
- **Decisor:** Nycolas Garcia

## Contexto

ADR-0007 havia dispensado DVC por não ser critério de nota no TC3. O autor
reverteu essa decisão: o pipeline entregue ao usuário/avaliador precisa cobrir
**do download/setup do dataset até o resultado final**, de ponta a ponta e de
forma reproduzível — não só o treino do modelo. Rastreabilidade de dados por
hash manual (a alternativa escolhida em ADR-0007) cobre "qual versão foi usada",
mas não cobre "como reproduzir os dados a partir do zero" com o mesmo rigor que
um pipeline declarado em `dvc.yaml` (estágios `download` → `preprocess` →
`split`), que é executável com um único comando e documenta as dependências
entre estágios.

## Decisão

**Adotar DVC** para versionar o dataset (bruto e processado) e declarar como
pipeline (`dvc.yaml`) os estágios de dados que antecedem o treino. Remote de
armazenamento **local** (diretório fora do repositório, referenciado em
`.dvc/config`) — sem credencial de nuvem, mantendo o escopo de infraestrutura
alinhado ao que o TC3 realmente pede: sem deploy em nuvem nesta fase.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| Hash manual (ADR-0007, revertida) | Zero dependência nova | Não reproduz os dados a partir do zero com um comando; depende de disciplina manual | Não atende ao requisito de pipeline completo agora explícito |
| DVC com remote em nuvem | Backup fora da máquina | Exige credencial de storage externo — fora do escopo de infraestrutura do TC3 | Sem necessidade real: o projeto não tem deploy em nuvem para justificar a credencial |
| DVC com remote local (decisão adotada) | Pipeline declarado e reproduzível, sem credencial externa | Sem backup fora da máquina do autor | Nível certo de rigor para o requisito, sem adicionar superfície de infraestrutura que o TC3 não pede |

## Consequências

**Positivas**

- Pipeline de dados reproduzível com um comando (`dvc repro`), do dataset bruto
  ao dataset processado que alimenta o treino.
- Estágios (`download`, `preprocess`, `split`) documentam explicitamente as
  dependências entre etapas — mais forte do que o hash manual de ADR-0007.

**Negativas / dívidas aceitas**

- Mais uma ferramenta para configurar, manter e explicar no vídeo.
- Setup real (`dvc init`, `dvc.yaml` com os estágios) só é possível quando o
  loader do dataset existir (F1, caixa 1.1) — aqui em F0 apenas a dependência é
  adicionada e `dvc init` é executado.

## Como revisitar

Se o remote local se mostrar insuficiente (ex.: trabalhar de mais de uma
máquina), migrar para um remote em nuvem é uma mudança de configuração, não de
ferramenta — não precisa de novo ADR, só de registro no `RUNBOOK.md`.
