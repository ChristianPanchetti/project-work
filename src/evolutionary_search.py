"""Genetic search and greedy route decoder."""

from __future__ import annotations

import random

import numpy as np
from tqdm import tqdm

from .path_metrics import loaded_move_cost


class EvolutionaryCollector:
    """Optimize the order in which cities are collected."""

    def __init__(
        self,
        problem,
        distance_table,
        powered_distance_table,
        population_size=50,
        generation_count=1000,
    ):
        self.problem = problem
        self.distance_table = distance_table
        self.powered_distance_table = powered_distance_table
        self.population_size = population_size
        self.generation_count = generation_count

        # Fitness is called many times, so keep gold values in a compact array.
        self.gold = np.array(
            [
                problem._graph.nodes[node]["gold"]
                for node in range(len(problem.graph.nodes))
            ]
        )

        # An individual is a permutation of every city except depot 0.
        self.collectable_cities = list(range(1, len(problem.graph.nodes)))

    def _initial_population(self):
        """Create the first population of random permutations."""
        population = []
        for _ in range(self.population_size):
            individual = self.collectable_cities[:]
            random.shuffle(individual)
            population.append(individual)
        return population

    def _decode_and_score(self, individual):
        """Insert depot returns and compute the exact route cost."""
        depot = 0
        alpha = self.problem.alpha
        beta = self.problem.beta
        distances = self.distance_table
        powered_distances = self.powered_distance_table

        total_cost = 0.0
        current_trip = [depot]
        current_load = 0.0

        # The first depot marker is internal. It is removed from final output.
        decoded_path = [(depot, 0)]

        for city in individual:
            city_pickup = self.gold[city]

            # A new trip always reaches its first city with zero load.
            if len(current_trip) == 1:
                total_cost += distances[depot, city]
                current_trip.append(city)
                current_load = city_pickup
                decoded_path.append((city, city_pickup))
                continue

            previous_city = current_trip[-1]
            load_after_pickup = current_load + city_pickup

            # Cost of closing the current trip before visiting this city.
            close_current = loaded_move_cost(
                previous_city,
                depot,
                current_load,
                distances,
                powered_distances,
                alpha,
                beta,
            )

            # Cost of adding the city to the current trip.
            reach_city = loaded_move_cost(
                previous_city,
                city,
                current_load,
                distances,
                powered_distances,
                alpha,
                beta,
            )
            close_after_city = loaded_move_cost(
                city,
                depot,
                load_after_pickup,
                distances,
                powered_distances,
                alpha,
                beta,
            )
            extension_delta = reach_city + close_after_city - close_current

            # Alternative: serve this city in a separate depot trip.
            separate_trip = (
                distances[depot, city]
                + loaded_move_cost(
                    city,
                    depot,
                    city_pickup,
                    distances,
                    powered_distances,
                    alpha,
                    beta,
                )
            )

            if extension_delta <= separate_trip:
                # Keep the trip open and update the carried gold.
                total_cost += reach_city
                current_trip.append(city)
                current_load = load_after_pickup
                decoded_path.append((city, city_pickup))
            else:
                # Return to 0, unload, then start a new trip.
                total_cost += close_current
                decoded_path.append((depot, 0))

                total_cost += distances[depot, city]
                current_trip = [depot, city]
                current_load = city_pickup
                decoded_path.append((city, city_pickup))

        # Every solution must end at the depot.
        if len(current_trip) > 1:
            total_cost += loaded_move_cost(
                current_trip[-1],
                depot,
                current_load,
                distances,
                powered_distances,
                alpha,
                beta,
            )
            decoded_path.append((depot, 0))

        return total_cost, decoded_path

    @staticmethod
    def _select_by_tournament(scored_population, tournament_size=3):
        """Select the best individual from a small random group."""
        candidates = random.sample(scored_population, tournament_size)
        return min(candidates, key=lambda item: item[1])[0]

    @staticmethod
    def _ordered_recombination(parent_a, parent_b):
        """Create one valid permutation with Ordered Crossover."""
        size = len(parent_a)
        start, end = sorted(random.sample(range(size), 2))
        child = [None] * size

        # Keep one slice from the first parent.
        child[start:end] = parent_a[start:end]
        inherited = set(child[start:end])

        # Fill empty positions following the order of the second parent.
        parent_b_index = 0
        for position in range(size):
            if child[position] is not None:
                continue
            while parent_b[parent_b_index] in inherited:
                parent_b_index += 1
            child[position] = parent_b[parent_b_index]
            parent_b_index += 1

        return child

    @staticmethod
    def _relocate_mutation(individual):
        """Move one city to another position."""
        source, destination = random.sample(range(len(individual)), 2)
        city = individual.pop(source)
        individual.insert(destination, city)

    @staticmethod
    def _reverse_mutation(individual):
        """Reverse a random part of the permutation."""
        start, end = sorted(random.sample(range(len(individual)), 2))
        individual[start:end] = individual[start:end][::-1]

    def _mutate(self, individual):
        """Apply one of the two mutation operators."""
        draw = random.random()

        # Relocation and reversal both have probability 20%.
        if draw < 0.2:
            self._relocate_mutation(individual)
        elif draw < 0.4:
            self._reverse_mutation(individual)

    def search(self):
        """Run the GA and return its best decoded path."""
        population = self._initial_population()
        best_cost = float("inf")
        best_decoded_path = None

        for _ in tqdm(range(self.generation_count)):
            scored_population = []

            # Decode and evaluate each city permutation.
            for individual in population:
                cost, decoded_path = self._decode_and_score(individual)
                scored_population.append((individual, cost, decoded_path))

            scored_population.sort(key=lambda item: item[1])
            _, generation_cost, generation_path = scored_population[0]

            # Keep the best result found across all generations.
            if generation_cost < best_cost:
                best_cost = generation_cost
                best_decoded_path = generation_path[:]

            # Copy the best 5% without crossover or mutation.
            elite_count = max(2, int(self.population_size * 0.05))
            next_population = [
                individual
                for individual, _, _ in scored_population[:elite_count]
            ]

            # Fill the rest of the population with new children.
            while len(next_population) < self.population_size:
                parent_a = self._select_by_tournament(scored_population)
                parent_b = self._select_by_tournament(scored_population)
                child = self._ordered_recombination(parent_a, parent_b)
                self._mutate(child)
                next_population.append(child)

            population = next_population

        return best_decoded_path, best_cost
