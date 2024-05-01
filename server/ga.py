from algorithms.graph_algorithms import get_graph, optimize_graph_nx
from v2oop.genetic_algorithm_v2 import genetic_algorithm
from v2oop.graph import precompute_distances, set_node_all_point_list
from v2oop.preprocess import points_to_points, reorder_points_json


def ga(points, config):
    city_graph = get_graph(config['city_name'], config['graph_filename'])
    graph_nx = optimize_graph_nx(city_graph)

    city_points = points_to_points(points)
    set_node_all_point_list(city_points, city_graph)

    distance_matrix = precompute_distances(graph_nx, city_points)
    route = genetic_algorithm(population_size=10, generations=100, points=city_points, matrix=distance_matrix,
                                    capacity=config['vehicle_capacity'])

    cur_route = route[0].points
    sorted_route = reorder_points_json(points, cur_route)
    return sorted_route
