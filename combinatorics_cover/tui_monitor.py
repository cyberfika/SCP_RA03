# -*- coding: utf-8 -*-
"""
SCP_RA03 - TUI Dashboard Monitor
Permite visualizar a execução concorrente de todos os resolvedores (p=14, 13, 12, 11)
com barras de progresso coloridas, estatísticas de execução e status.

Suporta:
  - Modo de Demonstração (Escala Reduzida: n=15, k=11) -> Roda em ~5s para ver o painel vivo.
  - Modo Real (Escala Completa: n=25, k=15) -> Roda em tempo real (aviso: p=11 e p=12 são lentos).
"""

import sys
import os
import time

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "tui")
import queue
from itertools import combinations
from math import comb
import multiprocessing

import numpy as np

# Ativa cores ANSI e processamento virtual de terminal no Windows via ctypes / colorama
def ativar_ansi():
    # Tenta usar colorama se disponível
    try:
        import colorama
        colorama.init()
        return
    except ImportError:
        pass
        
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            hStdOut = kernel32.GetStdHandle(-11) # STD_OUTPUT_HANDLE
            if hStdOut and hStdOut != -1:
                mode = ctypes.c_ulong()
                if kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode)):
                    # 0x0004 = ENABLE_VIRTUAL_TERMINAL_PROCESSING
                    kernel32.SetConsoleMode(hStdOut, mode.value | 0x0004)
        except Exception:
            # Fallback para o comando color
            os.system('color')

ativar_ansi()

# Codificação UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Estruturas de dados básicas (gerador e verificador rápido)
# ---------------------------------------------------------------------------

def combo_para_bitmask(combo):
    mask = 0
    for e in combo:
        mask |= (1 << (e - 1))
    return mask

def gerar_array_bitmasks(n, p):
    total = comb(n, p)
    arr = np.empty(total, dtype=np.uint32)
    for i, combo in enumerate(combinations(range(1, n + 1), p)):
        mask = 0
        for e in combo:
            mask |= (1 << (e - 1))
        arr[i] = mask
    return arr


# ---------------------------------------------------------------------------
# Tarefa do resolvedor rodando em processo separado
# ---------------------------------------------------------------------------

def resolver_task(p, n, k, is_demo, q):
    """
    Roda o resolvedor guloso e envia atualizações de progresso para a fila.
    """
    try:
        q.put({"p": p, "type": "status", "val": "Gerando arrays..."})
        s_cand = gerar_array_bitmasks(n, k)
        s_alvo = gerar_array_bitmasks(n, p)
        
        n_cand = len(s_cand)
        n_sp = len(s_alvo)
        
        cobertura_inicial = comb(k, p)
        extensoes_por_y = comb(n - p, k - p)
        
        # Estratégia híbrida
        updates_por_iter = cobertura_inicial * (extensoes_por_y - 1)
        usar_heap = updates_por_iter <= 10_000
        
        # Índices rápidos
        s15_index = {int(x): i for i, x in enumerate(s_cand)}
        sp_index = {int(y): j for j, y in enumerate(s_alvo)}
        
        count = np.full(n_cand, cobertura_inicial, dtype=np.int32)
        nao_coberto = np.ones(n_sp, dtype=bool)
        total_nao_coberto = n_sp
        
        if usar_heap:
            import heapq
            heap = [(-cobertura_inicial, i) for i in range(n_cand)]
            heapq.heapify(heap)
        else:
            heap = None
            
        sb_masks = []
        iter_num = 0
        t0 = time.time()
        
        q.put({
            "p": p, 
            "type": "init", 
            "total_alvos": n_sp, 
            "modo": "heap" if usar_heap else "argmax"
        })
        
        # Loop principal
        while total_nao_coberto > 0:
            if usar_heap:
                while True:
                    if not heap:
                        break
                    neg_cnt, i_best = heapq.heappop(heap)
                    if count[i_best] == -neg_cnt:
                        break
                if not heap and count[i_best] <= 0:
                    break
            else:
                i_best = int(np.argmax(count))
                
            if count[i_best] <= 0:
                break
                
            x_best = int(s_cand[i_best])
            count[i_best] = -1
            sb_masks.append(x_best)
            iter_num += 1
            
            elementos_x = [e for e in range(n) if x_best & (1 << e)]
            novos_cobertos = 0
            extensoes_necessarias = k - p
            
            for combo_y in combinations(elementos_x, p):
                y_mask = 0
                for e in combo_y:
                    y_mask |= (1 << e)
                    
                j = sp_index.get(y_mask)
                if j is None or not nao_coberto[j]:
                    continue
                    
                nao_coberto[j] = False
                novos_cobertos += 1
                
                # Otimização de atualização
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
            
            # Envia atualização
            freq_envio = 5 if is_demo else (500 if p == 14 else 50)
            if iter_num % freq_envio == 0 or total_nao_coberto == 0:
                pct = 100.0 * (n_sp - total_nao_coberto) / n_sp
                q.put({
                    "p": p,
                    "type": "progress",
                    "iter": iter_num,
                    "sb_size": len(sb_masks),
                    "cobertos_pct": pct,
                    "elapsed": time.time() - t0
                })
                
        # Concluído
        tempo_final = time.time() - t0
        os.makedirs(RESULTS_DIR, exist_ok=True)
        fn = os.path.join(RESULTS_DIR, f"tui_resultado_SB{k}_{p}.npy")
        np.save(fn, np.array(sb_masks, dtype=np.uint32))
        
        q.put({
            "p": p,
            "type": "done",
            "sb_size": len(sb_masks),
            "elapsed": tempo_final,
            "file": fn
        })
        
    except Exception as e:
        q.put({"p": p, "type": "error", "msg": str(e)})


# ---------------------------------------------------------------------------
# Renderizador TUI Dashboard
# ---------------------------------------------------------------------------

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_CYAN = "\033[36m"
C_RED = "\033[31m"
C_BG_BLUE = "\033[44m"
C_WHITE = "\033[37m"

def renderizar_tela(n, k, params_p, progresso, total_tempo_inicio):
    # Move o cursor para o topo-esquerdo e limpa o terminal abaixo dele
    sys.stdout.write("\033[H\033[J")
    
    elapsed_total = time.time() - total_tempo_inicio
    modo_str = 'DEMO' if n==15 else 'REAL'
    print(f" {C_BOLD}{C_BLUE}[SCP_RA03 - PAINEL]{C_RESET} Universo: U={n} | Cand: S{k} | Modo: {modo_str} | Tempo: {elapsed_total:.1f}s")
    print("-" * 85)
    
    for p in params_p:
        state = progresso[p]
        status = state["status"]
        
        if status == "CONCLUÍDO":
            st_color = C_GREEN + C_BOLD
        elif status == "ERRO":
            st_color = C_RED + C_BOLD
        elif status == "EM EXECUÇÃO":
            st_color = C_CYAN
        else:
            st_color = C_YELLOW
            
        pct = state["cobertos_pct"]
        num_blocos = int(pct / 5.0)  # 20 blocos max (barra menor)
        barra = "█" * num_blocos + "░" * (20 - num_blocos)
        barra_formatada = f"[{C_GREEN}{barra}{C_RESET}] {pct:5.1f}%"
        
        metodo = state["modo"]
        sb_size = f"{state['sb_size']:,}" if state["sb_size"] > 0 else "—"
        tempo_str = f"{state['elapsed']:.1f}s" if state["elapsed"] > 0 else "—"
        
        print(f"  S{p:<2} | {metodo:<6} | {barra_formatada} | SB: {sb_size:>7} | {tempo_str:>5} | {st_color}{status:<12}{C_RESET}")
        
    print("-" * 85)
    
    ativos = sum(1 for p in params_p if progresso[p]["status"] in ("EM EXECUÇÃO", "Gerando arrays..."))
    if ativos == 0:
        print(f"  {C_GREEN}{C_BOLD}>> CONCLUÍDO! Pressione ENTER para voltar ao menu principal. <<{C_RESET}")
    else:
        print(f"  {C_CYAN}Rodando resolvedores em paralelo... Pressione Ctrl+C para parar.{C_RESET}")


# ---------------------------------------------------------------------------
# Loop Principal de Monitoramento
# ---------------------------------------------------------------------------

def executar_dashboard(is_demo, usar_tui=True):
    if is_demo:
        n, k = 15, 11
        params_p = [10, 9, 8, 7]
    else:
        n, k = 25, 15
        params_p = [14, 13, 12, 11]
        
    q = multiprocessing.Queue()
    
    progresso = {}
    for p in params_p:
        progresso[p] = {
            "status": "AGUARDANDO",
            "cobertos_pct": 0.0,
            "sb_size": 0,
            "elapsed": 0.0,
            "modo": "—"
        }
        
    processos = []
    
    if usar_tui:
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        print(f"\n[SCP_RA03] Inicializando processos em Modo Texto Simples (Sem TUI). Universo: U={n}, Candidatos: S{k}.\n")
        
    total_tempo_inicio = time.time()
    
    for p in params_p:
        proc = multiprocessing.Process(target=resolver_task, args=(p, n, k, is_demo, q))
        proc.start()
        processos.append(proc)
        progresso[p]["status"] = "Gerando arrays..."
        if not usar_tui:
            print(f"  S{p}: Processo disparado...")
            
    last_printed_pct = {p: -20.0 for p in params_p}
    
    try:
        while True:
            ativos = sum(1 for proc in processos if proc.is_alive())
            
            while True:
                try:
                    msg = q.get_nowait()
                    p = msg["p"]
                    t_msg = msg["type"]
                    
                    if t_msg == "init":
                        progresso[p]["status"] = "EM EXECUÇÃO"
                        progresso[p]["modo"] = msg["modo"]
                        if not usar_tui:
                            print(f"  S{p}: Iniciando busca via resolvedor {msg['modo']}...")
                    elif t_msg == "status":
                        progresso[p]["status"] = msg["val"]
                    elif t_msg == "progress":
                        progresso[p]["cobertos_pct"] = msg["cobertos_pct"]
                        progresso[p]["sb_size"] = msg["sb_size"]
                        progresso[p]["elapsed"] = msg["elapsed"]
                        if not usar_tui and msg["cobertos_pct"] - last_printed_pct[p] >= 20.0:
                            print(f"  S{p}: Cobertos={msg['cobertos_pct']:5.1f}% | SB={msg['sb_size']:,} | Tempo={msg['elapsed']:.1f}s")
                            last_printed_pct[p] = msg["cobertos_pct"]
                    elif t_msg == "done":
                        progresso[p]["status"] = "CONCLUÍDO"
                        progresso[p]["cobertos_pct"] = 100.0
                        progresso[p]["sb_size"] = msg["sb_size"]
                        progresso[p]["elapsed"] = msg["elapsed"]
                        if not usar_tui:
                            print(f"  S{p}: {C_GREEN}{C_BOLD}CONCLUÍDO!{C_RESET} Cobertos=100.0% | SB={msg['sb_size']:,} | Tempo={msg['elapsed']:.1f}s")
                    elif t_msg == "error":
                        progresso[p]["status"] = "ERRO"
                        if not usar_tui:
                            print(f"  S{p}: {C_RED}ERRO:{C_RESET} {msg.get('msg')}")
                    
                except queue.Empty:
                    break
                    
            if usar_tui:
                renderizar_tela(n, k, params_p, progresso, total_tempo_inicio)
            
            if ativos == 0:
                time.sleep(0.5)
                # Processa mensagens remanescentes da fila
                while True:
                    try:
                        msg = q.get_nowait()
                        p = msg["p"]
                        t_msg = msg["type"]
                        if t_msg == "done":
                            progresso[p]["status"] = "CONCLUÍDO"
                            progresso[p]["cobertos_pct"] = 100.0
                            progresso[p]["sb_size"] = msg["sb_size"]
                            progresso[p]["elapsed"] = msg["elapsed"]
                            if not usar_tui:
                                print(f"  S{p}: {C_GREEN}{C_BOLD}CONCLUÍDO!{C_RESET} Cobertos=100.0% | SB={msg['sb_size']:,} | Tempo={msg['elapsed']:.1f}s")
                    except queue.Empty:
                        break
                
                if usar_tui:
                    renderizar_tela(n, k, params_p, progresso, total_tempo_inicio)
                    try:
                        input()
                    except (KeyboardInterrupt, EOFError):
                        pass
                else:
                    print(f"\n{C_GREEN}{C_BOLD}>> CONCLUÍDO! Todos os processos finalizaram. <<{C_RESET}")
                    print(f"  Tempo total decorrido: {time.time() - total_tempo_inicio:.1f}s")
                    print(f"  Os resultados foram salvos em '{os.path.abspath(RESULTS_DIR)}'.")
                    print("  Pressione ENTER para voltar ao menu principal.")
                    try:
                        input()
                    except (KeyboardInterrupt, EOFError):
                        pass
                break
                
            if usar_tui:
                time.sleep(0.1) # 10 FPS
            else:
                time.sleep(0.5) # Atualiza a fila mais espaçadamente em modo texto
            
    except KeyboardInterrupt:
        print(f"\n\n{C_YELLOW}Interrompendo processos em execução...{C_RESET}")
        for proc in processos:
            if proc.is_alive():
                proc.terminate()
                proc.join()
        print(f"{C_GREEN}Todos os processos foram encerrados com sucesso.{C_RESET}")
        time.sleep(1.5)


# ---------------------------------------------------------------------------
# Menu Inicial
# ---------------------------------------------------------------------------

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{C_BOLD}{C_BLUE}======================================================================{C_RESET}")
        print(f"{C_BOLD}{C_CYAN}              PAINEL DE CONTROLE DE COBERTURA COMBINATÓRIA            {C_RESET}")
        print(f"{C_BOLD}{C_BLUE}======================================================================{C_RESET}")
        print("  Escolha uma opção de execução:")
        print(f"\n  {C_BOLD}1. Modo TUI (Gráfico) — Escala Reduzida (~5s){C_RESET}")
        print("     Painel interativo compacto com barras de progresso (requer console compatível).")
        print(f"\n  {C_BOLD}2. Modo LOG (Texto) — Escala Reduzida (~5s){C_RESET}")
        print("     Texto puro que apenas lista eventos importantes. Ideal se a TUI fizer scroll.")
        print(f"\n  {C_BOLD}3. Modo TUI (Gráfico) — Escala Real (Demorado){C_RESET}")
        print("     Executa o problema completo de forma gráfica (N=25, candidatos K=15).")
        print(f"\n  {C_BOLD}4. Modo LOG (Texto) — Escala Real (Demorado){C_RESET}")
        print("     Executa o problema completo em formato texto puro, listando progresso a cada 20%.")
        print(f"\n  {C_BOLD}5. SAIR{C_RESET}")
        print(f"\n{C_BOLD}{C_BLUE}======================================================================{C_RESET}")
        
        opcao = input("  Opção desejada (1-5): ").strip()
        
        if opcao == '1':
            executar_dashboard(is_demo=True, usar_tui=True)
        elif opcao == '2':
            executar_dashboard(is_demo=True, usar_tui=False)
        elif opcao == '3':
            confirmacao = input("  Você escolheu a escala real. Deseja prosseguir? (s/n): ").strip().lower()
            if confirmacao == 's':
                executar_dashboard(is_demo=False, usar_tui=True)
        elif opcao == '4':
            confirmacao = input("  Você escolheu a escala real. Deseja prosseguir? (s/n): ").strip().lower()
            if confirmacao == 's':
                executar_dashboard(is_demo=False, usar_tui=False)
        elif opcao == '5':
            print("\n  Saindo. Até logo!")
            break
        else:
            print("\n  Opção inválida! Pressione Enter para tentar novamente...")
            input()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
