# -*- coding: utf-8 -*-
"""
Programa 5 - Cobertura de Combinacoes de 11 Elementos (versao paralela)
Determina SB15,11 <= S15 tal que toda combinacao de 11 elementos
esteja contida em pelo menos um elemento de SB15,11.

  Para todo Y em S11, existe X em SB15,11 tal que Y <= X

Lower bound LP: |SB| >= ceil(C(25,11) / C(15,11)) = ceil(4.457.400 / 1.365) = 3.266

Paralelismo:
  A selecao do maximo (argmax) permanece sequencial — cada passo depende
  do estado atualizado de count[], impossibilitando sobreposicao.

  O loop interno de atualizacao e paralelizado: para cada X selecionado,
  os Y's novamente cobertos sao distribuidos entre N_WORKERS processos.
  Cada worker enumera as C(14,4)=1001 extensoes de seus Y's via
  combinations() e retorna os indices dos X's a decrementar.

  Os indices retornados sao agregados com np.bincount (vetorizado) e
  aplicados a count[] de uma vez no processo principal.

  Lookup em s15: em vez de dict Python (memoria pesada em workers),
  workers recebem s15 pre-ordenado e usam np.searchsorted vetorizado,
  eliminando o overhead de construcao e serializacao de dicionarios.

Speedup esperado (4 nucleos):
  Iteracoes     : 12.733  (sequencial, nao paralelizavel)
  Updates/iter  : 1.366.365  (paralelizavel)
  Speedup teorico: ~4x | Speedup pratico estimado: ~3x
  Tempo seq.    : ~3.4 h  -> Tempo paralelo: ~1.1 h
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

sys.path.insert(0, ".")
from program1_generation import gerar_array
from solver_greedy import verificar_cobertura

N = 25
K = 15
P = 11

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "greedy")

# ---------------------------------------------------------------------------
# Globais do worker — inicializados uma vez por processo via _init_worker
# ---------------------------------------------------------------------------
_s15_sorted  = None   # np.ndarray uint32: s15 ordenado para searchsorted
_s15_argsort = None   # np.ndarray int32:  s15_argsort[i] = indice original de s15_sorted[i]
_N_G         = None   # int: tamanho do universo


def _init_worker(s15_sorted_bytes: bytes, s15_argsort_bytes: bytes, n: int) -> None:
    """
    Inicializa o processo worker com os arrays pre-ordenados de S15.
    Executado uma unica vez na criacao do Pool (nao por iteracao).

    Recebe s15 como bytes (np.ndarray.tobytes()) para serializacao eficiente:
    - s15_sorted  : 3.268.760 x uint32 = 13,1 MB
    - s15_argsort : 3.268.760 x int32  = 13,1 MB
    Total por worker: ~26 MB (vs ~200 MB para dict Python equivalente).
    """
    global _s15_sorted, _s15_argsort, _N_G
    _s15_sorted  = np.frombuffer(s15_sorted_bytes,  dtype=np.uint32).copy()
    _s15_argsort = np.frombuffer(s15_argsort_bytes, dtype=np.int32).copy()
    _N_G = n


def _processar_chunk(args: tuple) -> list:
    """
    Processa um chunk de Y's nao cobertos — executado em worker.

    Para cada (j, y_mask) no chunk:
      1. Enumera os C(14,4)=1001 bitmasks de extensao (bits nao em y_mask).
      2. Realiza busca binaria vetorizada via np.searchsorted sobre s15_sorted.
      3. Retorna os indices originais em S15 que devem ter count[] decrementado.

    Busca vetorizada: todos os x_masks do chunk sao consultados em uma unica
    chamada np.searchsorted, eliminando loops Python para lookup.
    """
    ys_chunk, ext_nec = args
    n = _N_G

    # Gera todos os x_masks do chunk de uma vez (loop Python — gargalo restante)
    x_masks = []
    for _j, y_mask in ys_chunk:
        bits_livres = [e for e in range(n) if not (y_mask & (1 << e))]
        for ext_combo in combinations(bits_livres, ext_nec):
            x_mask = y_mask
            for e in ext_combo:
                x_mask |= (1 << e)
            x_masks.append(x_mask)

    if not x_masks:
        return []

    # Busca binaria vetorizada: O(m * log(|S15|)) com m = len(x_masks)
    arr = np.array(x_masks, dtype=np.uint32)
    pos = np.searchsorted(_s15_sorted, arr)
    valid = (pos < len(_s15_sorted)) & (_s15_sorted[pos] == arr)
    return _s15_argsort[pos[valid]].tolist()


# ---------------------------------------------------------------------------
# Greedy paralelo
# ---------------------------------------------------------------------------

def greedy_cover11_paralelo(
    s15: np.ndarray,
    sp: np.ndarray,
    n: int = N,
    k: int = K,
    p: int = P,
    n_workers: int | None = None,
    verbose: bool = True,
) -> np.ndarray:
    """
    Greedy Set Cover para p=11 com loop interno paralelizado.

    Etapas por iteracao:
      [SEQ]  argmax(count)             -> seleciona i_best
      [SEQ]  combinations(elementos_x) -> encontra ys_novos
      [PAR]  pool.map(_processar_chunk) -> calcula x_indices por worker
      [SEQ]  np.bincount + count -=    -> aplica decrementos

    Retorna np.ndarray uint32 com os bitmasks de SB.
    """
    if n_workers is None:
        n_workers = min(os.cpu_count() or 4, 4)

    n_s15 = len(s15)
    n_sp  = len(sp)
    ext_nec = k - p  # = 4 para p=11, k=15

    # Indice de sp para lookup O(1) na etapa [SEQ]
    sp_index = {int(y): j for j, y in enumerate(sp)}

    # Prepara arrays ordenados para workers (lookup vetorizado)
    s15_sorted  = np.sort(s15)
    s15_argsort = np.argsort(s15).astype(np.int32)

    count         = np.full(n_s15, comb(k, p), dtype=np.int32)
    nao_coberto   = np.ones(n_sp, dtype=bool)
    total_nao_cob = n_sp
    sb_masks      = []
    iter_num      = 0
    t0            = time.time()

    if verbose:
        print(f"\n[Greedy Paralelo p={p}] workers={n_workers} | "
              f"|S{k}|={n_s15:,} | |S{p}|={n_sp:,}")
        print(f"  C({k},{p})={comb(k,p):,} subsets/iter | "
              f"C({n-p},{k-p})={comb(n-p,k-p):,} extensoes/Y | "
              f"~{comb(k,p)*comb(n-p,k-p):,} updates/iter")
        print(f"  Inicializando pool ({n_workers} workers)...",
              end=" ", flush=True)

    with multiprocessing.Pool(
        n_workers,
        initializer=_init_worker,
        initargs=(
            s15_sorted.tobytes(),
            s15_argsort.tobytes(),
            n,
        ),
    ) as pool:
        if verbose:
            print(f"OK ({time.time()-t0:.1f}s)\n")
        t_loop = time.time()

        while total_nao_cob > 0:
            # ------------------------------------------------------------------
            # [SEQ] Selecionar X com maior cobertura atual
            # ------------------------------------------------------------------
            i_best = int(np.argmax(count))
            if count[i_best] <= 0:
                if verbose:
                    print("  [aviso] nenhum candidato util restante")
                break

            x_best = int(s15[i_best])
            count[i_best] = np.iinfo(np.int32).min  # sentinela: nunca re-selecionado
            sb_masks.append(x_best)
            iter_num += 1

            # ------------------------------------------------------------------
            # [SEQ] Encontrar Y's de x_best ainda nao cobertos — O(C(k,p))
            # ------------------------------------------------------------------
            elementos_x = [e for e in range(n) if x_best & (1 << e)]
            ys_novos = []
            for combo_y in combinations(elementos_x, p):
                y_mask = 0
                for e in combo_y:
                    y_mask |= (1 << e)
                j = sp_index.get(y_mask)
                if j is not None and nao_coberto[j]:
                    ys_novos.append((j, y_mask))
                    nao_coberto[j] = False  # atualiza estado antes de enviar ao pool

            total_nao_cob -= len(ys_novos)

            # ------------------------------------------------------------------
            # [PAR] Distribuir Y's entre workers para calcular extensoes
            # ------------------------------------------------------------------
            if ys_novos:
                n_chunks = min(n_workers, len(ys_novos))
                chunks   = [ys_novos[i::n_chunks] for i in range(n_chunks)]

                resultados = pool.map(
                    _processar_chunk,
                    [(chunk, ext_nec) for chunk in chunks if chunk],
                )

                # ------------------------------------------------------------------
                # [SEQ] Agregar e aplicar decrementos — vetorizado
                # ------------------------------------------------------------------
                todos_idx = []
                for parcial in resultados:
                    todos_idx.extend(parcial)

                if todos_idx:
                    decr = np.bincount(
                        np.array(todos_idx, dtype=np.intp),
                        minlength=n_s15,
                    ).astype(np.int32)
                    count -= decr

            # ------------------------------------------------------------------
            # Progresso
            # ------------------------------------------------------------------
            if verbose and (iter_num <= 5 or iter_num % 500 == 0 or total_nao_cob == 0):
                elapsed = time.time() - t_loop
                pct = 100.0 * (n_sp - total_nao_cob) / n_sp
                vel = iter_num / elapsed if elapsed > 0 else 1e-9
                eta = (total_nao_cob / max(len(ys_novos), 1)) / vel
                print(
                    f"  iter={iter_num:>6,} | |SB|={len(sb_masks):>6,} | "
                    f"cobertos={pct:5.1f}% | novos={len(ys_novos):>5,} | "
                    f"loop={elapsed:.1f}s | ETA={eta:.0f}s"
                )

    elapsed_total = time.time() - t0
    if verbose:
        print(f"\n[Greedy Paralelo] Concluido em {elapsed_total:.1f}s")
        print(f"  |SB|         = {len(sb_masks):,}")
        print(f"  Nao cobertos = {int(np.sum(nao_coberto)):,}")
        print(f"  Cobertura    = {100*(n_sp - int(np.sum(nao_coberto)))/n_sp:.4f}%")

    return np.array(sb_masks, dtype=np.uint32)


# ---------------------------------------------------------------------------
# Entrada principal
# ---------------------------------------------------------------------------

def main():
    n_workers = min(os.cpu_count() or 4, 4)

    print("=" * 64)
    print(f"Programa 5 - Cobertura de {P} elementos  [Versao Paralela]")
    print(f"Universo U = {{1..{N}}}, candidatos S{K}, alvos S{P}")
    lb = -(-comb(N, P) // comb(K, P))
    print(f"Lower bound LP: |SB| >= ceil(C(25,11)/C(15,11)) = {lb:,}")
    print(f"Workers: {n_workers}  (os.cpu_count()={os.cpu_count()})")
    print("=" * 64)

    t_total = time.time()

    print(f"\n[1/3] Gerando S{K} (C({N},{K}) = {comb(N,K):,} elementos)...")
    t = time.time()
    s15 = gerar_array(N, K)
    print(f"      OK em {time.time()-t:.1f}s | memoria: {s15.nbytes/1e6:.1f} MB")

    print(f"\n[2/3] Gerando S{P} (C({N},{P}) = {comb(N,P):,} elementos)...")
    t = time.time()
    sp = gerar_array(N, P)
    print(f"      OK em {time.time()-t:.1f}s | memoria: {sp.nbytes/1e6:.1f} MB")

    print(f"\n[3/3] Executando Greedy Paralelo (p={P}, {n_workers} workers)...")
    sb = greedy_cover11_paralelo(s15, sp, n=N, k=K, p=P,
                                 n_workers=n_workers, verbose=True)

    print("\n--- Verificacao de corretude ---")
    verificar_cobertura(sb, sp, verbose=True)

    print("\n--- Resultado final ---")
    lb = -(-comb(N, P) // comb(K, P))
    print(f"  |S{K}|          = {len(s15):,}")
    print(f"  |S{P}|          = {len(sp):,}")
    print(f"  Lower bound LP = {lb:,}")
    print(f"  |SB{K},{P}|      = {len(sb):,}")
    print(f"  Gap de otim.   = {len(sb) / lb:.2f}x")
    print(f"  Tempo total    = {time.time()-t_total:.1f}s")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    saida = os.path.join(RESULTS_DIR, f"resultados_SB{K}_{P}.npy")
    np.save(saida, sb)
    print(f"\n  Resultado salvo em: {saida}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
