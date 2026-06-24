# -*- coding: utf-8 -*-
"""Benchmark runner for RA03 experimental set-cover approaches.

The output files are intentionally presentation-friendly: CSV for spreadsheet
charts, JSON for automation, and Markdown in Portuguese for direct reuse in
slides or reports.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

try:
    from .column_generation_demo import ColumnGenerationOptions, solve_column_generation_demo
    from .common import (
        PRESETS,
        ExperimentResult,
        SolverOutput,
        configure_utf8_stdout,
        describe_instance,
        ensure_results_dir,
        generate_masks,
        greedy_baseline,
        make_result,
        precompute_candidate_coverage,
        save_solution_masks,
        time_solver,
        write_results_csv,
        write_results_json,
        write_results_markdown,
    )
    from .grasp import GraspOptions, solve_grasp
    from .lagrangian_demo import LagrangianOptions, solve_lagrangian_demo
    from .local_search import prune_redundant_candidates
    from .stochastic_greedy import StochasticGreedyOptions, solve_stochastic_greedy
except ImportError:  # pragma: no cover - permite `python benchmark.py`.
    CURRENT_DIR = Path(__file__).resolve().parent
    if str(CURRENT_DIR) not in sys.path:
        sys.path.insert(0, str(CURRENT_DIR))
    from column_generation_demo import ColumnGenerationOptions, solve_column_generation_demo
    from common import (
        PRESETS,
        ExperimentResult,
        SolverOutput,
        configure_utf8_stdout,
        describe_instance,
        ensure_results_dir,
        generate_masks,
        greedy_baseline,
        make_result,
        precompute_candidate_coverage,
        save_solution_masks,
        time_solver,
        write_results_csv,
        write_results_json,
        write_results_markdown,
    )
    from grasp import GraspOptions, solve_grasp
    from lagrangian_demo import LagrangianOptions, solve_lagrangian_demo
    from local_search import prune_redundant_candidates
    from stochastic_greedy import StochasticGreedyOptions, solve_stochastic_greedy


SOLVER_ORDER = [
    "greedy",
    "stochastic",
    "grasp",
    "local-search",
    "lagrangian",
    "column-generation",
]


def _run_greedy(
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    n: int,
    p: int,
    coverage_sets: list[set[int]],
) -> SolverOutput:
    """Run the deterministic greedy baseline."""

    selected = greedy_baseline(candidate_masks, target_masks, n, p, coverage_sets)
    return SolverOutput(
        selected_masks=selected,
        notes_pt="Baseline guloso determinístico com escolha de maior ganho marginal.",
    )


def _run_local_search_from_greedy(
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    n: int,
    p: int,
    coverage_sets: list[set[int]],
) -> SolverOutput:
    """Run greedy, then prune redundant candidates as post-processing."""

    greedy_solution = greedy_baseline(candidate_masks, target_masks, n, p, coverage_sets)
    return prune_redundant_candidates(greedy_solution, target_masks, n, p)


def run_one_solver(
    solver_name: str,
    preset_name: str,
    candidate_masks: np.ndarray,
    target_masks: np.ndarray,
    config,
    coverage_sets: list[set[int]],
) -> ExperimentResult:
    """Run one named solver and normalize its metrics."""

    solver_map = {
        "greedy": (
            "Greedy baseline",
            "Algoritmo guloso",
            lambda: _run_greedy(candidate_masks, target_masks, config.n, config.p, coverage_sets),
            "greedy",
        ),
        "stochastic": (
            "Stochastic Greedy",
            "Probabilístico / randômico",
            lambda: solve_stochastic_greedy(
                candidate_masks,
                target_masks,
                config.n,
                config.p,
                StochasticGreedyOptions(sample_size=256, seed=42),
                coverage_sets,
            ),
            "stochastic_greedy",
        ),
        "grasp": (
            "GRASP",
            "Metaheurística",
            lambda: solve_grasp(
                candidate_masks,
                target_masks,
                config.n,
                config.p,
                GraspOptions(iterations=5, restricted_candidate_size=10, seed=123),
                coverage_sets,
            ),
            "grasp",
        ),
        "local-search": (
            "Greedy + poda local",
            "Busca local pós-greedy",
            lambda: _run_local_search_from_greedy(
                candidate_masks,
                target_masks,
                config.n,
                config.p,
                coverage_sets,
            ),
            "local_search",
        ),
        "lagrangian": (
            "Relaxação Lagrangiana",
            "Relaxação / lower bound",
            lambda: solve_lagrangian_demo(
                candidate_masks,
                target_masks,
                config.n,
                config.p,
                LagrangianOptions(iterations=40),
                coverage_sets,
            ),
            "lagrangian",
        ),
        "column-generation": (
            "Column Generation",
            "Programação linear / pricing",
            lambda: solve_column_generation_demo(
                candidate_masks,
                target_masks,
                config.n,
                config.p,
                ColumnGenerationOptions(max_iterations=25),
                coverage_sets,
            ),
            "column_generation",
        ),
    }

    method, category_pt, solver_callable, slug = solver_map[solver_name]
    print(f"  - Running {method}...")
    elapsed_seconds, output = time_solver(solver_callable)
    save_solution_masks(f"{preset_name}_{slug}", config, output.selected_masks)
    return make_result(method, category_pt, config, elapsed_seconds, output, target_masks)


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""

    parser = argparse.ArgumentParser(
        description="Run reduced-instance benchmarks for RA03 set-cover alternatives.",
    )
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS.keys()),
        default="small",
        help="Reduced instance size to run.",
    )
    parser.add_argument(
        "--solver",
        choices=["all", *SOLVER_ORDER],
        default="all",
        help="Solver to run. Use all for the full comparison.",
    )
    parser.add_argument(
        "--skip-advanced-on-large",
        action="store_true",
        help="Skip Lagrangian and Column Generation on large-demo to keep runtime short.",
    )
    return parser.parse_args()


def main() -> int:
    """Run benchmarks and export presentation-ready artifacts."""

    configure_utf8_stdout()
    args = parse_args()
    config = PRESETS[args.preset]

    print("RA03 experimental benchmark")
    print(describe_instance(config))

    candidate_masks = generate_masks(config.n, config.k)
    target_masks = generate_masks(config.n, config.p)
    print(f"Generated |Sk|={len(candidate_masks):,} candidates and |Sp|={len(target_masks):,} targets.")
    print("Precomputing exact candidate coverage...")
    coverage_sets = precompute_candidate_coverage(candidate_masks, target_masks, config.n, config.p)

    if args.solver == "all":
        solver_names = list(SOLVER_ORDER)
    else:
        solver_names = [args.solver]

    if args.skip_advanced_on_large and config.name == "large-demo":
        solver_names = [
            solver
            for solver in solver_names
            if solver not in {"lagrangian", "column-generation"}
        ]

    results: list[ExperimentResult] = []
    for solver_name in solver_names:
        results.append(
            run_one_solver(
                solver_name,
                args.preset,
                candidate_masks,
                target_masks,
                config,
                coverage_sets,
            )
        )

    output_dir = ensure_results_dir()
    base_name = f"benchmark_{args.preset}_{args.solver}"
    csv_path = output_dir / f"{base_name}.csv"
    json_path = output_dir / f"{base_name}.json"
    markdown_path = output_dir / f"{base_name}.md"

    write_results_csv(results, csv_path)
    write_results_json(results, json_path)
    write_results_markdown(results, markdown_path)

    print("\nExported results:")
    print(f"  CSV      : {csv_path}")
    print(f"  JSON     : {json_path}")
    print(f"  Markdown : {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
