# -*- coding: utf-8 -*-
"""
Analysis — Relatorio Comparativo de Resultados
Carrega os arquivos .npy gerados pelos Programas 2-5 e exibe:
  - Tabela de resultados (|SB|, lower bound, gap, tempo)
  - Comparacao greedy vs randomizado
  - Analise de complexidade assintótica
"""

import sys
import os
import time

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "greedy")
from math import comb, log

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, ".")
from program1_generation import gerar_array
from solver_greedy import verificar_cobertura

N = 25
K = 15

# ---------------------------------------------------------------------------
# Lower bounds
# ---------------------------------------------------------------------------

def lower_bound_lp(n: int, k: int, p: int) -> int:
    """Lower bound de relaxacao linear: ceil(C(n,p) / C(k,p))."""
    return -(-comb(n, p) // comb(k, p))  # ceil com inteiros


def lower_bound_schoenheim(n: int, k: int, p: int) -> int:
    """Limite de Schonheim: L(n,k,p) = ceil(n/k * L(n-1,k-1,p-1)).
    Caso base: L(p,p,p) = 1.
    """
    if p == 0 or k == n:
        return 1
    if k < p:
        return 0
    sub = lower_bound_schoenheim(n - 1, k - 1, p - 1)
    return -(-n * sub // k)  # ceil(n/k * sub)


# ---------------------------------------------------------------------------
# Analise de complexidade
# ---------------------------------------------------------------------------

def complexidade_greedy(n: int, k: int, p: int) -> dict:
    """Calcula parametros de complexidade do greedy para dados n, k, p."""
    n_sk     = comb(n, k)
    n_sp     = comb(n, p)
    cob_x    = comb(k, p)    # C(k,p): Y's cobertos por X
    ext_y    = comb(n-p, k-p)  # C(n-p, k-p): X's que contem Y
    lb       = lower_bound_lp(n, k, p)
    updates_iter = cob_x * (ext_y - 1)
    # Tempo total teorico (proporcional): K * C(k,p) * C(n-p,k-p)
    # onde K ~ |SB_greedy|
    return {
        "n_sk": n_sk, "n_sp": n_sp,
        "cob_x": cob_x, "ext_y": ext_y,
        "lb_lp": lb, "lb_sch": lower_bound_schoenheim(n, k, p),
        "updates_iter": updates_iter,
    }


# ---------------------------------------------------------------------------
# Tabela principal
# ---------------------------------------------------------------------------

def cabecalho():
    sep = "=" * 90
    print(sep)
    print("RELATORIO DE RESULTADOS — RA03 Combinatoria")
    print(f"Universo U = {{1..{N}}}, candidatos S{K}")
    print(sep)


def tabela_lower_bounds():
    print("\n--- Lower Bounds teoricos ---\n")
    print(f"{'p':>4} | {'C(25,p)':>10} | {'C(15,p)':>8} | "
          f"{'LB (LP)':>10} | {'LB (Sch)':>10} | {'ln(C(25,p))':>12}")
    print("-" * 70)
    for p in [14, 13, 12, 11]:
        cx = comb(N, p)
        ck = comb(K, p)
        lb = lower_bound_lp(N, K, p)
        ls = lower_bound_schoenheim(N, K, p)
        ln_n = log(cx)
        print(f"  {p:>2} | {cx:>10,} | {ck:>8,} | {lb:>10,} | {ls:>10,} | {ln_n:>12.2f}")


def tabela_complexidade():
    print("\n--- Complexidade do Greedy por iteracao ---\n")
    print(f"{'p':>4} | {'C(k,p)':>8} | {'C(n-p,k-p)':>12} | "
          f"{'updates/iter':>14} | {'estrategia':>18}")
    print("-" * 65)
    for p in [14, 13, 12, 11]:
        c = complexidade_greedy(N, K, p)
        if p == 11:
            # O Programa 5 usa paralelismo para dividir a etapa mais cara de atualizacao.
            estrategia = "parallel update"
        else:
            estrategia = "heap lazy" if c["updates_iter"] <= 10_000 else "numpy argmax"
        print(f"  {p:>2} | {c['cob_x']:>8,} | {c['ext_y']:>12,} | "
              f"{c['updates_iter']:>14,} | {estrategia:>18}")


def tabela_resultados():
    print("\n--- Resultados obtidos (arquivos .npy) ---\n")
    print(f"{'p':>4} | {'|SB| greedy':>12} | {'LB (LP)':>10} | "
          f"{'gap':>6} | {'|SB| random':>12} | {'gap rand':>9} | {'arquivo':>22}")
    print("-" * 90)

    for p in [14, 13, 12, 11]:
        arq_g = os.path.join(RESULTS_DIR, f"resultados_SB{K}_{p}.npy")
        arq_r = os.path.join(RESULTS_DIR, f"resultados_SB{K}_{p}_random.npy")
        lb    = lower_bound_lp(N, K, p)

        sb_g_str = sb_r_str = gap_g = gap_r = "—"

        if os.path.exists(arq_g):
            sb_g = np.load(arq_g)
            sb_g_str = f"{len(sb_g):,}"
            gap_g = f"{len(sb_g)/lb:.2f}x"
        else:
            sb_g_str = "(pendente)"

        if os.path.exists(arq_r):
            sb_r = np.load(arq_r)
            sb_r_str = f"{len(sb_r):,}"
            gap_r = f"{len(sb_r)/lb:.2f}x"

        print(f"  {p:>2} | {sb_g_str:>12} | {lb:>10,} | "
              f"{gap_g:>6} | {sb_r_str:>12} | {gap_r:>9} | {arq_g:>22}")


def tabela_complexidade_assintotica():
    print("\n--- Complexidade assintotica (notacao O / Theta / Omega) ---\n")

    print("Programa 1 — Geracao de Sp:")
    print("  Tempo:  Theta(C(n,p))  —  linear no numero de combinacoes geradas")
    print("  Espaco: Theta(p) se lazy | Theta(C(n,p)) se em array")

    print("\nSolver Greedy (Programas 2-5):")
    print("  Seja K = |SB_greedy|, N15 = C(25,15), Np = C(25,p)")
    print("  Tempo por iteracao: O(C(k,p) * C(n-p,k-p))  [updates de count]")
    print("                    + O(log N15)               [heap] ou O(N15) [argmax]")
    print("  Tempo total:        O(K * C(k,p) * C(n-p,k-p) + K * log N15)")
    print("  Espaco:             O(N15 + Np)")
    print("  Garantia sol.:      |SB| <= H(Np) * |OPT|  onde H(n) = ln(n) + O(1)")

    print("\nSolver Randomizado:")
    print("  Tempo por tentativa: O(|S15| * |Sp|)  (no pior caso)")
    print("  Espaco:              O(|S15| + |Sp|)")
    print("  Garantia:            Nenhuma de otimalidade")

    print("\nGargalos computacionais identificados:")
    print("  1. Construcao dos indices hash: O(|S15| + |Sp|) — executado uma vez")
    print("  2. Loop interno de updates: C(k,p) * C(n-p,k-p) iteracoes Python/iter")
    print("     -> Explode para p pequeno: p=11 => 1.365.000 updates/iter")
    print("  3. Verificacao de cobertura: O(|SB| * |Sp|) — usar amostragem em escala")

    print("\nEscalabilidade:")
    print("  p=14: viavel em ~10 min  (heap eficiente, poucos updates/iter)")
    print("  p=13: viavel em ~30 min")
    print("  p=12: moderado, ~3 horas")
    print("  p=11: mitigado com paralelismo no Programa 5 (1.37M updates/iter)")
    print("  Melhoria possivel: C/Cython, bitsets vetorizados ou particionamento distribuido")


# ---------------------------------------------------------------------------
# Entrada principal
# ---------------------------------------------------------------------------

def main():
    cabecalho()
    tabela_lower_bounds()
    tabela_complexidade()
    tabela_resultados()
    tabela_complexidade_assintotica()
    print("\n" + "=" * 90)


if __name__ == "__main__":
    main()
