from algorithms.graph_algorithms import get_graph, optimize_graph_nx
from preprocessing.input_preprocess import get_all_filenames
from v2oop.graph import set_node_all_point_list, precompute_distances
from v2oop.preprocess import read_csv_to_point_list

if __name__ == '__main__':
    city_name = "Saint Petersburg, Russia"
    graph_filename = "../public/road_network_graph.pickle"

    city_graph = get_graph(city_name, graph_filename)
    graph_nx = optimize_graph_nx(city_graph)

    filenames = get_all_filenames("public/example_routes")
    for file in filenames:

        input_csv = f'../public/example_routes/{file}'
        output_csv = f'../public/result_routes/{file}'

        points = read_csv_to_point_list(input_csv)
        set_node_all_point_list(points, city_graph)

        distance_matrix = precompute_distances(graph_nx, points)

