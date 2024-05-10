import numpy as np
from random import randint, sample, choice
from tqdm import tqdm
from objects.route import Route
from v2oop.preprocess import reorder_save_to_csv, get_meta_data
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
    route.calculate_length_M(matrix)
    return 1 / route.length


def select_best(population, fitness_values, num_best):
    # сортировка в порядке убывания по значению приспособленности
    indices = np.argsort(fitness_values)[-num_best:]
    return [population[i] for i in indices]


# Скрещивание двух маршрутов, ребенок это часть родителя те маршрута 1 и маршрута 2 (родителя)
def crossover(parent1, parent2, matrix):
    prob = []
    for i in range(parent1.size - 1):
        dist = matrix[parent1.points[i].it, parent2.points[i + 1].it]
        if dist > 0:
            # Если длина больше 0, она используется в качестве вероятности (чем меньше длина, тем выше вероятность).
            prob.append(1 / dist)
        else:
            # Если расстояние равно 0, устанавливается вероятность 1 (это предотвращает деление на ноль).
            prob.append(1)

    prob = prob / np.sum(prob)  # нормализация вероятностей

    crossover_point = np.random.choice(np.arange(1, parent1.size), p=prob)

    child = parent1.points[:crossover_point]
    child += [point for point in parent2.points if point not in child]
    return Route(child)


def inversion_mutation(route):
    # Select two random indices for the inversion mutation
    idx1, idx2 = sorted(sample(range(route.size), 2))

    inverse_route = route.points[:idx1] + route.points[idx1:idx2][::-1] + route.points[idx2:]
    route.set_points(inverse_route)


def rgibnnm_mutation(route, matrix):
    # Select a random gene
    random_gene_idx = randint(0, route.size - 1)

    # Find the nearest neighbor
    distances = matrix[random_gene_idx]
    nearest_neighbor = np.argmin(
        [distances[i] if i != random_gene_idx else float('inf') for i in range(len(distances))])

    # Select a random neighbor of the nearest neighbor within a range (using modulo for wraparound)
    neighbors = range(max(0, nearest_neighbor - 5), min(route.size, nearest_neighbor + 6))
    swap_with = choice([route.points[n] for n in neighbors if n != random_gene_idx])

    # Swap random idx point and his nearest neighbor
    swap_with_idx = route.points.index(swap_with)
    new_route = route.points[:]
    new_route[random_gene_idx], new_route[swap_with_idx] = new_route[swap_with_idx], new_route[random_gene_idx]
    route.set_points(new_route)


# Мутация маршрута - Random Gene Inserted beside Nearest Neighbor Mutation
def hybrid_mutation(route, matrix):
    inversion_mutation(route)
    return rgibnnm_mutation(route, matrix)


def simple_mutation(route, rate):
    new_route = route.points[:]
    for i in range(1, route.size - 2):  # убираем первую и последнюю точки из отрезков доступных для мутации
        if np.random.rand() < rate:  # элемент случайности
            j = np.random.randint(i + 1, route.size - 1)
            new_route[i:j + 1] = new_route[i:j + 1][::-1]  # смена отрезков из точек в маршруте
    route.set_points(new_route)


def create_offspring(parents, matrix):
    parent1, parent2 = parents[:2]
    offspring = crossover(parent1, parent2, matrix)
    hybrid_mutation(offspring, matrix)
    # simple_mutation(offspring, 0.1)
    return offspring


def reorder_to_start_point(route, point):
    index = route.points.index(point)
    new_route = route.points[index:] + route.points[:index]
    route.set_points(new_route)


def genetic_algorithm(population_size, generations, points, matrix):
    start_point = points[0]
    population = generate_initial_population(population_size, points=points)

    for _ in tqdm(range(generations), desc="Genetic Algorithm Progress"):
        # Значения приспособленности поколения в полуляции
        fitness_values = [fitness(route, matrix) for route in population]

        best_routes = select_best(population, fitness_values, num_best=2)

        new_population = best_routes
        while len(new_population) < population_size:
            offspring = create_offspring(best_routes, matrix)
            new_population.append(offspring)

        population = new_population

    # Найденный оптимальный маршрут, выбор первого из списка популяции
    [route] = select_best(population, fitness_values, num_best=1)
    reorder_to_start_point(route, start_point)
    return route


if __name__ == "__main__":
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'input_dir': "../public/test_routes/",
        'output_dir': "../public/result_routes/",
        'file': '10_ex_1.csv'
    }

    distance_matrix, city_points, input_csv, output_csv, G = get_meta_data(config, config['file'])

    best_route = genetic_algorithm(population_size=10, generations=100, points=city_points, matrix=distance_matrix)
    print("\nОптимальный маршрут готов")

    best_route.calculate_length_G(G)
    print("\n----------------")
    print("\tДлина, км:\t\t\t\t\t\t", best_route.length)
    print("\tПоследовательность, osmnx ids:\t", best_route)

    reorder_save_to_csv(input_csv, output_csv, best_route)
    print("Сохранено в файл:\t\t\t\t", output_csv)
