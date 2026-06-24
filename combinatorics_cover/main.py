# -*- coding: utf-8 -*-
"""
SCP_RA03 — Menu Principal
Ponto de entrada unificado para todos os programas e utilitarios do projeto.

Uso:
    python main.py
"""

import sys
import os
import subprocess
import time
from math import comb

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "..", "results", "greedy")
EXPERIMENT_RESULTS_DIR = os.path.join(SCRIPT_DIR, "..", "results", "experiments")
LOGS_DIR    = os.path.join(SCRIPT_DIR, "..", "logs")

N, K = 25, 15

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def limpar():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\nPressione ENTER para voltar ao menu...")


def status_resultados():
    """Retorna dict p -> (existe, tamanho) para os 4 casos."""
    status = {}
    for p in [14, 13, 12, 11]:
        arq = os.path.join(RESULTS_DIR, f"resultados_SB{K}_{p}.npy")
        if os.path.exists(arq):
            kb = os.path.getsize(arq) / 1024
            status[p] = (True, kb)
        else:
            status[p] = (False, 0)
    return status


def linha_status(p, st):
    existe, kb = st[p]
    lb = -(-comb(N, p) // comb(K, p))
    if existe:
        return f"  p={p}  [OK  {kb:>8.1f} KB]  LB={lb:,}"
    else:
        return f"  p={p}  [pendente      ]  LB={lb:,}"


def status_experimentos():
    """Retorna status dos benchmarks experimentais usados na apresentacao."""
    expected_files = {
        "small": "benchmark_small_all.md",
        "medium": "benchmark_medium_all.md",
        "large-demo": "benchmark_large-demo_all.md",
    }
    status = {}
    for preset, filename in expected_files.items():
        path = os.path.join(EXPERIMENT_RESULTS_DIR, filename)
        status[preset] = (os.path.exists(path), path)
    return status


def linha_status_experimento(preset, st):
    """Formata uma linha de status para um preset experimental."""
    exists, path = st[preset]
    marker = "OK" if exists else "pendente"
    return f"  {preset:<10} [{marker:<8}]  {os.path.relpath(path, SCRIPT_DIR)}"


def executar(script, args=None, log_path=None):
    """
    Executa script Python com saida em tempo real.
    Se log_path informado, salva saida simultaneamente no arquivo.
    """
    cmd = [sys.executable, script] + (args or [])
    proc = subprocess.Popen(
        cmd,
        cwd=SCRIPT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    f_log = None
    if log_path:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        f_log = open(log_path, "w", encoding="utf-8")
        print(f"[log] Salvando em: {log_path}\n")
    try:
        for linha in proc.stdout:
            print(linha, end="", flush=True)
            if f_log:
                f_log.write(linha)
    finally:
        if f_log:
            f_log.close()
    proc.wait()
    return proc.returncode


def executar_script_path(script_path, args=None, log_path=None):
    """Executa um script Python por caminho relativo ao projeto combinatorics_cover."""
    return executar(script_path, args=args, log_path=log_path)


def perguntar_log(nome_log):
    """Pergunta se usuario quer salvar log. Retorna path ou None."""
    r = input(f"\nSalvar saida em logs/{nome_log}? [s/N] ").strip().lower()
    if r == "s":
        return os.path.join(LOGS_DIR, nome_log)
    return None


# ---------------------------------------------------------------------------
# Acoes do menu
# ---------------------------------------------------------------------------

def rodar_programa(numero, p=None):
    scripts = {
        1:  ("program1_generation.py",         None),
        11: ("program1_generation_parallel.py", None),
        2:  ("program2_cover14.py",             "logs_p14.txt"),
        3:  ("program3_cover13.py",             "logs_p13.txt"),
        4:  ("program4_cover12.py",             "logs_p12.txt"),
        5:  ("program5_cover11.py",             "logs_p11.txt"),
    }
    script, nome_log = scripts[numero]
    log = perguntar_log(nome_log) if nome_log else None
    print()
    t0 = time.time()
    rc = executar(script, log_path=log)
    elapsed = time.time() - t0
    print(f"\n[Concluido em {elapsed:.0f}s | codigo de saida: {rc}]")
    pausar()


def rodar_todos():
    print("\nRodara Programas 2, 3, 4 e 5 em sequencia.")
    print("Tempo estimado total: ~8 horas.")
    r = input("Confirma? [s/N] ").strip().lower()
    if r != "s":
        return
    salvar = input("Salvar logs individuais? [s/N] ").strip().lower() == "s"
    for num, nome_log in [(2, "logs_p14.txt"), (3, "logs_p13.txt"),
                          (4, "logs_p12.txt"), (5, "logs_p11.txt")]:
        scripts = {2: "program2_cover14.py", 3: "program3_cover13.py",
                   4: "program4_cover12.py", 5: "program5_cover11.py"}
        log = os.path.join(LOGS_DIR, nome_log) if salvar else None
        print(f"\n{'='*60}")
        print(f"  Iniciando Programa {num}...")
        print(f"{'='*60}")
        t0 = time.time()
        executar(scripts[num], log_path=log)
        print(f"\n[Programa {num} concluido em {time.time()-t0:.0f}s]")
    pausar()


def rodar_todos_programas_e_experimentos():
    print("\nRodara Programas 1, 1 paralelo, 2, 3, 4, 5 e benchmarks experimentais.")
    print("Tempo estimado: programas reais podem levar varias horas.")
    print("Benchmarks: small, medium e large-demo (large-demo sem Lagrangiana/Column Generation).")
    r = input("Confirma execucao completa? [s/N] ").strip().lower()
    if r != "s":
        return

    print("\n[Etapa 1/3] Geracao sequencial e paralela")
    executar("program1_generation.py")
    executar("program1_generation_parallel.py")

    print("\n[Etapa 2/3] Programas 2-5")
    salvar = input("Salvar logs dos Programas 2-5? [s/N] ").strip().lower() == "s"
    for script, log_name in [
        ("program2_cover14.py", "logs_p14.txt"),
        ("program3_cover13.py", "logs_p13.txt"),
        ("program4_cover12.py", "logs_p12.txt"),
        ("program5_cover11.py", "logs_p11.txt"),
    ]:
        log = os.path.join(LOGS_DIR, log_name) if salvar else None
        executar(script, log_path=log)

    print("\n[Etapa 3/3] Benchmarks experimentais")
    rodar_todos_experimentos(pausar_ao_final=False, confirmar=False)
    pausar()


def rodar_inspecao():
    args_extra = input("\nDigite p para detalhes (ex: 14) ou ENTER para resumo: ").strip()
    verify = ""
    if args_extra:
        v = input("Verificar cobertura por amostragem? [s/N] ").strip().lower()
        verify = "--verify" if v == "s" else ""
    print()
    args = [args_extra] if args_extra else []
    if verify:
        args.append(verify)
    executar("inspect_results.py", args=args)
    pausar()


def rodar_auditoria():
    print("\nVerificacao exata (sem amostragem) dos arquivos .npy.")
    print("Tempo estimado: p=11 ~5s | p=12 ~20s | p=13 ~60s | p=14 ~3min")
    casos = input("Quais p verificar? (ex: 11 12 | ENTER = todos): ").strip()
    args = casos.split() if casos else []
    print()
    executar("audit_cobertura.py", args=args)
    pausar()


def rodar_tui():
    print()
    executar("tui_monitor.py")


def rodar_analysis():
    print()
    executar("analysis.py")
    pausar()


def rodar_update_relatorio():
    dry = input("\nModo dry (apenas visualizar, sem salvar)? [s/N] ").strip().lower()
    args = ["--dry"] if dry == "s" else []
    print()
    executar("update_relatorio.py", args=args)
    pausar()


def rodar_experimento(preset, solver="all", skip_advanced=False):
    """Executa benchmark experimental e exporta CSV/JSON/Markdown."""
    args = ["--preset", preset, "--solver", solver]
    if skip_advanced:
        args.append("--skip-advanced-on-large")
    return executar_script_path(os.path.join("experiments", "benchmark.py"), args=args)


def rodar_todos_experimentos(pausar_ao_final=True, confirmar=True):
    print("\nBenchmarks experimentais disponiveis:")
    print("  small      : todos os metodos, rapido")
    print("  medium     : todos os metodos, ~2 min")
    print("  large-demo : metodos construtivos; pula Lagrangiana/Column Generation")
    if confirmar:
        r = input("Rodar todos os benchmarks experimentais? [s/N] ").strip().lower()
        if r != "s":
            return
    rodar_experimento("small")
    rodar_experimento("medium")
    rodar_experimento("large-demo", skip_advanced=True)
    if pausar_ao_final:
        pausar()


def menu_experimentos():
    while True:
        limpar()
        st_exp = status_experimentos()
        print("=" * 58)
        print("  SCP_RA03 — Experimentos Algoritmicos")
        print("=" * 58)
        print("\n  Status dos artefatos:")
        for preset in ["small", "medium", "large-demo"]:
            print(linha_status_experimento(preset, st_exp))
        print("\n  1. Benchmark small — todos os metodos")
        print("  2. Benchmark medium — todos os metodos")
        print("  3. Benchmark large-demo — metodos construtivos")
        print("  4. Benchmark customizado")
        print("  5. Rodar todos os benchmarks experimentais")
        print("  0. Voltar")
        print("=" * 58)

        opcao = input("\n  Opcao: ").strip()
        if opcao == "0":
            break
        elif opcao == "1":
            rodar_experimento("small")
            pausar()
        elif opcao == "2":
            rodar_experimento("medium")
            pausar()
        elif opcao == "3":
            rodar_experimento("large-demo", skip_advanced=True)
            pausar()
        elif opcao == "4":
            preset = input("Preset (small/medium/large-demo): ").strip()
            solver = input("Solver (all/greedy/stochastic/grasp/local-search/lagrangian/column-generation): ").strip()
            skip = input("Pular metodos avancados se large-demo? [S/n] ").strip().lower() != "n"
            rodar_experimento(preset, solver or "all", skip_advanced=skip)
            pausar()
        elif opcao == "5":
            rodar_todos_experimentos()
        else:
            input("  Opcao invalida. ENTER para tentar novamente...")


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------

def menu():
    while True:
        limpar()
        st = status_resultados()

        print("=" * 58)
        print("  SCP_RA03 — Cobertura Combinatoria  |  U={1..25}")
        print("=" * 58)
        print("\n  Status dos resultados:")
        for p in [14, 13, 12, 11]:
            print(linha_status(p, st))
        print("\n  Status dos experimentos:")
        st_exp = status_experimentos()
        for preset in ["small", "medium", "large-demo"]:
            print(linha_status_experimento(preset, st_exp))

        print("\n  --- Geracao ---")
        print("  1. Programa 1 — Gerar e validar S15..S11 (sequencial)")
        print(" 1b. Programa 1 — Gerar S15..S11 em paralelo (multiprocessing)")

        print("\n  --- Cobertura Greedy ---")
        print("  2. Programa 2 — SB{15,14}  (~18 min)")
        print("  3. Programa 3 — SB{15,13}  (~3 h)")
        print("  4. Programa 4 — SB{15,12}  (~79 min)")
        print("  5. Programa 5 — SB{15,11}  (~3.4 h)")
        print("  6. Todos os programas 2-5 em sequencia")
        print(" 6b. Todos os programas e experimentos")

        print("\n  --- Interface Visual ---")
        print("  7. Monitor TUI (demo / escala real)")
        print(" 7b. Menu de experimentos")

        print("\n  --- Utilitarios ---")
        print("  8. Inspecionar resultados (.npy)")
        print("  9. Auditar cobertura (verificacao exata)")
        print(" 10. Analise de complexidade")
        print(" 11. Atualizar relatorio.tex")

        print("\n  0. Sair")
        print("=" * 58)

        opcao = input("\n  Opcao: ").strip()

        if   opcao == "0":  break
        elif opcao == "1":  rodar_programa(1)
        elif opcao == "1b": rodar_programa(11)
        elif opcao == "2":  rodar_programa(2)
        elif opcao == "3":  rodar_programa(3)
        elif opcao == "4":  rodar_programa(4)
        elif opcao == "5":  rodar_programa(5)
        elif opcao == "6":  rodar_todos()
        elif opcao == "6b": rodar_todos_programas_e_experimentos()
        elif opcao == "7":  rodar_tui()
        elif opcao == "7b": menu_experimentos()
        elif opcao == "8":  rodar_inspecao()
        elif opcao == "9":  rodar_auditoria()
        elif opcao == "10": rodar_analysis()
        elif opcao == "11": rodar_update_relatorio()
        else:
            input("  Opcao invalida. ENTER para tentar novamente...")

    limpar()
    print("  Ate logo!\n")


if __name__ == "__main__":
    menu()
