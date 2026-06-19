# -*- coding: utf-8 -*-
"""Corrige a linha 620 do relatorio.tex."""
import os

TEX = os.path.join("..", "docs", "relatorio.tex")

with open(TEX, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Linha 620 (0-indexed: 619): corrigir o acento malformado
# Conteudo correto com UTF-8 direto (arquivo usa [utf8]{inputenc})
correct = r"11 & $\approx 6$h     & $\bigo{K \cdot 1.366.365}$ & Requer C/Cython ou " + "\u00edndice invertido \\\\\n"
lines[619] = correct

with open(TEX, "w", encoding="utf-8") as f:
    f.writelines(lines)

# Verificar
with open(TEX, "r", encoding="utf-8") as f:
    lines_check = f.readlines()
print(repr(lines_check[619]))
