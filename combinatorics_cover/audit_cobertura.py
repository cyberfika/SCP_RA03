# -*- coding: utf-8 -*-
"""
Auditoria de Cobertura — verificacao exata dos arquivos .npy salvos.

Para cada p em {14, 13, 12, 11}, carrega SB15,p e verifica se TODA
combinacao de p elementos de U={1..25} esta coberta por pelo menos um
elemento de SB (verificacao 100%, sem amostragem).

Metodo: para cada x em SB, vetoriza sobre Sp inteiro via NumPy.
Complexidade: O(|SB| * |Sp|) por caso.
Estimativa de tempo:
  p=11: ~5 s   (|SB|=12.733,  |Sp|=4.457.400)
  p=12: ~20 s  (|SB|=38.100,  |Sp|=5.200.300)
  p=13: ~60 s  (|SB|=128.827, |Sp|=5.200.300)
  p=14: ~3 min (|SB|=532.555, |Sp|=4.457.400)

Uso:
    python audit_cobertura.py           -- verifica p=14,13,12,11
    python audit_cobertura.py 11 12     -- verifica apenas p=11 e p=12
"""

import sys
import os
import time
from math import comb

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, ".")
from program1_generation import gerar_array

N, K = 25, 15
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(_SCRIPT_DIR, "..", "results", "greedy")


def verificar_exato(sb: np.ndarray, sp: np.ndarray) -> tuple[bool, int]:
    """
    Verifica exatamente se todo Y em sp esta coberto por algum X em sb.

    Itera sobre sb; para cada x, marca em coberto[] quais Y satisfazem
    (Y & x) == Y (ou seja, Y e subconjunto de x).

    Retorna (ok, n_nao_cobertos).
    """
    n_sp = len(sp)
    coberto = np.zeros(n_sp, dtype=bool)
    n_cobertos = 0
    t0 = time.time()

    for i, x in enumerate(sb):
        mask = np.uint32(x)
        novos = ~coberto & ((sp & mask) == sp)
        n_novos = int(novos.sum())
        if n_novos:
            coberto |= novos
            n_cobertos += n_novos

        # Saida antecipada quando cobertura e total
        if n_cobertos == n_sp:
            elapsed = time.time() - t0
            print(
                f"\r    {i+1:>7,}/{len(sb):,} elem. SB | "
                f"cobertos=100.00% | {elapsed:.1f}s (saida antecipada)      "
            )
            return True, 0

        # Progresso a cada 5000 iteracoes
        if (i + 1) % 5000 == 0:
            pct = 100.0 * n_cobertos / n_sp
            elapsed = time.time() - t0
            vel = (i + 1) / elapsed if elapsed > 0 else 1
            eta = (len(sb) - i - 1) / vel
            print(
                f"\r    {i+1:>7,}/{len(sb):,} elem. SB | "
                f"cobertos={pct:6.2f}% | "
                f"{elapsed:.0f}s | ETA {eta:.0f}s   ",
                end="",
                flush=True,
            )

    print()
    n_nao = n_sp - n_cobertos
    return n_nao == 0, n_nao


def auditar(p: int):
    print(f"\n{'='*62}")
    print(f"  p={p} | SB{{15,{p}}} — cobertura de S{p} (C({N},{p})={comb(N,p):,})")
    print(f"{'='*62}")

    arq = os.path.join(RESULTS_DIR, f"resultados_SB{K}_{p}.npy")
    if not os.path.exists(arq):
        print(f"  [SKIP] Arquivo nao encontrado: {arq}")
        return None

    sb = np.load(arq)
    lb = -(-comb(N, p) // comb(K, p))
    print(f"  |SB|={len(sb):,} | LB-LP={lb:,} | gap={len(sb)/lb:.2f}x")

    print(f"  Gerando S{p}...", end=" ", flush=True)
    t = time.time()
    sp = gerar_array(N, p)
    print(f"OK em {time.time()-t:.1f}s | {len(sp):,} elementos")

    custo_bilhoes = len(sb) * len(sp) / 1e9
    print(f"  Custo: {len(sb):,} x {len(sp):,} = {custo_bilhoes:.1f}B ops")
    print(f"  Verificando...")

    t_ver = time.time()
    ok, n_nao = verificar_exato(sb, sp)
    elapsed = time.time() - t_ver

    if ok:
        print(f"  [APROVADO] Cobertura 100% confirmada em {elapsed:.1f}s")
    else:
        print(f"  [REPROVADO] {n_nao:,} elementos de S{p} NAO cobertos!")

    return ok


def main():
    args = [int(a) for a in sys.argv[1:] if a.isdigit()]
    casos = args if args else [14, 13, 12, 11]

    print("Auditoria de Cobertura — verificacao exata dos .npy")
    print(f"Casos: p in {casos}")

    resultados = {}
    for p in casos:
        resultados[p] = auditar(p)

    print(f"\n{'='*62}")
    print("  RESUMO")
    print(f"{'='*62}")
    for p in casos:
        r = resultados[p]
        if r is None:
            status = "SKIP (arquivo ausente)"
        elif r:
            status = "APROVADO"
        else:
            status = "REPROVADO"
        print(f"  p={p}: {status}")
    print()


if __name__ == "__main__":
    main()
