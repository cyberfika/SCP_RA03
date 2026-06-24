# -*- coding: utf-8 -*-
"""Shared utilities for experimental set-cover solvers.

The production project solves the real instance U={1..25}, k=15 and
p in {14, 13, 12, 11}.  This package focuses on reduced instances that make it
possible to compare advanced alternatives quickly and reproducibly.
"""

from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import asdict, dataclass
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Callable, Iterable

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_RESULTS_DIR = PROJECT_ROOT / "results" / "experiments"


@dataclass(frozen=True)
class ExperimentConfig:
    """Describes one reduced covering-design instance."""

    name: str
    n: int
    k: int
    p: int


@dataclass
class ExperimentResult:
    """Normalized row exported by every benchmarked algorithm."""

    method: str
    category_pt: str
    preset: str
    n: int
    k: int
    p: int
    elapsed_seconds: float
    selected_count: int | None
    lower_bound_lp: int
    gap_vs_lb: float | None
    coverage_percent: float | None
    is_exactly_covered: bool | None
    notes_pt: str


@dataclass
class SolverOutput:
    """Raw solver payload used before formatting a benchmark row."""

    selected_masks: np.ndarray | None
    notes_pt: str = ""
    extra: dict | None = None


PRESETS: dict[str, ExperimentConfig] = {
    # Pequeno o bastante para rodar todos os métodos, inclusive LP/CG.
    "small": ExperimentConfig(name="small", n=12, k=7, p=4),
    # Ainda barato, mas já evidencia crescimento combinatório.
    "medium": ExperimentConfig(name="medium", n=15, k=9, p=6),
    # Maior que medium, mas ainda reprodutível em Python puro.
    "large-demo": ExperimentConfig(name="large-demo", n=16, k=10, p=6),
}


def combo_to_mask(combo: Iterable[int]) -> int:
    """Convert a zero-based combination into an integer bitmask."""

    mask = 0
    for element in combo:
        mask |= 1 << element
    return mask


def mask_to_tuple(mask: int, n: int) -> tuple[int, ...]:
    """Convert a bitmask into a one-based tuple for human-readable output."""

    return tuple(index + 1 for index in range(n) if mask & (1 << index))


def generate_masks(n: int, size: int) -> np.ndarray:
    """Generate all size-subsets of {0, ..., n-1} as uint32 bitmasks."""

    total = comb(n, size)
    masks = np.empty(total, dtype=np.uint32)
    for index, combo in enumerate(combinations(range(n), size)):
        masks[index] = combo_to_mask(combo)
    return masks


def lower_bound_lp(n: int, k: int, p: int) -> int:
    """Return ceil(C(n,p) / C(k,p))."""

    return -(-comb(n, p) // comb(k, p))


def build_target_index(target_masks: np.ndarray) -> dict[int, int]:
    """Map each target bitmask to its row index."""

    return {int(mask): index for index, mask in enumerate(target_masks)}


def covered_target_indices(
    candidate_mask: int,
    p: int,
    n: int,
    target_index: dict[int, int],
) -> set[int]:
    """Return all target row indices covered by one candidate mask."""

    # Comentário: enumerar os subconjuntos de tamanho p de X evita varrer Sp inteiro.
    elements = [index for index in range(n) if candidate_mask & (1 << index)]
    covered: set[int] = set()
    for combo in combinations(elements, p):
        target_mask = combo_to_mask(combo)
        target_position = target_index.get(target_mask)
        if target_position is not None:
            covered.add(target_position)
    return covered


def precompute_candidate_coverage(
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    n: int,
    p: int,
) -> list[set[int]]:
    """Precompute the exact targets covered by each candidate."""

    target_index = build_target_index(target_masks)
    return [
        covered_target_indices(int(candidate_mask), p, n, target_index)
        for candidate_mask in candidate_masks
    ]


def validate_exact_coverage(
    selected_masks: np.ndarray,
    target_masks: np.ndarray,
    n: int,
    p: int,
) -> tuple[bool, int, float]:
    """Validate exactly whether selected candidates cover every target."""

    if selected_masks is None or len(selected_masks) == 0:
        return False, len(target_masks), 0.0

    target_index = build_target_index(target_masks)
    covered: set[int] = set()
    for candidate_mask in map(int, selected_masks):
        covered.update(covered_target_indices(candidate_mask, p, n, target_index))

    covered_count = len(covered)
    total = len(target_masks)
    uncovered_count = total - covered_count
    coverage_percent = 100.0 * covered_count / total if total else 100.0
    return uncovered_count == 0, uncovered_count, coverage_percent


def greedy_baseline(
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    n: int,
    p: int,
    coverage_sets: list[set[int]] | None = None,
) -> np.ndarray:
    """Deterministic greedy baseline used as a common comparator."""

    if coverage_sets is None:
        coverage_sets = precompute_candidate_coverage(candidate_masks, target_masks, n, p)

    uncovered = set(range(len(target_masks)))
    selected_indices: list[int] = []

    while uncovered:
        best_index = -1
        best_gain = -1
        for index, covered in enumerate(coverage_sets):
            gain = len(covered & uncovered)
            if gain > best_gain:
                best_gain = gain
                best_index = index

        if best_index < 0 or best_gain <= 0:
            break

        selected_indices.append(best_index)
        uncovered -= coverage_sets[best_index]

    return candidate_masks[selected_indices].astype(np.uint32)


def make_result(
    method: str,
    category_pt: str,
    config: ExperimentConfig,
    elapsed_seconds: float,
    output: SolverOutput,
    target_masks: np.ndarray,
) -> ExperimentResult:
    """Convert a raw solver output into a presentation-ready result row."""

    lower_bound = lower_bound_lp(config.n, config.k, config.p)
    if output.selected_masks is None:
        selected_count = None
        gap = None
        coverage_percent = None
        is_covered = None
    else:
        selected_count = len(output.selected_masks)
        gap = selected_count / lower_bound if lower_bound else None
        is_covered, _uncovered, coverage_percent = validate_exact_coverage(
            output.selected_masks,
            target_masks,
            config.n,
            config.p,
        )

    return ExperimentResult(
        method=method,
        category_pt=category_pt,
        preset=config.name,
        n=config.n,
        k=config.k,
        p=config.p,
        elapsed_seconds=elapsed_seconds,
        selected_count=selected_count,
        lower_bound_lp=lower_bound,
        gap_vs_lb=gap,
        coverage_percent=coverage_percent,
        is_exactly_covered=is_covered,
        notes_pt=output.notes_pt,
    )


def time_solver(callable_solver: Callable[[], SolverOutput]) -> tuple[float, SolverOutput]:
    """Run one solver and return elapsed wall-clock time plus its output."""

    started_at = time.perf_counter()
    output = callable_solver()
    elapsed_seconds = time.perf_counter() - started_at
    return elapsed_seconds, output


def ensure_results_dir() -> Path:
    """Create and return the experiment result directory."""

    EXPERIMENT_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return EXPERIMENT_RESULTS_DIR


def write_results_csv(results: list[ExperimentResult], path: Path) -> None:
    """Write benchmark rows as CSV for spreadsheets and charts."""

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def write_results_json(results: list[ExperimentResult], path: Path) -> None:
    """Write benchmark rows as JSON for later automation."""

    with path.open("w", encoding="utf-8") as handle:
        json.dump([asdict(result) for result in results], handle, indent=2, ensure_ascii=False)


def format_pt_number(value: float | int | None, decimals: int = 2) -> str:
    """Format a number with Portuguese decimal conventions for Markdown tables."""

    if value is None:
        return "-"
    if isinstance(value, bool):
        return "sim" if value else "não"
    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def write_results_markdown(results: list[ExperimentResult], path: Path) -> None:
    """Write a Portuguese-ready Markdown table for report and slide drafting."""

    lines = [
        "# Resultados experimentais",
        "",
        "| Método | Categoria | Instância | Tempo (s) | |SB| | LB-LP | Gap | Cobertura | Observação |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for result in results:
        instance = f"n={result.n}, k={result.k}, p={result.p}"
        coverage = (
            f"{format_pt_number(result.coverage_percent, 2)}%"
            if result.coverage_percent is not None
            else "-"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    result.method,
                    result.category_pt,
                    instance,
                    format_pt_number(result.elapsed_seconds, 3),
                    format_pt_number(result.selected_count),
                    format_pt_number(result.lower_bound_lp),
                    format_pt_number(result.gap_vs_lb, 2),
                    coverage,
                    result.notes_pt,
                ]
            )
            + " |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_solution_masks(method_slug: str, config: ExperimentConfig, masks: np.ndarray | None) -> None:
    """Persist selected masks for reproducibility when a solver returns a solution."""

    if masks is None:
        return
    directory = ensure_results_dir()
    output_path = directory / f"{config.name}_{method_slug}_solution.npy"
    np.save(output_path, masks.astype(np.uint32))


def describe_instance(config: ExperimentConfig) -> str:
    """Return a compact human-readable description of one instance."""

    return (
        f"{config.name}: n={config.n}, k={config.k}, p={config.p}, "
        f"|Sk|={comb(config.n, config.k):,}, |Sp|={comb(config.n, config.p):,}"
    )


def configure_utf8_stdout() -> None:
    """Force UTF-8 output on Windows terminals when supported."""

    if hasattr(os, "device_encoding"):
        pass
    try:
        import sys

        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        # Comentário: saída UTF-8 é melhoria de terminal, não requisito algorítmico.
        return
