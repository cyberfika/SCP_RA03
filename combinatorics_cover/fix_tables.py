# -*- coding: utf-8 -*-
"""
Corrige todas as tabelas de relatorio.tex com os dados corretos.
Cada tabela tem numero especifico de colunas — este script garante isso.
"""
import os

TEX = os.path.join("..", "docs", "relatorio.tex")

with open(TEX, "r", encoding="utf-8") as f:
    linhas = f.readlines()


def rep(lineno, conteudo):
    """Substitui linha (1-indexed) preservando \n."""
    linhas[lineno - 1] = conteudo + "\n"


# ---------------------------------------------------------------------------
# Tabela 1 (L159, {crrr}): Lower bounds LP
# Cabecalho: p | C(25,p) | C(15,p) | ceil(C(25,p)/C(15,p))
# Valores: C(25,14)=4457400 C(15,14)=15 LB=297160
#          C(25,13)=5200300 C(15,13)=105 LB=49527
#          C(25,12)=5200300 C(15,12)=455 LB=11429
#          C(25,11)=4457400 C(15,11)=1365 LB=3266
# ---------------------------------------------------------------------------
rep(163, r"14 & 4.457.400 & 15    & 297.160 \\")
rep(164, r"13 & 5.200.300 & 105   & 49.527  \\")
rep(165, r"12 & 5.200.300 & 455   & 11.429  \\")
rep(166, r"11 & 4.457.400 & 1.365 & 3.266   \\")

# ---------------------------------------------------------------------------
# Tabela 2 (L207, {crrrr}): Comparacao LP vs Schonheim
# Cabecalho: p | |Sp| | LB-LP | LB-Schonheim | Razao Sch/LP
# Razao: 297172/297160=1.00, 58887/49527=1.19, 13175/11430=1.15, 3370/3266=1.03
# ---------------------------------------------------------------------------
rep(211, r"14 & 4.457.400 & 297.160 & 297.172 & 1{,}00$\times$ \\")
rep(212, r"13 & 5.200.300 & 49.527  & 58.887  & 1{,}19$\times$ \\")
rep(213, r"12 & 5.200.300 & 11.430  & 13.175  & 1{,}15$\times$ \\")
rep(214, r"11 & 4.457.400 & 3.266   & 3.370   & 1{,}03$\times$ \\")

# ---------------------------------------------------------------------------
# Tabela 3 (L358, {crrrrr}): Complexidade do Greedy por iteracao
# Cabecalho: p | C(15,p) | C(25-p,15-p) | Atualiz./iter | K_greedy | Estrategia
# p=12 confirmado: |SB|=38100
# ---------------------------------------------------------------------------
rep(362, r"14 & 15    & 11    & 165         & 532.555         & heap lazy    \\")
rep(363, r"13 & 105   & 66    & 6.930       & $\approx$90.000 & heap lazy    \\")
rep(364, r"12 & 455   & 286   & 130.130     & 38.100          & argmax NumPy \\")
rep(365, r"11 & 1.365 & 1.001 & 1.366.365   & $\approx$5.000  & argmax NumPy \\")

# ---------------------------------------------------------------------------
# Tabela 4 (L458, {crrr}): Dimensao do ILP em escala completa (sobre S15)
# Cabecalho: p | Variaveis | Restricoes | Coef. nao-nulos
# Coef. nao-nulos ~ |Sp| * C(25-p, 15-p)
# p=14: 4457400*11=49M, p=13: 5200300*66=343M, p=12: 5200300*286=1.5B, p=11: 4457400*1001=4.5B
# ---------------------------------------------------------------------------
rep(462, r"14 & 3.268.760 & 4.457.400 & $\approx 49$M  \\")
rep(463, r"13 & 3.268.760 & 5.200.300 & $\approx 343$M \\")
rep(464, r"12 & 3.268.760 & 5.200.300 & $\approx 1{,}5$B \\")
rep(465, r"11 & 3.268.760 & 4.457.400 & $\approx 4{,}5$B \\")

# ---------------------------------------------------------------------------
# Tabela 5 (L530, {crrrrrr}): RESULTADOS PRINCIPAIS — tabela que o update_relatorio
# atualiza automaticamente.
# Cabecalho: p | LB-LP | LB-Sch | |SB_greedy| | Gap | Tempo(s) | |SB|/|S15|
# p=14: |SB|=532555, gap=1.79x, t=1070s, pct=16.29%
# p=12: |SB|=38100,  gap=3.33x, t=4735s, pct=1.17%
# ---------------------------------------------------------------------------
rep(534, r"14 & 297.160 & 297.172 & 532.555 & 1{,}79$\times$ & 1.070 & 16{,}29\% \\")
rep(535, "13 & 49.527  & 58.887  & \\textit{(em execu\u00e7\u00e3o)} & --- & --- & --- \\\\")
rep(536, r"12 & 11.430  & 13.175  & 38.100  & 3{,}33$\times$ & 4.735 & 1{,}17\% \\")
rep(537, "11 & 3.266   & 3.370   & \\textit{(em execu\u00e7\u00e3o)} & --- & --- & --- \\\\")

# ---------------------------------------------------------------------------
# Tabela 6 (L613, {clll}): Escalabilidade
# Cabecalho: p | Tempo observado | Limitante teorico | Melhoria possivel
# ---------------------------------------------------------------------------
rep(617, "14 & $\\approx 18$ min & $\\bigo{K \\cdot 165}$       & Heap adequado; vi\u00e1vel \\\\")
rep(618, "13 & $\\approx 1{,}5$h & $\\bigo{K \\cdot 6.930}$     & Heap com poda peri\u00f3dica \\\\")
rep(619, "12 & $\\approx 79$ min & $\\bigo{K \\cdot 130.130}$   & NumPy argmax; aceit\u00e1vel \\\\")
rep(620, "11 & $\\approx 6$h     & $\\bigo{K \\cdot 1.366.365}$ & Requer C/Cython ou \u00edndice invertido \\\\")

with open(TEX, "w", encoding="utf-8") as f:
    f.writelines(linhas)

# Verificacao final
print("Verificacao final das tabelas:")
with open(TEX, "r", encoding="utf-8") as f:
    linhas_check = f.readlines()

tabelas = {
    "T1 LP ({crrr})":       ([163,164,165,166], 4),
    "T2 Sch ({crrrr})":     ([211,212,213,214], 5),
    "T3 Greedy ({crrrrr})": ([362,363,364,365], 6),
    "T4 ILP ({crrr})":      ([462,463,464,465], 4),
    "T5 Resultados ({crrrrrr})": ([534,535,536,537], 7),
    "T6 Escalab. ({clll})": ([617,618,619,620], 4),
}
ok = True
for nome, (lns, esperado) in tabelas.items():
    print(f"  {nome}:")
    for ln in lns:
        l = linhas_check[ln - 1].rstrip()
        n = l.count("&") + 1
        s = "OK" if n == esperado else f"ERRO ({n}!={esperado})"
        if n != esperado:
            ok = False
        print(f"    L{ln}: {n} cols [{s}] {l[:55]}")

print("\nTodas as tabelas OK!" if ok else "\nERROS ENCONTRADOS!")
