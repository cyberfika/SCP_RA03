# -*- coding: utf-8 -*-
"""
Atualiza APENAS a tabela de resultados em docs/relatorio.tex
com os dados dos arquivos .npy disponiveis.

A tabela de resultados e identificada pelo caption:
  caption{Resultados do algoritmo Greedy

Como usar:
    python update_relatorio.py       -- atualiza se houver novos resultados
    python update_relatorio.py --dry -- imprime o que seria atualizado, sem salvar
"""

import sys
import os
import re
import time

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(_SCRIPT_DIR, "..", "results", "greedy")
LOGS_DIR = os.path.join(_SCRIPT_DIR, "..", "logs")
from math import comb

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np

N, K = 25, 15
RELATORIO = os.path.join("..", "docs", "relatorio.tex")

# Timing conhecido para p=14 (log da execucao original nao disponivel)
TIMING_CONHECIDO = {14: 577, 12: 4735}


def lower_bound_lp(n, k, p):
    return -(-comb(n, p) // comb(k, p))


def lower_bound_schoenheim(n, k, p):
    if p == 1:
        return -(-n // k)
    if k == p:
        return 1
    if k < p:
        return float("inf")
    return -(-n * lower_bound_schoenheim(n - 1, k - 1, p - 1) // k)


def carregar(p):
    arq = os.path.join(RESULTS_DIR, f"resultados_SB{K}_{p}.npy")
    if not os.path.exists(arq):
        return None
    return np.load(arq)


def tempo_execucao(p):
    """Le o tempo de execucao do log se disponivel."""
    log = os.path.join(LOGS_DIR, f"logs_p{p}.txt")
    if not os.path.exists(log):
        return TIMING_CONHECIDO.get(p)
    with open(log, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    m = re.search(r"Concluido em (\d+\.\d+)s", content)
    if m:
        return float(m.group(1))
    return TIMING_CONHECIDO.get(p)


def fmt(n):
    """Formata inteiro com ponto como separador de milhar (estilo brasileiro)."""
    return f"{n:,}".replace(",", ".")


def fmt_dec(f, decimais=1):
    """Formata float com virgula decimal (LaTeX: 1{,}7). Padrao: 1 decimal."""
    s = f"{f:.{decimais}f}"          # "1.7"
    return s.replace(".", "{,}")     # "1{,}7"


def gerar_linha_resultados(p):
    """Gera linha para a tabela de RESULTADOS (7 colunas).
    Colunas: p | LB-LP | LB-Sch | |SB_greedy| | Gap vs LB-Sch | Tempo (s) | |SB|/|S15|
    """
    sb = carregar(p)
    lb_lp  = lower_bound_lp(N, K, p)
    lb_sch = lower_bound_schoenheim(N, K, p)

    if sb is None:
        return (
            f"{p} & {fmt(lb_lp)} & {fmt(lb_sch)} & "
            "\\textit{em execu\u00e7\u00e3o} & --- & --- & --- \\\\"
        )

    n_sb  = len(sb)
    gap   = n_sb / lb_sch   # gap vs LB-Schonheim (coluna do cabecalho)
    pct   = 100 * n_sb / comb(N, K)

    return (
        f"{p} & {fmt(lb_lp)} & {fmt(lb_sch)} & {fmt(n_sb)} & "
        f"${fmt_dec(gap, 2)}\\times$ & --- & {fmt_dec(pct, 1)}\\% \\\\"
    )


def atualizar_relatorio(dry=False):
    if not os.path.exists(RELATORIO):
        print(f"[ERRO] Arquivo nao encontrado: {RELATORIO}")
        return False

    with open(RELATORIO, "r", encoding="utf-8") as f:
        linhas_arquivo = f.readlines()

    # Localizar a tabela de resultados pelo seu caption unico
    CAPTION = r"\caption{Resultados do algoritmo Greedy"
    idx_caption = next(
        (i for i, l in enumerate(linhas_arquivo) if CAPTION in l), None
    )
    if idx_caption is None:
        print("[ERRO] Tabela de resultados nao encontrada no arquivo.")
        return False

    # Encontrar \midrule dentro dos proximos 10 linhas
    idx_midrule = next(
        (i for i in range(idx_caption, idx_caption + 10)
         if r"\midrule" in linhas_arquivo[i]),
        None,
    )
    if idx_midrule is None:
        print("[ERRO] \\midrule nao encontrado.")
        return False

    print("Atualizando tabela de resultados:")
    modificado = False
    for offset, p in enumerate([14, 13, 12, 11]):
        idx = idx_midrule + 1 + offset
        nova = gerar_linha_resultados(p)
        atual = linhas_arquivo[idx].rstrip("\n")
        status = "OK" if carregar(p) is not None else "(pendente)"
        if atual != nova:
            linhas_arquivo[idx] = nova + "\n"
            modificado = True
            print(f"  p={p} [{status}] L{idx+1}: ATUALIZADO")
        else:
            print(f"  p={p} [{status}] L{idx+1}: sem alteracao")

    if dry:
        print("\n[dry] Nenhuma alteracao salva.")
        return True

    if modificado:
        with open(RELATORIO, "w", encoding="utf-8") as f:
            f.writelines(linhas_arquivo)
        print(f"\n[OK] {RELATORIO} atualizado.")
    else:
        print("\n[OK] Nenhuma alteracao necessaria.")

    return True


def monitorar(intervalo_s=300):
    """Monitora e atualiza o relatorio a cada intervalo_s segundos."""
    print(f"Monitorando (intervalo: {intervalo_s}s). Ctrl+C para parar.\n")
    while True:
        pendentes = [p for p in [13, 12, 11] if carregar(p) is None]
        print(f"[{time.strftime('%H:%M:%S')}] Pendentes: {pendentes}")
        atualizar_relatorio()
        if not pendentes:
            print("\nTodos os resultados disponiveis!")
            break
        print(f"  Aguardando {intervalo_s}s...\n")
        time.sleep(intervalo_s)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--monitor" in args:
        idx = args.index("--monitor")
        intervalo = int(args[idx + 1]) if idx + 1 < len(args) else 300
        monitorar(intervalo)
    elif "--dry" in args:
        atualizar_relatorio(dry=True)
    else:
        atualizar_relatorio()
