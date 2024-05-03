import numpy as np

from v2oop.objects.route import Route
from v3_cvrp.individual import Individual


def calc_prob(points, matrix):
    # Calculate selection probabilities based on distances
    prob = []
    for i in range(len(points) - 1):
        dist = matrix[points[i].it, points[i + 1].it]
        prob.append(1 / (dist if dist > 0 else 1))  # probability is higher for shorter distances

    # Normalize probabilities
    prob = np.array(prob) / np.sum(prob)
    return prob


def can_fit_vehicle(extra_point, current_demand, vehicle_capacity):
    return extra_point.demand + current_demand <= vehicle_capacity


def crossover(parent1, parent2, matrix, capacity, depot):
    # create point pool and exclude depot points
    pool = [point for route in parent1.routes for point in route.points[1:]] + \
           [point for route in parent2.routes for point in route.points[1:]]

    prob = calc_prob(pool, matrix)

    offspring = Individual()
    current_route = [depot]
    available_points_set = list(set(pool))
    current_demand = 0

    while len(available_points_set) > 0:
        can_be_added = any(can_fit_vehicle(point, current_demand, capacity) for point in available_points_set)
        if not can_be_added:
            if current_route:
                offspring.add_route(Route(current_route))
            current_route = [depot]
            current_demand = 0

        chosen_point, chosen_index = None, None
        if len(available_points_set) > 1:
            while available_points_set and chosen_point not in available_points_set:
                chosen_index = np.random.choice(range(len(pool) - 1), p=prob)
                chosen_point = pool[chosen_index]
        else:
            chosen_index = pool.index(available_points_set[-1])
            chosen_point = pool[chosen_index]

        # Add the chosen point if it fits the capacity
        if can_fit_vehicle(chosen_point, current_demand, capacity):
            pool.pop(chosen_index)

            current_route.append(chosen_point)
            current_demand += chosen_point.demand
            available_points_set.remove(chosen_point)

            prob = calc_prob(pool, matrix)

    if current_route:
        offspring.add_route(Route(current_route))

    return offspring
