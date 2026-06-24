# -*- coding: utf-8 -*-
"""GRASP-style randomized adaptive construction plus local pruning."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from .common import SolverOutput, precompute_candidate_coverage
    from .local_search import prune_redundant_candidates
except ImportError:  # pragma: no cover
    from common import SolverOutput, precompute_candidate_coverage
    from local_search import prune_redundant_candidates


@dataclass(frozen=True)
class GraspOptions:
    """Configuration for the GRASP construction."""

    iterations: int = 5
    restricted_candidate_size: int = 10
    seed: int = 123
    use_pruning: bool = True


def _construct_one_solution(
    candidate_masks: np.ndarray,
    target_count: int,
    coverage_sets: list[set[int]],
    rng: np.random.Generator,
    restricted_candidate_size: int,
) -> np.ndarray:
    """Construct one randomized greedy cover using a restricted candidate list."""

    uncovered = set(range(target_count))
    selected_indices: list[int] = []
    available = set(range(len(candidate_masks)))

    while uncovered:
        scored: list[tuple[int, int]] = []
        for candidate_index in available:
            gain = len(coverage_sets[candidate_index] & uncovered)
            if gain > 0:
                scored.append((gain, candidate_index))

        if not scored:
            break

        scored.sort(reverse=True)
        rcl = scored[: max(1, restricted_candidate_size)]
        chosen_position = int(rng.integers(0, len(rcl)))
        _gain, chosen_index = rcl[chosen_position]

        selected_indices.append(chosen_index)
        uncovered -= coverage_sets[chosen_index]
        available.remove(chosen_index)

    return candidate_masks[selected_indices].astype(np.uint32)


def solve_grasp(
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    n: int,
    p: int,
    options: GraspOptions | None = None,
    coverage_sets: list[set[int]] | None = None,
) -> SolverOutput:
    """Run multiple randomized greedy constructions and keep the best cover."""

    if options is None:
        options = GraspOptions()
    if coverage_sets is None:
        coverage_sets = precompute_candidate_coverage(candidate_masks, target_masks, n, p)

    rng = np.random.default_rng(options.seed)
    best_solution: np.ndarray | None = None

    for _iteration in range(options.iterations):
        candidate_solution = _construct_one_solution(
            candidate_masks=candidate_masks,
            target_count=len(target_masks),
            coverage_sets=coverage_sets,
            rng=rng,
            restricted_candidate_size=options.restricted_candidate_size,
        )
        if options.use_pruning:
            candidate_solution = prune_redundant_candidates(
                candidate_solution,
                target_masks,
                n,
                p,
            ).selected_masks

        if best_solution is None or len(candidate_solution) < len(best_solution):
            best_solution = candidate_solution

    notes = (
        f"{options.iterations} construções; RCL={options.restricted_candidate_size}; "
        f"poda local={'sim' if options.use_pruning else 'não'}; seed={options.seed}."
    )
    return SolverOutput(
        selected_masks=best_solution.astype(np.uint32) if best_solution is not None else None,
        notes_pt=notes,
        extra={
            "iterations": options.iterations,
            "restricted_candidate_size": options.restricted_candidate_size,
            "seed": options.seed,
        },
    )
