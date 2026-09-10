# Model Card — Classificador de urgência de laudos

> Rascunho de F2 — candidato provisório (baseline, sem calibração/otimização).
> Versão final em F7, após tuning (F6) e possível troca de modelo/limiar.

## 1. Detalhes do modelo

| Campo | Valor |
|---|---|
| Tarefa | Classificação de texto multiclasse ordinal (`normal` < `atencao` < `urgente`) |
| Arquitetura | TF-IDF (unigramas, max_features=20000) + Regressão Logística, **sem calibração** |
| Versão | Baseline F2 — melhor dos 3 candidatos comparados, não o modelo final |
| Data | 2026-09-10 |
| Framework | scikit-learn (ONNX Runtime entra em F6) |
| Autor | Nycolas Garcia |
| Rastreabilidade | MLflow run id `0dd51d0c`, experimento `triagem-urgencia` |

## 2. Uso pretendido

**Pretendido:** exercício acadêmico de MLOps — demonstrar ciclo de vida de modelo em
produção (CI/CD, orquestração, monitoramento, otimização de latência).

**Não pretendido:** qualquer decisão clínica, priorização real de pacientes ou
substituição de julgamento profissional. O rótulo de urgência é derivado (ADR-0001).

## 3. Dados

Ver `data_card.md`. Ponto crítico: o alvo é **proxy**, não urgência observada.

## 4. Performance

Média de 5-fold CV estratificada sobre `data/processed/train.csv` (8.980 amostras);
o conjunto de teste (2.245 amostras) segue reservado, não usado nesta fase. Tabela
comparativa completa (incluindo Dummy e Random Forest) em `docs/EXPERIMENTS.md`.

| Métrica | Valor | Observação |
|---|---|---|
| F1 macro | 0,731 | vs. 0,339 do DummyClassifier |
| F1 weighted | 0,733 | |
| Recall `urgente` | 0,796 | métrica mais importante deste modelo |
| Recall `atencao` | 0,818 | |
| Recall `normal` | 0,584 | classe com mais confusão (ver matriz) |
| ROC-AUC (OvR) | 0,877 | |

Matriz de confusão 3×3: artefato `confusion_matrix.csv` no run MLflow `0dd51d0c`.

### Erros por tipo (sub-triagem vs. sobre-triagem)

Contagem agregada das 5 dobras (8.980 predições no total). Quebra por magnitude
(1 nível vs. 2 níveis) e custo sob a matriz assimétrica ficam para F6 (ADR-0005) —
esta é a "primeira leitura" prevista na caixa 2.6, não a análise final.

| Tipo de erro | Contagem | % |
|---|---|---|
| Sub-triagem (agregada) | 1.057 | 11,8% |
| Sobre-triagem (agregada) | 1.315 | 14,6% |
| Acerto exato | 6.608 | 73,6% |

Custo total sob a matriz assimétrica (ADR-0005): pendente — matriz de custo ainda
não implementada (F6, caixa 6.3).

## 5. Política de decisão

Calibração aplicada: nenhuma ainda — planejada para F6 (Platt/isotônica, caixa 6.2).
Limiares por classe: nenhum ajuste ainda — decisão hoje é o argmax padrão do
`predict_proba`. Ajuste orientado a reduzir sub-triagem entra em F6 (ADR-0005).
Trade-off aceito: nenhum ainda formalizado — os números de sub/sobre-triagem acima
são a linha de base **antes** de qualquer política deliberada de limiar.

## 6. Latência

Ainda não medida — entra em F3 (baseline, API em container) e F6 (comparativo
original vs. otimizado). Ver `LATENCY.md`.

## 7. Limitações

1. Rótulo derivado por heurística (ADR-0001) — a performance mede aderência ao
   mapeamento, não acurácia clínica.
2. Corpus de abstracts, não laudos reais.
3. Modelo de saco de palavras (unigramas): negação e contexto de frase não são
   capturados — "sem sinais de X" e "sinais de X" têm representação muito parecida
   nesta versão. Negadores **não são removidos** pelo vetorizador (stopwords
   desativado por padrão), mas isso só evita perder a palavra, não captura o
   contexto. N-gramas (1,2) para mitigar isso ficam para o tuning de F6.
4. Sem detecção de fora-de-distribuição: texto de domínio distinto recebe classe com
   confiança possivelmente alta e sem sentido.

## 8. Vieses

- Vieses do corpus de origem (áreas médicas sobre-representadas) propagam para as
  faixas de urgência via mapeamento.
- Sem atributos demográficos, não é possível auditar viés por grupo — isso é uma
  limitação, não uma ausência de viés.

## 9. Cenários de falha

| Cenário | Efeito | Mitigação |
|---|---|---|
| Texto muito curto / vazio | Predição instável | Validação de tamanho mínimo na API |
| Laudo com negação pesada | Sub ou sobre-triagem | Negadores não são removidos hoje; n-gramas (1,2) planejados para F6 |
| Vocabulário novo (drift) | Queda silenciosa de qualidade | Monitorar distribuição de classes preditas (F5) |
| Idioma diferente do treino | Saída sem sentido | Checagem de idioma na ingestão |

## 10. Monitoramento em produção

Métricas expostas e painéis: ver `RUNBOOK.md` e o dashboard do Grafana.
Sinal de alerta principal: mudança na distribuição de classes preditas + aumento de p95.
