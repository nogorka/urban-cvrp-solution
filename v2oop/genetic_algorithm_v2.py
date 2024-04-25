import random

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


def generate_initial_population(population_size, points):
    population = []
    nn_distance_matrix = fill_nn_matrix(points)

    for _ in range(population_size):
        route = Route(points)
        if random.randint(0, 1):
            route.create_nn_dependant_specimens(nn_distance_matrix)
        else:
            route.create_random_specimen()
        population.append(route)
    return population

def genetic_algorithm(population_size, generations, mutation_rate, points, DM):
    population = generate_initial_population(population_size, points=points)
    print(population)

# for _ in tqdm(range(generations), desc="Genetic Algorithm Progress"):
#     # Значения приспособленности поколения в полуляции
#     fitness_values = [fitness(route, PID, DM) for route in population]
#
#     # Выбор 2 лучших родителей
#     best_routes = select_best(population, fitness_values, num_best=2)
#
#     # Скрещивание и мутация для создания новой популяции
#     new_population = best_routes
#     while len(new_population) < population_size:
#         parent1, parent2 = best_routes[:2]
#         child = crossover(parent1, parent2, PID, DM)  # скрещивание родителей
#         child = mutate(child, mutation_rate)  # случайная мутация
#         new_population.append(child)  # добавление ребенка в новую популяцию
#
#     population = new_population
#
# # Найденный оптимальный маршрут, выбор первого из списка популяции
# route = select_best(population, fitness_values, num_best=1)[0]
# return route[:-1]


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

    best_route = genetic_algorithm(population_size=10, generations=300, mutation_rate=0.1, points=city_points,
                                   DM=distance_matrix)
