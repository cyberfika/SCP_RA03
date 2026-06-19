Abaixo está um prompt pronto para usar no **Claude Code**. Eu deixei em formato operacional, para ele **pensar, comparar, selecionar e planejar** quais abordagens aplicar em um problema real.

As referências citadas são reais: FPT/algoritmos parametrizados têm como base moderna Cygan et al., *Parameterized Algorithms*; kernelização é consolidada por Fomin, Lokshtanov, Saurabh e Zehavi; aproximação por Vazirani; bidimensionalidade/decomposição estrutural por Demaine e Hajiaghayi; coresets por Agarwal, Har-Peled e Varadarajan e também Phillips; sketching/streaming por Cormode e Muthukrishnan; sparsificação espectral por Spielman e Teng; e as abordagens práticas incluem Algorithm Engineering, SATzilla, SMAC, Chaff, Z3 e CP-SAT-LP. ([mimuw.edu.pl][1])

---

## Prompt para Claude Code

> Você é um pesquisador sênior em algoritmos, teoria da computação, otimização combinatória e engenharia de software algorítmica.
>
> Sua tarefa é **pensar, comparar e planejar** o uso de abordagens modernas capazes de reduzir a complexidade assintótica, ou tornar computacionalmente tratável um problema que parece difícil no pior caso.
>
> O objetivo não é simplesmente escolher uma técnica. O objetivo é construir uma **análise comparativa fundamentada**, identificando quais técnicas podem efetivamente reduzir a complexidade assintótica, quais reduzem principalmente o tamanho da instância, quais oferecem aproximação com garantia, quais exploram estrutura do input e quais apenas melhoram o desempenho prático sem alterar o pior caso teórico.
>
> ## Problema a ser analisado
>
> Analise o seguinte problema:
>
> ```text
> D:\Projects\SCP_RA03\docs\Trabalho 03 RA03 Combinatoria 5U.pdf
> ```
>
> Considere também:
>
> ```text
> Tamanho esperado da entrada: [n, m, número de variáveis, número de restrições, número de registros, tamanho do grafo etc.]
> Tipo de entrada: [grafo, matriz, fluxo de dados, conjunto de pontos, problema combinatório, problema de otimização, problema de decisão etc.]
> Objetivo: [ótimo exato, aproximação, decisão, ranking, predição, alocação, roteirização, clustering etc.]
> Restrições práticas: [tempo máximo, memória, necessidade de resposta online, dados em streaming, paralelização, precisão mínima etc.]
> ```
>
> ## Abordagens que devem ser comparadas
>
> Compare obrigatoriamente as seguintes abordagens que, quando aplicáveis, podem reduzir complexidade assintótica ou tornar o problema tratável por outro regime de análise:
>
> 1. **FPT — Fixed-Parameter Tractability / Complexidade Parametrizada**
>
>    * Avalie se há um parâmetro estrutural (k) pequeno.
>    * Exemplos de parâmetros: tamanho da solução, treewidth, vertex cover number, número de conflitos, dimensão, sparsity, número de clusters, número de exceções, distância para uma classe fácil.
>    * Verifique se o problema pode ser resolvido em tempo (f(k) \cdot n^{O(1)}).
>    * Referências reais a considerar: Rod Downey e Michael Fellows; Cygan, Fomin, Kowalik, Lokshtanov, Marx, Pilipczuk, Pilipczuk e Saurabh, *Parameterized Algorithms*, 2015.
> 2. **Kernelização**
>
>    * Verifique se existe pré-processamento polinomial que reduza a instância para um núcleo de tamanho limitado por uma função do parâmetro (k).
>    * Avalie se o kernel é polinomial, linear, quadrático ou apenas exponencial em (k).
>    * Diferencie kernelização exata de kernelização aproximada/lossy.
>    * Referências reais a considerar: Fomin, Lokshtanov, Saurabh e Zehavi, *Kernelization: Theory of Parameterized Preprocessing*, 2019.
> 3. **Algoritmos de Aproximação**
>
>    * Avalie se o problema admite aproximação com garantia formal.
>    * Classifique a possibilidade de:
>
>      * razão constante;
>      * (O(\log n));
>      * PTAS;
>      * EPTAS;
>      * FPTAS;
>      * aproximação parametrizada.
>    * Explique o trade-off entre perder otimalidade e ganhar eficiência.
>    * Referências reais a considerar: Vijay V. Vazirani, *Approximation Algorithms*, 2001; David P. Williamson e David B. Shmoys, *The Design of Approximation Algorithms*, 2011.
> 4. **Decomposição Estrutural**
>
>    * Investigue se a entrada possui estrutura explorável.
>    * Exemplos:
>
>      * baixa treewidth;
>      * pathwidth;
>      * grafos planares;
>      * grafos de gênero limitado;
>      * grafos esparsos;
>      * grafos excluindo menores;
>      * decomposição modular;
>      * separadores balanceados.
>    * Verifique se programação dinâmica sobre decomposição em árvore ou separadores reduz a complexidade.
>    * Referências reais a considerar: Robertson e Seymour, Graph Minors; Courcelle; Bodlaender; Demaine e Hajiaghayi, especialmente a linha de bidimensionalidade.
> 5. **Coresets**
>
>    * Avalie se a entrada pode ser substituída por um subconjunto pequeno, ponderado ou resumido, preservando aproximadamente a função objetivo.
>    * Especialmente relevante para:
>
>      * clustering;
>      * k-means;
>      * k-median;
>      * regressão;
>      * geometria computacional;
>      * machine learning;
>      * big data distribuído.
>    * Verifique tamanho do coreset, erro (\varepsilon), tempo de construção e possibilidade de manutenção em streaming/distribuído.
>    * Referências reais a considerar: Pankaj K. Agarwal, Sariel Har-Peled e Kasturi R. Varadarajan, “Geometric Approximation via Coresets”, 2005; Jeff M. Phillips, “Coresets and Sketches”, 2016; Dan Feldman, “Introduction to Core-sets: an Updated Survey”, 2020.
> 6. **Sketching**
>
>    * Avalie se é possível representar a entrada por um esboço probabilístico de baixa dimensão ou baixo espaço.
>    * Considere:
>
>      * Count-Min Sketch;
>      * Johnson–Lindenstrauss projections;
>      * linear sketches;
>      * frequency moments;
>      * sketches para álgebra linear numérica.
>    * Indique erro, probabilidade de falha, espaço usado e tempo por atualização.
>    * Referências reais a considerar: Graham Cormode e S. Muthukrishnan, “An Improved Data Stream Summary: The Count-Min Sketch and its Applications”, 2005; David P. Woodruff, “Sketching as a Tool for Numerical Linear Algebra”, 2014.
> 7. **Streaming / Algoritmos Sublineares**
>
>    * Avalie se o problema pode ser resolvido sem ler ou armazenar toda a entrada.
>    * Considere:
>
>      * uma passagem;
>      * múltiplas passagens;
>      * memória sublinear;
>      * property testing;
>      * algoritmos de consulta;
>      * algoritmos online.
>    * Diferencie redução de tempo, redução de memória e redução de acesso à entrada.
>    * Referências reais a considerar: S. Muthukrishnan, *Data Streams: Algorithms and Applications*, 2005; Oded Goldreich, Dana Ron e outros trabalhos clássicos de property testing.
> 8. **Sparsificação**
>
>    * Avalie se a entrada, especialmente grafos ou matrizes, pode ser substituída por uma versão esparsa que preserve propriedades relevantes.
>    * Considere:
>
>      * cut sparsifiers;
>      * spectral sparsifiers;
>      * preservação de cortes;
>      * preservação de formas quadráticas do Laplaciano;
>      * redução de arestas mantendo aproximação.
>    * Verifique se isso habilita algoritmos quase lineares para fluxos, cortes, sistemas lineares, clustering em grafos ou otimização.
>    * Referências reais a considerar: Benczúr e Karger, sparsificação de cortes; Daniel A. Spielman e Shang-Hua Teng, “Spectral Sparsification of Graphs”; Spielman e Srivastava, effective resistances.
>
> ## Abordagens que melhoram principalmente a complexidade prática
>
> Além das técnicas acima, avalie também as seguintes abordagens. Elas podem ser decisivas na prática, mas normalmente **não alteram o pior caso assintótico teórico**:
>
> 1. **Algorithm Engineering**
>
>    * Avalie implementação, estrutura de dados, cache, paralelismo, profiling, benchmarks e experimentação sistemática.
>    * Referências reais: Peter Sanders; Lasse Kliemann e Peter Sanders, *Algorithm Engineering: Selected Results and Surveys*, 2016.
> 2. **Algorithm Portfolios**
>
>    * Avalie selecionar diferentes algoritmos conforme características da instância.
>    * Referência real: SATzilla, de Lin Xu, Frank Hutter, Holger H. Hoos e Kevin Leyton-Brown.
> 3. **Configuração Automática de Algoritmos**
>
>    * Avalie tuning automático de parâmetros, Bayesian optimization, SMAC, ParamILS e irace.
>    * Referências reais: Frank Hutter, Holger H. Hoos e Kevin Leyton-Brown; SMAC; ParamILS.
> 4. **SAT/SMT Solvers**
>
>    * Avalie modelar o problema como SAT, MaxSAT, SMT ou pseudo-Boolean optimization.
>    * Considere CDCL, clause learning, restarts, watched literals, propagação e teoria de fundo.
>    * Referências reais: Chaff, de Moskewicz, Madigan, Zhao, Zhang e Malik, 2001; Z3, de Leonardo de Moura e Nikolaj Bjørner, 2008.
> 5. **CP-SAT / Constraint Programming híbrida**
>
>    * Avalie se o problema combina restrições lógicas, inteiras, combinatórias e de scheduling.
>    * Considere OR-Tools CP-SAT/CP-SAT-LP, Lazy Clause Generation, propagadores, SAT, programação inteira e cortes lineares.
>    * Referências reais: Laurent Perron, Frédéric Didier e Steven Gay, “The CP-SAT-LP Solver”, 2023; Ohrimenko, Stuckey e Codish, Lazy Clause Generation.
>
> ## Entregável esperado
>
> Produza uma análise estruturada em português brasileiro com as seguintes seções:
>
> ### 1. Diagnóstico inicial do problema
>
> * Classifique o tipo de problema.
> * Indique se parece ser P, NP-difícil, problema de otimização combinatória, problema geométrico, problema de grafo, problema de dados massivos ou problema online/streaming.
> * Declare explicitamente quais informações ainda faltam.
>
> ### 2. Tabela comparativa das abordagens fortes
>
> Crie uma tabela com as colunas:
>
> * Abordagem;
> * Ideia central;
> * Quando aplicar;
> * Que tipo de complexidade pode reduzir;
> * Garantia teórica;
> * Risco/limitação;
> * Autores/fontes clássicas;
> * Aplicabilidade ao problema analisado: alta, média ou baixa.
>
> Inclua obrigatoriamente:
>
> * FPT;
> * kernelização;
> * aproximação;
> * decomposição estrutural;
> * coresets;
> * sketching;
> * streaming/sublinear;
> * sparsificação.
>
> ### 3. Tabela das abordagens práticas
>
> Crie outra tabela para:
>
> * algorithm engineering;
> * algorithm portfolios;
> * configuração automática;
> * SAT/SMT;
> * CP-SAT.
>
> Explique que essas técnicas podem reduzir tempo real de execução, memória, robustez e escalabilidade prática, mas não necessariamente mudam a complexidade assintótica no pior caso.
>
> ### 4. Estratégia recomendada
>
> Monte uma estratégia em camadas:
>
> 1. Primeiro: identificar estrutura e parâmetros.
> 2. Segundo: tentar FPT/kernelização/decomposição estrutural.
> 3. Terceiro: se ótimo exato for caro, avaliar aproximação, coresets, sketching ou sparsificação.
> 4. Quarto: se os dados forem grandes ou contínuos, avaliar streaming/sublinear.
> 5. Quinto: usar algorithm engineering, portfolios, configuração automática, SAT/SMT ou CP-SAT como camada prática de implementação.
>
> ### 5. Plano de experimento
>
> Proponha benchmarks e métricas:
>
> * tempo assintótico estimado;
> * tempo real;
> * memória;
> * qualidade da solução;
> * erro de aproximação;
> * escalabilidade;
> * sensibilidade ao parâmetro (k);
> * robustez por distribuição de instâncias;
> * comparação contra baseline ingênuo.
>
> ### 6. Conclusão executiva
>
> Finalize com uma recomendação objetiva:
>
> * abordagem mais promissora;
> * segunda melhor abordagem;
> * abordagem de baixo risco para protótipo;
> * abordagem de maior impacto teórico;
> * abordagem de maior impacto prático.
>
> Não invente garantias teóricas. Quando uma técnica só melhorar desempenho prático, diga expressamente. Quando uma técnica depender de parâmetro pequeno, estrutura especial, erro (\varepsilon), aleatoriedade ou perda de otimalidade, deixe isso claro.
>
> Use linguagem técnica, mas clara. Pense como pesquisador, arquiteto de algoritmos e engenheiro de software ao mesmo tempo.

[1]: https://www.mimuw.edu.pl/~malcin/book/parameterized-algorithms.pdf?utm_source=chatgpt.com "Parameterized Algorithms"
