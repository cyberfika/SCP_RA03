We are implementing an Algorithms Complexity project (PUCPR) in Python.

# Comentários no código devem ser em português.

## Problem
Universe U = {1, 2, ..., 25}
S_p = all combinations of size p from U.

## Programs to implement

**Program 1:** Generate S15, S14, S13, S12, S11.

**Programs 2-5:** For each p in {14, 13, 12, 11}, find the minimum
subset SB ⊆ S15 such that every combination of p elements is contained
in at least one element of SB (Minimum Set Cover).

## Primary approach: Integer Linear Programming (ILP) via PySCIPOpt
- Binary variable x_i for each combination X_i ∈ S15
- Minimize: sum of x_i
- Constraint: for each Y ∈ S_p, at least one X_i ∈ S15 containing Y must have x_i = 1
- Watch out for scale: S15 has 3,268,760 elements, constraints may be massive

## Comparison approaches (implement after ILP)
- Greedy
- Randomized

## For each solution, analyze
- Time complexity: O(·), Θ(·), Ω(·)
- Space complexity
- Computational bottlenecks
- Scalability

## Suggested file structure
combinatorics_cover/
  program1_generation.py
  program2_cover14.py
  program3_cover13.py
  program4_cover12.py
  program5_cover11.py
  solver_ilp.py
  solver_greedy.py
  solver_random.py
  analysis.py
  requirements.txt

Start with Program 1 and solver_ilp.py using a small test case
before running at full scale.