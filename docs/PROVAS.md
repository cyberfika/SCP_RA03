# Provas Formais — RA03 Cobertura de Combinações
**PUCPR — Complexidade de Algoritmos**

---

## Índice

1. Definições e Notação
2. Prova: NP-dificuldade do Set Cover
3. Prova: Lower Bound por Relaxação Linear (LP)
4. Prova: Lower Bound de Schönheim
5. Prova: Corretude do Algoritmo Greedy
6. Prova: Razão de Aproximação do Greedy — H(|Sp|) · |OPT|
7. Prova: O gap de 1,79× (p=14) é consistente com a teoria
8. Prova: Complexidade de Tempo do Greedy

---

## 1. Definições e Notação

```
U   = {1, 2, ..., 25}           universo
Sk  = { X ⊆ U | |X| = k }       conjunto de todas as combinações de tamanho k
Sp  = { Y ⊆ U | |Y| = p }       conjunto de todas as combinações de tamanho p
SB  ⊆ S15                        subconjunto de cobertura procurado
OPT = solução ótima (mínimo |SB|)
```

O problema é:
```
Dado S15 e Sp, encontrar o menor SB ⊆ S15 tal que:
∀ Y ∈ Sp, ∃ X ∈ SB com Y ⊆ X
```

Este é uma instância do problema clássico **Minimum Set Cover**:
- Universo de elementos: Sp (as combinações a cobrir)
- Família de conjuntos: { {Y ∈ Sp | Y ⊆ X} | X ∈ S15 }

---

## 2. Prova: NP-dificuldade do Set Cover

**Teorema:** Minimum Set Cover é NP-difícil.

**Prova (redução de Vertex Cover):**

Dado grafo G = (V, E) e inteiro k, construímos uma instância de Set Cover:
- Universo: U' = E (arestas do grafo)
- Para cada vértice v ∈ V, definir S_v = { e ∈ E | v é extremo de e }
- Pergunta: existe cobertura de conjuntos de tamanho ≤ k?

**Equivalência:**
- (→) Se C ⊆ V é vertex cover de tamanho k, então { S_v | v ∈ C } é set cover de tamanho k, pois toda aresta e = {u,v} tem u ∈ C ou v ∈ C, logo e ∈ S_u ou e ∈ S_v.
- (←) Se { S_{v1}, ..., S_{vk} } é set cover de tamanho k, então {v1,...,vk} é vertex cover, pois toda aresta e = {u,v} está em algum S_{vi}, logo vi = u ou vi = v é extremo de e.

Vertex Cover é NP-completo (Karp, 1972), portanto Set Cover é NP-difícil. □

**Corolário:** O problema de cobertura de combinações (Programas 2-5) é NP-difícil,
pois é uma instância de Set Cover com |Sp| = C(25,p) elementos e S15 como família.

---

## 3. Prova: Lower Bound por Relaxação Linear (LP)

**Lema:** |SB| ≥ ⌈ C(25,p) / C(15,p) ⌉

**Prova:**

Cada X ∈ S15 contém exatamente C(15, p) subconjuntos de tamanho p (pois |X| = 15 e
escolhemos p elementos de X de C(15,p) formas).

Todo Y ∈ Sp deve ser coberto por pelo menos um X ∈ SB.
Portanto o conjunto SB deve cobrir os C(25,p) elementos de Sp.

Como cada X ∈ SB cobre no máximo C(15,p) elementos de Sp:

```
|SB| · C(15,p) ≥ |Sp| = C(25,p)
         |SB|  ≥ C(25,p) / C(15,p)
         |SB|  ≥ ⌈ C(25,p) / C(15,p) ⌉   (pois |SB| é inteiro)
```

| p  | C(25,p)   | C(15,p) | Lower Bound LP |
|----|-----------|---------|----------------|
| 14 | 4.457.400 | 15      | 297.160        |
| 13 | 5.200.300 | 105     | 49.527         |
| 12 | 5.200.300 | 455     | 11.430         |
| 11 | 4.457.400 | 1.365   | 3.266          |

□

---

## 4. Prova: Lower Bound de Schönheim

**Definição:** O número de cobertura C(n, k, t) é o menor |SB| tal que todo
t-subconjunto de {1..n} está contido em algum elemento de SB ⊆ C(n,k).

**Teorema (Schönheim, 1964):** C(n, k, t) ≥ L(n, k, t), onde:
```
L(n, k, t) = ⌈ (n/k) · L(n-1, k-1, t-1) ⌉
L(t, t, t) = 1   (caso base)
L(k, k, t) = 1   (caso base)
```

**Prova (por indução em n-t):**

*Caso base:* n = t. Só existe um t-subconjunto de {1..t}: o próprio {1..t}.
Um k-subconjunto de {1..t} com k = t contém {1..t}. Logo L(t,t,t) = 1. ✓

*Passo indutivo:* Seja SB uma cobertura ótima de C(n,k,t), com |SB| = C(n,k,t).

Fixe um elemento x ∈ {1..n}. Particione SB em:
- SB_x = { X ∈ SB | x ∈ X }     (conjuntos que contêm x)
- SB_x' = { X ∈ SB | x ∉ X }    (conjuntos que não contêm x)

Todo t-subconjunto Y contendo x deve ser coberto. O elemento x aparece
em C(n-1, k-1) membros de S_k (os outros k-1 elementos de X são escolhidos
de {1..n}\{x}). Por dupla contagem:

```
|SB_x| · C(k-1, t-1) ≥ C(n-1, t-1)
               |SB_x| ≥ C(n-1,t-1) / C(k-1,t-1)
```

Os conjuntos de SB_x, ao remover x, formam uma cobertura de (t-1)-subconjuntos
de {1..n}\{x}. Logo:

```
|SB_x| ≥ C(n-1, k-1, t-1) ≥ L(n-1, k-1, t-1)   (por hipótese de indução)
```

Como cada x ∈ {1..n} deve ser representado, e cada X ∈ SB contribui com k elementos:

```
n · |SB_x|  ≥  n · L(n-1, k-1, t-1)
                        mas conta x de forma redundante
|SB| = |SB_x| + |SB_x'| ≥ ...
```

Pela média sobre todos os x ∈ {1..n}:
```
∑_{x} |SB_x| = k · |SB|   (cada X contribui com k elementos)
Média: k · |SB| / n = |SB_x̄|
|SB_x̄| ≥ L(n-1, k-1, t-1)  para algum x
Logo: k · |SB| / n ≥ L(n-1, k-1, t-1)
      |SB| ≥ (n/k) · L(n-1, k-1, t-1)
      |SB| ≥ ⌈ (n/k) · L(n-1, k-1, t-1) ⌉   (inteiro)
```

Portanto C(n,k,t) ≥ L(n,k,t). □

**Valores calculados para nosso problema (n=25, k=15):**

| p  | L(25,15,p) |
|----|------------|
| 14 | 297.172    |
| 13 | 58.887     |
| 12 | 13.175     |
| 11 | 3.370      |

Observe que o lower bound de Schönheim é mais apertado que o LP para p=13,12,11.

---

## 5. Prova: Corretude do Algoritmo Greedy

**Algoritmo (formal):**
```
Entrada: S15, Sp
Saída: SB ⊆ S15

SB ← ∅
N ← Sp   (conjunto de Y's não cobertos)

enquanto N ≠ ∅:
    X* ← argmax_{X ∈ S15} |{ Y ∈ N : Y ⊆ X }|
    SB ← SB ∪ {X*}
    N  ← N \ { Y ∈ N : Y ⊆ X* }
retornar SB
```

**Teorema:** O algoritmo greedy termina e retorna um SB válido.

**Prova:**

*Terminação:* A cada iteração, |N| decresce estritamente. De fato, X* é escolhido
pois cobre pelo menos um Y ∈ N (caso contrário N = ∅ e o loop não executaria).
Como |N| é inteiro e decresce estritamente, o algoritmo termina em no máximo |Sp|
iterações.

*Corretude:* Ao término, N = ∅ por definição do loop. Portanto todo Y ∈ Sp foi
removido de N em alguma iteração, o que ocorre somente quando Y ⊆ X* para o X*
selecionado naquela iteração. Logo Y está coberto por algum X ∈ SB. □

---

## 6. Prova: Razão de Aproximação do Greedy — H(|Sp|) · |OPT|

**Teorema:** Seja G o algoritmo greedy e OPT a solução ótima. Então:
```
|SB_greedy| ≤ H(|Sp|) · |OPT|
```
onde H(m) = 1 + 1/2 + 1/3 + ... + 1/m ≤ ln(m) + 1 é o m-ésimo número harmônico.

**Prova (Johnson 1974, Lovász 1975):**

Seja m = |Sp|. Numere os elementos de Sp na ordem em que são cobertos pelo greedy:
y_1, y_2, ..., y_m (y_1 é o primeiro coberto, y_m o último).

Atribua a cada y_i um **custo** c(y_i) = 1 / (número de y's cobertos quando y_i foi coberto).

Se y_i é coberto na t-ésima iteração juntamente com d_t outros elementos novos,
então c(y_i) = 1/d_t para todos esses elementos.

**Observação 1:** O custo total é exatamente |SB_greedy|:
```
∑_i c(y_i) = ∑_{iterações t} d_t · (1/d_t) = ∑_{iterações t} 1 = |SB_greedy|
```

**Observação 2:** Para cada X ∈ OPT, sua contribuição ao custo total é ≤ H(|X ∩ Sp|).

*Prova da Observação 2:* Considere X ∈ OPT com |X ∩ Sp| = s. Ordenando os
elementos de X ∩ Sp na ordem em que são cobertos pelo greedy: z_1, ..., z_s.

Quando z_j está prestes a ser coberto, ainda há pelo menos s - j + 1 elementos
de X ∩ Sp não cobertos. O greedy escolhe o X* que maximiza a cobertura de N.
Como X ∈ S15 cobre pelo menos s - j + 1 elementos de N, o greedy cobre pelo
menos s - j + 1 elementos na iteração em que z_j é coberto:

```
c(z_j) ≤ 1 / (s - j + 1)
```

Logo a contribuição de X ao custo é:
```
∑_{j=1}^{s} c(z_j) ≤ ∑_{j=1}^{s} 1/(s-j+1) = 1/s + 1/(s-1) + ... + 1 = H(s) ≤ H(m)
```

**Conclusão:**
```
|SB_greedy| = ∑_i c(y_i) = ∑_{X ∈ OPT} (contribuição de X) ≤ |OPT| · H(m)
```

Portanto:
```
|SB_greedy| ≤ H(|Sp|) · |OPT| ≤ (ln|Sp| + 1) · |OPT|
```
□

**Corolário:** Para p = 14, |Sp| = C(25,14) = 4.457.400:
```
|SB_greedy| ≤ H(4.457.400) · |OPT| ≈ (ln(4.457.400) + 1) · |OPT| ≈ 16,3 · |OPT|
```

Portanto |OPT| ≥ |SB_greedy| / 16,3 = 532.555 / 16,3 ≈ 32.671.
Mas o lower bound LP já diz |OPT| ≥ 297.160. O LP é mais informativo aqui.

**Observação:** A razão de aproximação H(m) = ln(m) é assintoticamente ótima —
não existe algoritmo polinomial com razão (1-ε)·ln(m) para nenhum ε > 0,
a menos que P = NP (Feige, 1998; Dinur & Steurer, 2014).

---

## 7. Prova: O Gap de 1,79× (p=14) é Consistente com a Teoria

**Afirmação:** O gap observado de |SB_greedy| / |OPT| = 532.555 / 297.160 ≈ 1,79
não contradiz nenhuma das provas anteriores.

**Prova:**

O Teorema da Seção 6 garante:
```
|SB_greedy| / |OPT| ≤ H(|Sp|) ≈ ln(4.457.400) + 1 ≈ 16,3
```

Portanto 1,79 ≤ 16,3. ✓ Nenhuma contradição.

O lower bound LP (Seção 3) garante |OPT| ≥ 297.160. Portanto:
```
gap_real = |SB_greedy| / |OPT| ≥ |SB_greedy| / (upper_bound_on_OPT)
         ≤ |SB_greedy| / 297.160 = 532.555 / 297.160 ≈ 1,79
```

O gap de 1,79× é um upper bound no gap real (pois 297.160 pode ser menor que |OPT|).
O gap real satisfaz:
```
1,00 ≤ gap_real ≤ 1,79
```

Para determinar o gap exato seria necessário resolver o problema de otimização
exata (ILP), que é NP-difícil. □

---

## 8. Prova: Complexidade de Tempo do Greedy

**Teorema:** O algoritmo greedy para nossa instância tem complexidade de tempo:
```
O( K · C(15,p) · C(25-p, 15-p) · log(C(25,15)) )   com heap lazy
O( K · C(15,p) · C(25-p, 15-p) + K · C(25,15) )    com numpy argmax
```
onde K = |SB_greedy|.

**Prova:**

*Pré-processamento:* Construção dos índices hash para S15 e Sp: O(C(25,15) + C(25,p)).

*Por iteração do loop principal:*

1. Seleção do melhor X:
   - Heap lazy: amortizado O(log|S15|) = O(log C(25,15)) por pop válido
   - Numpy argmax: O(|S15|) = O(C(25,15))

2. Geração dos subconjuntos de X:
   - Enumerar C(15,p) subconjuntos de tamanho p de X (|X| = 15): O(C(15,p))
   - Para cada Y recém-coberto, gerar C(25-p, 15-p) extensões de Y até tamanho 15:
     O(C(15,p) · C(25-p, 15-p)) extensões totais

3. Atualização de count:
   - C(15,p) · C(25-p, 15-p) operações de dict lookup + decremento: O(1) cada

*Total por iteração:* O(C(15,p) · C(25-p, 15-p) + log C(25,15)) com heap.

*Total geral (K iterações):*
```
O( K · [C(15,p) · C(25-p, 15-p) + log C(25,15)] )
= O( K · C(15,p) · C(25-p, 15-p) )   pois o segundo termo é dominado
```

**Instâncias concretas:**

| p  | C(15,p)·C(25-p,15-p) | K (greedy) | Tempo estimado |
|----|-----------------------|------------|----------------|
| 14 | 15 × 11 = 165        | 532.555    | O(87,9 M ops)  |
| 13 | 105 × 66 = 6.930     | ~100.000   | O(693 M ops)   |
| 12 | 455 × 286 = 130.130  | ~25.000    | O(3,25 B ops)  |
| 11 | 1.365 × 1.001 = 1,37M| ~5.000     | O(6,84 B ops)  |

*Complexidade de espaço:* O(C(25,15) + C(25,p)) para os arrays e índices hash. □

---

## Referências

- Karp, R.M. (1972). Reducibility among combinatorial problems. *Complexity of Computer Computations*, 85-103.
- Johnson, D.S. (1974). Approximation algorithms for combinatorial problems. *JCSS*, 9(3), 256-278.
- Lovász, L. (1975). On the ratio of optimal integral and fractional covers. *Discrete Mathematics*, 13(4), 383-390.
- Schönheim, J. (1964). On coverings. *Pacific Journal of Mathematics*, 14(4), 1405-1411.
- Feige, U. (1998). A threshold of ln n for approximating set cover. *JACM*, 45(4), 634-652.
- Dinur, I., Steurer, D. (2014). Analytical approach to parallel repetition. *STOC*, 624-633.
