import time

from tqdm import tqdm

from v2oop.genetic_algorithm_tsp import select_best
from v2oop.preprocess import get_meta_data, convert_route_to_obj, save_json
from v2oop.utils import fill_nn_matrix
from v3_cvrp.crossover import crossover
from v3_cvrp.graph import precompute_distances_nn_based
from v3_cvrp.initial_population import generate_initial_population
from v3_cvrp.mutation import hybrid_mutation


# если машина загружена больше чем возможно или почти не занружена то штрафуем иначе штраф 0
def calculate_capacity_penalty(individual, vehicle_capacity,
                               over_penalty_rate=0.8, under_penalty_rate=0.5, penalty_weight=3):
    penalty = 0
    for route in individual.routes:
        route_demand = route.calculate_demand()
        if route_demand > vehicle_capacity:
            excess = route_demand - vehicle_capacity
            penalty += (excess / vehicle_capacity) ** over_penalty_rate
        elif route_demand < vehicle_capacity:
            shortage = vehicle_capacity - route_demand
            penalty += (shortage / vehicle_capacity) ** under_penalty_rate
    return penalty * penalty_weight


def calculate_route_compactness_bonus(individual, matrix, G,
                                      bonus_rate=0.2, bonus_weight=1, desired_threshold=250000):
    bonus = 0
    for route in individual.routes:
        distance = route.calculate_length_M_G(matrix, G)
        if distance < desired_threshold:
            bonus += bonus_weight
    return bonus * bonus_rate


def fitness(individual, matrix, vehicle_capacity, G):
    if not individual.routes:
        return float('inf')

    total_distance = individual.calculate_distance(matrix, G)
    capacity_penalty = calculate_capacity_penalty(individual, vehicle_capacity)
    compactness_bonus = calculate_route_compactness_bonus(individual, matrix, G)

    # print(1 / total_distance, capacity_penalty, compactness_bonus)
    fitness_value = (1 / total_distance) * (capacity_penalty - compactness_bonus)
    return fitness_value


def create_offspring(parents, matrix, vehicle_capacity, depot):
    parent1, parent2 = parents[:2]
    offspring = crossover(parent1, parent2, matrix, vehicle_capacity, depot)
    hybrid_mutation(offspring, vehicle_capacity, mutation_rate=0.1)
    return offspring


def genetic_algorithm(population_size, generations, points, matrix, capacity, G, nn_matrix):
    start_point = points[0]
    population = generate_initial_population(population_size, points, capacity, start_point)

    for _ in tqdm(range(generations), desc="Genetic Algorithm Progress"):
        # Значения приспособленности поколения в полуляции
        fitness_values = [fitness(route, matrix, capacity, G) for route in population]

        best_routes = select_best(population, fitness_values, num_best=2)

        new_population = best_routes
        while len(new_population) < population_size:
            offspring = create_offspring(best_routes, nn_matrix, capacity, start_point)
            new_population.append(offspring)

        population = new_population

    # Найденный оптимальный маршрут, выбор первого из списка популяции
    [route] = select_best(population, fitness_values, num_best=1)
    return route


if __name__ == "__main__":
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'input_dir': "../public/example_routes/",
        'output_dir': "../public/result_routes/",
        'file': '30_ex_12.csv',
        'vehicle_capacity': 500,
        'n_targets': 30
    }

    start = time.time()
    graph_nx, city_points, input_csv, output_csv, G = get_meta_data(config, config['file'])

    nn_matrix = fill_nn_matrix(city_points)
    distance_matrix = precompute_distances_nn_based(graph_nx, city_points, nn_matrix,
                                                    num_neighbors=int(config['n_targets'] * 0.5))

    best_route = genetic_algorithm(population_size=10, generations=10, points=city_points, matrix=distance_matrix,
                                   capacity=config['vehicle_capacity'], G=graph_nx, nn_matrix=nn_matrix)

    data = convert_route_to_obj(best_route, input_csv)
    end = time.time()
    output = output_csv.replace(".csv", ".json")
    save_json(data, output)

    print("\nОптимальный маршрут готов")

    # best_route.calculate_length_G(G)
    print(f'Time: {end - start}')
    print("\n----------------")
    print("\tДлина, км:\t\t\t\t\t\t", best_route.distance)
    print("\tПоследовательность, osmnx ids:\t", best_route)
    for route in best_route.routes:
        print(f'Route distance: {route.length}')

    # reorder_save_to_csv(input_csv, output_csv, best_route)
    # print("Сохранено в файл:\t\t\t\t", output_csv)
