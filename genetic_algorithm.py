import numpy as np
import random
import csv
import pandas as pd
from tqdm import tqdm
from geopy.distance import geodesic


# Чтение точек и преобразование к формату работы { 'id': (lat, long), ....}
def read_csv_to_dict(file_path):
    data_dict = {}

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Преобразуем значения широты и долготы в кортеж
            data_dict[row['id']] = (float(row['lat']), float(row['long']))

    return data_dict

# Сопоставлении ключей и переупорядочивания строк в DataFrame
def reorder_csv(input_csv, output_csv, keys):
    df = pd.read_csv(input_csv)
    df['id'] = df['id'].astype(str)
    df_selected = df[df['id'].isin(keys)]
    df_reordered = df_selected.set_index('id').loc[keys].reset_index()
    df_reordered.to_csv(output_csv, index=False)


# Генерация начальной популяции, где одна особь это рандомный маршрут
def generate_initial_population(population_size, points):
    population = []
    for _ in range(population_size):
        route = list(points.keys())
        np.random.shuffle(route)
        population.append(route)
    return population

# Вычисление расстояния между двумя точками (Евклидово, по прямой)
def distance_euclid(point1, point2, points):
    x1, y1 = points[point1]
    x2, y2 = points[point2]
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Вычисление расстояния между двумя точками (Манхэтанское, гор. кварталы)
def distance_manhattan(point1, point2, points):
    x1, y1 = points[point1]
    x2, y2 = points[point2]
    return np.abs(x2 - x1) + np.abs(y2 - y1)

# Вычисление приспособленности маршрута (меньше значение - лучше)
def fitness(route, points):
    total_distance = 0
    for i in range(len(route) - 1):
        # расстояние соседних точек
        # total_distance += distance_euclid(route[i], route[i + 1], points)
        # total_distance += distance_manhattan(route[i], route[i + 1], points)
        point1 = points[route[i]]
        point2 = points[route[i + 1]]
        total_distance += geodesic(point1, point2).kilometers

    return 1 / total_distance

# Скрещивание двух маршрутов, ребенок это часть родителя те маршрута 1 и маршрута 2 (родителя)
def crossover(parent1, parent2):
    crossover_point = np.random.randint(1, len(parent1) - 1)
    child = parent1[:crossover_point]
    child += [point for point in parent2 if point not in child]
    return child

# Мутация маршрута (случайное изменение маршрута)
def mutate(route, mutation_rate):
    for i in range(len(route)):
        if np.random.rand() < mutation_rate: # элемент случайности
            j = np.random.randint(len(route))
            route[i], route[j] = route[j], route[i] # смена мест точек в маршруте
    return route

# Выбор лучших маршрутов
def select_best(population, fitness_values, num_best):
    # сортировка в порядке убывания по значению приспособленности
    indices = np.argsort(fitness_values)[-num_best:]
    return [population[i] for i in indices]

def genetic_algorithm(population_size, generations, mutation_rate, points):
    population = generate_initial_population(population_size, points)

    for generation in tqdm(range(generations), desc="Genetic Algorithm Progress"):
        # Значения приспособленности поколения в полуляции
        fitness_values = [fitness(route, points) for route in population]

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
    input_csv = 'public/15_ex.csv'
    output_csv = 'public/output_ordered_points.csv'

    points = read_csv_to_dict(input_csv)
    best_route = genetic_algorithm(population_size=60, generations=1600, mutation_rate=0.1, points=points)
    print("\nОптимальный маршрут готов")

    reorder_csv(input_csv, output_csv, best_route)
