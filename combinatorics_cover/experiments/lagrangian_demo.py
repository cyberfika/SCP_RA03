# -*- coding: utf-8 -*-
"""Lagrangian-relaxation demonstration for reduced set-cover instances."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from .common import SolverOutput, greedy_baseline, precompute_candidate_coverage
except ImportError:  # pragma: no cover
    from common import SolverOutput, greedy_baseline, precompute_candidate_coverage


@dataclass(frozen=True)
class LagrangianOptions:
    """Configuration for the subgradient demonstration."""

    iterations: int = 40
    initial_step: float = 2.0
    step_decay: float = 0.95


def _repair_solution(
    selected_indices: list[int],
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    coverage_sets: list[set[int]],
    n: int,
    p: int,
) -> np.ndarray:
    """Repair a relaxed solution until it becomes a feasible set cover."""

    selected = list(dict.fromkeys(selected_indices))
    covered: set[int] = set()
    for index in selected:
        covered.update(coverage_sets[index])

    uncovered = set(range(len(target_masks))) - covered
    while uncovered:
        best_index = -1
        best_gain = -1
        for index, covered_by_candidate in enumerate(coverage_sets):
            if index in selected:
                continue
            gain = len(covered_by_candidate & uncovered)
            if gain > best_gain:
                best_gain = gain
                best_index = index
        if best_index < 0 or best_gain <= 0:
            break
        selected.append(best_index)
        uncovered -= coverage_sets[best_index]

    return candidate_masks[selected].astype(np.uint32)


def solve_lagrangian_demo(
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    n: int,
    p: int,
    options: LagrangianOptions | None = None,
    coverage_sets: list[set[int]] | None = None,
) -> SolverOutput:
    """Run a Lagrangian relaxation with subgradient updates and greedy repair."""

    # Comentário: a demonstração relaxa as restrições Ax >= 1 e penaliza alvos
    # descobertos com multiplicadores lambda. Em escala real, o gargalo seria
    # recalcular milhões de scores por iteração.
    if options is None:
        options = LagrangianOptions()
    if coverage_sets is None:
        coverage_sets = precompute_candidate_coverage(candidate_masks, target_masks, n, p)

    target_count = len(target_masks)
    multipliers = np.full(target_count, 1.0 / max(1, len(coverage_sets[0])), dtype=np.float64)

    best_lower_bound = float("-inf")
    best_solution = greedy_baseline(candidate_masks, target_masks, n, p, coverage_sets)
    best_solution_size = len(best_solution)
    step_size = options.initial_step

    for _iteration in range(options.iterations):
        # Comentário: score(X) = soma dos multiplicadores dos Y cobertos por X.
        scores = np.array(
            [float(multipliers[list(covered)].sum()) for covered in coverage_sets],
            dtype=np.float64,
        )
        reduced_costs = 1.0 - scores
        relaxed_selected = np.where(reduced_costs < 0.0)[0].astype(np.int32)

        lower_bound = float(multipliers.sum() + np.minimum(0.0, reduced_costs).sum())
        best_lower_bound = max(best_lower_bound, lower_bound)

        repaired = _repair_solution(
            relaxed_selected.tolist(),
            candidate_masks,
            target_masks,
            coverage_sets,
            n,
            p,
        )
        if len(repaired) < best_solution_size:
            best_solution = repaired
            best_solution_size = len(repaired)

        coverage_count = np.zeros(target_count, dtype=np.int16)
        for index in relaxed_selected:
            if coverage_sets[int(index)]:
                coverage_count[list(coverage_sets[int(index)])] += 1

        # Comentário: subgradiente de restrição relaxada é 1 - cobertura atual.
        subgradient = 1.0 - coverage_count.astype(np.float64)
        norm_squared = float(np.dot(subgradient, subgradient))
        if norm_squared == 0.0:
            break

        multipliers = np.maximum(0.0, multipliers + step_size * subgradient / norm_squared)
        step_size *= options.step_decay

    notes = (
        f"Relaxação Lagrangiana demonstrativa; {options.iterations} iterações; "
        f"melhor bound lagrangiano={best_lower_bound:.2f}; solução reparada por greedy."
    )
    return SolverOutput(
        selected_masks=best_solution.astype(np.uint32),
        notes_pt=notes,
        extra={"best_lagrangian_bound": best_lower_bound},
    )

