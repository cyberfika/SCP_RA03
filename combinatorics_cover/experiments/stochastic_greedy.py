# -*- coding: utf-8 -*-
"""Stochastic Greedy solver for reduced set-cover experiments."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from .common import SolverOutput, precompute_candidate_coverage
except ImportError:  # pragma: no cover - permite executar o arquivo diretamente.
    from common import SolverOutput, precompute_candidate_coverage


@dataclass(frozen=True)
class StochasticGreedyOptions:
    """Configuration for the randomized greedy construction."""

    sample_size: int = 256
    seed: int = 42


def solve_stochastic_greedy(
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    n: int,
    p: int,
    options: StochasticGreedyOptions | None = None,
    coverage_sets: list[set[int]] | None = None,
) -> SolverOutput:
    """Build a cover by evaluating only a random sample per iteration."""

    # Comentário: esta abordagem mostra o trade-off central do stochastic greedy:
    # menos candidatos avaliados por iteração, com possível perda de qualidade.
    if options is None:
        options = StochasticGreedyOptions()
    if coverage_sets is None:
        coverage_sets = precompute_candidate_coverage(candidate_masks, target_masks, n, p)

    rng = np.random.default_rng(options.seed)
    uncovered = set(range(len(target_masks)))
    available_indices = np.arange(len(candidate_masks), dtype=np.int32)
    selected_indices: list[int] = []

    while uncovered:
        sample_count = min(options.sample_size, len(available_indices))
        if sample_count == 0:
            break

        sampled_indices = rng.choice(available_indices, size=sample_count, replace=False)
        best_index = -1
        best_gain = -1
        for candidate_index in sampled_indices:
            gain = len(coverage_sets[int(candidate_index)] & uncovered)
            if gain > best_gain:
                best_gain = gain
                best_index = int(candidate_index)

        if best_index < 0 or best_gain <= 0:
            # Comentário: se a amostra não ajuda, faz fallback determinístico para garantir cobertura.
            for candidate_index, covered in enumerate(coverage_sets):
                gain = len(covered & uncovered)
                if gain > best_gain:
                    best_gain = gain
                    best_index = candidate_index
            if best_index < 0 or best_gain <= 0:
                break

        selected_indices.append(best_index)
        uncovered -= coverage_sets[best_index]
        available_indices = available_indices[available_indices != best_index]

    notes = (
        f"Amostra {options.sample_size} por iteração; seed={options.seed}; "
        "fallback determinístico quando a amostra não cobre novos alvos."
    )
    return SolverOutput(
        selected_masks=candidate_masks[selected_indices].astype(np.uint32),
        notes_pt=notes,
        extra={"sample_size": options.sample_size, "seed": options.seed},
    )

