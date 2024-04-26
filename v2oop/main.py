import os
from algorithms.graph_algorithms import get_graph, optimize_graph_nx
from preprocessing.input_preprocess import get_all_filenames
from v2oop.genetic_algorithm_v2 import genetic_algorithm
from v2oop.graph import set_node_all_point_list, precompute_distances
from v2oop.preprocess import read_csv_to_point_list, reorder_save_to_csv

if __name__ == '__main__':
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'input_dir': "../public/example_routes/",
        'output_dir': "../public/result_routes/",
    }

    city_graph = get_graph(config['city_name'], config['graph_filename'])
    graph_nx = optimize_graph_nx(city_graph)

    filenames = get_all_filenames(config['input_dir'])
    for file in filenames:
        input_csv = os.path.join(config['input_dir'], file)
        output_csv = os.path.join(config['output_dir'], file)

        points = read_csv_to_point_list(input_csv)
        set_node_all_point_list(points, city_graph)

        distance_matrix = precompute_distances(graph_nx, points)

        best_route = genetic_algorithm(population_size=10, generations=10, points=points, matrix=distance_matrix)
        reorder_save_to_csv(input_csv, output_csv, best_route)
        print(f"Сохранено в файл: {output_csv}")
