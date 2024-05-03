import numpy as np
from random import randint, sample, choice, shuffle
from tqdm import tqdm

from v2oop.genetic_algorithm_tsp import create_nn_dependant_specimens, create_random_specimen, select_best
from v2oop.objects.route import Route
from v2oop.preprocess import get_meta_data
from v3_cvrp.crossover import crossover
from v3_cvrp.individual import Individual
from v3_cvrp.mutation import hybrid_mutation

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


def create_offspring(parents, matrix, vehicle_capacity):
    parent1, parent2 = parents[:2]
    offspring = crossover(parent1, parent2, matrix, vehicle_capacity)
    hybrid_mutation(offspring, mutation_rate=0.1)
    return offspring


# def reorder_to_start_point(route, point):
#     index = route.points.index(point)
#     new_route = route.points[index:] + route.points[:index]
#     route.set_points(new_route)


def genetic_algorithm(population_size, generations, points, matrix, capacity):
    start_point = points[0]
    population = generate_initial_population(population_size, points, capacity)

    for _ in tqdm(range(generations), desc="Genetic Algorithm Progress"):
        # Значения приспособленности поколения в полуляции
        fitness_values = [fitness(route, matrix, capacity) for route in population]

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
