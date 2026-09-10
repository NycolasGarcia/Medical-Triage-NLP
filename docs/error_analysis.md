# Análise qualitativa de erros

Passo específico de NLP e o de maior retorno por hora investida no projeto.
Preencher em F6, depois de escolher o modelo final.

## Amostragem

- Total de erros no conjunto de teste: `<n>`
- Amostra lida manualmente: `<n>` (priorizar **sub-triagem**, o erro perigoso)

## Erros de sub-triagem (`urgente` -> `atencao`/`normal`)

| # | Trecho do texto | Real | Predito | Hipótese do erro |
|---|---|---|---|---|
| 1 | | urgente | normal | |

## Erros de sobre-triagem

| # | Trecho do texto | Real | Predito | Hipótese do erro |
|---|---|---|---|---|
| 1 | | normal | urgente | |

## Padrões identificados

| Padrão | Frequência na amostra | Ação possível |
|---|---|---|
| Negação (`sem sinais de...`) | | manter negadores; n-gramas (1,2) |
| Abreviação médica não normalizada | | dicionário de expansão |
| Texto muito curto | | validação de tamanho mínimo na API |
| Ambiguidade real do mapeamento | | revisitar ADR-0001 |

## Termos mais influentes por classe

<Coeficientes do modelo linear ou permutation importance. Evidência forte e barata
para o vídeo.>

| Classe | Top n-gramas positivos | Top n-gramas negativos |
|---|---|---|
| urgente | | |
| atencao | | |
| normal | | |

## Conclusões acionáveis

1.
2.
