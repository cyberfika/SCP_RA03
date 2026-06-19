# -*- coding: utf-8 -*-
"""
Programa 3 - Cobertura de Combinacoes de 13 Elementos
Determina SB15,13 <= S15 tal que toda combinacao de 13 elementos
esteja contida em pelo menos um elemento de SB15,13.

  Para todo Y em S13, existe X em SB15,13 tal que Y <= X

Lower bound LP: |SB| >= C(25,13) / C(15,13) = 5.200.300 / 105 = 49.527
"""

import sys
import time
from math import comb

import numpy as np

sys.path.insert(0, ".")
from program1_generation import gerar_array
from solver_greedy import greedy_set_cover, verificar_cobertura

N = 25
K = 15
P = 13


def main():
    print("=" * 60)
    print(f"Programa 3 - Cobertura de {P} elementos")
    print(f"Universo U = {{1..{N}}}, candidatos S{K}, alvos S{P}")
    print(f"Lower bound LP: |SB| >= {comb(N,P) // comb(K,P):,}")
    print("=" * 60)

    t_total = time.time()

    print(f"\n[1/3] Gerando S{K} (C({N},{K}) = {comb(N,K):,} elementos)...")
    t = time.time()
    s15 = gerar_array(N, K)
    print(f"      OK em {time.time()-t:.1f}s | memoria: {s15.nbytes/1e6:.1f} MB")

    print(f"\n[2/3] Gerando S{P} (C({N},{P}) = {comb(N,P):,} elementos)...")
    t = time.time()
    sp = gerar_array(N, P)
    print(f"      OK em {time.time()-t:.1f}s | memoria: {sp.nbytes/1e6:.1f} MB")

    print(f"\n[3/3] Executando Greedy Set Cover (p={P})...")
    sb = greedy_set_cover(s15, sp, p=P, n=N, k=K, verbose=True)

    print("\n--- Verificacao de corretude ---")
    verificar_cobertura(sb, sp, verbose=True)

    print("\n--- Resultado final ---")
    print(f"  |S{K}|          = {len(s15):,}")
    print(f"  |S{P}|          = {len(sp):,}")
    print(f"  Lower bound LP = {comb(N,P) // comb(K,P):,}")
    print(f"  |SB{K},{P}|      = {len(sb):,}")
    print(f"  Gap de otim.   = {len(sb) / (comb(N,P) // comb(K,P)):.2f}x")
    print(f"  Tempo total    = {time.time()-t_total:.1f}s")

    saida = f"resultados_SB{K}_{P}.npy"
    np.save(saida, sb)
    print(f"\n  Resultado salvo em: {saida}")


if __name__ == "__main__":
    main()
