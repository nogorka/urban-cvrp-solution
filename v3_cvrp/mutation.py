import numpy as np
from random import choice, randint, sample


def hybrid_mutation(individual, capacity, matrix, mutation_rate=0.3):
    if np.random.rand() < mutation_rate:
        pool = [swap_mutation, inter_route_swap_mutation, inversion_mutation]
        mutation = choice(pool)
        mutation(individual, capacity)
        hybrid_irgibnnm_mutation(individual, matrix, capacity)
    else:
        relocation_mutation(individual, capacity)


def can_add_point_to_route(point, route, capacity):
    route.calculate_demand()
    return route.demand + point.demand <= capacity


def swap_mutation(individual, capacity=None):
    """swaps two randomly chosen points within selected route"""

    route = choice(individual.routes)
    swap(route)


def swap(route, i=None, j=None):
    if route.size > 3:
        if not i and not j:
            i, j = np.random.choice(range(1, route.size - 1), 2, replace=False)
        route.points[i], route.points[j] = route.points[j], route.points[i]


def inter_route_swap_mutation(individual, capacity):
    """picks two different routes from the individual and swaps one point from each"""

    if individual.size > 1:
        r1, r2 = np.random.choice(individual.routes, 2, replace=False)
        if r1.size > 2 and r2.size > 2:
            i, j = choice(range(1, r1.size - 1)), choice(range(1, r2.size - 1))
            can_be_added_r1 = can_add_point_to_route(r1.points[i], r2, capacity)
            if can_be_added_r1 and can_add_point_to_route(r2.points[j], r1, capacity):
                r1.points[i], r2.points[j] = r2.points[j], r1.points[i]


def relocation_mutation(individual, capacity):
    """selects a point from one route and moves it to another route"""

    if individual.size > 1:
        source_route = choice(individual.routes)
        if source_route.size > 2:
            point_index = randint(1, source_route.size - 2)
            point = source_route.get_point(point_index)
            target_route = choice(individual.routes)
            if can_add_point_to_route(point, target_route, capacity):
                source_route.pop_point(point_index)
                target_route.add_point(point)


def inversion_mutation(individual, capacity=None):
    """selects a segment within a route and invert the sequence of points in that segment"""

    route = choice(individual.routes)
    inverse(route)


def inverse(route):
    if route.size > 3:
        start, end = sorted(np.random.choice(range(1, route.size - 1), 2, replace=False))
        route.points[start:end + 1] = reversed(route.points[start:end + 1])


def hybrid_irgibnnm_mutation(individual, matrix, capacity=None):
    for route in individual.routes:
        inverse(route)
        rgibnnm_mutation(route, matrix)


def rgibnnm_mutation(route, nn_matrix, param=3):
    if route.size > 4:
        route_its = [p.it for p in route.points[1:-1]]
        random_gene_it = choice(route_its)  # -2 cuz route length initially longer in 2 node
        random_gene_idx = route_its.index(random_gene_it)

        distances = nn_matrix[random_gene_it]
        cur_route_dist = sorted(((i, distances[i]) for i in range(len(distances) - 1) if i in route_its),
                                    key=lambda x: x[1])

        if len(cur_route_dist) > 3:
            filtered_nn = [cur_route_dist[i] if cur_route_dist[i][0] != random_gene_it else float('inf')
                           for i in range(len(cur_route_dist))]

            nearest_neighbor = filtered_nn[1]  # filtered_nn[0] = inf, item structure: (it, distance)
            nearest_neighbor_idx = route_its.index(nearest_neighbor[0])

            # Select a random neighbor of the nearest neighbor within a range (using modulo for wraparound)
            neighbors_route_range = range(max(0, nearest_neighbor_idx - param),
                                    min(len(route_its), nearest_neighbor_idx + param + 1))
            swap_with_it = choice([route_its[n_it] for n_it in neighbors_route_range if n_it != random_gene_it])

            # Perform the swap mutation
            swap_with_idx = route_its.index(swap_with_it)
            swap(route, i=random_gene_idx, j=swap_with_idx)
