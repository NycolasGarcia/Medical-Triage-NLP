# ADR-0006 — Gestor de dependências: uv

- **Status:** aceito
- **Data:** 2026-09-08
- **Fase:** F0
- **Decisor:** Nycolas Garcia

## Contexto

O projeto precisa de um gestor de dependências Python com `pyproject.toml` como
fonte única de verdade, separação clara entre dependências de produção e de
desenvolvimento, e lock file determinístico e commitado (herança de TC1/TC2).
O enunciado do TC3 não exige uma ferramenta específica.

## Decisão

Usar **uv** como gestor de dependências e de ambiente virtual do projeto.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| Poetry | Maduro, amplamente adotado, `pyproject.toml` + lock nativo | Resolvedor de dependências sensivelmente mais lento; instalação de ambiente mais lenta em CI | uv resolve e instala em uma fração do tempo, o que importa em pipeline de CI/CD (F4, 30% da rubrica) e em iteração local |
| pip + pip-tools | Simples, sem ferramenta extra além do ecossistema padrão | Não gera lock determinístico por padrão sem configuração adicional; sem gestão nativa de grupos de dependências | Exige mais peças coordenadas manualmente para o mesmo resultado que uv entrega de fábrica |
| Conda/Mamba | Bom para dependências binárias pesadas (ex. científicas) | Ambiente mais pesado; lock menos portável entre SO; não é o padrão do ecossistema FastAPI/Airflow | Nenhuma dependência do projeto exige binários fora do PyPI |

## Consequências

**Positivas**

- Lock determinístico (`uv.lock`) commitado, resolução rápida e reprodutível.
- Grupos de dependências nativos (`[dependency-groups]`) separam prod/dev sem
  ferramentas adicionais.
- `uv run` remove a necessidade de ativar venv manualmente em scripts/Makefile.

**Negativas / dívidas aceitas**

- uv é uma ferramenta mais nova que Poetry; ecossistema de tutoriais/Stack Overflow
  é menor caso surja um problema incomum.
- O binário `uv` precisou ser instalado manualmente neste ambiente (não vinha
  pré-instalado) — documentado em `docs/RUNBOOK.md`.

## Como revisitar

Se o CI (F4) apresentar instabilidade de resolução de dependências atribuível ao uv,
ou se uma dependência do projeto exigir recurso que só Poetry/Conda oferecem,
reabrir esta decisão com um novo ADR.
