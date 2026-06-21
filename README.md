# Gold Collection Problem

## Problem

The graph contains one depot, node `0`, and several cities with gold. The thief
starts from the depot, collects all the gold and returns to node `0`.

The route can contain more than one trip. Returning to the depot resets the
carried load, which can reduce the cost of later moves.

## Cost function

The cost of crossing an edge of length `d` while carrying load `w` is:

```text
d + (alpha * d * w)^beta
```

`alpha` controls the weight penalty. `beta` controls how fast this penalty
grows. If a move uses a shortest path with several edges, the cost is computed
edge by edge.

## Project structure

- `Problem.py`: official problem definition. It creates the graph, gold values
  and parameters, and provides the baseline and cost functions.
- `s347543.py`: main entry point. It builds the cached tables, runs the solver
  and returns the final path.
- `base_requirements.txt`: Python libraries required by the project.
- `src/evolutionary_search.py`: evolutionary algorithm, greedy decoder,
  selection, crossover, mutations and elitism.
- `src/path_metrics.py`: shortest-path preprocessing, cached cost terms and
  expansion of the final path.
- `src/path_validation.py`: checks output format, graph edges and collected
  gold.
- `src/benchmark.py`: runs the selected benchmark cases and prints the
  baseline, GA cost and percentage improvement.

## Evolutionary approach

Each individual is a permutation of all cities except the depot. The
permutation defines the collection order, while a greedy decoder decides when
to return to node `0`.

The population contains 100 individuals and the search runs for 1000
generations.

### Selection

Parents are selected with tournament selection. Three random candidates are
compared and the one with the lowest cost is chosen.

### Crossover

The solver uses Ordered Crossover. A segment of the first parent is copied to
the child, then the missing cities are inserted using the order of the second
parent. The result is always a valid permutation.

### Mutation

Two mutation operators are used:

- relocation moves one city to another position;
- reversal inverts a part of the permutation.

Each operator has a probability of 20%.

### Elitism

The best 5% of the population is copied directly to the next generation. At
least two elite individuals are always preserved.

### Greedy decoder

For each city, the decoder compares two choices:

- add the city to the current trip;
- return to the depot and visit the city in a new trip.

The comparison uses the real load-dependent cost. The load increases after a
pickup and becomes zero after a depot return.

## Design choices

The chromosome only stores the city order. Depot returns are handled by the
decoder, so crossover and mutation remain simple.

Shortest paths are computed before the GA starts. Their distance terms are
cached because the fitness function is evaluated many times. The final path is
then expanded so every consecutive movement is a real graph edge.

## Output format

The solver returns:

```python
[(city_1, pickup_1), ..., (0, 0)]
```

The initial depot is implicit. Each pickup is the gold collected at that visit,
not the total carried load. Intermediate shortest-path nodes have pickup zero,
and the last element is always `(0, 0)`.

## Results

The benchmark uses problem seed `42` and random seed `0`.

### Results - N = 100

| N | Density | Alpha | Beta | Baseline | GA cost | Improvement |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.2 | 2.0 | 1.0 | 50,425.31 | 50,393.20 | 0.06% |
| 100 | 0.2 | 1.0 | 2.0 | 5,334,401.93 | 4,961,639.03 | 6.99% |
| 100 | 0.2 | 1.0 | 5.0 | 187,088,165,532,885.91 | 53,366,459,363,497.97 | 71.48% |
| 100 | 0.2 | 1.0 | 1.0 | 25,266.41 | 25,234.65 | 0.13% |
| 100 | 1.0 | 2.0 | 1.0 | 36,457.92 | 36,448.23 | 0.03% |
| 100 | 1.0 | 1.0 | 2.0 | 5,404,978.09 | 4,215,010.89 | 22.02% |
| 100 | 1.0 | 1.0 | 5.0 | 347,651,302,495,115.25 | 82,899,380,880,519.67 | 76.15% |
| 100 | 1.0 | 1.0 | 1.0 | 18,266.19 | 18,252.80 | 0.07% |

### Results - N = 1000

| N | Density | Alpha | Beta | Baseline | GA cost | Improvement |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 0.2 | 2.0 | 1.0 | 390,028.72 | 389,943.24 | 0.02% |
| 1000 | 0.2 | 1.0 | 2.0 | 37,545,927.70 | 25,670,626.75 | 31.63% |
| 1000 | 0.2 | 1.0 | 5.0 | 1,575,163,721,306,340.75 | 129,281,783,300,647.83 | 91.79% |
| 1000 | 0.2 | 1.0 | 1.0 | 195,402.96 | 195,309.23 | 0.05% |
| 1000 | 1.0 | 2.0 | 1.0 | 385,105.64 | 384,953.63 | 0.04% |
| 1000 | 1.0 | 1.0 | 2.0 | 57,580,018.87 | 45,950,804.83 | 20.20% |
| 1000 | 1.0 | 1.0 | 5.0 | 3,798,422,113,393,741.00 | 962,754,996,671,261.00 | 74.65% |
| 1000 | 1.0 | 1.0 | 1.0 | 192,936.23 | 192,768.15 | 0.09% |

Main observations:

- Increasing `alpha` from `1.0` to `2.0` with `beta = 1.0` increases the
  absolute cost, but the percentage improvement remains below `0.1%`.
- Increasing `beta` has a much stronger effect. With `beta = 2.0` the gain is
  between `6.99%` and `31.63%`; with `beta = 5.0` it reaches `71.48%` to
  `91.79%`.
- Density `1.0` helps the `N = 100` quadratic case, while density `0.2` gives
  better improvements for the larger `N = 1000` cases with `beta > 1`.
- The `N = 1000` instances take much longer because the search evaluates
  larger permutations and the shortest-path preprocessing uses more memory.
