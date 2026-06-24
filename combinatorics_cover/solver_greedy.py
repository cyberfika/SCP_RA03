# -*- coding: utf-8 -*-
"""
Solver Greedy para Set Cover
Encontra SB <= S15 tal que todo Y em Sp esta contido em algum X em SB.

Estrategia:
  A cada iteracao, escolhe o X em S15 que cobre o maior numero de
  combinacoes de tamanho p ainda nao cobertas (greedy maximo).

Estruturas de dados:
  - Bitmask uint32: cada combinacao = inteiro de 25 bits
  - s15_index: dict {bitmask -> indice em s15} para lookup O(1)
  - sp_index:  dict {bitmask -> indice em sp}  para lookup O(1)
  - count[i]:  numero de Y nao cobertos que X_i cobre (heap lazy)
  - nao_coberto[j]: bool, True se Y_j ainda nao foi coberto

Complexidade:
  Seja K = |SB|, P = p, N15 = |S15| = C(25,15), Np = |Sp| = C(25,p)
  Tempo:  O(K * C(15,P) * C(25-P, 15-P) * log(N15))
  Espaco: O(N15 + Np)

Garantia de aproximacao:
  |SB_greedy| <= H(Np) * |SB_otimo|  onde H(n) = ln(n) + O(1)
"""

import sys
import time
import heapq
from itertools import combinations
from math import comb

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Importa funcoes de geracao do Programa 1
sys.path.insert(0, ".")
from program1_generation import gerar_array, gerar_combinacoes_lazy


# ---------------------------------------------------------------------------
# Construcao dos indices
# ---------------------------------------------------------------------------

def construir_indices(s15: np.ndarray, sp: np.ndarray) -> tuple[dict, dict]:
    """Constroi dicionarios bitmask->indice para S15 e Sp. O(|S15| + |Sp|)."""
    s15_index = {int(x): i for i, x in enumerate(s15)}
    sp_index  = {int(y): j for j, y in enumerate(sp)}
    return s15_index, sp_index


# ---------------------------------------------------------------------------
# Algoritmo Greedy com heap lazy
# ---------------------------------------------------------------------------

def greedy_set_cover(
    s15: np.ndarray,
    sp: np.ndarray,
    p: int,
    n: int = 25,
    k: int = 15,
    verbose: bool = True,
    limite_iter: int | None = None,
) -> np.ndarray:
    """
    Greedy Set Cover: seleciona um subconjunto SB <= Sk que cobre todo Y em Sp.

    Parametros
    ----------
    s15        : array uint32 com todos os bitmasks de C(n,k)
    sp         : array uint32 com todos os bitmasks de C(n,p)
    p          : tamanho das combinacoes a cobrir
    n          : tamanho do universo (padrao: 25)
    k          : tamanho dos conjuntos candidatos (padrao: 15)
    verbose    : imprime progresso
    limite_iter: para apos este numero de iteracoes (None = rodar ate o fim)

    Retorna
    -------
    np.ndarray uint32 com os bitmasks dos elementos selecionados para SB
    """
    n_s15 = len(s15)
    n_sp  = len(sp)
    cobertura_inicial = comb(k, p)       # C(k,p) subconjuntos de tamanho p por X
    extensoes_por_y   = comb(n - p, k - p)  # quantos X contem cada Y

    if verbose:
        print(f"\n[Greedy] p={p} | |S15|={n_s15:,} | |Sp|={n_sp:,}")
        print(f"         Cobertura por X: C({k},{p})={cobertura_inicial:,}")
        print(f"         Extensoes por Y: C({n-p},{k-p})={extensoes_por_y:,}")
        print(f"         Lower bound |SB| >= {-(-n_sp // cobertura_inicial):,}\n")

    t0 = time.time()

    # ------------------------------------------------------------------
    # Pre-processamento: indices para lookup O(1)
    # ------------------------------------------------------------------
    if verbose:
        print("  Construindo indices...", end=" ", flush=True)
    s15_index, sp_index = construir_indices(s15, sp)
    if verbose:
        print(f"OK ({time.time()-t0:.1f}s)")

    # ------------------------------------------------------------------
    # Selecao automatica de estrategia para argmax
    # Heap lazy: eficiente quando ha poucas atualizacoes por iteracao
    #   (p alto, ex: p=14 -> 15 * 10 = 150 updates/iter)
    # Numpy argmax: eficiente quando ha muitas atualizacoes por iteracao
    #   (p baixo, ex: p=11 -> 1365 * 1001 = 1.37M updates/iter)
    # Limiar empirico: se updates/iter > 10.000, usar argmax
    updates_por_iter = cobertura_inicial * (extensoes_por_y - 1)
    usar_heap = updates_por_iter <= 10_000
    # ------------------------------------------------------------------
    # Estado inicial
    # ------------------------------------------------------------------
    count       = np.full(n_s15, cobertura_inicial, dtype=np.int32)
    nao_coberto = np.ones(n_sp, dtype=bool)
    total_nao_coberto = n_sp

    if usar_heap:
        # Heap lazy (max via valores negativos): (-count, indice)
        heap = [(-cobertura_inicial, i) for i in range(n_s15)]
        heapq.heapify(heap)
    else:
        heap = None

    if verbose:
        modo = "heap lazy" if usar_heap else "numpy argmax"
        print(f"  Estrategia: {modo} ({updates_por_iter:,} updates/iter estimados)")

    sb_masks = []
    iter_num = 0
    t_loop = time.time()  # timer so apos a inicializacao

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    while total_nao_coberto > 0:
        if limite_iter is not None and iter_num >= limite_iter:
            if verbose:
                print(f"  [limite atingido: {limite_iter} iteracoes]")
            break

        # Encontrar X com maior cobertura atual
        if usar_heap:
            while True:
                neg_cnt, i_best = heapq.heappop(heap)
                if count[i_best] == -neg_cnt:
                    break  # entrada valida
        else:
            i_best = int(np.argmax(count))

        if count[i_best] <= 0:
            if verbose:
                print("  [aviso] nenhum X util restante")
            break

        x_best = int(s15[i_best])
        count[i_best] = -1  # marcar como usado
        sb_masks.append(x_best)
        iter_num += 1

        # Elementos de x_best (k bits setados)
        elementos_x = [e for e in range(n) if x_best & (1 << e)]

        # Processar cada subconjunto de tamanho p de x_best
        novos_cobertos = 0
        extensoes_necessarias = k - p

        for combo_y in combinations(elementos_x, p):
            y_mask = 0
            for e in combo_y:
                y_mask |= (1 << e)

            j = sp_index.get(y_mask)
            if j is None or not nao_coberto[j]:
                continue  # ja coberto ou invalido

            # Marcar Y como coberto
            nao_coberto[j] = False
            novos_cobertos += 1

            # Decrementar count de todos os X que contem Y
            bits_livres = [e for e in range(n) if not (y_mask & (1 << e))]

            for ext_combo in combinations(bits_livres, extensoes_necessarias):
                x_mask = y_mask
                for e in ext_combo:
                    x_mask |= (1 << e)

                idx = s15_index.get(x_mask)
                if idx is not None and count[idx] > 0:
                    count[idx] -= 1
                    if usar_heap:
                        heapq.heappush(heap, (-count[idx], idx))

        total_nao_coberto -= novos_cobertos

        # Relatorio de progresso
        if verbose and (iter_num <= 10 or iter_num % 100 == 0):
            elapsed_loop = time.time() - t_loop  # tempo so das iteracoes
            pct = 100 * (n_sp - total_nao_coberto) / n_sp
            vel = iter_num / elapsed_loop if elapsed_loop > 0 else 0
            eta = (total_nao_coberto / (novos_cobertos + 1e-9)) / (vel + 1e-9)
            print(
                f"  iter={iter_num:>6} | |SB|={len(sb_masks):>6,} | "
                f"cobertos={pct:5.1f}% | "
                f"novos={novos_cobertos:>5,} | "
                f"loop={elapsed_loop:.1f}s | ETA={eta:.0f}s"
            )

    # ------------------------------------------------------------------
    # Resultado final
    # ------------------------------------------------------------------
    elapsed = time.time() - t0
    restantes = int(np.sum(nao_coberto))

    if verbose:
        print(f"\n[Greedy] Concluido em {elapsed:.1f}s")
        print(f"  |SB|          = {len(sb_masks):,}")
        print(f"  Nao cobertos  = {restantes:,}")
        print(f"  Cobertura     = {100*(n_sp-restantes)/n_sp:.4f}%")

    return np.array(sb_masks, dtype=np.uint32)


# ---------------------------------------------------------------------------
# Verificacao de corretude
# ---------------------------------------------------------------------------

def verificar_cobertura(
    sb: np.ndarray,
    sp: np.ndarray,
    verbose: bool = True,
    n_amostras: int = 10_000,
    rng_seed: int = 42,
) -> bool:
    """Verifica cobertura por amostragem aleatoria de sp.

    Para |SB| * |Sp| muito grande (ex: 500K * 4.5M), verificacao completa
    e inviavel. Usamos amostragem: se N_AMOSTRAS elementos aleatorios de sp
    estao todos cobertos, reportamos OK com alta confianca.

    Para verificacao exata em escala pequena (|sb| * |sp| < 1 bilhao),
    usa o metodo completo automaticamente.
    """
    n_sb = len(sb)
    n_sp = len(sp)
    custo = n_sb * n_sp

    if custo <= 1_000_000_000:
        # Verificacao exata: O(|SB| * |Sp|)
        coberto = np.zeros(n_sp, dtype=bool)
        for x in sb:
            coberto |= (sp & x) == sp
        total = int(np.sum(coberto))
        ok = total == n_sp
        if verbose:
            status = "OK" if ok else "FALHOU"
            print(f"  Verificacao exata: {total:,}/{n_sp:,} cobertos [{status}]")
        return ok

    # Verificacao por amostragem vetorizada: batches de sb x amostras
    # Evita loop Python elemento a elemento sobre sb (532K iters = lento)
    rng = np.random.default_rng(rng_seed)
    idx = rng.choice(n_sp, size=min(n_amostras, n_sp), replace=False)
    amostras = sp[idx]           # (n_amostras,) uint32
    m = len(amostras)

    nao_cob = np.ones(m, dtype=bool)
    SB_BATCH = 512               # (SB_BATCH, m) bool = 512*10K = 5MB por batch

    for start in range(0, n_sb, SB_BATCH):
        batch = sb[start : start + SB_BATCH]   # (B,) uint32
        # (B, m): True onde batch[i] cobre amostras[j]
        cobre = (batch[:, None] & amostras[None, :]) == amostras[None, :]
        nao_cob &= ~cobre.any(axis=0)
        if not nao_cob.any():
            break

    nao_cobertos = int(np.sum(nao_cob))
    ok = nao_cobertos == 0
    if verbose:
        status = "OK" if ok else f"FALHOU ({nao_cobertos} nao cobertos)"
        print(
            f"  Verificacao por amostragem ({m:,} de {n_sp:,}): [{status}]"
        )
    return ok


# ---------------------------------------------------------------------------
# Entrada principal — teste em escala reduzida
# ---------------------------------------------------------------------------

def main():
    print("Solver Greedy - Teste em escala reduzida")
    print("Universo reduzido: n=15, cobrindo p=10 com combinacoes de 11\n")

    # Teste com parametros menores para validacao rapida
    N_TESTE = 15
    P_GRANDE = 11   # equivalente a S15 no problema real
    P_ALVO   = 10   # equivalente a S11 no problema real

    print(f"  Gerando S{P_GRANDE} de n={N_TESTE}: C({N_TESTE},{P_GRANDE})={comb(N_TESTE,P_GRANDE):,} elementos")
    s_grande = gerar_array(N_TESTE, P_GRANDE)

    print(f"  Gerando S{P_ALVO}  de n={N_TESTE}: C({N_TESTE},{P_ALVO})={comb(N_TESTE,P_ALVO):,} elementos")
    s_alvo   = gerar_array(N_TESTE, P_ALVO)

    sb = greedy_set_cover(s_grande, s_alvo, p=P_ALVO, n=N_TESTE, k=P_GRANDE, verbose=True)

    print()
    verificar_cobertura(sb, s_alvo, verbose=True)

    lower_bound = -(-comb(N_TESTE, P_ALVO) // comb(P_GRANDE, P_ALVO))
    print(f"  Lower bound LP: |SB| >= {lower_bound}")
    print(f"  Solucao greedy (nao otima): |SB| = {len(sb)}")
    print(f"  Gap vs lower bound: {len(sb)/lower_bound:.2f}x")


if __name__ == "__main__":
    main()
