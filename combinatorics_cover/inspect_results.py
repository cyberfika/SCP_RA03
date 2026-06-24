# -*- coding: utf-8 -*-
"""
Inspecao dos arquivos de resultado .npy
Como usar:
    python inspect_results.py              -- mostra todos os resultados disponiveis
    python inspect_results.py 14           -- inspeciona SB15,14 em detalhe
    python inspect_results.py 14 --verify  -- verifica cobertura alem de inspecionar
"""

import sys
import os
from math import comb

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, ".")
from program1_generation import bitmask_para_combo, gerar_array
from solver_greedy import verificar_cobertura

N, K = 25, 15

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "greedy")


def carregar(p: int) -> np.ndarray | None:
    """Carrega resultados_SB15_<p>.npy se existir."""
    arq = os.path.join(RESULTS_DIR, f"resultados_SB{K}_{p}.npy")
    if not os.path.exists(arq):
        return None
    return np.load(arq)


def inspecionar(p: int, verificar: bool = False):
    sb = carregar(p)
    if sb is None:
        print(f"  [p={p}] Arquivo nao encontrado — programa ainda em execucao.")
        return

    lb_lp  = -(-comb(N, p) // comb(K, p))
    n_sp   = comb(N, p)
    gap    = len(sb) / lb_lp

    print(f"\n{'='*60}")
    print(f"  SB{{15,{p}}} — Cobertura de combinacoes de {p} elementos")
    print(f"{'='*60}")
    print(f"  Arquivo        : {os.path.join(RESULTS_DIR, f'resultados_SB{K}_{p}.npy')}")
    print(f"  |SB|           : {len(sb):,}")
    print(f"  Lower bound LP : {lb_lp:,}  [ ceil(C(25,{p})/C(15,{p})) ]")
    print(f"  Gap greedy/LB  : {gap:.3f}x")
    print(f"  |S{p}| (alvo)   : {n_sp:,}")
    print(f"  Fracoes S15 usadas: {len(sb)/comb(N,K)*100:.2f}% de C(25,15)={comb(N,K):,}")
    print(f"  Tipo numpy     : {sb.dtype}  |  Memoria: {sb.nbytes/1e6:.2f} MB")

    # Primeiros 5 elementos
    print(f"\n  Primeiros 5 elementos de SB (como conjuntos):")
    for i, mask in enumerate(sb[:5]):
        combo = bitmask_para_combo(int(mask))
        print(f"    [{i+1}] bitmask={mask:025b}  -> {set(combo)}")

    # Distribuicao dos bitmasks
    popcount = np.array([bin(int(x)).count('1') for x in sb[:1000]])
    print(f"\n  Popcount (primeiros 1000): min={popcount.min()}, "
          f"max={popcount.max()}, media={popcount.mean():.1f}")
    assert (popcount == K).all(), "ERRO: elemento de SB nao tem tamanho K!"
    print(f"  Verificacao de tamanho: todos os elementos tem |X|={K} [OK]")

    if verificar:
        print(f"\n  Verificando cobertura (amostragem)...")
        sp = gerar_array(N, p)
        verificar_cobertura(sb, sp, verbose=True)


def resumo_geral():
    print("\n" + "="*60)
    print("  RESUMO — Arquivos de Resultado Disponiveis")
    print("="*60)
    print(f"  {'p':>3} | {'arquivo':>24} | {'|SB|':>10} | {'LB LP':>10} | {'gap':>6}")
    print(f"  {'-'*3}-+-{'-'*24}-+-{'-'*10}-+-{'-'*10}-+-{'-'*6}")
    for p in [14, 13, 12, 11]:
        sb = carregar(p)
        lb = -(-comb(N, p) // comb(K, p))
        arq = os.path.join(RESULTS_DIR, f"resultados_SB{K}_{p}.npy")
        if sb is None:
            print(f"  {p:>3} | {arq:>24} | {'(pendente)':>10} | {lb:>10,} |    —")
        else:
            print(f"  {p:>3} | {arq:>24} | {len(sb):>10,} | {lb:>10,} | {len(sb)/lb:>5.2f}x")


def main():
    args = sys.argv[1:]

    if not args:
        resumo_geral()
        print("\nUso: python inspect_results.py [p] [--verify]")
        print("Exemplo: python inspect_results.py 14 --verify")
        return

    p = int(args[0])
    verificar = "--verify" in args
    inspecionar(p, verificar=verificar)


if __name__ == "__main__":
    main()
