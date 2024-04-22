import numpy as np
from tqdm import tqdm

from preprocessing.input_preprocess import reorder_csv, read_csv_to_dict, read_csv_to_strct
from graph_algorithms import get_graph, get_node_all, set_node_strct_all, optimize_graph_nx, precompute_distances


# Генерация начальной популяции, где одна особь это рандомный маршрут
# изначальная структура данных (dict) не позволяют хранить закальцованный
# маршрут, поэтому последняя точка добавляется искуственно.
# Они должны совпадать тк машина доkжна вернуться назад на склад

def generate_initial_population(population_size, type='strct'):
    population = []
    for _ in range(population_size):
        route = []
        if type == 'strct':
            route = list(NODE_POINTS['id'])
        else:
            route = list(NODE_POINTS.keys())
        first_point, last_point = route[0], route[0]
        route.pop(0)
        np.random.shuffle(route)
        route.insert(0, first_point)
        route.append(last_point)
        population.append(route)
    return population


def get_distance_from_matrix(point1, point2, type='strct'):
    if type == 'strct':
        point_index1 = NODE_POINTS[NODE_POINTS['id'] == point1]['it'][0]
        point_index2 = NODE_POINTS[NODE_POINTS['id'] == point2]['it'][0]
        return DISTANCE_MATRIX[point_index1, point_index2]

    else:
        point_index1 = POINT_INDEX_DICT[point1]
        point_index2 = POINT_INDEX_DICT[point2]
        return DISTANCE_MATRIX[point_index1, point_index2]


# Вычисление приспособленности маршрута (меньше значение - лучше)
def fitness(route):
    total_distance = np.sum(
        [get_distance_from_matrix(route[i], route[i + 1], type=TYPE) for i in range(len(route) - 1)])
    return 1 / total_distance


# Скрещивание двух маршрутов, ребенок это часть родителя те маршрута 1 и маршрута 2 (родителя)
def crossover(parent1, parent2):
    prob = []
    for i in range(len(parent1)):
        # Если расстояние больше 0, оно используется в качестве вероятности
        # (чем меньше расстояние, тем выше вероятность). Если расстояние равно 0,
        # устанавливается вероятность 1 (это предотвращает деление на ноль).
        dist = get_distance_from_matrix(parent1[i], parent2[i], type=TYPE)
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


def genetic_algorithm(population_size, generations, mutation_rate):
    population = generate_initial_population(population_size, type=TYPE)

    for generation in tqdm(range(generations), desc="Genetic Algorithm Progress"):
        # Значения приспособленности поколения в полуляции
        fitness_values = [fitness(route) for route in population]

        # Выбор 2 лучших родителей
        best_routes = select_best(population, fitness_values, num_best=2)

        # Скрещивание и мутация для создания новой популяции
        new_population = best_routes
        while len(new_population) < population_size:
            parent1, parent2 = best_routes[:2]
            child = crossover(parent1, parent2)  # скрещивание родителей
            child = mutate(child, mutation_rate)  # случайная мутация
            new_population.append(child)  # добавление ребенка в новую популяцию

        population = new_population

    # Найденный оптимальный маршрут, выбор первого из списка популяции
    best_route = select_best(population, fitness_values, num_best=1)[0]
    return best_route


if __name__ == "__main__":
    city_name = "Saint Petersburg, Russia"
    graph_filename = "../public/road_network_graph.pickle"
    TYPE = 'dict'
    file = '30_ex_9.csv'

    city_graph = get_graph(city_name, graph_filename)

    # filenames = get_all_filenames("public/example_routes")
    # for file in filenames:

    input_csv = f'public/example_routes/{file}'
    output_csv = f'public/result_routes/{file}'

    points = []
    NODE_POINTS = []
    if TYPE == 'strct':
        points = read_csv_to_strct(input_csv)
        NODE_POINTS = set_node_strct_all(points, city_graph)

    else:
        points = read_csv_to_dict(input_csv)
        NODE_POINTS = get_node_all(points, city_graph)

    graph_nx = optimize_graph_nx(city_graph, node_points=NODE_POINTS, type=TYPE)

    DISTANCE_MATRIX, POINT_INDEX_DICT = precompute_distances(graph_nx, NODE_POINTS, type=TYPE)

    best_route = genetic_algorithm(population_size=10, generations=300, mutation_rate=0.1)
    print("\nОптимальный маршрут готов")

    reorder_csv(input_csv, output_csv, best_route, type=TYPE)
