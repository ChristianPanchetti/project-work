"""Shortest-path tables and final path expansion."""

from __future__ import annotations

import networkx as nx
import numpy as np


def loaded_move_cost(
    source: int,
    destination: int,
    carried_gold: float,
    distance_table: np.ndarray,
    powered_distance_table: np.ndarray,
    alpha: float,
    beta: float,
) -> float:
    """Compute the cost of a cached shortest-path move."""
    # The two path sums are cached. Only the load term changes in the GA.
    return (
        distance_table[source, destination]
        + (alpha * carried_gold) ** beta
        * powered_distance_table[source, destination]
    )


def build_path_tables(problem):
    """Precompute shortest paths and their two cost terms."""
    graph = problem.graph
    beta = problem.beta
    node_count = graph.number_of_nodes()

    distances = np.full((node_count, node_count), np.inf)
    powered_distances = np.full((node_count, node_count), np.inf)

    # Dijkstra uses the edge distance defined in Problem.py.
    shortest_paths = dict(nx.all_pairs_dijkstra_path(graph, weight="dist"))

    for source in graph.nodes:
        for destination in graph.nodes:
            if source == destination:
                continue

            distance_sum = 0.0
            powered_sum = 0.0
            node_path = shortest_paths[source][destination]

            # Keep both sums because beta applies to each edge separately.
            for node_a, node_b in zip(node_path, node_path[1:]):
                edge_distance = graph[node_a][node_b]["dist"]
                distance_sum += edge_distance
                powered_sum += edge_distance**beta

            distances[source, destination] = distance_sum
            powered_distances[source, destination] = powered_sum

    return distances, powered_distances, shortest_paths


def materialize_edge_path(decoded_path, shortest_paths):
    """Expand every decoder move into adjacent graph nodes."""
    final_path = []
    current_node = 0

    # Skip the internal starting marker because the public start is implicit.
    for target_node, pickup in decoded_path[1:]:
        segment = shortest_paths[current_node][target_node]

        # Transit nodes collect zero. The target keeps its local pickup.
        for node in segment[1:]:
            local_pickup = pickup if node == target_node else 0
            final_path.append((node, local_pickup))

        current_node = target_node

    return final_path
