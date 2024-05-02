import numpy as np
from random import randint, sample, choice, shuffle
from tqdm import tqdm

from v2oop.genetic_algorithm_tsp import create_nn_dependant_specimens, create_random_specimen, select_best
from v2oop.objects.route import Route
from v2oop.preprocess import get_meta_data
from v3_cvrp.individual import Individual

# Генерация начальной популяции, где одна особь это рандомный маршрут
# изначальная структура данных (dict) не позволяют хранить закальцованный
# маршрут, поэтому последняя точка добавляется искуственно.
# Они должны совпадать тк машина доkжна вернуться назад на склад

'''создание начальной популяции: 
только половина особей должна быть сгенерирована случайно, 
другая - с учетом коэффициента близости соседа. 
Коэффициент следует рассчитывать на основе геодезических координат 
'''


def create_feasible_route(available_points, vehicle_capacity):
    route = []
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
    return Route(route), shuffled_available_points + not_suitable_points


def generate_initial_population(population_size, points, vehicle_capacity):
    population = []

    for i in range(population_size):
        remaining_points = points.copy()
        individual = Individual()

        while len(remaining_points) > 0:
            new_route, remaining_points = create_feasible_route(remaining_points, vehicle_capacity)
            if new_route and new_route.points:  # Ensure only non-empty routes are added
                individual.add_route(new_route)

        population.append(individual)

    return population


# если машина загружена больше чем возможно то штрафуем иначе штраф 0
def calculate_capacity_penalty(individual, vehicle_capacity, penalty_rate=0.8):
    penalty = 0
    for route in individual.routes:
        route_demand = route.calculate_demand()
        # print(f'route demand {route_demand}', abs(route_demand - vehicle_capacity) * penalty_rate)
        if route_demand > vehicle_capacity:
            penalty += (route_demand - vehicle_capacity) * penalty_rate
    return penalty


def fitness(individual, matrix, vehicle_capacity):
    if not individual.routes:
        return float('inf')

    total_distance = individual.calculate_distance(matrix)
    capacity_penalty = calculate_capacity_penalty(individual, vehicle_capacity)

    fitness_value = (1 / total_distance) + capacity_penalty
    return fitness_value


# def capacity_constrained_mutation(route, rate, vehicle_capacity):
#     for i in range(route.size):
#         if np.random.rand() < rate:
#             for swap_attempt in range(100):  # Limit the number of swap attempts
#                 j = np.random.randint(route.size)
#                 # Check if swapping does not exceed capacity
#                 if i != j and abs(route.points[i].demand - route.points[j].demand) <= (
#                         vehicle_capacity - calculate_route_demand(route)):
#                     route.points[i], route.points[j] = route.points[j], route.points[i]
#                     break

def calc_prob(route, matrix):
    # Calculate selection probabilities based on distances
    prob = []
    for i in range(route.size - 1):
        dist = matrix[route.points[i].it, route.points[i + 1].it]
        prob.append(1 / (dist if dist > 0 else 1))  # probability is higher for shorter distances

    # Normalize probabilities
    prob = np.array(prob) / np.sum(prob)
    return prob


def choose_point_based_prob_set(pool_route, tour_set, prob):
    available_pool_points = set(pool_route.points.copy()).difference(tour_set)
    chosen_point = list(tour_set)[-1] if len(tour_set) > 0 else None
    while available_pool_points:
        chosen_index = np.random.choice(range(pool_route.size - 1), p=prob)
        chosen_point = pool_route.get_point(chosen_index)
        if chosen_point in available_pool_points:
            pool_route.pop_point(chosen_index)
            break
    return chosen_point


def enhanced_crossover(parent1, parent2, matrix, vehicle_capacity):
    point_pool = [point for route in parent1.routes for point in route.points] + \
                 [point for route in parent2.routes for point in route.points]
    n_points = len(point_pool) / 2
    point_pool_route = Route(point_pool)
    prob = calc_prob(point_pool_route, matrix)

    offspring = Individual()
    cur_tour = []
    cur_tour_set = set()
    current_demand = 0

    while len(cur_tour_set) < n_points:
        print(point_pool_route.points)
        print(cur_tour_set)
        print(current_demand)
        if current_demand < vehicle_capacity:
            # Choose a point based on the defined probabilities
            if point_pool_route.size > 1:
                chosen_point = choose_point_based_prob_set(point_pool_route, cur_tour_set, prob)
                prob = calc_prob(point_pool_route, matrix) if point_pool_route.size > 1 else np.array([])
            else:
                chosen_point = point_pool_route.pop_point(0)
            print(f'chosen point: {chosen_point}')

        else:

            # If the current route is full, start a new route
            offspring.add_route(Route(cur_tour))
            print(f'added route: {cur_tour}')
            cur_tour = []
            current_demand = 0
            continue

        # Add the chosen point if it fits the capacity
        print(f'current demand: {current_demand}', f'chosen demand {chosen_point.demand}')
        if current_demand + chosen_point.demand <= vehicle_capacity:
            cur_tour.append(chosen_point)
            current_demand += chosen_point.demand
            cur_tour_set.add(chosen_point)
        else:
            # Otherwise, place it back and try another point
            point_pool_route.add_point(chosen_point)
            shuffle(point_pool)
            prob = calc_prob(point_pool_route, matrix)

    # Add the last route if it has any points
    if cur_tour:
        offspring.add_route(Route(cur_tour))

    return offspring


def create_offspring(parents, matrix, vehicle_capacity):
    parent1, parent2 = parents[:2]
    offspring = enhanced_crossover(parent1, parent2, matrix, vehicle_capacity)
    # capacity_constrained_mutation(offspring, 0.1, vehicle_capacity)

    return offspring


# def reorder_to_start_point(route, point):
#     index = route.points.index(point)
#     new_route = route.points[index:] + route.points[:index]
#     route.set_points(new_route)


def genetic_algorithm(population_size, generations, points, matrix, capacity):
    start_point = points[0]
    population = generate_initial_population(population_size, points, capacity)
    print(population)

    for _ in tqdm(range(generations), desc="Genetic Algorithm Progress"):
        # Значения приспособленности поколения в полуляции
        fitness_values = [fitness(route, matrix, capacity) for route in population]
        print(fitness_values)

        best_routes = select_best(population, fitness_values, num_best=2)

        new_population = best_routes
        while len(new_population) < population_size:
            offspring = create_offspring(best_routes, matrix, capacity)
            new_population.append(offspring)

        population = new_population

    # Найденный оптимальный маршрут, выбор первого из списка популяции
    [route] = select_best(population, fitness_values, num_best=1)
    # reorder_to_start_point(route, start_point)
    return route


if __name__ == "__main__":
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'input_dir': "../public/example_routes/",
        'output_dir': "../public/result_routes/",
        'file': '10_ex_1.csv',
        'vehicle_capacity': 1000,
    }

    distance_matrix, city_points, input_csv, output_csv, G = get_meta_data(config, config['file'])

    best_route = genetic_algorithm(population_size=10, generations=5, points=city_points, matrix=distance_matrix,
                                   capacity=config['vehicle_capacity'])
    print("\nОптимальный маршрут готов")

    # best_route.calculate_length_G(G)
    print("\n----------------")
    print("\tДлина, км:\t\t\t\t\t\t", best_route.distance)
    print("\tПоследовательность, osmnx ids:\t", best_route)

    # reorder_save_to_csv(input_csv, output_csv, best_route)
    # print("Сохранено в файл:\t\t\t\t", output_csv)
