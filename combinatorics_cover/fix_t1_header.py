# -*- coding: utf-8 -*-
"""Corrige o spec e header da Tabela 1 (LP lower bounds) em relatorio.tex."""
import os

TEX = os.path.join("..", "docs", "relatorio.tex")

with open(TEX, "r", encoding="utf-8") as f:
    lines = f.readlines()

# L159: spec {crrrrrr} -> {crrr}
lines[158] = r"\begin{tabular}{crrr}" + "\n"

# L161: remover "& --- & --- & ---" do header
lines[160] = (
    r"$p$ & $\C{25}{p}$ & $\C{15}{p}$ & $\lceil \C{25}{p}/\C{15}{p} \rceil$ \\"
    + "\n"
)

with open(TEX, "w", encoding="utf-8") as f:
    f.writelines(lines)

# Verificar
with open(TEX, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"L159: {lines[158]!r}")
print(f"L161: {lines[160]!r}")

# Verificar contagem de colunas: spec vs header vs dados
spec_line  = lines[158].rstrip()
hdr_line   = lines[160].rstrip()
data_lines = [lines[i] for i in [162, 163, 164, 165]]

spec_cols = spec_line.count("}") - 1  # contar fechamentos de {} apos {
# Contar letras de alinhamento dentro das chaves
import re
m = re.search(r"\{([^}]+)\}", spec_line.split("{tabular}")[-1])
if m:
    spec_cols = len(m.group(1))

hdr_cols  = hdr_line.count("&") + 1
data_cols = [l.count("&") + 1 for l in data_lines]

print(f"\nEspec colunas: {spec_cols}")
print(f"Header colunas: {hdr_cols}")
print(f"Dados colunas: {data_cols}")
print("OK!" if spec_cols == hdr_cols == data_cols[0] else "ERRO!")
