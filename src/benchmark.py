"""Run the benchmark cases used in the report."""

from __future__ import annotations

import random
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Problem import Problem
from s347543 import solution
import src.evolutionary_search as evolutionary_search


evolutionary_search.tqdm = lambda values: values


TEST_CASES = [
    # N = 100
    (100, 0.2, 2.0, 1.0),
    (100, 0.2, 1.0, 2.0),
    (100, 0.2, 1.0, 5.0),
    (100, 0.2, 1.0, 1.0),
    (100, 1.0, 2.0, 1.0),
    (100, 1.0, 1.0, 2.0),
    (100, 1.0, 1.0, 5.0),
    (100, 1.0, 1.0, 1.0),

    # N = 1000
    (1000, 0.2, 2.0, 1.0),
    (1000, 0.2, 1.0, 2.0),
    (1000, 0.2, 1.0, 5.0),
    (1000, 0.2, 1.0, 1.0),
    (1000, 1.0, 2.0, 1.0),
    (1000, 1.0, 1.0, 2.0),
    (1000, 1.0, 1.0, 5.0),
    (1000, 1.0, 1.0, 1.0),
]


def evaluate_path(problem, path):
    """Compute the official edge-by-edge cost."""
    current_node = 0
    current_load = 0.0
    total_cost = 0.0

    for next_node, pickup in path:
        if next_node != current_node:
            total_cost += problem.cost(
                [current_node, next_node],
                current_load,
            )

        current_node = next_node
        if next_node == 0:
            current_load = 0.0
        else:
            current_load += pickup

    return total_cost


def run_case(n, density, alpha, beta):
    """Run one case and return its result row."""
    random.seed(0)
    problem = Problem(
        n,
        density=density,
        alpha=alpha,
        beta=beta,
        seed=42,
    )

    path = solution(problem)

    baseline = float(problem.baseline())
    ga_cost = float(evaluate_path(problem, path))
    improvement = 100.0 * (baseline - ga_cost) / baseline

    return n, density, alpha, beta, baseline, ga_cost, improvement


def print_table(n, rows):
    """Print one Markdown table for a problem size."""
    print(f"### Results - N = {n}")
    print()
    print(
        "| N | Density | Alpha | Beta | Baseline | GA cost | Improvement |"
    )
    print("|---:|---:|---:|---:|---:|---:|---:|")

    for row in rows:
        _, density, alpha, beta, baseline, ga_cost, improvement = row
        print(
            f"| {n} | {density:.1f} | {alpha:.1f} | {beta:.1f} | "
            f"{baseline:,.2f} | {ga_cost:,.2f} | {improvement:.2f}% |"
        )
    print()


def run_benchmarks():
    """Print each completed test, then the two final tables."""
    results = {100: [], 1000: []}
    total_cases = len(TEST_CASES)

    for index, test_case in enumerate(TEST_CASES, start=1):
        n, density, alpha, beta = test_case
        print(
            f"[{index}/{total_cases}] Running: "
            f"N={n}, density={density:.1f}, alpha={alpha:.1f}, beta={beta:.1f}",
            flush=True,
        )

        row = run_case(*test_case)
        results[row[0]].append(row)

        _, _, _, _, baseline, ga_cost, improvement = row
        print(
            f"  Baseline: {baseline:,.2f} | GA cost: {ga_cost:,.2f} | "
            f"Improvement: {improvement:.2f}%",
            flush=True,
        )
        print(flush=True)

    print("Final results:", flush=True)
    print(flush=True)
    print_table(100, results[100])
    print_table(1000, results[1000])


if __name__ == "__main__":
    run_benchmarks()
