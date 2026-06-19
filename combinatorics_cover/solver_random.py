# -*- coding: utf-8 -*-
"""
Solver Randomizado (Monte Carlo) para Set Cover
Encontra SB <= S15 tal que todo Y em Sp esta contido em algum X em SB.

Estrategia:
  Seleciona elementos de S15 aleatoriamente, sem ordenacao por cobertura.
  Repete multiplas tentativas e retorna a melhor solucao encontrada.
  Util como baseline de comparacao com o greedy.

Complexidade por tentativa:
  Tempo:  O(|S15| + |Sp|)  — linear (sem contagem de cobertura)
  Espaco: O(|S15| + |Sp|)

Garantia: nenhuma de otimalidade. Probabilisticamente, para cobertura
completa, espera-se selecionar O(|S15|/|SB_otimo| * ln(|Sp|)) elementos.
"""

import sys
import time
from math import comb

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, ".")
from program1_generation import gerar_array
from solver_greedy import verificar_cobertura


def random_set_cover(
    s15: np.ndarray,
    sp: np.ndarray,
    p: int,
    n: int = 25,
    k: int = 15,
    n_tentativas: int = 5,
    seed: int = 42,
    verbose: bool = True,
) -> np.ndarray:
    """
    Monte Carlo Set Cover: seleciona elementos aleatorios de S15 ate cobrir Sp.

    Parametros
    ----------
    s15         : array uint32 — candidatos C(n,k)
    sp          : array uint32 — alvos C(n,p)
    p           : tamanho das combinacoes a cobrir
    n, k        : parametros do universo e candidatos
    n_tentativas: numero de repeticoes independentes
    seed        : semente para reproducibilidade
    verbose     : imprime progresso

    Retorna
    -------
    np.ndarray uint32 — melhor SB encontrado entre as tentativas
    """
    rng = np.random.default_rng(seed)
    n_sp = len(sp)
    melhor_sb = None
    t0 = time.time()

    if verbose:
        lb = n_sp // comb(k, p)
        print(f"\n[Random] p={p} | {n_tentativas} tentativas | lower bound >= {lb:,}")

    for tentativa in range(1, n_tentativas + 1):
        # Permutacao aleatoria dos candidatos
        ordem = rng.permutation(len(s15))
        s15_embaralhado = s15[ordem]

        sb_indices = []
        nao_coberto = np.ones(n_sp, dtype=bool)
        total_nao_coberto = n_sp

        for x in s15_embaralhado:
            if total_nao_coberto == 0:
                break

            # Verificar quais Y nao cobertos sao cobertos por x
            novos = (sp[nao_coberto] & x) == sp[nao_coberto]
            if novos.any():
                sb_indices.append(x)
                # Atualizar nao_coberto
                idx_nao_cob = np.where(nao_coberto)[0]
                nao_coberto[idx_nao_cob[novos]] = False
                total_nao_coberto -= int(novos.sum())

        sb = np.array(sb_indices, dtype=np.uint32)
        elapsed = time.time() - t0

        if verbose:
            print(
                f"  tentativa={tentativa} | |SB|={len(sb):,} | "
                f"restantes={total_nao_coberto:,} | tempo={elapsed:.1f}s"
            )

        if total_nao_coberto == 0:
            if melhor_sb is None or len(sb) < len(melhor_sb):
                melhor_sb = sb

    if melhor_sb is None:
        if verbose:
            print("  [aviso] nenhuma tentativa cobriu tudo")
        melhor_sb = sb  # retorna a ultima mesmo incompleta

    if verbose:
        lb = n_sp // comb(k, p)
        print(f"\n[Random] Melhor |SB| = {len(melhor_sb):,}")
        print(f"         Lower bound  = {lb:,}")
        print(f"         Gap          = {len(melhor_sb)/lb:.2f}x")

    return melhor_sb


# ---------------------------------------------------------------------------
# Entrada principal — teste e comparacao com greedy
# ---------------------------------------------------------------------------

def main():
    print("Solver Randomizado - Teste em escala reduzida")
    print("Universo reduzido: n=15, k=11, p=10\n")

    N_TESTE, K_TESTE, P_TESTE = 15, 11, 10

    s_grande = gerar_array(N_TESTE, K_TESTE)
    s_alvo   = gerar_array(N_TESTE, P_TESTE)

    sb = random_set_cover(
        s_grande, s_alvo, p=P_TESTE, n=N_TESTE, k=K_TESTE,
        n_tentativas=10, verbose=True
    )

    print()
    verificar_cobertura(sb, s_alvo, verbose=True)

    lb = comb(N_TESTE, P_TESTE) // comb(K_TESTE, P_TESTE)
    print(f"  Lower bound LP: |SB| >= {lb}")
    print(f"  Solucao random: |SB|  = {len(sb)}")


if __name__ == "__main__":
    main()
