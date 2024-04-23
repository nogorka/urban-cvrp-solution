import time
from algorithms.genetic_algorithm_dict import genetic_algorithm
from algorithms.graph_algorithms import get_graph, get_node_all, optimize_graph_nx, precompute_distances, \
    calculate_route_lengths
from algorithms.simulated_annealing import simulated_annealing
from evaluating_comparing.compare_routes import levenshtein_distance
from preprocessing.input_preprocess import read_csv_to_dict, reorder_csv, write_compare_csv


def main():
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'data_type': 'dict',
        'input_csv': '../public/example_routes/10_ex_1.csv',
        'output_csv': '../public/result_routes/10_ex_1.csv',
        'compare_output_csv': '../public/compare_result_routes/10_ex_1.csv',
    }

    city_graph = get_graph(config['city_name'], config['graph_filename'])
    points = read_csv_to_dict(config['input_csv'])
    node_points = get_node_all(points, city_graph)
    graph_nx = optimize_graph_nx(city_graph, node_points, config['data_type'])

    distance_matrix, point_index_dict = precompute_distances(graph_nx, node_points, config['data_type'])

    algorithms = [run_simulated_annealing, run_genetic_algorithm]
    results = {}
    for algorithm in algorithms:
        best_route, time_taken = algorithm(node_points, distance_matrix, point_index_dict)
        best_length = calculate_route_lengths(best_route, city_graph, node_points)
        method_name = algorithm.__name__.replace('run_', '').replace('_', ' ').title()
        # print_route_info(method_name, best_route, best_length, time_taken)
        results[method_name] = [best_route, best_length, time_taken]

    for it, (alg_name, (cur_route, cur_length, seconds)) in list(enumerate(results.items())):
        optimal_length = results['Simulated Annealing'][1]
        length_diff = (optimal_length - cur_length) / 1000
        results[alg_name].append(round(length_diff, 1))

        optimal_route = results['Simulated Annealing'][0]
        distance = levenshtein_distance(optimal_route, cur_route) / len(cur_route)
        reverse_distance = levenshtein_distance(optimal_route, cur_route[::-1]) / len(cur_route)

        resemble_rate = 1 - distance if distance < reverse_distance else reverse_distance
        results[alg_name].append(resemble_rate)

    write_compare_csv(config['compare_output_csv'], results)

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
    best_route = genetic_algorithm(population_size=10, generations=300, mutation_rate=0.1,
                                   NP=node_points, PID=point_index_dict, DM=distance_matrix)
    end = time.time()
    return best_route, end - start


def print_route_info(method_name, route, length, time_taken):
    print(f"\nOptimal route ready using {method_name}")
    print(f"Execution time, seconds: {time_taken}")
    print(f"Length, km: {length / 1000:.1f}")
    print(f"Sequence, osmnx ids: {route}")


if __name__ == "__main__":
    main()
