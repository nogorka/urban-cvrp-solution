from random import sample, randint

from objects.route import Route
from v2oop.utils import fill_nn_matrix
from objects.individual import Individual


def create_random_based_feasible_route(available_points, vehicle_capacity, depot):
    route = [depot]
    current_demand = 0
    shuffled_available_points = sample(available_points, len(available_points))

    not_suitable_points = []
    while current_demand < vehicle_capacity:
        if len(shuffled_available_points) > 0:
            point = shuffled_available_points.pop()
            if current_demand + point.demand <= vehicle_capacity:
                route.append(point)
                current_demand += point.demand
            else:
                not_suitable_points.append(point)
        else:
            break
    route.append(depot)
    return Route(route), shuffled_available_points + not_suitable_points


def create_nn_dependant_feasible_route(available_points, matrix, vehicle_capacity, depot):
    current_demand = 0
    route = [depot]
    visited = set()

    available_indices = list(range(len(available_points)))
    not_suitable_points = []

    current_index = available_indices[randint(0, len(available_indices) - 1)]
    while current_demand < vehicle_capacity and available_indices:
        next_index_candidates = [idx for idx in available_indices if idx not in visited]
        if not next_index_candidates:
            break

        next_index = min(next_index_candidates, key=lambda idx: matrix[current_index][idx])
        point = available_points[next_index]
        visited.add(next_index)

        if current_demand + point.demand <= vehicle_capacity:
            route.append(point)
            current_demand += point.demand
        else:
            not_suitable_points.append(point)

        current_index = next_index
        available_indices.remove(next_index)

    route.append(depot)
    return Route(route), [available_points[i] for i in available_indices if i not in visited] + not_suitable_points


def generate_initial_population(population_size, points, vehicle_capacity, depot):
    population = []
    nn_distance_matrix = fill_nn_matrix(points)

    for i in range(population_size):
        remaining_points = [p for p in points if p != depot]
        individual = Individual()

        if randint(0, 1):
            while len(remaining_points) > 0:
                new_route, remaining_points = create_nn_dependant_feasible_route(remaining_points, nn_distance_matrix,
                                                                                 vehicle_capacity, depot)
                if new_route and new_route.size > 1:  # Ensure only routes with more than just the depot are added
                    individual.add_route(new_route)
        else:
            while len(remaining_points) > 0:
                new_route, remaining_points = create_random_based_feasible_route(remaining_points, vehicle_capacity,
                                                                                 depot)
                if new_route and new_route.size > 1:  # Ensure only routes with more than just the depot are added
                    individual.add_route(new_route)

        population.append(individual)

    return population
