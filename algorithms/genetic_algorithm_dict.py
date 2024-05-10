import numpy as np
from tqdm import tqdm

from preprocessing.input_preprocess import reorder_csv, read_csv_to_dict
from graph_algorithms import get_graph, get_node_all, optimize_graph_nx, precompute_distances, calculate_route_lengths


# Генерация начальной популяции, где одна особь это рандомный маршрут
# изначальная структура данных (dict) не позволяют хранить закальцованный
# маршрут, поэтому последняя точка добавляется искуственно.
# Они должны совпадать тк машина доkжна вернуться назад на склад

def generate_initial_population(population_size, node_points):
    population = []
    for _ in range(population_size):
        route = list(node_points.keys())
        first_point, last_point = route[0], route[0]
        route.pop(0)
        np.random.shuffle(route)
        route.insert(0, first_point)
        route.append(last_point)
        population.append(route)
    return population


def get_distance_from_matrix(point1, point2, point_index_dict, distance_matrix):
    point_index1 = point_index_dict[point1]
    point_index2 = point_index_dict[point2]
    return distance_matrix[point_index1, point_index2]


# Вычисление приспособленности маршрута (меньше значение - лучше)
def fitness(route, PID, DM):
    total_distance = np.sum(
        [
            get_distance_from_matrix(
                route[i], route[i + 1],
                point_index_dict=PID, distance_matrix=DM
            ) for i in range(len(route) - 1)
        ])
    return 1 / total_distance


# Скрещивание двух маршрутов, ребенок это часть родителя те маршрута 1 и маршрута 2 (родителя)
def crossover(parent1, parent2, PID, DM):
    prob = []
    for i in range(len(parent1)):
        # Если расстояние больше 0, оно используется в качестве вероятности
        # (чем меньше расстояние, тем выше вероятность). Если расстояние равно 0,
        # устанавливается вероятность 1 (это предотвращает деление на ноль).
        dist = get_distance_from_matrix(parent1[i], parent2[i], point_index_dict=PID, distance_matrix=DM)
        if dist > 0:
            prob.append(1 / dist)
        else:
            prob.append(1)

    prob = prob / np.sum(prob)  # нормализация вероятностей

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
        if np.random.rand() < mutation_rate:  # элемент случайности
            j = np.random.randint(i + 1, len(route) - 1)
            route[i:j + 1] = route[i:j + 1][::-1]  # смена отрезков из точек в маршруте
    return route


# Выбор лучших маршрутов
def select_best(population, fitness_values, num_best):
    # сортировка в порядке убывания по значению приспособленности
    indices = np.argsort(fitness_values)[-num_best:]
    return [population[i] for i in indices]


def genetic_algorithm(population_size, generations, mutation_rate, NP, PID, DM):
    population = generate_initial_population(population_size, node_points=NP)

    for _ in tqdm(range(generations), desc="Genetic Algorithm Progress"):
        # Значения приспособленности поколения в полуляции
        fitness_values = [fitness(route, PID, DM) for route in population]

        # Выбор 2 лучших родителей
        best_routes = select_best(population, fitness_values, num_best=2)

        # Скрещивание и мутация для создания новой популяции
        new_population = best_routes
        while len(new_population) < population_size:
            parent1, parent2 = best_routes[:2]
            child = crossover(parent1, parent2, PID, DM)  # скрещивание родителей
            child = mutate(child, mutation_rate)  # случайная мутация
            new_population.append(child)  # добавление ребенка в новую популяцию

        population = new_population

    # Найденный оптимальный маршрут, выбор первого из списка популяции
    route = select_best(population, fitness_values, num_best=1)[0]
    return route[:-1]


if __name__ == "__main__":
    city_name = "Saint Petersburg, Russia"
    graph_filename = "../public/road_network_graph.pickle"
    file = '10_ex_1.csv'
    type='dict'

    city_graph = get_graph(city_name, graph_filename)

    # filenames = get_all_filenames("public/test_routes")
    # for file in filenames:

    input_csv = f'../public/example_routes/{file}'
    output_csv = f'../public/result_routes/{file}'

    points = read_csv_to_dict(input_csv)
    node_points = get_node_all(points, city_graph)

    graph_nx = optimize_graph_nx(city_graph, node_points=node_points, type=type)

    distance_matrix, point_index_dict = precompute_distances(graph_nx, node_points, type=type)

    best_route = genetic_algorithm(population_size=10, generations=300, mutation_rate=0.1,
                                   NP=node_points, PID=point_index_dict, DM=distance_matrix)
    best_length = calculate_route_lengths(best_route, city_graph, node_points)
    print("\nОптимальный маршрут готов")
    print("Длина, км:\t\t\t\t\t\t", best_length)
    print("Последовательность, osmnx ids:\t", best_route)

    reorder_csv(input_csv, output_csv, best_route, type=type)
    print("Сохранено в файл:\t\t\t\t", output_csv)
