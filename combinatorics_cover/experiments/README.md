# RA03 Experimental Algorithms

This folder contains reduced-instance experiments for the RA03 combinatorial
covering project. The production programs remain outside this folder and are
not modified by these experiments.

## Purpose

The assignment asks teams to investigate alternatives to brute force, including
greedy algorithms, integer programming, randomized algorithms, metaheuristics,
parallel or distributed computation, and other literature-based approaches.

The scripts here generate reproducible benchmark artifacts for the presentation:

- `results/experiments/*.csv` for spreadsheet charts.
- `results/experiments/*.json` for automation.
- `results/experiments/*.md` for Portuguese-ready tables.
- `results/experiments/*.npy` for saved selected covers.

## Implemented Approaches

- `Greedy baseline`: deterministic greedy set cover.
- `Stochastic Greedy`: randomized sample-based greedy construction.
- `GRASP`: randomized adaptive construction with local pruning. The default
  benchmark uses 5 restarts so medium-sized demonstrations finish quickly.
- `Greedy + local pruning`: post-greedy redundant-candidate removal.
- `Lagrangian Relaxation`: subgradient demonstration with greedy repair.
- `Column Generation`: restricted LP plus explicit pricing and repair.

## Why Reduced Instances?

The real instance uses `n=25`, `k=15` and `p in {14,13,12,11}`. Advanced methods
such as Lagrangian Relaxation and Column Generation need repeated scoring or LP
pricing over millions of targets and candidates. These demos therefore use
smaller instances by default so the methods can be compared during development
and shown honestly in the presentation.

## Recommended Commands

```powershell
python combinatorics_cover\experiments\benchmark.py --preset small --solver all
python combinatorics_cover\experiments\benchmark.py --preset medium --solver all
python combinatorics_cover\experiments\benchmark.py --preset large-demo --solver all --skip-advanced-on-large
```

## Presentation Interpretation

Use the exported Markdown table to show that the project did not only cite
advanced alternatives. It tested representative reduced instances and measured:

- runtime;
- selected cover size;
- LP lower-bound gap;
- exact coverage.

For the final `n=25` deliverable, keep the production greedy/paralellized
programs as the main solution and use these experiments as evidence of the
investigation requested by the assignment.
