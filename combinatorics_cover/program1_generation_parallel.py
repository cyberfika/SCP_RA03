# -*- coding: utf-8 -*-
"""
Program 1 (Versao Paralela) - Geracao dos Conjuntos de Combinacoes

Gera S15, S14, S13, S12 e S11 a partir do universo U = {1..25},
usando multiprocessing.Pool para produzir os 5 arrays concorrentemente.

Paralelismo aplicado:
  Cada Sp e gerado por um worker independente — sem dados compartilhados,
  sem sincronizacao, sem IPC de retorno pesado (cada array e retornado
  uma unica vez apos a geracao completa).

  Pool.map distribui os 5 tamanhos entre os workers disponiveis; o processo
  principal aguarda todos e exibe os resultados ao final.

Complexidade por worker:
  Tempo : O(C(n,p)) — enumera todas as combinacoes de tamanho p
  Espaco: O(C(n,p)) — aloca array uint32 completo

Speedup esperado:
  Com 5 tamanhos independentes e >= 5 nucleos: ~5x
  Com 4 nucleos (tipico): ~4x (S15 e o maior, domina o tempo total)
  Ganho absoluto: geracao sequencial ~4s -> paralela ~1s

Comparacao com a versao sequencial (program1_generation.py):
  - Sequencial: gera S15, S14, ..., S11 um por vez  (~4s total)
  - Paralela  : gera todos os 5 simultaneamente     (~1s total)
  A versao paralela e recomendada quando todos os 5 conjuntos sao necessarios.
"""

import sys
import os
import time
import multiprocessing
from itertools import combinations
from math import comb

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

UNIVERSE_N = 25
SIZES      = [15, 14, 13, 12, 11]


# ---------------------------------------------------------------------------
# Funcao worker
# ---------------------------------------------------------------------------

def _generate_array_worker(args: tuple) -> tuple:
    """
    Gera o array de bitmasks uint32 para C(n, p).
    Executado em processo separado pelo Pool.

    Retorna (p, array) para que o processo principal possa identificar
    qual tamanho corresponde ao resultado.
    """
    n, p = args
    total = comb(n, p)
    arr = np.empty(total, dtype=np.uint32)
    for i, combo in enumerate(combinations(range(1, n + 1), p)):
        mask = 0
        for e in combo:
            mask |= (1 << (e - 1))
        arr[i] = mask
    return p, arr


# ---------------------------------------------------------------------------
# Funcoes utilitarias
# ---------------------------------------------------------------------------

def combo_to_bitmask(combo: tuple) -> int:
    """Converte uma combinacao de inteiros em bitmask de 25 bits."""
    mask = 0
    for element in combo:
        mask |= (1 << (element - 1))
    return mask


def bitmask_to_combo(mask: int) -> tuple:
    """Converte um bitmask de 25 bits de volta para tupla de elementos."""
    return tuple(e + 1 for e in range(UNIVERSE_N) if mask & (1 << e))


# ---------------------------------------------------------------------------
# Geracao paralela
# ---------------------------------------------------------------------------

def generate_all_parallel(
    n: int = UNIVERSE_N,
    sizes: list = None,
    n_workers: int = None,
    verbose: bool = True,
) -> dict:
    """
    Gera todos os arrays Sp em paralelo usando multiprocessing.Pool.

    Parametros
    ----------
    n        : tamanho do universo (padrao 25)
    sizes    : lista de valores p a gerar (padrao [15, 14, 13, 12, 11])
    n_workers: numero de workers (padrao: min(cpu_count, len(sizes)))
    verbose  : imprime progresso

    Retorna
    -------
    dict {p: np.ndarray uint32}  — um array por tamanho
    """
    if sizes is None:
        sizes = SIZES

    if n_workers is None:
        n_workers = min(os.cpu_count() or len(sizes), len(sizes))

    if verbose:
        print(f"\n[Parallel] Generating {len(sizes)} sets with {n_workers} workers")
        for p in sizes:
            # exibe tamanho esperado e custo de memoria
            print(f"  S{p}: C({n},{p}) = {comb(n,p):>10,} elements  "
                  f"({comb(n,p)*4/1e6:.1f} MB)")

    t0 = time.time()

    with multiprocessing.Pool(n_workers) as pool:
        results = pool.map(
            _generate_array_worker,
            [(n, p) for p in sizes],
        )

    elapsed = time.time() - t0
    arrays = {p: arr for p, arr in results}

    if verbose:
        print(f"\n  Generation complete in {elapsed:.2f}s\n")
        for p in sizes:
            arr = arrays[p]
            ok = len(arr) == comb(n, p)
            status = "OK" if ok else "ERROR"
            print(f"  S{p}: {len(arr):>10,} elements  [{status}]")

    return arrays


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Program 1 (Parallel) - Combination Set Generation")
    print(f"Universe U = {{1, ..., {UNIVERSE_N}}}")
    print(f"Available workers: {os.cpu_count()}")
    print("=" * 60)

    t_total = time.time()

    arrays = generate_all_parallel(verbose=True)

    print(f"\nTotal time: {time.time()-t_total:.2f}s")

    # verifica cardinalidades geradas
    print("\nCardinality check:")
    all_ok = True
    for p in SIZES:
        expected = comb(UNIVERSE_N, p)
        obtained = len(arrays[p])
        status   = "OK" if obtained == expected else "ERROR"
        if status == "ERROR":
            all_ok = False
        print(f"  S{p}: obtained {obtained:>9,} | expected {expected:>9,} | {status}")

    if all_ok:
        print("\n  All sets generated correctly.")
    else:
        print("\n  [ERROR] Inconsistency detected!")

    # demonstra as primeiras 5 combinacoes de S15
    print("\nExample - first 5 combinations of S15:")
    s15 = arrays[15]
    for i in range(5):
        bitmask = int(s15[i])
        combo   = bitmask_to_combo(bitmask)
        print(f"  bitmask={bitmask:025b}  ->  {combo}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
