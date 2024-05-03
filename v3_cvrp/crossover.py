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


def get_available_points(pool, tour_set):
    return set(pool).difference(tour_set)


def choose_point_based_prob_set(pool, tour_set, prob):
    available_pool_points = get_available_points(pool, tour_set)
    chosen_point = list(tour_set)[-1] if len(tour_set) > 0 else None

    while available_pool_points:
        chosen_index = np.random.choice(range(len(pool) - 1), p=prob)
        chosen_point = pool[chosen_index]
        if chosen_point in available_pool_points:
            pool.pop(chosen_index)
            break
    return chosen_point


def can_add_any_point(points, current_demand, vehicle_capacity):
    return any(point.demand + current_demand <= vehicle_capacity for point in points)


def crossover(parent1, parent2, matrix, vehicle_capacity, depot):
    # create point pool and exclude depot points
    pool = [point for route in parent1.routes for point in route.points[1:]] + \
                 [point for route in parent2.routes for point in route.points[1:]]

    n_points = len(pool) / 2
    prob = calc_prob(pool, matrix)

    offspring = Individual()
    current_route = [depot]
    used_points_set = set()
    current_demand = 0

    while len(used_points_set) < n_points:
        available_points = get_available_points(pool, used_points_set)
        can_be_added = can_add_any_point(available_points, current_demand, vehicle_capacity)
        if not can_be_added:
            if current_route:
                offspring.add_route(Route(current_route))
            current_route = [depot]
            current_demand = 0

        if len(pool) > 1:
            chosen_point = choose_point_based_prob_set(pool, used_points_set, prob)
            prob = calc_prob(pool, matrix) if len(pool) > 1 else np.array([])
        else:
            chosen_point = pool.pop(0)

        # Add the chosen point if it fits the capacity
        if current_demand + chosen_point.demand <= vehicle_capacity:
            current_route.append(chosen_point)
            current_demand += chosen_point.demand
            used_points_set.add(chosen_point)
        else:
            pool.append(chosen_point)
            prob = calc_prob(pool, matrix)

    if current_route:
        offspring.add_route(Route(current_route))

    return offspring
