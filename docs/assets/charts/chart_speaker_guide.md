# Guia de fala - slides com gráficos

Use este guia como roteiro oral para os novos slides inseridos em `docs/RA03_Complexidade.pptx`.

## Gargalo computacional por iteração

O que dizer:
- Este gráfico explica por que o custo real não depende apenas do tamanho final de `SB`.
- Para `p=11`, a solução final tem menos conjuntos, mas cada iteração exige aproximadamente `1.366.365` atualizações de `count[]`.
- Essa diferença de ordens de grandeza justifica a escolha de paralelismo especificamente no Programa 5.
- A mensagem central é: `p=11` parece menor no resultado, mas é o mais pesado por iteração.

## Ganho com paralelismo no Programa 1

O que dizer:
- A geração dos conjuntos é naturalmente paralelizável, porque `S15`, `S14`, `S13`, `S12` e `S11` podem ser gerados de forma independente.
- A versão sequencial levou cerca de `80s`; a versão paralela levou cerca de `18,7s`.
- Isso representa speedup aproximado de `4,3x`.
- Esse resultado mostra ganho significativo de desempenho sem alterar a lógica matemática do problema.

## Resultado final versus lower bound

O que dizer:
- Este gráfico compara o tamanho obtido pelo greedy com o lower bound de Schönheim.
- A escala logarítmica permite comparar `p=14`, `p=13`, `p=12` e `p=11` no mesmo slide.
- O greedy não garante ótimo global, mas ficou relativamente próximo dos limites inferiores.
- O ponto importante é que o gap real ficou entre `1,79x` e `3,78x`, muito abaixo do pior caso teórico.

## Tempo por abordagem experimental

O que dizer:
- Este gráfico usa escala logarítmica porque os tempos variam de menos de 1 segundo a mais de 140 segundos.
- O Stochastic Greedy é claramente o método mais rápido nas duas instâncias testadas.
- No `medium`, ele foi `13,5x` mais rápido que o greedy baseline.
- No `large-demo`, foi `20,6x` mais rápido.
- O GRASP validou o eixo de metaheurísticas, mas teve custo alto nestes testes.

## Trade-off entre tempo e qualidade

O que dizer:
- O eixo X mostra tempo em escala logarítmica; quanto mais à esquerda, mais rápido.
- O eixo Y mostra `|SB|`; quanto mais abaixo, menor a solução.
- O melhor compromisso medido é o Stochastic Greedy: muito mais rápido, com aumento inferior a 10% no tamanho da solução.
- Este slide é a defesa principal da frase do enunciado sobre ganhos significativos de desempenho devidamente justificados.
