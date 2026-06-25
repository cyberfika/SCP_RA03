# -*- coding: utf-8 -*-
"""
Generate white-background chart assets for docs/relatorio.tex.

These charts are designed for a printed/PDF report, not for the dark slide deck.
They avoid large internal titles because the LaTeX captions provide the context.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


OUTPUT_DIR = Path(__file__).resolve().parent

BG = "#ffffff"
TEXT = "#111827"
MUTED = "#4b5563"
GRID = "#d1d5db"
CYAN = "#0284c7"
GREEN = "#059669"
AMBER = "#d97706"
PURPLE = "#7c3aed"
PINK = "#db2777"
SLATE = "#64748b"
RED = "#dc2626"

METHOD_COLORS = {
    "Greedy baseline": CYAN,
    "Stochastic Greedy": GREEN,
    "GRASP": AMBER,
    "Relaxação Lagrangiana": PURPLE,
    "Column Generation": PINK,
    "Greedy + poda local": SLATE,
}


@dataclass(frozen=True)
class ExperimentResult:
    instance: str
    method: str
    seconds: float
    selected_count: int


EXPERIMENTS = [
    ExperimentResult("medium", "Greedy baseline", 10.035, 140),
    ExperimentResult("medium", "Stochastic Greedy", 0.743, 152),
    ExperimentResult("medium", "GRASP", 48.813, 143),
    ExperimentResult("medium", "Relaxação Lagrangiana", 23.948, 140),
    ExperimentResult("medium", "Column Generation", 18.551, 171),
    ExperimentResult("large-demo", "Greedy baseline", 24.895, 105),
    ExperimentResult("large-demo", "Stochastic Greedy", 1.208, 115),
    ExperimentResult("large-demo", "GRASP", 143.862, 107),
    ExperimentResult("large-demo", "Greedy + poda local", 28.268, 105),
]

FINAL_RESULTS = [
    {"p": "14", "lb_sch": 297_172, "sb": 532_555, "updates": 165},
    {"p": "13", "lb_sch": 58_887, "sb": 128_827, "updates": 6_930},
    {"p": "12", "lb_sch": 13_175, "sb": 38_100, "updates": 130_130},
    {"p": "11", "lb_sch": 3_370, "sb": 12_733, "updates": 1_366_365},
]


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "savefig.facecolor": BG,
            "font.family": ["DejaVu Sans", "Arial", "sans-serif"],
            "text.color": TEXT,
            "axes.labelcolor": TEXT,
            "axes.edgecolor": GRID,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "figure.dpi": 160,
            "savefig.dpi": 300,
        }
    )


def style_axes(ax: plt.Axes, *, xgrid: bool = True, ygrid: bool = False) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, pad=8)
    if xgrid:
        ax.grid(axis="x", color=GRID, alpha=0.75, linewidth=0.8)
    if ygrid:
        ax.grid(axis="y", color=GRID, alpha=0.75, linewidth=0.8)
    ax.set_axisbelow(True)


def format_seconds(value: float) -> str:
    return f"{value:.3f}".replace(".", ",") + "s"


def save(fig: plt.Figure, filename: str) -> None:
    path = OUTPUT_DIR / filename
    fig.savefig(path, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    print(path)


def chart_experiment_runtime_log() -> None:
    rows = sorted(EXPERIMENTS, key=lambda item: item.seconds)
    labels = [f"{row.method}\n{row.instance}" for row in rows]
    values = [row.seconds for row in rows]
    colors = [METHOD_COLORS[row.method] for row in rows]

    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    y = np.arange(len(rows))
    ax.barh(y, values, color=colors, height=0.56, alpha=0.95)
    ax.set_xscale("log")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Tempo de execução em segundos (escala log)")
    style_axes(ax, xgrid=True)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:g}s"))
    ax.set_xlim(0.45, 220)

    for idx, value in enumerate(values):
        ax.text(value * 1.08, idx, format_seconds(value), va="center", ha="left", color=TEXT, fontsize=9.5)

    save(fig, "report_experiment_runtime_log.png")


def chart_experiment_tradeoff() -> None:
    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    markers = {"medium": "o", "large-demo": "s"}
    label_offsets = {
        ("medium", "Greedy baseline"): (7, 7),
        ("medium", "Stochastic Greedy"): (7, 7),
        ("medium", "GRASP"): (7, 7),
        ("medium", "Relaxação Lagrangiana"): (7, 7),
        ("medium", "Column Generation"): (7, 7),
        ("large-demo", "Greedy baseline"): (7, 12),
        ("large-demo", "Stochastic Greedy"): (7, 8),
        ("large-demo", "GRASP"): (7, -2),
        ("large-demo", "Greedy + poda local"): (7, -14),
    }

    for row in EXPERIMENTS:
        ax.scatter(
            row.seconds,
            row.selected_count,
            s=135,
            marker=markers[row.instance],
            color=METHOD_COLORS[row.method],
            edgecolors="white",
            linewidths=1.4,
            zorder=3,
        )
        label = row.method.replace("Greedy baseline", "Greedy").replace("Relaxação Lagrangiana", "Lagrangiana")
        ax.annotate(
            label,
            (row.seconds, row.selected_count),
            xytext=label_offsets.get((row.instance, row.method), (7, 7)),
            textcoords="offset points",
            color=TEXT,
            fontsize=8.8,
            zorder=4,
        )

    ax.set_xscale("log")
    ax.set_xlabel("Tempo em segundos (escala log)")
    ax.set_ylabel(r"$|SB|$ - tamanho da solução")
    style_axes(ax, xgrid=True, ygrid=True)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:g}s"))
    ax.set_xlim(0.45, 220)
    ax.set_ylim(95, 180)

    for instance, marker, y in [("medium", "o", 0.93), ("large-demo", "s", 0.88)]:
        ax.scatter([0.02], [y], transform=ax.transAxes, s=55, marker=marker, color=MUTED, clip_on=False)
        ax.text(0.045, y, instance, transform=ax.transAxes, va="center", color=MUTED, fontsize=9.5)

    save(fig, "report_experiment_tradeoff.png")


def chart_final_sb_vs_lower_bound() -> None:
    labels = [f"p={row['p']}" for row in FINAL_RESULTS]
    sb = np.array([row["sb"] for row in FINAL_RESULTS])
    lb = np.array([row["lb_sch"] for row in FINAL_RESULTS])
    x = np.arange(len(labels))
    width = 0.34

    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    ax.bar(x - width / 2, lb, width, label="LB-Schönheim", color=SLATE, alpha=0.85)
    ax.bar(x + width / 2, sb, width, label=r"$|SB|$ greedy", color=CYAN, alpha=0.95)
    ax.set_yscale("log")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Quantidade de conjuntos (escala log)")
    style_axes(ax, ygrid=True, xgrid=False)
    ax.legend(frameon=False, labelcolor=TEXT, loc="upper right")

    for xpos, value in zip(x - width / 2, lb):
        ax.text(xpos, value * 1.08, f"{value:,}".replace(",", "."), ha="center", va="bottom", color=MUTED, fontsize=8.5)
    for xpos, value in zip(x + width / 2, sb):
        ax.text(xpos, value * 1.08, f"{value:,}".replace(",", "."), ha="center", va="bottom", color=TEXT, fontsize=8.5)

    save(fig, "report_final_sb_vs_lower_bound.png")


def chart_updates_per_iteration() -> None:
    labels = [f"p={row['p']}" for row in FINAL_RESULTS]
    values = [row["updates"] for row in FINAL_RESULTS]
    colors = [CYAN, CYAN, AMBER, RED]

    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    bars = ax.bar(labels, values, color=colors, width=0.58, alpha=0.95)
    ax.set_yscale("log")
    ax.set_ylabel(r"Atualizações de $count[]$ por iteração (escala log)")
    style_axes(ax, ygrid=True, xgrid=False)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value * 1.12,
            f"{value:,}".replace(",", "."),
            ha="center",
            va="bottom",
            color=TEXT,
            fontsize=10,
            fontweight="bold",
        )

    save(fig, "report_updates_per_iteration.png")


def chart_parallel_speedup() -> None:
    labels = ["Programa 1\nsequencial", "Programa 1\nparalelo"]
    values = [80.0, 18.7]
    colors = [SLATE, GREEN]

    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    bars = ax.bar(labels, values, color=colors, width=0.46, alpha=0.95)
    ax.set_ylabel("Tempo observado (segundos)")
    style_axes(ax, ygrid=True, xgrid=False)
    ax.set_ylim(0, 92)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 2.5,
            f"{str(value).replace('.', ',')}s",
            ha="center",
            va="bottom",
            color=TEXT,
            fontsize=11,
            fontweight="bold",
        )

    ax.annotate(
        r"speedup $\approx 4{,}3\times$",
        xy=(1, 18.7),
        xytext=(0.43, 52),
        arrowprops={"arrowstyle": "->", "color": GREEN, "lw": 1.5},
        color=GREEN,
        fontsize=12,
        fontweight="bold",
    )

    save(fig, "report_parallel_speedup.png")


def main() -> None:
    configure_matplotlib()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    chart_experiment_runtime_log()
    chart_experiment_tradeoff()
    chart_final_sb_vs_lower_bound()
    chart_updates_per_iteration()
    chart_parallel_speedup()


if __name__ == "__main__":
    main()
