import numpy as np
import random


def hybrid_mutation(individual, mutation_rate=0.1):
    if np.random.rand() < mutation_rate:
        pool = [swap_mutation, inversion_mutation,
                relocation_mutation, inversion_mutation]
        mutation = random.choice(pool)
        mutation(individual)


def swap_mutation(individual):
    route = random.choice(individual.routes)
    if len(route.points) > 1:
        i, j = np.random.choice(len(route.points), 2, replace=False)
        route.points[i], route.points[j] = route.points[j], route.points[i]


def inter_route_swap_mutation(individual):
    if len(individual.routes) > 1:
        r1, r2 = np.random.choice(individual.routes, 2, replace=False)
        if r1.points and r2.points:
            i, j = random.choice(range(len(r1.points))), random.choice(range(len(r2.points)))
            r1.points[i], r2.points[j] = r2.points[j], r1.points[i]


def relocation_mutation(individual):
    if len(individual.routes) > 1:
        source_route = random.choice(individual.routes)
        if source_route.points:
            point = source_route.pop_point(random.randint(0, len(source_route.points) - 1))
            target_route = random.choice(individual.routes)
            target_route.add_point(point)


def inversion_mutation(individual):
    route = random.choice(individual.routes)
    if len(route.points) > 1:
        start, end = sorted(np.random.choice(len(route.points), 2, replace=False))
        route.points[start:end + 1] = reversed(route.points[start:end + 1])
