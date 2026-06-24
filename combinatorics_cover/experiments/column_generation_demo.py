# -*- coding: utf-8 -*-
"""Column-generation demonstration for reduced set-cover instances."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog

try:
    from .common import SolverOutput, greedy_baseline, precompute_candidate_coverage
except ImportError:  # pragma: no cover
    from common import SolverOutput, greedy_baseline, precompute_candidate_coverage


@dataclass(frozen=True)
class ColumnGenerationOptions:
    """Configuration for the LP column-generation loop."""

    max_iterations: int = 25
    max_new_columns_per_iteration: int = 5
    reduced_cost_tolerance: float = 1e-7
    rounding_threshold: float = 0.5


def _build_restricted_matrix(column_indices: list[int], coverage_sets: list[set[int]], target_count: int):
    """Build the restricted LP constraint matrix for the current columns."""

    matrix = np.zeros((target_count, len(column_indices)), dtype=np.float64)
    for column_position, candidate_index in enumerate(column_indices):
        covered = coverage_sets[candidate_index]
        if covered:
            matrix[list(covered), column_position] = 1.0
    return matrix


def _repair_from_columns(
    selected_indices: list[int],
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    coverage_sets: list[set[int]],
) -> np.ndarray:
    """Repair a rounded restricted LP solution using all available candidates."""

    selected = list(dict.fromkeys(selected_indices))
    covered: set[int] = set()
    for index in selected:
        covered.update(coverage_sets[index])

    uncovered = set(range(len(target_masks))) - covered
    while uncovered:
        best_index = -1
        best_gain = -1
        for index, covered_by_candidate in enumerate(coverage_sets):
            gain = len(covered_by_candidate & uncovered)
            if gain > best_gain:
                best_index = index
                best_gain = gain
        if best_index < 0 or best_gain <= 0:
            break
        selected.append(best_index)
        uncovered -= coverage_sets[best_index]

    return candidate_masks[selected].astype(np.uint32)


def _round_fractional_columns(
    column_indices: list[int],
    lp_solution: np.ndarray,
    coverage_sets: list[set[int]],
    target_count: int,
    threshold: float,
) -> list[int]:
    """Round LP columns by threshold, then greedily add large fractional values."""

    selected = [
        column_indices[index]
        for index, value in enumerate(lp_solution)
        if value >= threshold
    ]
    covered: set[int] = set()
    for candidate_index in selected:
        covered.update(coverage_sets[candidate_index])

    uncovered = set(range(target_count)) - covered
    if not uncovered:
        return selected

    # Comentário: se a solução LP é altamente fracionária, threshold 0.5 pode
    # selecionar pouco; por isso adicionamos colunas fracionárias em ordem de valor.
    ranked = sorted(
        ((float(value), column_indices[index]) for index, value in enumerate(lp_solution)),
        reverse=True,
    )
    existing = set(selected)
    for _value, candidate_index in ranked:
        if not uncovered:
            break
        if candidate_index in existing:
            continue
        gain = len(coverage_sets[candidate_index] & uncovered)
        if gain <= 0:
            continue
        selected.append(candidate_index)
        existing.add(candidate_index)
        uncovered -= coverage_sets[candidate_index]

    return selected


def solve_column_generation_demo(
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    n: int,
    p: int,
    options: ColumnGenerationOptions | None = None,
    coverage_sets: list[set[int]] | None = None,
) -> SolverOutput:
    """Solve a restricted LP, price columns, and round/repair the result."""

    # Comentário: isto é Column Generation didático. Branch-and-Price completo
    # adicionaria uma árvore branch-and-bound sobre este núcleo de geração.
    if options is None:
        options = ColumnGenerationOptions()
    if coverage_sets is None:
        coverage_sets = precompute_candidate_coverage(candidate_masks, target_masks, n, p)

    target_count = len(target_masks)
    greedy_solution = greedy_baseline(candidate_masks, target_masks, n, p, coverage_sets)
    candidate_lookup = {int(mask): index for index, mask in enumerate(candidate_masks)}
    column_indices = [candidate_lookup[int(mask)] for mask in greedy_solution]

    last_lp_value: float | None = None
    last_solution = None
    pricing_iterations = 0

    for iteration in range(options.max_iterations):
        pricing_iterations = iteration + 1
        restricted_matrix = _build_restricted_matrix(column_indices, coverage_sets, target_count)

        # Comentário: linprog aceita A_ub x <= b_ub; usamos -A x <= -1 para Ax >= 1.
        result = linprog(
            c=np.ones(len(column_indices), dtype=np.float64),
            A_ub=-restricted_matrix,
            b_ub=-np.ones(target_count, dtype=np.float64),
            bounds=[(0.0, None)] * len(column_indices),
            method="highs",
        )
        if not result.success:
            notes = f"LP restrito falhou: {result.message}"
            return SolverOutput(selected_masks=greedy_solution, notes_pt=notes, extra={"lp_success": False})

        last_solution = result.x
        last_lp_value = float(result.fun)

        # Comentário: para -A x <= -1, os duais originais são o oposto das marginals.
        dual_values = -np.asarray(result.ineqlin.marginals, dtype=np.float64)
        priced: list[tuple[float, int]] = []
        existing = set(column_indices)

        for candidate_index, covered in enumerate(coverage_sets):
            if candidate_index in existing:
                continue
            score = float(dual_values[list(covered)].sum()) if covered else 0.0
            reduced_cost = 1.0 - score
            if reduced_cost < -options.reduced_cost_tolerance:
                priced.append((reduced_cost, candidate_index))

        if not priced:
            break

        priced.sort(key=lambda item: item[0])
        for _reduced_cost, candidate_index in priced[: options.max_new_columns_per_iteration]:
            column_indices.append(candidate_index)

    selected_from_lp = _round_fractional_columns(
        column_indices,
        np.asarray(last_solution if last_solution is not None else [], dtype=np.float64),
        coverage_sets,
        target_count,
        options.rounding_threshold,
    )
    repaired = _repair_from_columns(selected_from_lp, candidate_masks, target_masks, coverage_sets)

    notes = (
        f"Column Generation relaxado; {pricing_iterations} rodadas de pricing; "
        f"valor LP={last_lp_value:.2f}; solução arredondada e reparada."
        if last_lp_value is not None
        else "Column Generation não obteve LP válido; retornou greedy."
    )
    return SolverOutput(
        selected_masks=repaired,
        notes_pt=notes,
        extra={"lp_value": last_lp_value, "pricing_iterations": pricing_iterations},
    )
