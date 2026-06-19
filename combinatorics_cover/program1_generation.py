# -*- coding: utf-8 -*-
"""
Programa 1 - Geracao das Combinacoes
Gera os conjuntos S15, S14, S13, S12 e S11 a partir do universo U = {1..25}.
Representa cada combinação como bitmask de 25 bits (uint32) para eficiência.
"""

import sys
from itertools import combinations
from math import comb
import numpy as np

# Garante saida UTF-8 no terminal Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


UNIVERSO_N = 25
TAMANHOS = [15, 14, 13, 12, 11]


# ---------------------------------------------------------------------------
# Conversão entre combinação e bitmask
# ---------------------------------------------------------------------------

def combo_para_bitmask(combo: tuple[int, ...]) -> int:
    """Converte uma combinação de inteiros em bitmask de 25 bits.

    Elemento e ocupa o bit (e-1). Ex: {1,3} → 0b101 = 5.
    """
    mascara = 0
    for elemento in combo:
        mascara |= (1 << (elemento - 1))
    return mascara


def bitmask_para_combo(mascara: int) -> tuple[int, ...]:
    """Converte um bitmask de 25 bits de volta para tupla de elementos."""
    return tuple(e + 1 for e in range(UNIVERSO_N) if mascara & (1 << e))


# ---------------------------------------------------------------------------
# Geração lazy (iterador) — usa O(p) de espaço
# ---------------------------------------------------------------------------

def gerar_combinacoes_lazy(n: int = UNIVERSO_N, p: int = 15):
    """Gerador lazy de bitmasks para C(n, p). Usa O(p) de memória por vez."""
    for combo in combinations(range(1, n + 1), p):
        yield combo_para_bitmask(combo)


# ---------------------------------------------------------------------------
# Geração em array NumPy — usa O(C(n,p)) de espaço
# ---------------------------------------------------------------------------

def gerar_array(n: int = UNIVERSO_N, p: int = 15) -> np.ndarray:
    """Gera todos os bitmasks de C(n, p) em um array uint32.

    Para C(25,15) = 3.268.760 elementos: ~13 MB em uint32.
    """
    total = comb(n, p)
    arr = np.empty(total, dtype=np.uint32)
    for i, combo in enumerate(combinations(range(1, n + 1), p)):
        mascara = 0
        for e in combo:
            mascara |= (1 << (e - 1))
        arr[i] = mascara
    return arr


# ---------------------------------------------------------------------------
# Verificação de subconjunto (operação central do projeto)
# ---------------------------------------------------------------------------

def contem(x: int, y: int) -> bool:
    """Retorna True se y ⊆ x (y está contido em x). O(1)."""
    return (x & y) == y


def contar_cobertos(x: int, sp_array: np.ndarray) -> int:
    """Conta quantos elementos de sp_array estão contidos em x. Vetorizado."""
    return int(np.sum((sp_array & x) == sp_array))


# ---------------------------------------------------------------------------
# Entrada principal — demonstração e verificação de cardinalidades
# ---------------------------------------------------------------------------

def main():
    print("Programa 1 - Geração das Combinações")
    print(f"Universo U = {{1, ..., {UNIVERSO_N}}}\n")

    for p in TAMANHOS:
        esperado = comb(UNIVERSO_N, p)

        # Conta via iterador (não armazena tudo em memória)
        contagem = sum(1 for _ in gerar_combinacoes_lazy(UNIVERSO_N, p))

        status = "OK" if contagem == esperado else "ERRO"
        print(f"  S{p}: gerado {contagem:>9,} | esperado {esperado:>9,} | {status}")

    print("\nExemplo - primeiras 5 combinacoes de S15:")
    gerador = gerar_combinacoes_lazy(UNIVERSO_N, 15)
    for _ in range(5):
        bitmask = next(gerador)
        combo = bitmask_para_combo(bitmask)
        print(f"  bitmask={bitmask:025b}  ->  {combo}")

    print("\nVerificacao de subconjunto (Y <= X):")
    x = combo_para_bitmask((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))
    y = combo_para_bitmask((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
    z = combo_para_bitmask((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 25))
    print(f"  X = {{1..15}},  Y = {{1..14}},  Z = {{1..14, 25}}")
    print(f"  Y <= X: {contem(x, y)}  (esperado: True)")
    print(f"  Z <= X: {contem(x, z)}  (esperado: False)")


if __name__ == "__main__":
    main()
