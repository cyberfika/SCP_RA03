# Prompt — Geração de Slides RA03 (Claude Design)

Crie uma apresentação de slides completa em HTML/CSS (artifact) para uma
apresentação acadêmica de 10 minutos. Design dark, profissional, navegável
por botões Anterior/Próximo. Cada slide deve caber em 1 tela sem scroll.

---

# CONTEXTO

Disciplina: Complexidade de Algoritmos — PUCPR (5º período)
Professor: Edson Emílio Scalabrin
Trabalho: RA03 — Cobertura de Combinações (Minimum Set Cover)

A apresentação DEVE cobrir obrigatoriamente:
1. Modelagem do problema
2. Estratégia algorítmica adotada
3. Estruturas de dados utilizadas
4. Resultados obtidos
5. Análise de complexidade (tempo, espaço, gargalos, escalabilidade, comparação)
6. Limitações e possíveis melhorias

---

# SLIDES (9 no total)

## Slide 1 — Modelagem do Problema
- Universo U = {1, 2, ..., 25}
- S_15 = todos os subconjuntos de tamanho 15 de U → C(25,15) = 3.268.760 conjuntos
- S_p  = todos os subconjuntos de tamanho p de U
- Cardinalidades:

| Conjunto | Fórmula    | Cardinalidade |
|----------|------------|---------------|
| S_15     | C(25,15)   | 3.268.760     |
| S_14     | C(25,14)   | 4.457.400     |
| S_13     | C(25,13)   | 5.200.300     |
| S_12     | C(25,12)   | 5.200.300     |
| S_11     | C(25,11)   | 4.457.400     |

- Objetivo formal: para cada p ∈ {14,13,12,11}, encontrar o menor SB ⊆ S_15 tal que:
    ∀ Y ∈ S_p,  ∃ X ∈ SB  tal que  Y ⊆ X
- Formulação ILP:
    Variáveis: x_i ∈ {0,1} para cada X_i ∈ S_15
    Minimizar:  Σ x_i
    Sujeito a:  Σ_{i: Y⊆X_i} x_i ≥ 1,  ∀ Y ∈ S_p
- Este é o Minimum Set Cover — NP-difícil (Karp, 1972)

## Slide 2 — Por que ILP Direto é Inviável?
- O ILP cresce em escala proibitiva:

| p  | Variáveis | Restrições  | Coeficientes não-nulos | Viável? |
|----|-----------|-------------|------------------------|---------|
| 14 | 3.268.760 | 4.457.400   | ~67 milhões            | ✗       |
| 13 | 3.268.760 | 5.200.300   | ~546 milhões           | ✗       |
| 12 | 3.268.760 | 5.200.300   | ~2,37 bilhões          | ✗       |
| 11 | 3.268.760 | 4.457.400   | ~6,08 bilhões          | ✗       |

- Força bruta: 2^3.268.760 possibilidades → impossível
- Inaproximável abaixo de (1-ε)·ln(n) a menos que P=NP (Feige, 1998)
- Solução: algoritmo greedy com garantia teórica de ln(n)-aproximação

## Slide 3 — Lower Bounds (base para medir qualidade)
- Lower Bound LP: cada X ∈ S_15 cobre exatamente C(15,p) subconjuntos de tamanho p
    |SB| ≥ ⌈ C(25,p) / C(15,p) ⌉    (prova: contagem direta)
- Lower Bound Schönheim (1964): L(n,k,t) = ⌈(n/k)·L(n-1,k-1,t-1)⌉ — mais apertado

| p  | C(15,p)  | LB-LP   | LB-Schönheim |
|----|----------|---------|--------------|
| 14 | 15       | 297.160 | 297.172      |
| 13 | 105      | 49.527  | 58.887       |
| 12 | 455      | 11.430  | 13.175       |
| 11 | 1.365    | 3.266   | 3.370        |

- Insight: p=11 exige SB mínimo de apenas ~3.370 elementos de 3,3 milhões disponíveis
- Paradoxo: menor p → SB menor, mas mais trabalho por iteração do greedy

## Slide 4 — Estruturas de Dados
Quatro estruturas centrais, todas indexadas por bitmask uint32:

1. BITMASK uint32 (representação de subconjuntos)
   - Cada subconjunto de {1..25} → inteiro de 25 bits
   - Verificar Y ⊆ X: (X & Y) == Y  →  O(1)
   - Arrays NumPy de uint32: S_15 ocupa 13 MB; S_p ocupa até 21 MB

   | Operação        | frozenset | bitmask | Ganho |
   |-----------------|-----------|---------|-------|
   | Verificar Y ⊆ X | O(p)      | O(1)    | ~15×  |
   | Vetorizar NumPy | ✗         | ✓       | ~100× |
   | Memória/elemento| ~300 bytes| 4 bytes | ~75×  |

2. DICIONÁRIOS HASH s15_index e sp_index
   - s15_index: bitmask → índice em S_15  (3,3M entradas, lookup O(1))
   - sp_index:  bitmask → índice em S_p   (até 5,2M entradas, lookup O(1))
   - Construção: O(|S_15| + |S_p|) — fase de pré-processamento

3. ARRAY count[i]  (int32, tamanho |S_15|)
   - count[i] = número de Y ∈ S_p ainda não cobertos que X_i cobre
   - Inicializado com C(15,p) para todo i
   - Decrementado a cada Y coberto pelos vizinhos de X*
   - Permite encontrar argmax sem recomputar tudo

4. HEAP LAZY (max-heap via valores negativos) — usado para p=14 e p=13
   - Entradas: (−count[i], i) — o menor negativo é o maior count
   - Evita percorrer o array inteiro para encontrar o máximo
   - "Lazy": entradas desatualizadas são descartadas no pop
   - Alternativa para p=12,11: NumPy argmax vetorizado (mais rápido quando
     há muitas atualizações por iteração)

5. ARRAY nao_coberto[j]  (bool, tamanho |S_p|)
   - nao_coberto[j] = True se Y_j ainda não foi coberto
   - Permite ignorar Y já cobertos em O(1) por lookup

## Slide 5 — Estratégia Algorítmica (Greedy)
- Pseudocódigo formal:
  ```
  Entrada: S_15, S_p
  Pré-proc: construir s15_index, sp_index, count[], nao_coberto[]
  SB ← ∅
  enquanto ∃ j com nao_coberto[j]:
      X* ← argmax_i count[i]          // heap lazy ou numpy argmax
      SB ← SB ∪ {X*};  count[X*] ← −1
      para cada combo Y de p elementos de X*:
          se nao_coberto[sp_index[Y]]:
              nao_coberto[sp_index[Y]] ← False
              para cada X que contém Y:   // C(25-p, 15-p) extensões
                  count[s15_index[X]] -= 1
                  atualizar heap (se heap lazy)
  retornar SB
  ```
- Garantia de aproximação (Johnson 1974, Lovász 1975):
    |SB_greedy| ≤ H(|S_p|) · |OPT|  onde H(m) ≈ ln(m) + 0,577
    Para |S_p| = 4,5M: garantia ≤ 15,4× |OPT|
- Esta é a melhor razão polinomial possível (Feige 1998; Dinur & Steurer 2014)
- Duas estratégias de argmax selecionadas automaticamente:
  - Heap lazy    → p=14,13 (poucas atualizações/iter: ≤ 6.930)
  - NumPy argmax → p=12,11 (muitas atualizações/iter: > 130.000)

## Slide 6 — Análise de Complexidade: Tempo e Espaço
Notação: N15 = C(25,15) = 3.268.760 | Np = C(25,p) | K = |SB_greedy|

PROGRAMA 1 — Geração de S_p:
| Métrica       | Complexidade           | Justificativa                    |
|---------------|------------------------|----------------------------------|
| Tempo         | Θ(C(n,p))              | Enumera cada combinação 1 vez    |
| Espaço (lazy) | Θ(p)                   | Pilha do iterador                |
| Espaço (array)| Θ(C(n,p))              | Armazena todos os bitmasks       |

PROGRAMAS 2–5 — Greedy Set Cover:
| Métrica           | Heap lazy (p=14,13)                      | NumPy argmax (p=12,11)             |
|-------------------|------------------------------------------|------------------------------------|
| Pré-processamento | O(N15 + Np)                              | O(N15 + Np)                        |
| Argmax por iter   | O(log N15) amortizado                    | O(N15)                             |
| Atualizações/iter | O(C(15,p)·C(25-p,15-p))                 | O(C(15,p)·C(25-p,15-p))           |
| Tempo total       | O(K·C(15,p)·C(25-p,15-p)·log N15)       | O(K·(C(15,p)·C(25-p,15-p)+N15))  |
| Espaço            | O(N15 + Np)                              | O(N15 + Np)                        |
| Ω (melhor caso)   | Ω(N15 + Np)                              | Ω(N15 + Np)                        |

Valores concretos de C(15,p)·C(25-p,15-p) por iteração:
| p  | C(15,p) | C(25-p,15-p) | Produto (updates/iter) | K (obtido) |
|----|---------|--------------|------------------------|------------|
| 14 | 15      | 11           | 165                    | 532.555    |
| 13 | 105     | 66           | 6.930                  | 128.827    |
| 12 | 455     | 286          | 130.130                | 38.100     |
| 11 | 1.365   | 1.001        | 1.366.365              | 12.733     |

## Slide 7 — Gargalos, Escalabilidade e Comparação
GARGALOS PRINCIPAIS:
1. Atualizações de count por iteração: cresce como C(15,p)·C(25-p,15-p)
   → p=11: 1,37M operações por iteração (dominante)
2. Heap lazy: operações de push acumulam entradas obsoletas (memória extra)
3. Construção de índices: O(N15 + Np) mas executada 1 vez — 14–30s na prática
4. Para p=12,11: NumPy argmax percorre 3,3M elementos/iter → custo O(N15) por iter

ESCALABILIDADE:
- A solução escala linearmente em memória: O(N15 + Np) ≈ 30–60 MB total ✓
- Tempo NÃO escala bem com n crescente: C(n,k) cresce exponencialmente em n
- Para n=30: C(30,15) = 155M → inviável com a abordagem atual
- Limite prático: n ≤ 26–27 com hardware convencional

COMPARAÇÃO ENTRE ESTRATÉGIAS:
| Abordagem      | Tempo       | Espaço     | Garante ótimo? | Gap observado |
|----------------|-------------|------------|----------------|---------------|
| Força bruta    | Ω(2^N15)    | O(N15)     | ✓              | 1,00×         |
| ILP direto     | NP (exp.)   | O(N15·Np)  | ✓              | 1,00×         |
| Greedy heap    | ver tabela  | O(N15+Np)  | ✗ (ln n)       | 1,79–2,19×    |
| Greedy argmax  | ver tabela  | O(N15+Np)  | ✗ (ln n)       | 2,89–3,78×    |
| Randômico      | O(T·N15·Np) | O(N15+Np)  | ✗ (nenhuma)    | —             |

## Slide 8 — Resultados Obtidos
Tabela central (destaque visual máximo):

| p  | |S_p|      | LB-LP   | LB-Schönheim | |SB_greedy| | Gap vs LB-Sch | Tempo   | % de S_15 |
|----|-----------|---------|--------------|------------|---------------|---------|-----------|
| 14 | 4.457.400 | 297.160 | 297.172      | 532.555    | 1,79×         | ~18 min | 16,3%     |
| 13 | 5.200.300 | 49.527  | 58.887       | 128.827    | 2,19×         | ~3 h    | 3,9%      |
| 12 | 5.200.300 | 11.430  | 13.175       | 38.100     | 2,89×         | ~79 min | 1,2%      |
| 11 | 4.457.400 | 3.266   | 3.370        | 12.733     | 3,78×         | ~3,4 h  | 0,4%      |

- Garantia teórica permitia gap até 15,4× — obtivemos 1,79–3,78×
  → greedy 4–9× melhor que o pior caso teórico
- Resultado esperado pela teoria de Rödl (1985): LB-LP é assintoticamente
  apertado para instâncias uniformes C(n,k,t) quando n→∞
- Todos os resultados verificados por amostragem de cobertura (10.000 amostras aleatórias)

## Slide 9 — Limitações e Possíveis Melhorias
LIMITAÇÕES:
- ILP direto inviável em escala completa (6 bilhões de coeficientes para p=11)
- Solução ótima não garantida para p=13,14 (NP-difícil)
- Greedy não permite refinamento pós-execução (sem backtracking)
- Escalabilidade limitada: n>27 inviável com abordagem atual
- Tempo de execução alto para p=13 (~3h) e p=11 (~3,4h)

POSSÍVEIS MELHORIAS:
1. ILP pós-greedy (p=11,12): usar SB_greedy como candidatos → reduz variáveis
   de 3,3M para ~12K–38K; ILP torna-se tratável em minutos
2. Column generation: gerar variáveis do ILP sob demanda → viável para p=11
3. Paralelização: multiprocessing para calcular count[] em paralelo
   → speedup teórico ~8× em 8 núcleos (gargalo é embaraçosamente paralelo)
4. Metaheurísticas pós-greedy: simulated annealing para remover elementos
   redundantes de SB → pode reduzir o gap de 1,79× para ~1,2–1,3×
5. Simetria combinatória: o grupo S_25 age sobre o problema → redução
   por órbitas pode diminuir o espaço de busca em até 25! / |estabilizador|

---

# AMBIENTE DE EXECUÇÃO (hardware real onde os experimentos foram rodados)

- Dispositivo: Dell OptiPlex 9020
- Processador: Intel Core i7-4770 @ 3,40 GHz (4 núcleos / 8 threads)
- RAM: 32 GB
- Placa gráfica: Intel HD Graphics 4600 (sem GPU dedicada — processamento 100% CPU)
- Armazenamento: HDD/SSD, 6,82 TB total
- Sistema operacional: Windows 11 Pro 64 bits

Mencionar no Slide 8 (Resultados) como nota de rodapé da tabela:
"Experimentos executados em Intel Core i7-4770 @ 3,40 GHz, 32 GB RAM, sem GPU."

---

# REQUISITOS DE DESIGN

- 9 slides navegáveis (botões ← Anterior / Próximo → + "Slide N de 9")
- Fundo: #0f1117; texto: #e2e8f0; destaque: #38bdf8 (azul ciano)
- Tabelas: cabeçalho em #1e3a5f, linhas alternadas #1a1f2e / #141820
- Slide 8 (resultados): tabela com borda destacada e fonte ligeiramente maior
- Código/pseudocódigo: fundo #1e1e2e, fonte monospace, syntax highlight simples
- Fórmulas matemáticas: fonte monospace em cor de destaque
- Fonte: system-ui / Inter / Segoe UI
- Rodapé fixo em todos os slides: "PUCPR · Complexidade de Algoritmos · RA03 · 2026"
- Slide atual destacado visualmente no rodapé (ex: ● ○ ○ ○ ...)
