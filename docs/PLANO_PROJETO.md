# Plano de Projeto — RA03: Cobertura de Combinações
**PUCPR — Complexidade de Algoritmos — 5º Período**
**Professor:** Edson Emílio Scalabrin | **Entrega:** 24/06/2026

---

## 1. Definição Formal do Problema

### Universo e Conjuntos

```
U = {1, 2, 3, ..., 25}
S_p = { X ⊆ U | |X| = p }
```

| Conjunto | Fórmula    | Cardinalidade |
|----------|------------|---------------|
| S₁₅      | C(25, 15)  | 3.268.760     |
| S₁₄      | C(25, 14)  | 4.457.400     |
| S₁₃      | C(25, 13)  | 5.200.300     |
| S₁₂      | C(25, 12)  | 5.200.300     |
| S₁₁      | C(25, 11)  | 4.457.400     |

### Problema de Cobertura (Programas 2 a 5)

Para cada p ∈ {14, 13, 12, 11}, encontrar o menor subconjunto SB ⊆ S₁₅ tal que:

```
∀ Y ∈ S_p  ∃ X ∈ SB  tal que  Y ⊆ X
```

Este é um caso específico do **Minimum Set Cover**, um problema NP-difícil clássico
(Karp, 1972 — um dos 21 problemas NP-completos originais).

---

## 2. Insight Matemático Central

### Quantas combinações cada X ∈ S₁₅ cobre?

Um conjunto X de 15 elementos contém exatamente C(15, p) subconjuntos de tamanho p.

| p  | C(15, p) subconjuntos cobertos por X | Lower bound de \|SB\| |
|----|--------------------------------------|-----------------------|
| 14 | C(15, 14) = **15**                   | ≥ 4.457.400 / 15 = **297.160** |
| 13 | C(15, 13) = **105**                  | ≥ 5.200.300 / 105 = **49.527** |
| 12 | C(15, 12) = **455**                  | ≥ 5.200.300 / 455 = **11.429** |
| 11 | C(15, 11) = **1.365**                | ≥ 4.457.400 / 1.365 = **3.265** |

### Implicação direta para a estratégia

- **p=14:** SB mínimo precisa de ~297 mil elementos de S₁₅ — ILP ingênuo é inviável.
- **p=11:** SB mínimo precisa de apenas ~3.265 elementos de S₁₅ — ILP é tratável.

A complexidade computacional **diminui à medida que p decresce**, apesar de S_p
ter cardinalidade similar para todos os p. Isso não é óbvio e é um ponto forte
para a apresentação.

### Lower Bound de Schönheim (fundamento teórico rigoroso)

O limite inferior de Schönheim para o número mínimo de cobertura C(n, k, t) é:

```
L(n, k, t) = ⌈ (n/k) · L(n-1, k-1, t-1) ⌉
com caso base L(t, t, t) = 1
```

Para nosso problema: n=25, k=15, t=p. Este limite é mais apertado que o lower
bound LP e permite medir a qualidade da solução obtida.

---

## 3. Estrutura de Dados: Representação por Bitmask

### Por que bitmask?

Cada subconjunto de U = {1..25} pode ser representado como um inteiro de 25 bits.

```python
# Subconjunto {1, 3, 5} → bit 0, bit 2, bit 4 setados
# Representação: 0b0000000000000000000010101 = 21

# Verificar se Y ⊆ X:
def contem(x, y):
    return (x & y) == y   # O(1) — uma instrução de máquina
```

### Vantagem computacional

| Operação          | frozenset Python | bitmask int   | Ganho   |
|-------------------|------------------|---------------|---------|
| Verificar Y ⊆ X   | O(p)             | O(1)          | ~15–30x |
| Vetorizar com NumPy| Impossível       | Possível      | ~100x   |
| Memória por elemento| 200–500 bytes  | 4 bytes (uint32)| ~50x  |

### Conversão

```python
import numpy as np
from itertools import combinations

def combo_para_bitmask(combo):
    """Converte uma combinação de inteiros para bitmask."""
    mascara = 0
    for elemento in combo:
        mascara |= (1 << (elemento - 1))
    return mascara

def gerar_bitmasks(n, p):
    """Gera todos os bitmasks de tamanho p a partir de {1..n}."""
    return np.array(
        [combo_para_bitmask(c) for c in combinations(range(1, n + 1), p)],
        dtype=np.uint32
    )
```

---

## 3.5 Resultados Empiricos do Greedy (medidos em execucao real)

| p  | Updates/iter (teorico)       | Estrategia | Velocidade medida | ETA completo |
|----|------------------------------|------------|-------------------|--------------|
| 14 | C(15,14)*C(11,1) = 150       | Heap lazy  | ~950 iter/s       | ~10 min      |
| 13 | C(15,13)*C(12,2) = 6.825     | Heap lazy  | ~40 iter/s        | ~20 min      |
| 12 | C(15,12)*C(13,3) = 129.675   | Numpy argm | ~1 iter/s         | ~3 horas     |
| 11 | C(15,11)*C(14,4) = 1.365.000 | Numpy argm | ~0,22 iter/s      | ~4 horas     |

**Conclusao empirica para a apresentacao:** A velocidade do greedy e inversamente
proporcional ao numero de updates por iteracao, que cresce como C(k,p) * C(n-p, k-p).
Essa explosao combinatorial e o gargalo computacional central do problema.
O lower bound de |SB| e proporcional a 1/C(k,p), enquanto o custo por iteracao
cresce como C(k,p) * C(n-p, k-p). Portanto o custo total cresce como C(n-p, k-p) * |SB_otimo|.

**Resultado greedy p=14 (executado):**
- |SB15,14| = 532.555 (greedy)
- Lower bound LP: 297.160  |  Lower bound Schonheim: 297.172
- Gap greedy: 1,79x  (garantia teorica permite ate ln(4.5M) ~ 15,3x)
- Tempo: ~17,8 min (init 8s + 532.555 iteracoes em ~1010s)

---

## 4. Algoritmos Implementados

### Programa 1 — Geração das Combinações

**Abordagem:** itertools.combinations com geração lazy (iterador), sem armazenar tudo
em memória simultaneamente. Para uso nos programas 2-5, converte para bitmask NumPy.

**Complexidade:**
- Tempo: O(C(n, p)) — linear no número de saídas
- Espaço: O(p) por elemento se gerado lazily; O(C(n,p)) se armazenado em array

---

### Solver Greedy (Programas 2–5)

**Algoritmo:**

```
SB = {}
nao_cobertos = conjunto de todos os Y ∈ S_p (como bitmasks)

enquanto nao_cobertos não estiver vazio:
    melhor_x = argmax_{X ∈ S15} |{Y ∈ nao_cobertos : Y ⊆ X}|
    SB ← SB ∪ {melhor_x}
    nao_cobertos ← nao_cobertos \ {Y : Y ⊆ melhor_x}
```

**Implementação vetorizada:**

```python
def cobertura_de(x, sp_array):
    """Conta quantos Y ∈ sp_array estão contidos em x. Vetorizado."""
    return np.sum((sp_array & x) == sp_array)
```

**Complexidade por iteração:**
- Contar cobertura de cada X: O(|S₁₅| · |S_p|) no pior caso
- Com vetorização NumPy: constante por operação de array

**Complexidade total (Greedy):**
- Tempo: O(|SB| · |S₁₅| · |S_p|)
- Espaço: O(|S₁₅| + |S_p|)

**Garantia de aproximação:**
O algoritmo greedy para Set Cover produz solução com razão de aproximação:
```
|SB_greedy| ≤ ln(|S_p|) · |SB_ótimo|
```
Esta é a melhor razão polinomial possível (a menos que P=NP).

---

### Solver ILP via PySCIPOpt (Programas 4 e 5 — p=11 e p=12)

**Modelagem:**

```
Variáveis: x_i ∈ {0, 1}  para cada X_i ∈ S₁₅

Minimizar:   Σ x_i

Sujeito a:   para cada Y ∈ S_p:
             Σ_{i : Y ⊆ X_i} x_i ≥ 1
```

**Viabilidade por p:**

| p  | Variáveis | Restrições | Coeficientes não-nulos | Viável? |
|----|-----------|------------|------------------------|---------|
| 14 | 3.268.760 | 4.457.400  | ~67 milhões            | Nao     |
| 13 | 3.268.760 | 5.200.300  | ~546 milhões           | Nao     |
| 12 | 3.268.760 | 5.200.300  | ~2,37 bilhões          | Nao     |
| 11 | 3.268.760 | 4.457.400  | ~6,08 bilhões          | Nao     |

O ILP direto é inviável em escala completa. Estratégia alternativa:

**Amostragem + ILP (para p=11, p=12):**
Como o SB mínimo tem ~3.265 elementos (p=11), é possível:
1. Executar o greedy para obter uma solução inicial SB_greedy
2. Usar SB_greedy como conjunto de candidatos para o ILP (reduz variáveis drasticamente)
3. O ILP então encontra o subconjunto mínimo de SB_greedy que ainda cobre tudo

**Complexidade ILP:**
- Tempo: NP no pior caso; exponencial em parâmetros do branch-and-bound
- Espaço: O(|variáveis| + |restrições|)

---

### Solver Randômico (comparação)

**Abordagem:** Monte Carlo com múltiplos reinicios

```
melhor_SB = None
para k = 1..NUM_TENTATIVAS:
    SB = {}
    nao_cobertos = cópia de S_p
    enquanto nao_cobertos não estiver vazio:
        x = elemento aleatório de S15
        SB ← SB ∪ {x}
        remover Y ⊆ x de nao_cobertos
    se |SB| < |melhor_SB|:
        melhor_SB = SB
```

**Complexidade:**
- Tempo: O(NUM_TENTATIVAS · C(25,15) · C(25,p))
- Não tem garantia de aproximação, mas útil para comparação empírica

---

## 5. Plano de Implementação (5 dias)

### Dia 1 — Fundação
- [ ] Criar estrutura de diretórios `combinatorics_cover/`
- [ ] `program1_generation.py` — geração lazy + conversão bitmask
- [ ] Testes unitários: verificar C(25,15) = 3.268.760

### Dia 2 — Solver Greedy
- [ ] `solver_greedy.py` — implementação vetorizada com NumPy
- [ ] Testar em escala reduzida: U={1..10}, p=4 cobrindo p=3
- [ ] Medir tempo de execução por iteração

### Dia 3 — Programas 2 a 5
- [ ] `program2_cover14.py` ... `program5_cover11.py`
- [ ] Executar greedy em escala real; registrar |SB| obtido
- [ ] Comparar |SB| com lower bound LP e Schönheim

### Dia 4 — ILP e Randomizado
- [ ] `solver_ilp.py` — PySCIPOpt com candidatos pré-filtrados pelo greedy
- [ ] `solver_random.py` — Monte Carlo, múltiplas tentativas
- [ ] `analysis.py` — tabela comparativa de resultados e tempos

### Dia 5 — Documentação e Apresentação
- [ ] Exportar `PLANO_PROJETO.md` para o NotebookLM
- [ ] Gerar slides com NotebookLM a partir deste documento
- [ ] Revisão final e ensaio da apresentação (10 min + 5 min arguição)

---

## 6. Estrutura de Arquivos

```
combinatorics_cover/
    program1_generation.py     # Geração de S15..S11
    program2_cover14.py        # Cobertura p=14
    program3_cover13.py        # Cobertura p=13
    program4_cover12.py        # Cobertura p=12
    program5_cover11.py        # Cobertura p=11
    solver_greedy.py           # Solver guloso vetorizado
    solver_ilp.py              # Solver ILP via PySCIPOpt
    solver_random.py           # Solver Monte Carlo
    analysis.py                # Análise comparativa e relatório
    requirements.txt           # pyscipopt, numpy, scipy
```

---

## 7. Análise de Complexidade Formal

### Notação assintótica usada

- **O(·)** — limite superior (pior caso)
- **Θ(·)** — limite exato (caso médio e pior caso coincidem)
- **Ω(·)** — limite inferior (melhor caso)

### Programa 1 — Geração

| Métrica        | Complexidade          |
|----------------|-----------------------|
| Tempo (lazy)   | Θ(C(n, p)) por iteração completa |
| Espaço (lazy)  | Θ(p) — pilha de recursão |
| Espaço (array) | Θ(C(n, p)) |

### Programas 2–5 — Solver Greedy

Seja:
- N₁₅ = |S₁₅| = C(25, 15) = 3.268.760
- Nₚ = |Sₚ|
- K = |SB_greedy| (tamanho da solução obtida)
- c = C(15, p) (cobertura por elemento de S₁₅)

| Métrica              | Complexidade              |
|----------------------|---------------------------|
| Tempo por iteração   | O(N₁₅ · Nₚ)              |
| Tempo total          | O(K · N₁₅ · Nₚ)          |
| Com NumPy vetorizado | O(K · N₁₅) — operações de array |
| Espaço               | O(N₁₅ + Nₚ)              |
| Garantia de solução  | ≤ ln(Nₚ) · |OPT|         |

### Gargalos Computacionais

1. **Contagem de cobertura** — O(N₁₅ · Nₚ) por iteração é o custo dominante
2. **Memória dos arrays** — S₁₅ como uint32 ocupa ~13 MB; S₁₁ ~18 MB (viável)
3. **Atualização do conjunto não-coberto** — pode ser acelerado com indexação invertida

### Escalabilidade

| Abordagem  | Escala real? | Garantia de ótimo? | Tempo estimado |
|------------|--------------|--------------------|--------------------|
| Força bruta | Não         | Sim                | Anos              |
| ILP direto  | Não         | Sim                | Dias–semanas      |
| ILP pós-greedy | Parcial | Sim (sobre candidatos) | Horas        |
| Greedy      | Sim         | Aproximado (ln n)  | Minutos           |
| Randômico   | Sim         | Nenhuma            | Segundos          |

---

## 8. Roteiro da Apresentação (10 minutos)

### Slide 1 — O Problema (1 min)
Universo U={1..25}. Queremos o menor conjunto SB ⊆ S₁₅ que "cobre" todas as
combinações menores. Analogia: menor conjunto de 15 números na loteria que
garante acertar qualquer 11, 12, 13 ou 14 números sorteados.

### Slide 2 — Por que é difícil? (1 min)
Set Cover é NP-difícil (Karp, 1972). Força bruta em S₁₅: 2^3.268.760 possibilidades.
Inviável. Precisamos de abordagens inteligentes.

### Slide 3 — Insight de escala (2 min)
Mostrar a tabela de lower bounds por p. Revelar que p=11 exige SB mínimo de
apenas ~3.265 elementos de 3,3 milhões disponíveis. Motivar a estratégia diferenciada.

### Slide 4 — Representação por Bitmask (1 min)
Mostrar a transformação de frozenset → uint32. Demonstrar verificação Y ⊆ X
em O(1) vs O(p). Mencionar vetorização NumPy.

### Slide 5 — Algoritmo Greedy (2 min)
Pseudocódigo. Razão de aproximação ln(n). Complexidade O(K · N₁₅ · Nₚ).
Resultado obtido para cada p.

### Slide 6 — ILP para p=11 e p=12 (1 min)
Modelagem formal. Por que ILP direto falha (tabela de escala). Como o greedy
reduz o problema para tornar o ILP tratável.

### Slide 7 — Resultados Comparativos (1 min)
Tabela: |SB| obtido vs lower bound LP vs lower bound Schönheim, para cada p.
Tempo de execução de cada abordagem.

### Slide 8 — Conclusão e Limitações (1 min)
O que funcionou, o que não funcionou. Possíveis melhorias: column generation,
metaheurísticas, paralelização com multiprocessing.

---

## 9. Pontos para Arguição do Professor

**Pergunta provável:** "Por que vocês escolheram greedy e não ILP?"
**Resposta:** ILP direto é inviável pela escala (mostrar tabela de restrições).
Greedy tem garantia teórica de ln(n)-aproximação e executa em tempo polinomial.
Para p=11/12, combinamos greedy + ILP.

**Pergunta provável:** "Como vocês sabem que a solução está próxima do ótimo?"
**Resposta:** Comparamos com o lower bound de Schönheim, que é o melhor limite
inferior conhecido para este tipo de problema de cobertura.

**Pergunta provável:** "Qual a complexidade do Programa 1?"
**Resposta:** Θ(C(25,p)) no tempo — linear no número de combinações geradas.
Com geração lazy (itertools), o espaço é Θ(p) por elemento processado.

**Pergunta provável:** "O problema é NP-difícil — como vocês o resolveram?"
**Resposta:** Não resolvemos de forma ótima para todos os casos. O greedy produz
uma solução aproximada com garantia teórica. Resolução ótima exige ILP, viável
apenas para os casos de menor escala (p=11, p=12).

---

## 10. Dependências (requirements.txt)

```
numpy>=1.24
pyscipopt>=4.0
scipy>=1.10
```

---

*Documento gerado para uso com Google NotebookLM — importar junto com o PDF do enunciado para geração dos slides da apresentação.*
