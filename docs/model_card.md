# Model Card — Classificador de urgência de laudos

> Versão final (F7). Substitui o rascunho de F2 — reescrito por completo após
> tuning de representação, calibração, matriz de custo, limiar e otimização de
> latência (F6). Métricas datadas e a fonte (MLflow run/ADR) de cada uma estão
> indicadas, não apenas o número.

## 1. Detalhes do modelo

| Campo | Valor |
|---|---|
| Tarefa | Classificação de texto multiclasse ordinal (`normal` < `atenção` < `urgente`) |
| Arquitetura (produção, backend `sklearn`) | `FeatureUnion` (TF-IDF palavra bigrama + TF-IDF char n-grama 3-5 + marcação de negação) → Regressão Logística → calibração isotônica → limiar cumulativo de decisão |
| Arquitetura (backend `onnx`, opt-in) | TF-IDF palavra bigrama (sem char n-grama/negação — limitação real do `skl2onnx`, ADR-0004) → Regressão Logística → calibração isotônica manual (Python, fora do grafo ONNX) → mesmo limiar |
| Versão | F6 final — MLflow Model Registry `triagem-urgencia`, versão 5, alias `@production` |
| Data | 2026-09-15 |
| Framework | scikit-learn 1.9 (produção) + ONNX Runtime 1.30 (variante opcional) |
| Autor | Nycolas Garcia |
| Decisões vinculadas | ADR-0001 (rótulo), ADR-0003 (modelo base), ADR-0004 (ONNX), ADR-0005 (custo/limiar), ADR-0010 (critério de promoção) |

## 2. Uso pretendido

**Pretendido:** exercício acadêmico de MLOps — demonstrar ciclo de vida de modelo em
produção (CI/CD, orquestração, monitoramento, otimização de latência) sobre um
problema de classificação de texto com custo assimétrico entre erros.

**Não pretendido:** qualquer decisão clínica, priorização real de pacientes ou
substituição de julgamento profissional. O rótulo de urgência é **derivado** por
heurística (ADR-0001), nunca validado clinicamente — ver §7.

## 3. Dados

Ver `data_card.md`. Ponto crítico, reafirmado após a análise qualitativa de F6
(§7 abaixo): o alvo é **proxy** (categoria de assunto do artigo médico), não
urgência clínica observada — essa é a causa dominante dos erros residuais do
modelo, não falha de representação ou calibração.

## 4. Performance

Duas leituras diferentes, não confundir: **CV** (5 dobras, `train.csv`, 8.980
amostras, usada para tunar cada componente) e **teste reservado** (`test.csv`,
2.245 amostras, nunca usado em nenhuma busca de F2/F6 — a leitura que mais importa).

### 4.1 Efeito de cada componente (CV, `docs/EXPERIMENTS.md`)

| Etapa | F1 macro | Recall `urgente` | Sub-triagem |
|---|---|---|---|
| TF-IDF unigrama (F2, sem nenhuma técnica de F6) | 0,731 | 0,796 | 11,8% |
| + representação tunada (6.1: bigramas+char n-grama+negação) | **0,734** | 0,792 | 11,9% |
| + calibração isotônica (6.2) | 0,724 | 0,815 | 9,3% |

O limiar de custo (6.4) não entra nesta tabela por ser avaliado sobre
probabilidades *out-of-fold* agrupadas, não médias por dobra (protocolo
diferente, mesma fonte de dados) — resultado em CV: recall `urgente` 0,903,
custo médio 0,645 (-45% vs. argmax). Efeito completo (incluindo F1-macro, que
cai de propósito) no teste reservado, tabela 4.2 — é a leitura que importa.

### 4.2 Teste reservado — modelo final vs. antes do limiar

| Métrica | Antes do limiar (argmax) | Modelo final (limiar tunado) |
|---|---|---|
| F1 macro | 0,728 | 0,523 |
| Recall `normal` | 0,545 | **0,044** |
| Recall `atenção` | 0,858 | 0,929 |
| Recall `urgente` | 0,799 | **0,880** |
| Sub-triagem | 10,3% | **4,3%** |
| Sobre-triagem | 15,9% | 32,6% |
| Custo médio (matriz §5) | 1,290 | **0,672** (-48%) |

## 5. Política de decisão (ADR-0005)

**Matriz de custo** (assimetria deliberada — §7 do enunciado): sub-triagem de 1
nível = 5, de 2 níveis = 15; sobre-triagem de 1 nível = 1, de 2 níveis = 2.
Sub-triagem custa 5-15× mais que o erro simétrico porque é o erro perigoso
(atraso no atendimento a paciente crítico); sobre-triagem é "caro, mas seguro".

**Calibração**: isotônica (`CalibratedClassifierCV`, sklearn; calibrador
one-vs-rest manual no backend ONNX) — vencedora sobre Platt em Brier e ECE
(`docs/EXPERIMENTS.md`).

**Limiar de decisão**: regra cumulativa, não argmax — prediz `urgente` se
`P(urgente) ≥ 0,31`; senão `atenção` se `P(atenção)+P(urgente) ≥ 0,09`; senão
`normal`. Os dois valores vêm de busca em CV (out-of-fold, sem vazamento),
não escolhidos à mão — `src/models/threshold.py`.

**Trade-off aceito, com número**: sub-triagem caiu de ~10% para ~4% (teste
reservado); em troca, sobre-triagem subiu de ~16% para ~33% e o recall de
`normal` caiu para 0,04 — o modelo praticamente para de prever `normal`. Revisado
pelo autor após leitura qualitativa de erros (§7) e mantido deliberadamente —
ver ADR-0005, seção "Revisão do autor".

## 6. Latência (ADR-0004, `docs/LATENCY.md`)

| Métrica | Backend `sklearn` (padrão) | Backend `onnx` (opt-in) | Ganho |
|---|---|---|---|
| p50 | 6,47 ms | 2,57 ms | -60,3% |
| p95 | 7,01 ms | 2,92 ms | **-58,3%** |
| p99 | 7,18 ms | 3,10 ms | -56,8% |
| Tamanho do artefato | 2,4 MB | 0,79 MB | -67% |

Medido em container, N=1.000, warm-up 100, 3 execuções (protocolo completo em
`docs/LATENCY.md`). Custo de qualidade do backend `onnx`: representação mais
simples (sem char n-gramas/negação — `skl2onnx` não converte nenhuma das duas),
F1-macro CV 0,723 vs. 0,734 do `sklearn` — a calibração e o limiar são
preservados nos dois backends igualmente.

## 7. Limitações

1. **Rótulo derivado por heurística (ADR-0001)** — a performance mede aderência
   ao mapeamento categoria-de-assunto → urgência, não acurácia clínica.
   **Achado concreto de F6** (`docs/error_analysis.md`): boa parte dos erros
   residuais (em ambas direções) são artigos de pesquisa/metodologia cujo texto
   diverge sistematicamente da categoria original do corpus — ex. um artigo
   sobre fibrilação ventricular classificado `normal` porque cai em "condições
   patológicas gerais", não "cardiovascular", no corpus original. Não é ruído
   aleatório, é um teto de qualidade estrutural do mapeamento.
2. Corpus de abstracts em **inglês**, não laudos reais em português. A entrada
   esperada pela API é inglês — decisão consciente (idioma do dataset), não
   inconsistência.
3. **Recall de `normal` extremamente baixo (0,04)** — efeito colateral
   matematicamente correto da assimetria de custo (§5), mas muda o caráter do
   sistema: deixa de ser um classificador 3-vias equilibrado e vira, na prática,
   um filtro "isto claramente não é normal?". Se isso for operacionalmente
   inviável, o ajuste correto é a matriz de custo (§14/ADR-0005), não o código
   do limiar.
4. Sem detecção de fora-de-distribuição: texto de domínio distinto recebe
   classe com confiança possivelmente alta e sem sentido.
5. Backend `onnx` não se atualiza sozinho se a representação vencedora mudar —
   dois pipelines para manter em sincronia (ADR-0004).

## 8. Vieses

- Vieses do corpus de origem (áreas médicas sobre-representadas) propagam para
  as faixas de urgência via mapeamento.
- Sem atributos demográficos, não é possível auditar viés por grupo — isso é
  uma limitação, não uma ausência de viés.
- A política de limiar (§5) introduz um viés **deliberado e documentado**: o
  sistema super-representa `atenção`/`urgente` às custas de `normal` — é a
  escolha de design do projeto, não um artefato de treino.

## 9. Cenários de falha

| Cenário | Efeito | Mitigação |
|---|---|---|
| Texto muito curto / vazio | Predição instável | Validação Pydantic na API (mínimo de caracteres) |
| Artigo de metodologia/pesquisa básica sobre tema grave, mas categorizado `normal` no corpus | Sobre-triagem sistemática (`normal`→`urgente`), não aleatória | Documentado como teto do mapeamento de rótulo (§7.1); não corrigível por limiar |
| Texto em português (ou outro idioma fora do treino) | Saída sem sentido — modelo espera inglês | Nenhuma — decisão consciente (item 2); exemplos de API/demo/vídeo em inglês |
| Vocabulário novo (drift) | Queda silenciosa de qualidade | Monitorar distribuição de classes preditas (F5, dashboard Grafana) |
| Alguém interpreta `normal` como "seguro" | Recall de `normal` é 0,04 — a classe quase não é usada por design | Documentado com destaque neste Model Card e em ADR-0005; não é bug |

## 10. Monitoramento em produção

Métricas expostas e painéis: ver `RUNBOOK.md` e o dashboard do Grafana
(`monitoring/grafana/provisioning/dashboards/triagem-urgencia.json`).
Sinal de alerta principal: mudança na distribuição de classes preditas (esperado
ser dominado por `atenção`/`urgente` dado o limiar — um salto de `normal` seria
o sinal anômalo, não o contrário) + aumento de p95.
