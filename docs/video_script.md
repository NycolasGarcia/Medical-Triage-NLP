# Roteiro do vídeo STAR (5 min)

Cinco minutos é curtíssimo: ~750 palavras faladas. Improvisar custa nota (R6, 15%).
Cronometrar em ensaio e cortar antes de gravar.

## Orçamento de tempo

| Bloco | Tempo | Conteúdo |
|---|---|---|
| Situation | 0:00–0:45 | Problema clínico: triagem lenta atrasa paciente crítico. Por que automatizar. |
| Task | 0:45–1:30 | Requisitos da fase: classificador NLP leve, API em container, CI/CD, Airflow, observabilidade, latência. |
| Action | 1:30–3:30 | Arquitetura, decisões (ADRs), custo FP/FN, otimização aplicada, como o monitoramento foi montado. |
| Result | 3:30–5:00 | Demo ao vivo: pipeline verde, dashboard com dados, números de latência antes/depois, lições aprendidas. |

## O que **mostrar** na tela (não só narrar)

1. CI verde no GitHub Actions.
2. DAG do Airflow com todas as tasks `success`.
3. `docker compose up` com os três serviços de pé.
4. Dashboard do Grafana **com dados** (rodar o load test antes de gravar).
5. Tabela de latência baseline vs. otimizado.

## Pontos que diferenciam (mencionar em Action/Result)

- Assimetria de custo: sub-triagem é o erro perigoso; a política de limiar foi
  enviesada para reduzi-la, com o trade-off medido.
- Limitação honesta: o rótulo de urgência é derivado (ADR-0001), não observado.
- Ganho de latência **medido** com protocolo (warm-up, N, percentis), não impressão.

## Erros comuns a evitar

- Gastar 2 min explicando o dataset e chegar em Result com 20 segundos.
- Mostrar código estático em vez do sistema rodando.
- Prometer validade clínica que o projeto não tem.

## Roteiro falado

### Situation (0:00–0:45)

Um hospital de referência recebe laudos médicos em texto o dia inteiro — e cada
um precisa ser lido e classificado por urgência antes de chegar ao médico
certo. Feito manualmente, isso atrasa exatamente o caso que não pode esperar:
o paciente crítico. A pergunta do projeto é simples de enunciar e difícil de
fazer direito: dá pra automatizar essa triagem sem trocar "lento" por
"perigoso de um jeito diferente"?

### Task (0:45–1:30)

O desafio pedia um classificador de texto leve para três faixas de
urgência — normal, atenção, urgente — servido como API em container. Mas o
foco real não era o modelo isolado, era o ciclo de vida completo em
produção: pipeline de CI/CD, orquestração de retreino com Airflow,
monitoramento com Prometheus e Grafana, e otimização de latência demonstrada
com números, não com impressão. E, por ser triagem hospitalar, uma exigência
que atravessa o projeto inteiro: os dois tipos de erro não podem custar a
mesma coisa.

### Action (1:30–3:30)

O modelo é TF-IDF mais Regressão Logística — decisão consciente, não
economia: comparei contra Random Forest, LightGBM, Naive Bayes e SVM
calibrado em validação cruzada, documentei em ADR por que o mais simples
venceu, e isso continua pagando dividendo lá na frente, na hora de otimizar
latência.

E aqui está o ponto mais importante do projeto: os dois erros dessa triagem
não são iguais. Classificar um paciente urgente como normal é o erro
perigoso; classificar um paciente normal como urgente custa tempo de equipe,
não risco. Então em vez de deixar o modelo decidir sozinho pela probabilidade
mais alta, eu construí uma matriz de custo explícita — sub-triagem custa até
quinze vezes mais que o erro seguro — calibrei as probabilidades do modelo, e
ajustei o limiar de decisão pra minimizar esse custo real, não a acurácia. O
resultado: sub-triagem caiu de dez por cento pra quatro, e o custo médio caiu
quase pela metade. Isso tem um preço — o modelo fica mais conservador, prevê
"normal" com menos frequência — e eu documentei esse trade-off com números,
não escondi.

Pra otimização de latência, testei exportar o modelo pra ONNX. Na prática,
descobri que duas das técnicas que mais ajudavam a qualidade — os n-gramas de
caractere e a marcação de negação — não são suportadas pelo conversor. Em vez
de descartar o ganho de latência ou o ganho de qualidade, montei os dois como
caminhos alternativos na mesma API, escolhidos por uma variável de ambiente:
o de melhor qualidade continua o padrão, o ONNX fica disponível pra quem
prioriza velocidade.

Todo esse ciclo é automatizado: uma DAG do Airflow reentreina o modelo, avalia
no conjunto de teste reservado e registra a versão no MLflow — a promoção pra
produção continua sendo uma decisão humana, com critério objetivo por trás,
não um clique às cegas.

### Result (3:30–5:00)

*(gravar com a stack rodando: CI verde, DAG com todas as tasks concluídas,
`docker compose up` de pé, dashboard do Grafana com dado real fluindo)*

Esse é o pipeline de CI/CD rodando — lint, testes e build, verde no GitHub
Actions a cada push. Essa é a DAG de retreino no Airflow, ponta a ponta.
Aqui está a stack completa de pé — API, Prometheus e Grafana — com o
dashboard mostrando requisições, latência e taxa de erro em tempo real. E
aqui está o número que mais importa pra essa fase: o backend otimizado em
ONNX responde cinquenta e oito por cento mais rápido que o original, medido
com protocolo — não impressão.

A lição principal não foi técnica de modelo, foi disciplina: toda decisão
que custaria caro reverter — mapeamento de rótulo, matriz de custo, técnica
de otimização — ficou registrada em ADR, com alternativa descartada e o
porquê. E a honestidade mais difícil do projeto: uma boa parte dos erros que
sobram não é falha do modelo, é o teto de qualidade de usar categoria de
assunto de artigo como proxy pra urgência clínica real — documentei isso com
exemplos reais lidos manualmente, não escondido atrás de uma métrica agregada.
Se este fosse um problema real, o próximo passo não seria mexer no modelo de
novo: seria conseguir rótulo de urgência de verdade.
