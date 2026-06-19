# -*- coding: utf-8 -*-
"""
Solver ILP (Programacao Inteira Linear) para Set Cover
Encontra SB <= S15 tal que todo Y em Sp esta contido em algum X em SB.

Modelagem:
  Variavel binaria x_i in {0,1} para cada X_i em S15
  Minimizar:   sum(x_i)
  Sujeito a:   para cada Y em Sp:
               sum_{i: Y <= X_i} x_i >= 1

Viabilidade por escala:
  ILP direto sobre S15 completo e inviavel para todos os p (3.3M variaveis,
  ate 5.2M restricoes). Estrategia: usar os candidatos do greedy como
  universo reduzido de variaveis, entao o ILP encontra o subconjunto
  minimo deles que ainda cobre tudo.

  Esta abordagem e exata dentro do conjunto de candidatos do greedy,
  nao necessariamente globalmente otima.

Requer: pip install pyscipopt
"""

import sys
import time
from math import comb
from itertools import combinations

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, ".")
from program1_generation import gerar_array
from solver_greedy import verificar_cobertura

try:
    from pyscipopt import Model
    SCIP_DISPONIVEL = True
except ImportError:
    SCIP_DISPONIVEL = False


# ---------------------------------------------------------------------------
# Construcao do modelo ILP
# ---------------------------------------------------------------------------

def ilp_set_cover(
    candidatos: np.ndarray,
    sp: np.ndarray,
    p: int,
    n: int = 25,
    k: int = 15,
    verbose: bool = True,
    limite_tempo_s: float = 300.0,
) -> np.ndarray | None:
    """
    Resolve o Set Cover via ILP sobre o conjunto de candidatos.

    Parametros
    ----------
    candidatos   : array uint32 — subconjunto de S15 a usar como variaveis
    sp           : array uint32 — alvos a cobrir
    p            : tamanho das combinacoes alvo
    n, k         : universo e tamanho dos candidatos
    limite_tempo_s: timeout em segundos para o solver

    Retorna
    -------
    np.ndarray uint32 com o SB otimo encontrado, ou None se timeout/erro
    """
    if not SCIP_DISPONIVEL:
        print("  [ERRO] PySCIPOpt nao instalado. Execute: pip install pyscipopt")
        return None

    n_cand = len(candidatos)
    n_sp   = len(sp)

    if verbose:
        print(f"\n[ILP] {n_cand:,} candidatos | {n_sp:,} restricoes | p={p}")
        print(f"      Timeout: {limite_tempo_s:.0f}s")

    t0 = time.time()

    # ------------------------------------------------------------------
    # Construir mapa: indice_sp -> lista de indices em candidatos que cobrem Y
    # ------------------------------------------------------------------
    if verbose:
        print("  Construindo mapa de cobertura...", end=" ", flush=True)

    # Indice: bitmask do candidato -> posicao
    cand_index = {int(x): i for i, x in enumerate(candidatos)}

    # Para cada Y em sp, quais candidatos o cobrem?
    cobertura = []  # cobertura[j] = lista de indices i tal que candidatos[i] contem sp[j]
    for j, y in enumerate(sp):
        y = int(y)
        # Extensoes de y ate tamanho k
        bits_livres = [e for e in range(n) if not (y & (1 << e))]
        cobre = []
        for ext in combinations(bits_livres, k - p):
            x_mask = y
            for e in ext:
                x_mask |= (1 << e)
            idx = cand_index.get(x_mask)
            if idx is not None:
                cobre.append(idx)
        cobertura.append(cobre)

    # Filtrar restricoes com pelo menos um candidato cobrindo
    restricoes_validas = [(j, cob) for j, cob in enumerate(cobertura) if cob]
    n_rest = len(restricoes_validas)

    if n_rest < n_sp and verbose:
        print(f"\n  [aviso] {n_sp - n_rest:,} Y's nao cobertos por nenhum candidato")

    if verbose:
        print(f"OK ({time.time()-t0:.1f}s) | {n_rest:,} restricoes ativas")

    # ------------------------------------------------------------------
    # Modelo SCIP
    # ------------------------------------------------------------------
    model = Model("set_cover")
    model.setRealParam("limits/time", limite_tempo_s)
    if not verbose:
        model.hideOutput()

    # Variaveis binarias x[i] para cada candidato
    x = [model.addVar(f"x_{i}", vtype="B", obj=1.0) for i in range(n_cand)]

    # Restricoes: para cada Y, pelo menos um x que o cobre deve ser 1
    for j, cob in restricoes_validas:
        model.addCons(sum(x[i] for i in cob) >= 1, name=f"cov_{j}")

    # Minimizar numero de candidatos selecionados
    model.setMinimize()

    if verbose:
        print(f"  Modelo: {n_cand:,} variaveis | {n_rest:,} restricoes")
        print(f"  Resolvendo...", end=" ", flush=True)

    model.optimize()
    elapsed = time.time() - t0

    status = model.getStatus()
    if verbose:
        print(f"{status} ({elapsed:.1f}s)")

    if status not in ("optimal", "bestsolfound"):
        if verbose:
            print(f"  [aviso] Status: {status}. Retornando melhor solucao parcial.")

    # Extrair solucao
    try:
        sol = model.getBestSol()
        sb_masks = [
            int(candidatos[i])
            for i in range(n_cand)
            if model.getSolVal(sol, x[i]) > 0.5
        ]
        if verbose:
            print(f"  |SB_ILP| = {len(sb_masks):,}")
        return np.array(sb_masks, dtype=np.uint32)
    except Exception as e:
        if verbose:
            print(f"  [erro ao extrair solucao] {e}")
        return None


# ---------------------------------------------------------------------------
# Entrada principal — teste em escala pequena
# ---------------------------------------------------------------------------

def main():
    print("Solver ILP — Teste em escala reduzida")
    print("Universo reduzido: n=15, k=11, p=10\n")

    N_TESTE, K_TESTE, P_TESTE = 15, 11, 10

    s_grande = gerar_array(N_TESTE, K_TESTE)
    s_alvo   = gerar_array(N_TESTE, P_TESTE)

    lb = comb(N_TESTE, P_TESTE) // comb(K_TESTE, P_TESTE)
    print(f"  Lower bound LP: {lb}")
    print(f"  |S{K_TESTE}| candidatos: {len(s_grande):,}")
    print(f"  |S{P_TESTE}| alvos:      {len(s_alvo):,}")

    if not SCIP_DISPONIVEL:
        print("\n  PySCIPOpt nao instalado. Para instalar:")
        print("    pip install pyscipopt")
        print("\n  Demonstrando estrutura do modelo sem resolver...\n")
        # Mostra estrutura sem resolver
        n_cand = len(s_grande)
        n_sp   = len(s_alvo)
        print(f"  Variaveis: {n_cand:,} binarias x_i")
        print(f"  Restricoes: {n_sp:,} (uma por Y em S{P_TESTE})")
        print(f"  Objetivo: minimizar sum(x_i)")
        return

    sb = ilp_set_cover(
        s_grande, s_alvo, p=P_TESTE, n=N_TESTE, k=K_TESTE,
        verbose=True, limite_tempo_s=60.0
    )

    if sb is not None:
        print()
        verificar_cobertura(sb, s_alvo, verbose=True)
        print(f"  Lower bound LP: |SB| >= {lb}")
        print(f"  Solucao ILP:    |SB|  = {len(sb)}")
        gap = len(sb) / lb if lb > 0 else float("inf")
        print(f"  Gap:            {gap:.2f}x")


if __name__ == "__main__":
    main()
