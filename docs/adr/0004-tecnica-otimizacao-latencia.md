# ADR-0004 — Técnica de otimização de latência

- **Status:** aceito
- **Data:** 2026-09-15
- **Fase:** F6
- **Decisor:** Nycolas Garcia

## Contexto

R1 (20% da nota) exige "conversão/otimização (ex. ONNX) bem-sucedida e melhoria de
latência demonstrada com números" — não basta o modelo já ser rápido "de fábrica"
(§4). `docs/LATENCY.md` já tinha o baseline medido desde F3 (p95 3,11 ms) e uma
leitura de onde o tempo é gasto: vetorização TF-IDF domina (73,7% do tempo de
processamento), então uma otimização que não toque a vetorização (só o
classificador) renderia pouco.

ONNX foi a técnica escolhida desde o planejamento (§4/§9), mas **não estava
validado que o pipeline real do projeto conseguiria ser convertido** — o pipeline
vencedor de caixa 6.1 usa uma `FeatureUnion` com char n-gramas e um preprocessador
Python customizado (marcação de negação), e é calibrado via `CalibratedClassifierCV`
(caixa 6.2). Testar a conversão antes de assumir sucesso era a única forma honesta
de saber se a técnica era viável como estava, ou se precisaria de adaptação.

## Decisão

**ONNX Runtime é a técnica de otimização**, confirmando a escolha planejada — mas
com uma representação **diferente** da vencedora de caixa 6.1, porque o `skl2onnx`
não converte duas das três técnicas que a compõem (achados abaixo). Para não
descartar o ganho de qualidade de 6.1-6.4, a API serve **duas variantes**,
escolhidas por uma flag (`MODEL_BACKEND=sklearn|onnx`, `src/config.py`,
`src/api/model_runtime.py`):

- `sklearn` (padrão): pipeline completo de 6.1-6.4 — melhor qualidade, latência
  maior.
- `onnx`: representação mais simples (só bigramas de palavra), calibração
  isotônica própria (não `CalibratedClassifierCV`) rodando em Python sobre a
  saída do ONNX Runtime — pior qualidade (~1 ponto de F1-macro), latência menor
  (-58,3% no p95).

### Achados técnicos que forçaram esta decisão (testados diretamente, não hipótese)

1. **`TfidfVectorizer(preprocessor=mark_negation)` não converte** —
   `NotImplementedError: Custom preprocessor cannot be converted into ONNX`. Um
   callable Python arbitrário não tem como virar operações ONNX; é limitação
   estrutural do conversor, não bug de configuração.
2. **`TfidfVectorizer(analyzer="char_wb")` (char n-gramas) não converte** —
   `NotImplementedError: CountVectorizer cannot be converted, only tokenizer='word'
   is fully supported`. A técnica isolada mais forte de caixa 6.1 é incompatível
   com o conversor.
3. **`CalibratedClassifierCV` não aceita entrada de texto** —
   `InvalidInputTypeException` exigindo tipo numérico (double/float/int/bool). O
   conversor assume que o estimador calibrado já opera sobre features numéricas,
   não sobre uma pipeline de texto encadeada — independe de qual representação
   está por baixo.
4. **`StringNormalizer` do onnxruntime falha sem locale UTF-8 instalado** — só
   apareceu testando em **container** (`python:3.11-slim` não vem com nenhum
   locale); rodando local, o locale do host mascarava o problema. Corrigido no
   Dockerfile (`locales` + `locale-gen en_US.UTF-8`); ver `docs/LATENCY.md`.

### Como a perda de qualidade foi tratada (não só aceita)

- **Duas variantes servíveis via flag**, não substituição do pipeline de
  produção — nenhum ganho de 6.1 (representação) ou 6.3/6.4 (custo/limiar) foi
  descartado; quem prioriza latência opta explicitamente pelo `onnx`.
- **Calibração preservada apesar do item 3 acima**: implementado
  `OneVsRestIsotonicCalibrator` (`src/optimization/calibrator.py`) — um
  `IsotonicRegression` por classe, ajustado e aplicado em Python sobre o
  `predict_proba` bruto que sai do ONNX Runtime. O ONNX cuida da parte cara
  (vetorização + regressão logística); a calibração (barata, um lookup
  monotônico por classe) fica fora do grafo. Sem essa peça, o backend `onnx`
  teria perdido também a redução de sub-triagem de caixa 6.2 — não só 1 ponto de
  F1-macro, mas o principal ganho de segurança do projeto.
- **Efeito colateral descoberto ao implementar o calibrador**: `sklearn` por
  padrão calibra sobre `decision_function` (margem bruta), não `predict_proba`,
  quando o estimador oferece os dois — confirmado empiricamente comparando as
  duas (saída batendo byte a byte usando `decision_function`, divergindo até 0,23
  usando `predict_proba`). O calibrador manual usa `predict_proba` porque é o que
  o runtime ONNX expõe — escolha consciente e documentada no docstring da classe,
  não uma tentativa (falha) de replicar exatamente o `CalibratedClassifierCV`.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que não |
|---|---|---|---|
| Servir só o backend ONNX (substituir o pipeline de produção) | Mais simples de manter (1 pipeline, não 2); latência sempre baixa | Descarta ~100% do ganho de caixa 6.1 (a técnica isolada mais forte, char n-gramas, é a que não converte) | Perda desproporcional ao ganho de latência para quem não precisa dela |
| Quantização (em vez de ONNX) | Evitaria os problemas de conversão do skl2onnx inteiramente | TF-IDF + LogReg já é um modelo pequeno (2,4 MB) — quantização de pesos rende pouco quando o gargalo é vetorização de texto, não tamanho de matriz. Sem framework maduro para quantizar `TfidfVectorizer` especificamente | Descartada sem nem testar: a leitura de "onde o tempo é gasto" (LATENCY.md) já apontava a vetorização como o gargalo, que quantização de pesos não ataca |
| Reescrever a marcação de negação como `FunctionTransformer` em vez de `preprocessor=` do `TfidfVectorizer` | Poderia, em tese, contornar a limitação específica do `preprocessor` | `FunctionTransformer` com callable Python arbitrário tem a mesma limitação de conversão — só move o problema, não resolve | Não testado a fundo por já ter uma explicação estrutural clara (nenhum conversor ONNX executa Python arbitrário) |
| Manter só o backend `sklearn`, não fazer ONNX | Zero risco de regressão de qualidade | Não cumpriria R1 ("conversão/otimização bem-sucedida... demonstrada") | Descartada — é exatamente o critério que esta caixa existe para atender |

## Consequências

**Positivas**

- Ganho de latência real e grande: p95 -58,3% (7,01 ms → 2,92 ms), medido em
  container, 3 execuções de N=1.000 cada, mesmo protocolo do baseline de F3.
- Ganho de tamanho de artefato: -67% (2,4 MB → 0,79 MB).
- Ganho de tamanho de imagem Docker: -32,4% (1,03 GB → 696 MB) — achado
  colateral (dependências de treino inchando a imagem de serving, adiado desde
  F3), fechado nesta caixa por estar diretamente relacionado a latência/deploy.
- Calibração (e a redução de sub-triagem que ela traz) preservada no backend
  ONNX, apesar da limitação do `CalibratedClassifierCV` — não era óbvio que daria
  para manter.
- Nenhum ganho de qualidade de 6.1-6.4 foi silenciosamente descartado — está
  disponível via flag, documentado com números exatos do custo de trocar para
  o caminho rápido.

**Negativas / dívidas aceitas**

- Dois pipelines para manter (`sklearn` e `onnx`), não um — mais superfície de
  código, mais um lugar para desalinhar se a representação vencedora mudar no
  futuro (o backend ONNX não se atualiza sozinho).
- Backend `onnx` perde ~1 ponto de F1-macro e não tem acesso às técnicas de char
  n-gramas/marcação de negação — quem escolher `onnx` está trocando qualidade por
  velocidade conscientemente, mas é uma troca real, não gratuita.
- Calibração do backend `onnx` usa `predict_proba` como escore bruto, não
  `decision_function` como o sklearn faz por padrão — as duas são calibrações
  isotônicas legítimas, mas não são numericamente idênticas entre si (nem
  precisam ser: são dois modelos diferentes).

## Como revisitar

Reabrir se: uma versão futura do `skl2onnx` passar a suportar `char_wb` ou
preprocessadores customizados (converter o pipeline vencedor de 6.1 inteiro
deixaria de exigir a segunda representação); o backend `onnx` virar o padrão de
produção (exigiria decidir se a perda de F1-macro é aceitável permanentemente,
não só como opção); ou a matriz de custo mudar (§14) de um jeito que altere o
cálculo de qual variante minimiza custo esperado em produção.
