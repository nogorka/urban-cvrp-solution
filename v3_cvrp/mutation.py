import numpy as np
from random import choice, randint


def hybrid_mutation(individual, capacity, mutation_rate=0.1):
    if np.random.rand() < mutation_rate:
        pool = [swap_mutation, inter_route_swap_mutation, relocation_mutation, inversion_mutation]
        mutation = choice(pool)
        mutation(individual, capacity)


def can_add_point_to_route(point, route, capacity):
    route.calculate_demand()
    return route.demand + point.demand <= capacity


def swap_mutation(individual, capacity=None):
    """swaps two randomly chosen points within selected route"""

    route = choice(individual.routes)
    if route.size > 2:
        i, j = np.random.choice(range(1, route.size), 2, replace=False)
        route.points[i], route.points[j] = route.points[j], route.points[i]


def inter_route_swap_mutation(individual, capacity):
    """picks two different routes from the individual and swaps one point from each"""

    if individual.size > 1:
        r1, r2 = np.random.choice(individual.routes, 2, replace=False)
        if r1.size > 1 and r2.size > 1:
            i, j = choice(range(1, r1.size)), choice(range(1, r2.size))
            can_be_added_r1 = can_add_point_to_route(r1.points[i], r2, capacity)
            if can_be_added_r1 and can_add_point_to_route(r2.points[j], r1, capacity):
                r1.points[i], r2.points[j] = r2.points[j], r1.points[i]


def relocation_mutation(individual, capacity):
    """selects a point from one route and moves it to another route"""

    if individual.size > 1:
        source_route = choice(individual.routes)
        if source_route.size > 1:
            point_index = randint(1, source_route.size - 1)
            point = source_route.get_point(point_index)
            target_route = choice(individual.routes)
            if can_add_point_to_route(point, target_route, capacity):
                source_route.pop_point(point_index)
                target_route.add_point(point)


def inversion_mutation(individual, capacity=None):
    """selects a segment within a route and invert the sequence of points in that segment"""

    route = choice(individual.routes)
    if route.size > 2:
        start, end = sorted(np.random.choice(range(1, route.size), 2, replace=False))
        route.points[start:end + 1] = reversed(route.points[start:end + 1])
