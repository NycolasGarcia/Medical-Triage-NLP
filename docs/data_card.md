# Data Card — Medical Abstracts TC Corpus (adaptado para triagem)

## Identificação

| Campo | Valor |
|---|---|
| Nome | Medical Abstracts TC Corpus |
| Fonte | `github.com/sebischair/Medical-Abstracts-TC-Corpus` (fonte canônica; também listado no Kaggle como espelho) |
| Citação | Schopf, Braun, Matthes. "Evaluating Unsupervised Text Classification: Zero-Shot and Similarity-Based Approaches." NLPIR 2022. DOI 10.1145/3582768.3582795 |
| Licença | CC BY-SA 3.0 |
| Versão / data de download | 2026-09-09, branch `main` do repositório |
| Registros brutos | 14.438 (11.550 train + 2.888 test, arquivos originais do repositório) |
| Registros após limpeza e dedupe | 11.225 (removidas 3.211 duplicatas exatas + 2 near-duplicates) |

## Conteúdo

| Coluna original | Tipo | Descrição |
|---|---|---|
| `condition_label` | int (1–5) | Classe original do corpus (sistema/condição), ver `medical_tc_labels.csv` |
| `medical_abstract` | str | Abstract médico em texto livre |

| Coluna derivada (pipeline do projeto) | Tipo | Descrição |
|---|---|---|
| `text` | str | Alias de `medical_abstract` |
| `original_label` | categórica | Nome da classe original (`condition_name`) |
| `urgency_label` | categórica ordinal | `normal` < `atencao` < `urgente` — **derivada** (ADR-0001) |

### Classes originais (verificado 2026-09-09, `condition_label`/`condition_name` de `medical_tc_labels.csv`)

| `condition_label` | `condition_name` | N (train) | N (test) | N (total) |
|---|---|---|---|---|
| 1 | neoplasms | 2.530 | 633 | 3.163 |
| 2 | digestive system diseases | 1.195 | 299 | 1.494 |
| 3 | nervous system diseases | 1.540 | 385 | 1.925 |
| 4 | cardiovascular diseases | 2.441 | 610 | 3.051 |
| 5 | general pathological conditions | 3.844 | 961 | 4.805 |
| **Total** | | **11.550** | **2.888** | **14.438** |

## Distribuição

Medida sobre os 11.225 registros após dedupe, antes do split (proporções de
treino/teste ficaram praticamente idênticas — ver `docs/PROGRESS.md`).

| Classe de urgência | N | % |
|---|---|---|
| urgente | 3.927 | 35,0 |
| atencao | 3.740 | 33,3 |
| normal | 3.558 | 31,7 |

## Estatísticas de texto

Medidas sobre os 14.438 registros brutos (antes do dedupe — caracteriza o texto do
corpus, não muda com a remoção de duplicatas).

| Métrica | Valor |
|---|---|
| Comprimento mediano (tokens) | 176 |
| p95 de comprimento (tokens) | 302 |
| Tamanho do vocabulário | 38.096 |
| Hapax legomena (%) | 23,5% |
| OOV treino -> teste (split original) (%) | 14,0% |
| Duplicatas exatas removidas | 3.211 |
| Near-duplicates removidos (limiar: 0,9 de similaridade de cosseno) | 2 |

## Pré-processamento aplicado

- Normalização: nenhuma alteração do texto armazenado (mantém capitalização e
  pontuação originais); strip+lowercase é usado só para comparação no dedupe exato,
  não para o texto salvo. Normalização de vocabulário (case, acentos, stopwords) é
  hiperparâmetro do vetorizador, decidido em F2/F6 — **negadores mantidos**
  (`não`, `sem`, `nem`) por padrão, texto clínico inverte de sentido sem eles.
- Deduplicação **antes** do split: sim (exato via `dedupe_exact`, depois
  near-duplicate via `dedupe_near`, limiar 0,9 de similaridade de cosseno em TF-IDF).
- Split: estratificado por `urgency_label`, seed `42`, proporção 80/20
  (8.980 treino / 2.245 teste) — reprodutível, checksum verificado igual em execuções
  repetidas.

## Limitações (obrigatório declarar)

1. **O rótulo de urgência é derivado, não observado.** Ver ADR-0001. O mapeamento é
   heurístico e didático, sem validação clínica.
2. Corpus de abstracts acadêmicos, não de laudos hospitalares reais — vocabulário e
   estrutura diferem do texto de produção.
3. Sem informação demográfica: não é possível auditar viés por população.
4. **O split treino/teste original do corpus tem vazamento grave e é descartado.**
   Verificado 2026-09-09: 1.010 das 2.888 linhas de teste (35%) têm texto idêntico a
   alguma linha de treino; 988 abstracts únicos aparecem nos dois lados; 100% desses
   988 têm `condition_label` divergente entre train e test (mesmo texto, categoria
   diferente). Por isso o projeto concatena train+test, deduplica e refaz um split
   estratificado próprio (caixas 1.5/1.6) — o split original nunca é usado como está.
5. **"Condições patológicas gerais" é uma classe heterogênea (catch-all)**, com a
   maior sobreposição lexical com todas as outras (Jaccard 0,44–0,53 entre todos os
   pares de classe, notebook seção 7) e mapeada inteiramente para `normal`. Nada
   garante que todo caso dessa classe seja de fato baixa urgência — é a maior fonte
   de ruído esperada no rótulo derivado, junto com o item 1.
6. ~22% do corpus bruto eram duplicatas exatas antes do dedupe (item 4 já cobre o
   vazamento; aqui é sobre volume de conteúdo repetido em geral) — corpus acadêmico
   compilado de múltiplas fontes, não texto de produção único por caso.

## Riscos de uso indevido

Este dataset e o modelo derivado **não devem** ser usados para decisão clínica real.
