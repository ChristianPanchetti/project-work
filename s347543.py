"""Entry point used by the evaluator."""

from Problem import Problem
from src.evolutionary_search import EvolutionaryCollector
from src.path_metrics import build_path_tables, materialize_edge_path
from src.path_validation import assert_valid_solution


def solution(p: Problem):
    """Build a valid collection path and return it."""
    # Cache shortest paths before starting the genetic search.
    distances, powered_distances, shortest_paths = build_path_tables(p)

    # These are the same GA parameters used in the tested version.
    optimizer = EvolutionaryCollector(
        problem=p,
        distance_table=distances,
        powered_distance_table=powered_distances,
        population_size=100,
        generation_count=1000,
    )
    decoded_path, _ = optimizer.search()

    # Convert shortest-path jumps into real graph edges.
    final_path = materialize_edge_path(decoded_path, shortest_paths)

    # Check the evaluator format before returning the result.
    assert_valid_solution(p, final_path)
    return final_path
