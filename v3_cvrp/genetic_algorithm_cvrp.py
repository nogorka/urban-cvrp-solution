from tqdm import tqdm

from v2oop.genetic_algorithm_tsp import select_best
from v2oop.preprocess import get_meta_data, convert_route_to_obj, save_json
from v3_cvrp.crossover import crossover
from v3_cvrp.fitness import fitness
from v3_cvrp.initial_population import generate_initial_population
from v3_cvrp.mutation import hybrid_mutation


def has_converged(history, threshold=1e-08, patience=5):
    """Check if the improvement of the best fitness value
    is less than the threshold for a number of generations"""
    if len(history) < patience + 1:
        return False
    recent_improvements = [history[i] - history[i + 1] for i in range(0, patience)]
    return all(improvement < threshold for improvement in recent_improvements)


def create_offspring(parents, matrix, vehicle_capacity, depot):
    parent1, parent2 = parents[:2]
    offspring = crossover(parent1, parent2, matrix, vehicle_capacity, depot)
    hybrid_mutation(offspring, vehicle_capacity, matrix, mutation_rate=0.1)
    return offspring


def genetic_algorithm(population_size, generations, points, matrix, capacity):
    start_point = points[0]
    population = generate_initial_population(population_size, points, capacity, start_point)

    fitness_history = []
    for _ in tqdm(range(generations), desc="Genetic Algorithm Progress"):
        # Значения приспособленности поколения в полуляции
        fitness_values = [fitness(route, matrix, capacity) for route in population]

        fitness_history.append(min(fitness_values))
        if has_converged(fitness_history):
            print("Convergence reached")
            break

        best_routes = select_best(population, fitness_values, num_best=2)

        new_population = best_routes
        while len(new_population) < population_size:
            offspring = create_offspring(best_routes, matrix, capacity, start_point)
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
        'file': '30_ex_10.csv',
        'vehicle_capacity': 1000,
    }

    distance_matrix, city_points, input_csv, output_csv, G = get_meta_data(config, config['file'])

    best_route = genetic_algorithm(population_size=10, generations=10, points=city_points, matrix=distance_matrix,
                                   capacity=config['vehicle_capacity'])

    data = convert_route_to_obj(best_route, input_csv)
    output = output_csv.replace(".csv", ".json")
    save_json(data, output)

    print("\nОптимальный маршрут готов")

    # best_route.calculate_length_G(G)
    print("\n----------------")
    print("\tДлина, км:\t\t\t\t\t\t", best_route.distance)
    print("\tПоследовательность, osmnx ids:\t", best_route)
    for route in best_route.routes:
        print(f'Route distance: {route.length}')
