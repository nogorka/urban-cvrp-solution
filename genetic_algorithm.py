import numpy as np
from tqdm import tqdm
from geopy.distance import geodesic

from input_preprocess import get_all_filenames, read_csv_to_dict, reorder_csv


# Генерация начальной популяции, где одна особь это рандомный маршрут
def generate_initial_population(population_size):
    population = []
    for _ in range(population_size):
        route = list(POINTS.keys())
        first_point = route[0]
        route.pop(0)
        np.random.shuffle(route)
        route.insert(0, first_point)
        population.append(route)
    return population

# Вычисление матрицы расстояний всех точек со всеми
def precompute_distances():
    num_points = len(POINTS)
    distances = np.zeros((num_points, num_points))
    point_indexes = {}
    enum_points = list(enumerate(POINTS.items()))
    for i, (id1, coord_tuple1) in tqdm(enum_points, desc="Precompute Progress"):
        point_indexes[id1] = i
        for j, (_, coord_tuple2) in enum_points:
            distances[i, j] = geodesic(coord_tuple1, coord_tuple2).kilometers
    return distances, point_indexes

def get_distance_from_matrix(point1, point2):
    point_index1 = POINT_INDEX_DICT[point1]
    point_index2 = POINT_INDEX_DICT[point2]
    return DISTANCE_MATRIX[point_index1, point_index2] #use precompiled distances

# Вычисление приспособленности маршрута (меньше значение - лучше)
def fitness(route):
    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += get_distance_from_matrix(route[i], route[i + 1])
    return 1 / total_distance

# Скрещивание двух маршрутов, ребенок это часть родителя те маршрута 1 и маршрута 2 (родителя)
def crossover(parent1, parent2):
    prob = []
    for i in range(len(parent1)):
        dist = get_distance_from_matrix(parent1[i],  parent2[i])
        if dist > 0:
            prob.append( 1 / dist)
        else:
            prob.append(1)

    prob = prob / np.sum(prob) # нормализация вероятностей

    crossover_point = np.random.choice(np.arange(1, len(parent1) + 1), p=prob)

    child = parent1[:crossover_point]
    child += [point for point in parent2 if point not in child]
    return child

# Мутация маршрута (случайное изменение маршрута)
def mutate(route, mutation_rate):
    for i in range(1, len(route) - 1):  # убираем первую точки из отрезков доступных для мутации
        if np.random.rand() < mutation_rate: # элемент случайности
            j = np.random.randint(i + 1, len(route))
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
    # file = '30_ex_10.csv'

    filenames = get_all_filenames("public/example_routes")
    for file in filenames:

        input_csv = f'public/example_routes/{file}'
        output_csv = f'public/result_routes/{file}'

        POINTS = read_csv_to_dict(input_csv)
        DISTANCE_MATRIX, POINT_INDEX_DICT = precompute_distances()

        best_route = genetic_algorithm(population_size=10, generations=300, mutation_rate=0.1)
        print("\nОптимальный маршрут готов")

        reorder_csv(input_csv, output_csv, best_route)
