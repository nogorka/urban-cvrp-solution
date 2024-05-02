import numpy as np
from random import randint, sample, choice
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


def calculate_route_demand(tour):
    if type(tour) == Route:
        return np.sum([p.demand for p in tour.points])
    elif type(tour) == list:
        return np.sum([p.demand for p in tour])
    else:
        return 0


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
        route_demand = calculate_route_demand(route)
        print(f'route demand {route_demand}', abs(route_demand - vehicle_capacity) * penalty_rate)
        if route_demand > vehicle_capacity:
            penalty += (route_demand - vehicle_capacity) * penalty_rate
    return penalty


def fitness(individual, matrix, vehicle_capacity):
    total_distance = individual.calculate_distance(matrix)
    capacity_penalty = calculate_capacity_penalty(individual, vehicle_capacity)

    fitness_value = (1 / total_distance) + capacity_penalty
    return fitness_value


#
# # Вычисление приспособленности маршрута (меньше значение - лучше)
# def fitness(route, matrix, vehicle_capacity):
#     route.calculate_length_M(matrix)
#     demand = calculate_route_demand(route)
#     if demand > vehicle_capacity:
#         return float('inf')  # Assigning a high cost if the capacity is exceeded
#     return 1 / route.length

#
# # Скрещивание двух маршрутов, ребенок это часть родителя те маршрута 1 и маршрута 2 (родителя)
# def capacity_constrained_crossover(parent1, parent2, matrix, vehicle_capacity):
#     # Start with the first part of parent1's route
#     child = parent1.points[:randint(1, parent1.size - 1)]
#     child_demand = calculate_route_demand(child)
#
#     # Attempt to add points from parent2 without exceeding capacity
#     for point in parent2.points:
#         if point not in child:
#             if child_demand + point.demand <= vehicle_capacity:
#                 child.append(point)
#                 child_demand += point.demand
#
#     # If the child is too short, try to fill it with remaining points from parent1
#     for point in parent1.points:
#         if point not in child:
#             if child_demand + point.demand <= vehicle_capacity:
#                 child.append(point)
#                 child_demand += point.demand
#
#     return Route(child)
#
#
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
#
#
# def create_offspring(parents, matrix, vehicle_capacity):
#     parent1, parent2 = parents[:2]
#     offspring = capacity_constrained_crossover(parent1, parent2, matrix, vehicle_capacity)
#     capacity_constrained_mutation(offspring, 0.1, vehicle_capacity)
#
#     return offspring
#

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

        # best_routes = select_best(population, fitness_values, num_best=2)

        # new_population = best_routes
        # while len(new_population) < population_size:
        #     offspring = create_offspring(best_routes, matrix, capacity)
        #     new_population.append(offspring)
        #
        # population = new_population

    # Найденный оптимальный маршрут, выбор первого из списка популяции
    [route] = select_best(population, fitness_values, num_best=1)
    # reorder_to_start_point(route, start_point)
    return [route]


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

    best_route = genetic_algorithm(population_size=10, generations=100, points=city_points, matrix=distance_matrix,
                                   capacity=config['vehicle_capacity'])
    print("\nОптимальный маршрут готов")

    # best_route.calculate_length_G(G)
    print("\n----------------")
    # print("\tДлина, км:\t\t\t\t\t\t", best_route.length)
    print("\tПоследовательность, osmnx ids:\t", best_route)

    # reorder_save_to_csv(input_csv, output_csv, best_route)
    # print("Сохранено в файл:\t\t\t\t", output_csv)
