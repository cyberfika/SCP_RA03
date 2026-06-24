# Prompt - Geracao de Slides Completos RA03

Crie um novo conjunto completo de slides para uma apresentacao academica de
aproximadamente 10 minutos sobre o trabalho RA03 de Complexidade de Algoritmos.

O resultado deve ser uma apresentacao completa, coerente, visualmente polida e
pronta para defesa oral. Gere todos os slides, incluindo capa.

Preserve um estilo profissional escuro, tecnico e academico, mas nao copie
mecanicamente nenhum deck anterior. O objetivo e produzir uma versao completa,
mais clara e mais convincente.

---

## Informacoes da Capa

A capa deve conter obrigatoriamente:

- Nome do trabalho: **Cobertura de Combinacoes (Minimum Set Cover)**
- Identificacao: **Trabalho Avaliativo - RA03**
- Disciplina: **Complexidade de Algoritmos**
- Instituicao: **Pontificia Universidade Catolica do Parana - PUCPR**
- Curso: **Bacharelado em Ciencia da Computacao**
- Aluno: **Jafte Carneiro Fagundes da Silva**
- Professor: **Edson Emilio Scalabrin**
- Local e ano: **Curitiba, 2026**

---

## Contexto do Problema

Universo:

```text
U = {1, 2, ..., 25}
```

Conjuntos:

```text
S15 = todos os subconjuntos de tamanho 15 de U
Sp  = todos os subconjuntos de tamanho p de U, para p em {14, 13, 12, 11}
```

Cardinalidades:

| Conjunto | Formula  | Cardinalidade |
|---|---:|---:|
| S15 | C(25,15) | 3.268.760 |
| S14 | C(25,14) | 4.457.400 |
| S13 | C(25,13) | 5.200.300 |
| S12 | C(25,12) | 5.200.300 |
| S11 | C(25,11) | 4.457.400 |

Objetivo:

Para cada `p in {14,13,12,11}`, encontrar um subconjunto
`SB15,p subset S15` tal que todo `Y in Sp` esteja contido em pelo menos um
`X in SB15,p`.

Formalmente:

```text
Para todo Y em Sp, existe X em SB15,p tal que Y subset X
```

O problema e uma instancia de **Minimum Set Cover**, conhecido por ser
NP-dificil.

---

## Requisitos Obrigatorios do Enunciado

A apresentacao deve contemplar explicitamente:

1. Modelagem do problema.
2. Estrategia algoritmica adotada.
3. Estruturas de dados utilizadas.
4. Resultados obtidos.
5. Analise de complexidade:
   - tempo;
   - espaco;
   - gargalos computacionais;
   - escalabilidade;
   - comparacao de estrategias.
6. Limitacoes e possiveis melhorias.
7. Discussao das alternativas sugeridas no enunciado:
   - Algoritmos Gulosos;
   - Branch and Bound;
   - Programacao Inteira;
   - Algoritmos Probabilisticos;
   - Algoritmos Randomicos;
   - Metaheuristicas;
   - Computacao Paralela ou Distribuida;
   - Outras abordagens fundamentadas na literatura cientifica.

---

## Conteudo Tecnico que Deve Aparecer

### 1. Modelagem

Explique que cada candidato `X in S15` cobre todos os subconjuntos `Y in Sp`
tais que `Y subset X`.

Mostre a formulacao por Programacao Linear Inteira (ILP):

```text
xi in {0,1}, para cada Xi in S15
minimizar sum xi
sujeito a sum_{i: Y subset Xi} xi >= 1, para todo Y in Sp
```

Explique tambem a diferenca entre:

- **LP**: Programacao Linear relaxada, com variaveis continuas.
- **ILP**: Programacao Linear Inteira, com variaveis inteiras/binarias.

### 2. Por que ILP direto e inviavel

Use a tabela correta:

| p | Variaveis | Restricoes | Coeficientes nao-nulos | Viavel? |
|---:|---:|---:|---:|:---:|
| 14 | 3.268.760 | 4.457.400 | 49.031.400 | Nao |
| 13 | 3.268.760 | 5.200.300 | 343.219.800 | Nao |
| 12 | 3.268.760 | 5.200.300 | 1.487.285.800 | Nao |
| 11 | 3.268.760 | 4.457.400 | 4.461.857.400 | Nao |

Explique que o ILP e exato, mas inviavel em escala completa por memoria e tempo.

### 3. Lower Bounds

Use os limites:

| p | C(15,p) | LB-LP | LB-Schonheim |
|---:|---:|---:|---:|
| 14 | 15 | 297.160 | 297.172 |
| 13 | 105 | 49.527 | 58.887 |
| 12 | 455 | 11.430 | 13.175 |
| 11 | 1.365 | 3.266 | 3.370 |

Explique:

- LB-LP vem de contagem direta: cada `X in S15` cobre `C(15,p)` alvos.
- Schonheim fornece limite inferior combinatorio mais apertado.

### 4. Estruturas de Dados

Apresente as estruturas:

- bitmask `uint32` para representar subconjuntos;
- teste de inclusao em O(1): `(X & Y) == Y`;
- arrays NumPy;
- dicionarios hash:
  - `s15_index: mask -> indice`;
  - `sp_index: mask -> indice`;
- array `count[]`;
- array booleano `nao_coberto[]`;
- heap lazy para `p=14` e `p=13`;
- `np.argmax` para `p=12`;
- atualizacao paralela no Programa 5 para `p=11`.

### 5. Algoritmo Greedy

Mostre o pseudocodigo:

```text
Entrada: S15, Sp
Pre-processamento: construir indices, count[] e nao_coberto[]
SB <- vazio

enquanto existir alvo nao coberto:
    escolher X* com maior count[X]
    adicionar X* a SB
    marcar X* como indisponivel

    para cada Y subset X* com |Y| = p:
        se Y ainda nao coberto:
            marcar Y como coberto
            para cada X que contem Y:
                decrementar count[X]

retornar SB
```

Explique a garantia:

```text
|SB_greedy| <= H(|Sp|) * |OPT|
```

Onde `H(n) ~= ln(n) + 0,577`.

### 6. Complexidade

Use a notacao:

```text
N15 = C(25,15)
Np  = C(25,p)
K   = |SB_greedy|
A   = C(15,p) * C(25-p,15-p)
```

Valores por iteracao:

| p | C(15,p) | C(25-p,15-p) | A = updates/iter | K obtido | Estrategia |
|---:|---:|---:|---:|---:|---|
| 14 | 15 | 11 | 165 | 532.555 | heap lazy |
| 13 | 105 | 66 | 6.930 | 128.827 | heap lazy |
| 12 | 455 | 286 | 130.130 | 38.100 | NumPy argmax |
| 11 | 1.365 | 1.001 | 1.366.365 | 12.733 | atualizacao paralela |

Explique:

- Programa 1: geracao de combinacoes em `Theta(C(n,p))`.
- Programas 2-5: greedy set cover.
- Gargalo principal: atualizacao de `count[]`.
- Espaco: `O(N15 + Np)`.

---

## Resultados Principais

Use a tabela:

| p | |Sp| | LB-LP | LB-Schonheim | |SB_greedy| | Gap vs LB-Sch | Tempo | % de S15 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 14 | 4.457.400 | 297.160 | 297.172 | 532.555 | 1,79x | ~18 min | 16,3% |
| 13 | 5.200.300 | 49.527 | 58.887 | 128.827 | 2,19x | ~3 h | 3,9% |
| 12 | 5.200.300 | 11.430 | 13.175 | 38.100 | 2,89x | ~79 min | 1,2% |
| 11 | 4.457.400 | 3.266 | 3.370 | 12.733 | 3,78x | ~3,4 h | 0,4% |

Mensagem principal:

- A garantia teorica permitiria gap de ate aproximadamente `15,4x`.
- Os resultados reais ficaram entre `1,79x` e `3,78x`.
- Portanto, o greedy ficou entre `4x` e `9x` melhor que o pior caso teorico.

Importante:

Nao afirmar que auditoria exata foi concluida para `p=11` ou `p=12` se isso
nao estiver comprovado. Se mencionar auditoria, escrever:

```text
A auditoria exata deve permanecer pendente ate o termino da execucao de audit_cobertura.py.
```

---

## Experimentos Alternativos

Inclua slides especificos para os novos experimentos, com foco em ganhos de
desempenho.

### Instancia medium

`n=15, k=9, p=6`

| Metodo | Tempo | |SB| | Leitura |
|---|---:|---:|---|
| Greedy baseline | 10,035 s | 140 | referencia deterministica |
| Stochastic Greedy | 0,743 s | 152 | 13,5x mais rapido; +8,6% em |SB| |
| GRASP | 48,813 s | 143 | mais caro; qualidade proxima do greedy |
| Relaxacao Lagrangiana | 23,948 s | 140 | bound 59,58; reparo igual ao greedy |
| Column Generation | 18,551 s | 171 | relaxacao LP e pricing; solucao arredondada e reparada |

### Instancia large-demo

`n=16, k=10, p=6`

| Metodo | Tempo | |SB| | Leitura |
|---|---:|---:|---|
| Greedy baseline | 24,895 s | 105 | referencia para escala maior |
| Stochastic Greedy | 1,208 s | 115 | 20,6x mais rapido; +9,5% em |SB| |
| GRASP | 143,862 s | 107 | 5,8x mais lento; melhora marginal em |SB| |
| Greedy + poda local | 28,268 s | 105 | removeu 0 candidatos redundantes |

Conclusao dos experimentos:

- Stochastic Greedy foi a alternativa com maior ganho de desempenho medido.
- Reduziu o tempo em `13,5x` no `medium` e `20,6x` no `large-demo`.
- O custo foi aumento inferior a `10%` no tamanho da solucao.
- GRASP validou o eixo de metaheuristicas, mas nao compensou o custo adicional
  nos benchmarks atuais.
- Relaxacao Lagrangiana e Column Generation entram como abordagens cientificas
  para lower bounds, relaxacao de Programacao Linear e alternativas ao ILP direto.

---

## Paralelismo

Explique que ha paralelismo em:

1. Programa 1:
   - geracao independente de `S15`, `S14`, `S13`, `S12`, `S11`;
   - tempo sequencial observado: ~80 s;
   - tempo paralelo observado: ~18,7 s;
   - speedup aproximado: 4,3x.

2. Programa 5:
   - caso `p=11`;
   - maior custo por iteracao: `1.366.365` updates/iter;
   - volume suficiente para amortizar overhead de multiprocessing;
   - estrategia: atualizacao paralela de `count[]`.

Explique por que os Programas 2, 3 e 4 nao foram paralelizados da mesma forma:

- `p=14`: apenas 165 updates/iter;
- `p=13`: 6.930 updates/iter;
- `p=12`: 130.130 updates/iter, mas `np.argmax` e overhead de IPC tornam o ganho
  menos evidente;
- no `p=11`, o volume e grande o bastante para justificar paralelismo.

---

## Limitacoes e Melhorias

Inclua:

- ILP direto inviavel em escala completa.
- Greedy nao garante solucao otima global.
- Cobertura exata em escala completa e cara.
- Escalabilidade limitada para `n > 27`.
- Tempo ainda alto para `p=13` e `p=11`.

Melhorias:

- ILP pos-greedy como refinamento possivel, nao como resultado principal.
- Branch and Bound / Branch-and-Price sobre espaco reduzido.
- Column Generation.
- Relaxacao Lagrangiana.
- Simulated Annealing pos-greedy.
- GRASP paralelo com mais restarts.
- Bitsets vetorizados, Cython ou C/C++ para gargalos.
- Distribuicao de trabalho em multiplos processos/maquinas.

---

## Estrutura Sugerida dos Slides

Crie entre 11 e 13 slides:

1. Capa.
2. Modelagem formal do problema.
3. Por que ILP direto e forca bruta sao inviaveis.
4. Lower bounds e criterio de qualidade.
5. Estruturas de dados.
6. Algoritmo greedy e garantia teorica.
7. Analise de complexidade.
8. Gargalos e paralelismo.
9. Resultados principais para `n=25`.
10. Eixo comparativo das abordagens do enunciado.
11. Experimentos alternativos e ganhos medidos.
12. Limitacoes e melhorias.
13. Conclusao tecnica, se houver espaco.

---

## Requisitos de Design

- Apresentacao completa, coesa e moderna.
- Fundo escuro profissional.
- Paleta sugerida:
  - fundo: `#020617` ou `#0f1117`;
  - texto principal: `#e2e8f0`;
  - texto secundario: `#94a3b8`;
  - destaque: `#38bdf8`;
  - sucesso/resultado: `#34d399`;
  - alerta/limitacao: `#f87171`.
- Usar tabelas legiveis, nao muito carregadas.
- Usar tipografia moderna: Inter, Segoe UI, system-ui ou equivalente.
- Usar rodape discreto:

```text
PUCPR · Complexidade de Algoritmos · RA03 · 2026
```

- Todos os slides devem caber em uma tela, sem rolagem.
- Se gerar HTML/CSS, incluir navegacao por botoes Anterior/Proximo e indicador
  "Slide N de M".
- Se gerar PPTX, manter todos os textos editaveis.
- Evitar excesso de texto corrido; priorizar tabelas, blocos comparativos,
  diagramas e mensagens de conclusao.

---

## Regras de Precisao

- Nao inventar resultados.
- Nao afirmar otimalidade global.
- Nao dizer que auditoria exata foi concluida sem evidencia local.
- Nao dizer que ILP pos-greedy foi executado como resultado principal.
- Explicar siglas quando aparecerem pela primeira vez:
  - LP = Programacao Linear;
  - ILP = Programacao Linear Inteira;
  - GRASP = Greedy Randomized Adaptive Search Procedure.
- Manter todos os numeros exatamente como informados neste prompt.
