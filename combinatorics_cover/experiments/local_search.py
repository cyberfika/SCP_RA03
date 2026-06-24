# -*- coding: utf-8 -*-
"""Local-search post-processing for cover solutions."""

from __future__ import annotations

from collections import Counter

import numpy as np

try:
    from .common import SolverOutput, build_target_index, covered_target_indices
except ImportError:  # pragma: no cover
    from common import SolverOutput, build_target_index, covered_target_indices


def prune_redundant_candidates(
    selected_masks: np.ndarray,
    target_masks: np.ndarray,
    n: int,
    p: int,
) -> SolverOutput:
    """Remove candidates whose covered targets are already covered by others."""

    # Comentário: este pós-processamento é simples, determinístico e fácil de defender.
    # Ele não encontra ótimo global, mas remove redundâncias deixadas pela construção.
    if selected_masks is None or len(selected_masks) == 0:
        return SolverOutput(selected_masks=selected_masks, notes_pt="Sem solução inicial para podar.")

    target_index = build_target_index(target_masks)
    coverage_by_selected = [
        covered_target_indices(int(mask), p, n, target_index) for mask in selected_masks
    ]

    target_cover_count: Counter[int] = Counter()
    for covered in coverage_by_selected:
        target_cover_count.update(covered)

    keep = [True] * len(selected_masks)
    removed_count = 0

    # Comentário: remove em ordem reversa para preservar mais a estrutura inicial.
    for index in range(len(selected_masks) - 1, -1, -1):
        if not keep[index]:
            continue
        covered = coverage_by_selected[index]
        can_remove = all(target_cover_count[target] >= 2 for target in covered)
        if not can_remove:
            continue

        keep[index] = False
        removed_count += 1
        for target in covered:
            target_cover_count[target] -= 1

    pruned_masks = selected_masks[np.array(keep, dtype=bool)].astype(np.uint32)
    notes = f"Removeu {removed_count} candidatos redundantes mantendo cobertura exata."
    return SolverOutput(
        selected_masks=pruned_masks,
        notes_pt=notes,
        extra={"removed_count": removed_count},
    )

