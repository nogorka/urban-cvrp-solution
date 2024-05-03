import numpy as np
import random


def hybrid_mutation(individual, capacity, mutation_rate=0.1):
    if np.random.rand() < mutation_rate:
        pool = [swap_mutation, inversion_mutation,
                relocation_mutation, inversion_mutation]
        mutation = random.choice(pool)
        mutation(individual, capacity)


def can_add_point_to_route(point, route, capacity):
    route.calculate_demand()
    return route.demand + point.demand <= capacity


def swap_mutation(individual, capacity=None):
    """swaps two randomly chosen points within selected route"""

    route = random.choice(individual.routes)
    if len(route.points) > 1:
        i, j = np.random.choice(len(route.points), 2, replace=False)
        route.points[i], route.points[j] = route.points[j], route.points[i]


def inter_route_swap_mutation(individual, capacity):
    """picks two different routes from the individual and swaps one point from each"""

    if len(individual.routes) > 1:
        r1, r2 = np.random.choice(individual.routes, 2, replace=False)
        if r1.points and r2.points:
            i, j = random.choice(range(len(r1.points))), random.choice(range(len(r2.points)))
            if can_add_point_to_route(r1.points[i], r2, capacity) and can_add_point_to_route(r2.points[j], r1, capacity):
                r1.points[i], r2.points[j] = r2.points[j], r1.points[i]


def relocation_mutation(individual, capacity):
    """selects a point from one route and moves it to another route"""

    if len(individual.routes) > 1:
        source_route = random.choice(individual.routes)
        if source_route.points:
            point_index = random.randint(0, len(source_route.points) - 1)
            point = source_route.get_point(point_index)
            target_route = random.choice(individual.routes)
            if can_add_point_to_route(point, target_route, capacity):
                source_route.pop_point(point_index)
                target_route.add_point(point)


def inversion_mutation(individual, capacity=None):
    """selects a segment within a route and invert the sequence of points in that segment"""

    route = random.choice(individual.routes)
    if len(route.points) > 1:
        start, end = sorted(np.random.choice(len(route.points), 2, replace=False))
        route.points[start:end + 1] = reversed(route.points[start:end + 1])
