"""Checks for the public solution format."""

from __future__ import annotations

from collections.abc import Iterable, Iterator


def edge_checks(problem, path: Iterable[tuple[int, float]]) -> Iterator[bool]:
    """Check each move, starting from the implicit depot."""
    graph = problem.graph
    previous_node = 0

    for node, _ in path:
        # Repeated nodes need no edge. Every real move must be adjacent.
        yield node == previous_node or graph.has_edge(previous_node, node)
        previous_node = node


def assert_valid_solution(
    problem,
    path: Iterable[tuple[int, float]],
    tolerance: float = 1e-8,
) -> None:
    """Validate path shape, edges and collected gold."""
    graph = problem.graph
    output = list(path)

    # The evaluator expects an implicit start and an explicit final depot.
    if not output:
        raise ValueError("The solution path cannot be empty")
    if output[0] == (0, 0):
        raise ValueError("The initial depot is implicit and must not be emitted")
    if output[-1] != (0, 0):
        raise ValueError("The final output element must be (0, 0)")

    # This also checks the first movement from depot 0.
    if not all(edge_checks(problem, output)):
        raise ValueError("The path contains a non-adjacent movement")

    collected = {node: 0.0 for node in graph.nodes}
    for node, pickup in output:
        if node not in graph:
            raise ValueError(f"Unknown node {node}")
        if pickup < 0:
            raise ValueError(f"Negative pickup at node {node}")

        if node == 0:
            if pickup != 0:
                raise ValueError("Pickup at the depot must be zero")
        else:
            # Output values are local pickups, not the current carried load.
            collected[node] += float(pickup)

    # Every city must provide exactly the gold stored in Problem.py.
    for node in graph.nodes:
        expected = float(graph.nodes[node].get("gold", 0.0))
        allowed_error = tolerance * max(1.0, abs(expected))
        if abs(collected[node] - expected) > allowed_error:
            raise ValueError(
                f"Node {node}: collected {collected[node]}, expected {expected}"
            )
