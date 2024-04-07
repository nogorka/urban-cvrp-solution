import numpy as np
from tqdm import tqdm
from geopy.distance import geodesic
import networkx as nx

from input_preprocess import get_all_filenames, read_csv_to_dict, reorder_csv
from graph_algorithms import calculate_distance, get_graph, get_node_all, optimize_graph_nx

# Генерация начальной популяции, где одна особь это рандомный маршрут
# изначальная структура данных (dict) не позволяют хранить закальцованный
# маршрут, поэтому последняя точка добавляется искуственно.
# Они должны совпадать тк машина доkжна вернуться назад на склад

def generate_initial_population(population_size):
    population = []
    for _ in range(population_size):
        route = list(NODE_POINTS.keys())
        first_point, last_point = route[0], route[0]
        route.pop(0)
        np.random.shuffle(route)
        route.insert(0, first_point)
        route.append(last_point)
        population.append(route)
    return population

# Вычисление матрицы расстояний всех точек со всеми,
# считается диагональ, заполняется полностью
def precompute_distances(graph_nx):
    num_points = len(NODE_POINTS)
    distances = np.zeros((num_points, num_points))
    point_indexes = {}
    enum_points = list(enumerate(NODE_POINTS.items()))

    for i, (id1, dct1) in tqdm(enum_points, desc="Precompute Progress"):
        point_indexes[id1] = i
        for j in range(i+1, num_points):  # Fill only the upper triangular part
            _, dct2 = enum_points[j][1]
            distances[i, j] = calculate_distance(dct1['node'], dct2['node'], graph_nx)
            distances[j, i] = distances[i, j]
    return distances, point_indexes

def get_distance_from_matrix(point1, point2):
    point_index1 = POINT_INDEX_DICT[point1]
    point_index2 = POINT_INDEX_DICT[point2]
    return DISTANCE_MATRIX[point_index1, point_index2] #use precompiled distances

# Вычисление приспособленности маршрута (меньше значение - лучше)
def fitness(route):
    total_distance = np.sum([get_distance_from_matrix(route[i], route[i + 1]) for i in range(len(route) - 1)])
    return 1 / total_distance

# Скрещивание двух маршрутов, ребенок это часть родителя те маршрута 1 и маршрута 2 (родителя)
def crossover(parent1, parent2):
    prob = []
    for i in range(len(parent1)):
        # Если расстояние больше 0, оно используется в качестве вероятности
        # (чем меньше расстояние, тем выше вероятность). Если расстояние равно 0,
        # устанавливается вероятность 1 (это предотвращает деление на ноль).
        dist = get_distance_from_matrix(parent1[i],  parent2[i])
        if dist > 0:
            prob.append( 1 / dist)
        else:
            prob.append(1)

    prob = prob / np.sum(prob) # нормализация вероятностей

    crossover_point = np.random.choice(np.arange(1, len(parent1) + 1), p=prob)

    if crossover_point > len(parent1) - 1:
        crossover_point = len(parent1) - 1

    child = parent1[:crossover_point]
    child += [point for point in parent2 if point not in child]
    child += parent1[-1:]
    return child

# Мутация маршрута (случайное изменение маршрута)
def mutate(route, mutation_rate):
    for i in range(1, len(route) - 2):  # убираем первую и последнюю точки из отрезков доступных для мутации
        if np.random.rand() < mutation_rate: # элемент случайности
            j = np.random.randint(i + 1, len(route) - 1)
            route[i:j+1] = route[i:j+1][::-1] # смена отрезков из точек в маршруте
    return route

# Выбор лучших маршрутов
def select_best(population, fitness_values, num_best):
    # сортировка в порядке убывания по значению приспособленности
    indices = np.argsort(fitness_values)[-num_best:]
    return [population[i] for i in indices]

def genetic_algorithm(population_size, generations, mutation_rate):
    population = generate_initial_population(population_size)

    for generation in tqdm(range(generations), desc="Genetic Algorithm Progress"):
        # Значения приспособленности поколения в полуляции
        fitness_values = [fitness(route) for route in population]

        # Выбор 2 лучших родителей
        best_routes = select_best(population, fitness_values, num_best=2)

        # Скрещивание и мутация для создания новой популяции
        new_population = best_routes
        while len(new_population) < population_size:
            parent1, parent2 = best_routes[:2]
            child = crossover(parent1, parent2) # скрещивание родителей
            child = mutate(child, mutation_rate) # случайная мутация
            new_population.append(child) # добавление ребенка в новую популяцию

        population = new_population

    # Найденный оптимальный маршрут, выбор первого из списка популяции
    best_route = select_best(population, fitness_values, num_best=1)[0]
    return best_route


if __name__ == "__main__":
    city_name = "Saint Petersburg, Russia"
    graph_filename = "road_network_graph.pickle"

    city_graph = get_graph(city_name, graph_filename)
    graph_nx = optimize_graph_nx(city_graph)
    file = '30_ex_12.csv'

    # filenames = get_all_filenames("public/example_routes")
    # for file in filenames:

    input_csv = f'public/example_routes/{file}'
    output_csv = f'public/result_routes/{file}'

    points = read_csv_to_dict(input_csv)
    NODE_POINTS = get_node_all(points, city_graph)
    DISTANCE_MATRIX, POINT_INDEX_DICT = precompute_distances(graph_nx)

    best_route = genetic_algorithm(population_size=10, generations=300, mutation_rate=0.1)
    print("\nОптимальный маршрут готов")

    reorder_csv(input_csv, output_csv, best_route)
