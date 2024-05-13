from algorithms.graph_algorithms import get_graph, optimize_graph_nx
from v2oop.graph import precompute_distances, set_node_all_point_list
from v2oop.preprocess import convert_req_points_to_ga_points, convert_individual_to_json_obj_based
from v3_cvrp.genetic_algorithm_cvrp import genetic_algorithm


def ga(points, config, settings):
    city_graph = get_graph(config['city_name'], config['graph_filename'])
    graph_nx = optimize_graph_nx(city_graph)

    city_points = convert_req_points_to_ga_points(points)
    set_node_all_point_list(city_points, city_graph)

    distance_matrix = precompute_distances(graph_nx, city_points)
    best_route = genetic_algorithm(points=city_points, matrix=distance_matrix,
                                   capacity=config['vehicle_capacity'], tuning=settings)

    return convert_individual_to_json_obj_based(best_route, points)
