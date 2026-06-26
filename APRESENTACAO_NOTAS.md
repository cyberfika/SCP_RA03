# Notas para Apresentação — RA03 Complexidade

## Slide 1: Capa
- "Este é um trabalho avaliativo de Complexidade de Algoritmos sobre o clássico problema de Set Cover."
- "A meta é encontrar o menor conjunto de 15-subconjuntos que cubra todas as combinações de tamanho 14, 13, 12 e 11."

## Slide 2: Modelagem do Problema
- "Temos um universo de 25 elementos e precisamos cobrir todas as combinações de tamanho p com subconjuntos de tamanho 15."
- "No pior caso — p=11 — temos 4,4 milhões de alvos a cobrir."
- "Esta é uma instância de Minimum Set Cover, que é NP-difícil."
- "A abordagem matemática é Programação Linear Inteira (ILP), mas em escala completa torna-se inviável."

## Slide 3: Por que NÃO ILP Direto
- "Para p=11, teríamos 4,46 bilhões de coeficientes não-nulos na matriz de restrições — impossível de armazenar."
- "Solvers como Gurobi não conseguem resolver ILPs desta magnitude em tempo útil."
- "Portanto, o ILP fica como referência teórica e benchmarking em subespaços reduzidos."

## Slide 4: Critério de Qualidade
- "Usamos dois lower bounds: LP direto (contagem simples) e o limite combinatório de Schönheim."
- "Schönheim é sempre mais apertado que LP — ele serve como nossa referência principal de qualidade."
- "Para p=14, o gap é mínimo; para p=13, o limite de Schönheim é 19% maior que o LP."

## Slide 5: Implementação
- "Cada conjunto é representado como bitmask de 32 bits — teste de inclusão em O(1)."
- "Usamos arrays NumPy para operações vetorizadas em C, sem overhead Python."
- "Heap lazy para p=14 e p=13 (volume baixo); argmax vetorizado para p=12; paralelismo para p=11 (1,3M updates por iteração)."

## Slide 6: Estratégia Adotada — Greedy
- "O algoritmo Greedy escolhe iterativamente o candidato que cobre mais alvos ainda não cobertos."
- "Tem garantia teórica: a solução é no máximo H(n) × OPT, onde H(n) é a série harmônica."
- "Para nosso problema, H(5.2M) ≈ 15,4× — ou seja, o pior caso teórico é 15,4 vezes o ótimo."
- "Mas os resultados reais ficaram entre 1,79× e 3,78× — de 4 a 9 vezes melhor que o pior caso."

## Slide 7: Análise Técnica
- "A complexidade por iteração é dominada pelas atualizações de contadores — cresce 8.280× de p=14 para p=11."
- "Por isso usamos estratégias diferentes: heap para p pequeno, NumPy para p médio, paralelismo para p grande."
- "Espaço total: O(N₁₅ + Nₚ) — cerca de 7 GB em memória RAM."

## Slide 8: Escalabilidade
- "Programa 1 (geração): paralelo reduziu 80s para 18,7s — speedup 4,3×."
- "Programa 5 (p=11): paralelismo é viável porque temos 1,3M updates por iteração."
- "Programas 2, 3 e 4 têm volume menor — overhead de IPC supera o ganho."

## Slide 9: Gargalo Computacional
- "p=11 é o caso menor em número de alvos, mas exige o maior custo por iteração."
- "Isto faz dele o gargalo dominante — apesar de 12.733 conjuntos selecionados, o tempo é ~3,4 horas."

## Slide 10: Computação Paralela
- "Ganho de 4,3× na geração prova que paralelismo funciona onde há independência de dados."

## Slide 11: Saída Experimental
- "p=14: 532.555 conjuntos selecionados, 1,79× acima do lower bound (16,3% de S₁₅)."
- "p=13: 128.827 conjuntos, 2,19× acima do lower bound (3,9% de S₁₅)."
- "p=12: 38.100 conjuntos, 2,89× acima do lower bound (1,2% de S₁₅)."
- "p=11: 12.733 conjuntos, 3,78× acima do lower bound (0,4% de S₁₅)."
- "A cobertura foi auditada e confirmada 100% para todos os casos."

## Slide 12: Resultado Final
- "Os resultados reais ficam significativamente abaixo dos lower bounds de Schönheim — a qualidade é boa."

## Slide 13: Alternativas Testadas
- "Greedy Randomizado: 13–20× mais rápido que baseline, custo <10% em tamanho."
- "GRASP: mais caro, sem ganho significativo nos nossos benchmarks."
- "Relaxação Lagrangiana e Column Generation: contribuições científicas, não solucionadores primários."
- "ILP e Branch & Bound: inviáveis em escala completa, viáveis como refinamento pós-greedy."

## Slide 14: Validação Experimental (Instâncias Reduzidas)
- "Em instância medium (n=15, k=9): Stochastic Greedy é 13,5× mais rápido e custa só 8,6% em tamanho."
- "Em instância large-demo (n=16, k=10): 20,6× mais rápido com +9,5% em tamanho."
- "GRASP é 5–6× mais lento e não justifica o custo."

## Slide 15: Stochastic Greedy Concentra Ganho
- "O Stochastic Greedy é a alternativa mais promissora para trade-off tempo vs qualidade."

## Slide 16: Melhor Compromisso
- "O ponto ideal de trade-off fica no Stochastic Greedy — não é nem o mais lento nem sacrifica muita qualidade."

## Slide 17: Limitações e Melhorias
- "Limitações: ILP inviável em escala, Greedy não é ótimo, auditoria exata é cara, limite de n ≤ 27."
- "Trabalhos futuros: ILP pós-greedy em subconjuntos reduzidos, Column Generation completa, GRASP paralelo."

## Slide 18: Síntese/Conclusão
- "Greedy Set Cover é a estratégia mais eficaz para esta escala — escalável e com garantia formal."
- "Os resultados práticos superaram a garantia teórica em 4–9 vezes."
- "Stochastic Greedy é a melhor alternativa — speedup de 13–20× com qualidade aceitável."
- "Paralelismo funciona onde há volume: Programa 1 (geração, 4,3×) e Programa 5 (p=11, updates massivos)."
- "Abordagens exatas permanecem viáveis em subescalas ou com hardware distribuído."
