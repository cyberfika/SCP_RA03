# Análise Comparativa de Abordagens Algorítmicas — RA03 Cobertura de Combinações

> **Pesquisador sênior:** Algoritmos, teoria da computação, otimização combinatória, engenharia de software algorítmica.

---

## 1. Diagnóstico Inicial do Problema

### Descrição formal

- **Universo:** $U = \{1, 2, \ldots, 25\}$
- **Família candidata:** $\mathcal{S}_{15}$ — todos os $\binom{25}{15} = 3.268.760$ subconjuntos de tamanho 15
- **Família alvo:** $\mathcal{S}_p$ — todos os $\binom{25}{p}$ subconjuntos de tamanho $p$
- **Objetivo:** encontrar o menor $SB \subseteq \mathcal{S}_{15}$ tal que todo $Y \in \mathcal{S}_p$ esteja contido em algum $X \in SB$
- **Instâncias:** $p \in \{14, 13, 12, 11\}$

### Classificação

| Dimensão | Classificação |
|----------|--------------|
| Tipo de problema | Otimização combinatória — **Minimum Set Cover** |
| Complexidade | **NP-difícil** (Karp 1972, redução de Vertex Cover) |
| Estrutura de entrada | Problema de design combinatório (Covering Design $C(25, 15, p)$) |
| Escala da entrada | $|\mathcal{S}_{15}| = 3.268.760$ conjuntos candidatos; $|\mathcal{S}_p|$ até $4.457.400$ restrições |
| Tipo de objetivo | Ótimo exato — minimizar $|SB|$ |
| Restrições práticas | Memória ~1–20 GB; tempo máximo ~horas; processamento offline em batch |

### Escala por instância

| $p$ | $|\mathcal{S}_{15}|$ | $|\mathcal{S}_p|$ | $|SB|$ greedy | LB-LP | LB-Schönheim |
|-----|---------------------|-------------------|---------------|-------|--------------|
| 14  | 3.268.760           | 4.457.400         | 532.555       | 297.160 | 297.172    |
| 13  | 3.268.760           | 5.200.300         | ~90.000       | 49.527  | 58.887     |
| 12  | 3.268.760           | 5.200.300         | ~20.000       | 11.430  | 13.175     |
| 11  | 3.268.760           | 4.457.400         | ~5.000        | 3.266   | 3.370      |

### O que distingue este problema de Set Cover genérico

Este é um caso especial de **Covering Design** — campo com literatura própria
e tabelas de soluções ótimas conhecidas (La Jolla Covering Repository, Dan Gordon, 2023).
A simetria combinatória do problema implica propriedades que técnicas genéricas não exploram:
- Todos os conjuntos candidatos têm o mesmo tamanho ($k = 15$)
- Todos os alvos têm o mesmo tamanho ($p$)
- A cobertura $\binom{k}{p}$ é idêntica para todo $X \in \mathcal{S}_{15}$ inicialmente

---

## 2. Tabela Comparativa das Abordagens Fortes

| Abordagem | Ideia central | Quando aplicar | Tipo de redução | Garantia teórica | Risco/Limitação | Referência | Aplicabilidade |
|-----------|--------------|----------------|-----------------|------------------|-----------------|------------|----------------|
| **FPT** | $f(k) \cdot n^{O(1)}$; parametrizar por solução pequena | Quando parâmetro $k = |SB|$ é pequeno | Complexidade exponencial migra para $f(k)$, poly em $n$ | Exato em FPT se $f(k)$ viável | Set Cover é **W[2]-hard** — sem FPT a não ser que FPT=W[2]; $k \approx 532$K inviável | Downey & Fellows; Cygan et al. 2015 | **Baixa** |
| **Kernelização** | Pré-processar até núcleo de tamanho $g(k)$ em tempo poly | Quando redução da instância é viável | Tamanho da instância | Exato se kernel exato | Set Cover não tem kernel polinomial (OR-composition); sem kernel polinomial salvo P ⊆ coNP/poly | Fomin, Lokshtandt, Saurabh, Zehavi 2019 | **Baixa** |
| **Aproximação** | $H(n)$-aproximação greedy; LP + rounding | Sempre que solução próxima do ótimo é aceitável | Custo computacional exponencial por polinomial | $H(|\mathcal{S}_p|) \approx \ln|\mathcal{S}_p| \approx 15{,}4\times$ | Feige (1998): $\ln n$ é ótimo — sem fator constante; perda de otimalidade | Vazirani 2001; Williamson & Shmoys 2011; Feige 1998 | **Alta — já implementado** |
| **Decomposição Estrutural** | Explorar treewidth, planaridade, hierarquia de grafo | Grafos com estrutura especial | Complexidade exponencial em treewidth | Exact em treewidth limitado | O hipergrafo $(\mathcal{S}_{15}, \mathcal{S}_p)$ tem $|\mathcal{S}_{15}|$ hipervértices — treewidth provavelmente alto; não é grafo plano | Robertson & Seymour; Demaine & Hajiaghayi | **Baixa** — não é problema de grafo |
| **Coresets** | Substituir entrada por subconjunto ponderado pequeno | Clustering, métricas, geometria | Tamanho da instância de forma aproximada | $\varepsilon$-aproximação com $|coreset| \ll n$ | Não se aplica naturalmente a Set Cover combinatório sem estrutura métrica | Agarwal, Har-Peled & Varadarajan 2005; Phillips 2016 | **Baixa** |
| **Sketching** | Resumo probabilístico de baixa dimensão | Grandes conjuntos de constraints redundantes | Espaço e tempo de processamento | Controla erro com probabilidade | Para Set Cover, o sketch de $\mathcal{S}_p$ via amostragem aleatória pode gerar candidatos; não garante cobertura total | Cormode & Muthukrishnan 2005; Woodruff 2014 | **Média** — útil para verificação amostral |
| **Streaming/Sublinear** | Processar sem armazenar tudo; 1-2 passes | Dados massivos em fluxo | Memória | Aproximação controlada | Precisa de múltiplos passes para Set Cover; instância fixa (não é streaming de eventos) | Muthukrishnan 2005; Goldreich & Ron | **Baixa** — dados estão em memória |
| **Sparsificação** | Remover arestas/restrições preservando estrutura | Grafos ou sistemas lineares esparsos | Tamanho do grafo | Preserva cortes/forma quadrática | Set Cover é um hipergrafo; não é sistema linear com Laplaciano; restrições são binárias — pouca sparsificação útil | Spielman & Teng; Benczúr & Karger | **Baixa** — não é problema de grafo/fluxo |

### Nota sobre Covering Designs (abordagem especializada)

A abordagem mais poderosa aqui **não está na lista genérica**, mas é essencial:

**Covering Designs / Teoria de Designs Combinatórios:**
- $C(25, 15, p)$ é um problema de *Lotto Design* / *Covering Number*
- O **La Jolla Covering Repository** (Dan Gordon, 2023) contém soluções ótimas ou próximas para centenas de instâncias
- Verificar se $C(25, 15, 14)$, $C(25, 15, 13)$, etc. têm soluções conhecidas
- Aplicabilidade: **Alta** — pode fornecer o ótimo sem computação

---

## 3. Tabela das Abordagens Práticas

> Estas técnicas podem reduzir significativamente o tempo real, a memória, a robustez e a escalabilidade prática, mas **não alteram a complexidade assintótica no pior caso**.

| Abordagem | Ideia central | Potencial de melhoria prática | Limitação | Referência | Aplicabilidade |
|-----------|--------------|-------------------------------|-----------|------------|----------------|
| **Algorithm Engineering** | Estruturas de dados cache-friendly, paralelismo, profiling, SIMD | **Enorme**: $\approx 100\text{–}300\times$ com C/Cython; $\approx 8\times$ com paralelismo 8 núcleos | Não muda $O(\cdot)$; custo de implementação | Sanders; Kliemann & Sanders 2016 | **Alta — parcialmente feito** (bitmasks, numpy, heap lazy, argmax auto) |
| **Algorithm Portfolios** | Selecionar algoritmo baseado em características da instância | Evita escolha subótima para cada $p$ | Overhead de classificação; instâncias similares | Lin Xu, Hutter, Hoos & Leyton-Brown (SATzilla) | **Alta — já implementado** (seleção heap vs argmax pelo limiar 10.000) |
| **Configuração Automática** | Bayesian optimization, SMAC, irace para tuning de hiperparâmetros | Otimizar limiar de 10.000 updates/iter; tamanho de batch de verificação | Custo de execução de benchmarks para tuning | Hutter, Hoos & Leyton-Brown; SMAC 3 | **Média** — limiar atual é empírico; SMAC poderia ajustar |
| **SAT/SMT Solvers** | Codificar Set Cover como MaxSAT; CDCL + clause learning | Para conjuntos menores de candidatos (pós-greedy), pode encontrar ótimo exato | 3,27M variáveis = inviável diretamente; apenas viável pós-greedy com $|SB_{\text{greedy}}|$ variáveis | Moskewicz et al. 2001 (Chaff); de Moura & Bjørner 2008 (Z3) | **Média** — viável sobre candidatos do greedy |
| **CP-SAT (OR-Tools)** | Solver híbrido CP/LP/SAT com cortes, propagação e Lazy Clause Generation | Mais eficiente que SCIP puro para problemas estruturados; escalável até milhões de vars com boas propagações | Setup necessita expertise; ainda limitado pela escala de $\mathcal{S}_{15}$ diretamente | Perron, Didier & Gay 2023 (OR-Tools CP-SAT-LP) | **Alta** — alternativa direta ao PySCIPOpt; mais robusta em escala |

---

## 4. Estratégia Recomendada em Camadas

### Camada 1 — Identificar estrutura e parâmetros

1. Verificar **La Jolla Covering Repository** para $C(25, 15, p)$ — pode estar resolvido otimamente
2. Calcular lower bounds: LP ($\lceil \binom{25}{p}/\binom{15}{p} \rceil$) e Schönheim
3. Identificar parâmetro natural: $k^* = |OPT|$ (muito grande para FPT direto)

### Camada 2 — FPT/Kernelização/Decomposição estrutural

- Set Cover é W[2]-hard: **não aplicável** para otimalidade
- Porém: a **estrutura combinatória** (todos os conjuntos de tamanho igual) permite
  redução da instância por dominância e LP relaxation
- Domination reduction: se $Y_1, Y_2 \in \mathcal{S}_p$ têm exatamente os mesmos conjuntos cobrindo, mesclar

### Camada 3 — Aproximação / Coresets

- **Greedy H(n)-aproximação:** implementado — resultado para $p=14$: gap $1{,}79\times$ (ótimo teórico: $\leq 15{,}4\times$)
- **LP relaxation + randomized rounding:** arredondamento aleatório com probabilidade proporcional à solução fracionária do LP; pode atingir $O(\log n)$-aproximação com esperança menor de candidatos que greedy puro
- **LP direta**: para $p=12$ e $p=11$ onde $|SB|$ é menor, a LP pode ser resolvida e arredondada

### Camada 4 — Streaming / Sublinear

- Não diretamente aplicável (instância fixa, não streaming)
- Porém: a **geração lazy** de $\mathcal{S}_p$ (já implementada) é o equivalente do modelo streaming

### Camada 5 — Implementação prática

| Prioridade | Técnica | Ganho esperado |
|------------|---------|---------------|
| 1 | Algorithm Engineering: Cython/C extension para o loop interno | $\approx 200\times$ (p=11: de 6h → 2min) |
| 2 | CP-SAT (OR-Tools) pós-greedy para $p \in \{11, 12\}$ | Ótimo sobre candidatos em minutos |
| 3 | Paralelismo (multiprocessing) nas extensões de Y | $\approx 8\times$ em 8 núcleos |
| 4 | Rebuild periódico do heap para $p=13$ | Evita inflação de 624M entradas |

---

## 5. Plano de Experimento

### Métricas de avaliação

| Métrica | Greedy | ILP pós-greedy | Randômico |
|---------|--------|----------------|-----------|
| Tempo assintótico | $O(K \cdot \binom{15}{p} \cdot \binom{10+p}{15-p})$ | NP-hard (espaço reduzido) | $O(T \cdot N_{15} \cdot N_p)$ |
| Tempo real (p=14) | ~18 min | ~300s (SCIP, candidatos greedy) | ~45 min × T tentativas |
| Memória | ~100 MB | ~500 MB (modelo ILP) | ~100 MB |
| Qualidade ($|SB|/|OPT|$) | $\leq H(N_p) \approx 15{,}4\times$; observado $1{,}79\times$ | Ótimo sobre candidatos | Sem garantia; $\approx 1{,}4\times$ sobre greedy |
| Escalabilidade | Degrada como $\binom{15}{p}\binom{25-p}{15-p}$ | Inviável direto em $\mathcal{S}_{15}$ | Linear em tentativas T |

### Benchmarks propostos

1. **Instância de validação:** $n=15, k=11, p=10$ — ótimo calculável por ILP exato
2. **Instâncias progressivas:** $n \in \{20, 22, 25\}$, $k = n-10$, $p = k-1$ — curva de escala
3. **Variação do parâmetro:** fixar $n=25, k=15$, variar $p$ de 14 a 7 — análise de sensibilidade
4. **Comparativo de estratégia:** heap lazy vs argmax vs argmax paralelo vs C extension

### Sensibilidade ao parâmetro $p$

| $p$ | $\binom{15}{p}\binom{25-p}{15-p}$ | Custo/iter (Python) | Tempo total observado |
|-----|-----------------------------------|--------------------|-----------------------|
| 14  | 165                               | ~1,1 ms            | ~18 min               |
| 13  | 6.930                             | ~25 ms             | ~1,5h                 |
| 12  | 130.130                           | ~130 ms            | ~3h                   |
| 11  | 1.366.365                         | ~2.300 ms          | ~6h                   |

---

## 6. Conclusão Executiva

### Classificação final das abordagens

| Posição | Abordagem | Justificativa |
|---------|-----------|--------------|
| **Mais promissora** | **Algorithm Engineering (C/Cython + paralelismo)** | Não muda $O(\cdot)$, mas reduz tempo de 6h para ~2min para $p=11$. Implementável sem alterar a solução matemática. |
| **Segunda melhor** | **CP-SAT (OR-Tools) pós-greedy** | Alternativa ao PySCIPOpt que demonstrou ser mais robusta em escala. Sobre os ~5.000 candidatos do $p=11$, encontra ótimo em minutos. |
| **Baixo risco para protótipo** | **Greedy com aproximação $H(n)$** | Já implementado; gap observado de $1{,}79\times$ muito melhor que garantia teórica $15{,}4\times$; cobertura completa garantida. |
| **Maior impacto teórico** | **Teoria de Covering Designs (La Jolla Repository)** | Possibilidade de consultar soluções ótimas conhecidas para $C(25, 15, p)$; o campo tem 60 anos de literatura específica. |
| **Maior impacto prático** | **Seleção automática de estratégia (algorithm portfolio)** | O limiar heap/argmax em 10.000 updates/iter já reduz tempo de execução; extensível para portfolio completo (greedy → ILP → CP-SAT). |

### Observação crítica sobre o problema

> Este não é um problema de Set Cover genérico. É um **Covering Design $C(n, k, t)$** — campo matemático com 60 anos de história e tabelas de valores ótimos. Antes de qualquer implementação adicional, a primeira ação de alto valor seria consultar o **La Jolla Covering Repository** (ljcrep.org) para $C(25, 15, 14)$, $C(25, 15, 13)$, $C(25, 15, 12)$ e $C(25, 15, 11)$. Se os ótimos já forem conhecidos, o trabalho se transforma em **verificação e reprodução**, não descoberta.

### Quando usar cada abordagem

- **FPT/Kernelização:** não aplicáveis — problema W[2]-hard sem estrutura paramétrica favorável
- **Aproximação:** já implementada (greedy); gap real muito bom ($1{,}79\times$ para $p=14$)
- **Decomposição estrutural:** não aplicável — hipergrafo sem baixo treewidth
- **Coresets/Sketching/Streaming:** não aplicáveis ao objetivo exato; úteis apenas para verificação amostral (já implementada)
- **Sparsificação:** não aplicável — não é problema de grafo/fluxo
- **Algorithm Engineering:** **implementar primeiro** — maior retorno por hora de desenvolvimento
- **CP-SAT:** **segunda prioridade** — substitui PySCIPOpt com melhor escala

---

*Análise produzida com referência a: Cygan et al. 2015; Fomin et al. 2019; Vazirani 2001; Williamson & Shmoys 2011; Feige 1998; Cormode & Muthukrishnan 2005; Spielman & Teng; Perron et al. 2023; Gordon 2023 (La Jolla).*
