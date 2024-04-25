import numpy as np
from random import randint, sample
from tqdm import tqdm

from algorithms.graph_algorithms import get_graph, optimize_graph_nx
from v2oop.graph import set_node_all_point_list, precompute_distances
from v2oop.objects.route import Route
from v2oop.preprocess import read_csv_to_point_list
from v2oop.utils import fill_nn_matrix

# Генерация начальной популяции, где одна особь это рандомный маршрут
# изначальная структура данных (dict) не позволяют хранить закальцованный
# маршрут, поэтому последняя точка добавляется искуственно.
# Они должны совпадать тк машина доkжна вернуться назад на склад

'''создание начальной популяции: 
только половина особей должна быть сгенерирована случайно, 
другая - с учетом коэффициента близости соседа. 
Коэффициент следует рассчитывать на основе геодезических координат 
'''


# now i removed fixing first point so later
# TODO:  don't forget to filter result route and fix first point
# also I romeved doubling it for the end

def create_random_specimen(route: Route):
    route.set_points(sample(route.points, route.size))


def create_nn_dependant_specimens(route, matrix):
    start_index = randint(0, route.size - 1)
    tour = [route.points[start_index]]
    visited = {start_index}

    current_index = start_index
    for _ in range(1, route.size):
        next_index = min((idx for idx in range(route.size) if idx not in visited),
                         key=lambda idx: matrix[current_index][idx])
        visited.add(next_index)
        tour.append(route.points[next_index])
        current_index = next_index

    route.set_points(tour)


def generate_initial_population(population_size, points):
    population = []
    nn_distance_matrix = fill_nn_matrix(points)

    for _ in range(population_size):
        route = Route(points)
        if randint(0, 1):
            create_nn_dependant_specimens(route, nn_distance_matrix)
        else:
            create_random_specimen(route)
        population.append(route)
    return population


# Вычисление приспособленности маршрута (меньше значение - лучше)
def fitness(route, matrix):
    route.calculate_length(matrix)
    return 1 / route.length


def select_best(population, fitness_values, num_best):
    # сортировка в порядке убывания по значению приспособленности
    indices = np.argsort(fitness_values)[-num_best:]
    return [population[i] for i in indices]


def create_offspring(parents, matrix):
    parent1, parent2 = parents[:2]
    # child = crossover(parent1, parent2, PID, DM)  # скрещивание родителей
    # child = mutate(child, mutation_rate)  # случайная мутация
    return parent1


def genetic_algorithm(population_size, generations, points, DM):
    population = generate_initial_population(population_size, points=points)

    for _ in tqdm(range(generations), desc="Genetic Algorithm Progress"):
        # Значения приспособленности поколения в полуляции
        fitness_values = [fitness(route, DM) for route in population]

        best_routes = select_best(population, fitness_values, num_best=2)

        new_population = best_routes
        while len(new_population) < population_size:
            offspring = create_offspring(best_routes, distance_matrix)
            new_population.append(offspring)

        population = new_population

    # Найденный оптимальный маршрут, выбор первого из списка популяции
    [route] = select_best(population, fitness_values, num_best=1)
    return route


if __name__ == "__main__":
    city_name = "Saint Petersburg, Russia"
    graph_filename = "../public/road_network_graph.pickle"
    file = '10_ex_1.csv'

    city_graph = get_graph(city_name, graph_filename)
    graph_nx = optimize_graph_nx(city_graph)

    input_csv = f'../public/example_routes/{file}'
    output_csv = f'../public/result_routes/{file}'

    city_points = read_csv_to_point_list(input_csv)
    set_node_all_point_list(city_points, city_graph)

    distance_matrix = precompute_distances(graph_nx, city_points)

    best_route = genetic_algorithm(population_size=3, generations=10, points=city_points, DM=distance_matrix)
    print(best_route)
