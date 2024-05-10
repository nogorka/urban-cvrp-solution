import time
import networkx as nx

from algorithms.adaptive_crossover_operations_genetic_algorithm import geneticAlgorithm, matrix_to_dict_with_keys, City
from algorithms.IRGIBNNM_genetic_algorithm import genetic_algorithm as irgibnnm_genetic_algorithm
from algorithms.genetic_algorithm_dict import genetic_algorithm
from algorithms.graph_algorithms import get_graph, get_node_all, optimize_graph_nx, precompute_distances, \
    calculate_route_lengths
from algorithms.simulated_annealing import simulated_annealing
from evaluating_comparing.compare_routes import levenshtein_distance
from preprocessing.input_preprocess import read_csv_to_dict, write_compare_csv, get_all_filenames


def main():
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'data_type': 'dict',
        'input_csv': '../public/test_routes/',
        'output_csv': '../public/result_routes/',
        'compare_output_csv': '../public/compare_result_routes/',
        'batch_size': 10
    }
    algorithms = [
        run_simulated_annealing,
        run_genetic_algorithm,
        run_genetic_algorithm_adaptive_crossover,
        run_irgibnnm_genetic_algorithm,
    ]

    filenames = get_all_filenames(config['input_csv'])
    for file in filenames:
        #     file = '10_ex_1.csv'

        input_csv = config['input_csv'] + file
        compare_output_csv = config['compare_output_csv'] + file

        city_graph = get_graph(config['city_name'], config['graph_filename'])
        points = read_csv_to_dict(input_csv)
        node_points = get_node_all(points, city_graph)
        graph_nx = optimize_graph_nx(city_graph, node_points, config['data_type'])
        not_opt_graph_nx = nx.Graph(city_graph)
        distance_matrix, point_index_dict = precompute_distances(graph_nx, node_points, config['data_type'])

        results = []
        for algorithm in algorithms:
            for batch_try in range(config['batch_size']):
                best_route, time_taken = algorithm(node_points, distance_matrix, point_index_dict)
                best_length = calculate_route_lengths(best_route, not_opt_graph_nx, node_points)
                method_name = algorithm.__name__.replace('run_', '').replace('_', ' ').title()
                results.append([method_name, best_route, best_length, round(time_taken, 3), batch_try])

        for it, (method_name, cur_route, cur_length, seconds, batch) in enumerate(results):
            optimal_length = results[0][2]  # Simulated Annealing - length
            length_diff = (optimal_length - cur_length) / 1000
            results[it].append(round(length_diff, 1))

            optimal_route = results[0][1]  # Simulated Annealing - route
            distance = levenshtein_distance(optimal_route, cur_route) / len(cur_route)
            reverse_distance = levenshtein_distance(optimal_route, cur_route[::-1]) / len(cur_route)

            resemble_rate = 1 - distance if distance < reverse_distance else reverse_distance
            results[it].append(resemble_rate)

            # print_route_info(method_name, cur_route, cur_length, seconds, length_diff, resemble_rate, batch)

        write_compare_csv(compare_output_csv, results)

    # reorder_csv(config['input_csv'], config['output_csv'], best_route, config['data_type'])
    # print(f"Saved to file: {config['output_csv']}")


def run_simulated_annealing(node_points, distance_matrix, point_index_dict):
    start = time.time()
    best_solution = simulated_annealing(distance_matrix, point_index_dict,
                                        initial_temp=1000, cooling_rate=0.995, min_temp=1)
    end = time.time()
    return best_solution, end - start


def run_genetic_algorithm(node_points, distance_matrix, point_index_dict):
    start = time.time()
    best_route = genetic_algorithm(population_size=10, generations=100, mutation_rate=0.01,
                                   NP=node_points, PID=point_index_dict, DM=distance_matrix)
    end = time.time()
    return best_route, end - start


def run_genetic_algorithm_adaptive_crossover(node_points, distance_matrix, point_index_dict):
    city_list = [City(ox_id, node_data['coords']) for ox_id, node_data in node_points.items()]
    distance_matrix = matrix_to_dict_with_keys(distance_matrix, point_index_dict)

    start = time.time()
    bestRoute = geneticAlgorithm(distance_matrix, city_list,
                                 popSize=10, eliteSize=2, mutationRate=0.01, generations=100)
    end = time.time()

    route = [node.node_id for node in bestRoute]
    return route, end - start


def run_irgibnnm_genetic_algorithm(node_points, distance_matrix, point_index_dict):
    start = time.time()
    best_route = irgibnnm_genetic_algorithm(population_size=10, generations=100,
                                            NP=node_points, PID=point_index_dict, DM=distance_matrix)
    end = time.time()
    return best_route, end - start


def print_route_info(method_name, route, length, time_taken, length_diff, resemble_rate, n_try):
    print(f"\n____ using {method_name} ____")
    print(f"Execution time, seconds: {time_taken}")
    print(f"Length, km: {length / 1000:.1f}")
    print(f"Length difference, km: {length_diff}")
    print(f"Resemble rate, %: {resemble_rate * 100:.1f}")
    print(f"Sequence, osmnx ids: {route}")
    print(f"TRY: {n_try}")


if __name__ == "__main__":
    main()
