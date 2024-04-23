import random
import math
from algorithms.graph_algorithms import precompute_distances, get_graph, set_node_strct_all, get_node_all, \
    optimize_graph_nx
from preprocessing.input_preprocess import read_csv_to_strct, read_csv_to_dict, reorder_csv


def simulated_annealing(dist_matrix, node_index_keys, initial_temp, cooling_rate, min_temp):
    current_solution = random.sample(list(node_index_keys.keys()), len(node_index_keys.keys()))
    current_cost = path_cost(current_solution, dist_matrix, node_index_keys)

    temperature = initial_temp
    while temperature > min_temp:
        new_solution = neighbour_solution(current_solution)
        new_cost = path_cost(new_solution, dist_matrix, node_index_keys)

        if new_cost < current_cost or random.uniform(0, 1) < math.exp((current_cost - new_cost) / temperature):
            current_solution, current_cost = new_solution, new_cost

        temperature *= cooling_rate

    return current_solution, current_cost


def neighbour_solution(solution):
    idx1, idx2 = random.sample(range(len(solution)), 2)
    solution[idx1], solution[idx2] = solution[idx2], solution[idx1]
    return solution


def path_cost(route, dist_matrix, node_index_keys):
    cost = 0
    for i in range(len(route) - 1):
        cost += get_distance(i, i+1, route, dist_matrix, node_index_keys)
    cost += get_distance(-1, 0, route, dist_matrix, node_index_keys)
    return cost


def get_distance(_from, to, route, dist_matrix, node_index_keys):
    return dist_matrix[node_index_keys[route[_from]]][node_index_keys[route[to]]]


if __name__ == "__main__":
    city_name = "Saint Petersburg, Russia"
    graph_filename = "../public/road_network_graph.pickle"
    TYPE = 'dict'
    file = '10_ex_1.csv'

    city_graph = get_graph(city_name, graph_filename)

    input_csv = f'../public/example_routes/{file}'
    output_csv = f'../public/result_routes/{file}'

    points = []
    NODE_POINTS = []
    if TYPE == 'strct':
        points = read_csv_to_strct(input_csv)
        NODE_POINTS = set_node_strct_all(points, city_graph)

    else:
        points = read_csv_to_dict(input_csv)
        NODE_POINTS = get_node_all(points, city_graph)

    graph_nx = optimize_graph_nx(city_graph, node_points=NODE_POINTS, type=TYPE)

    dist_matrix, city_names = precompute_distances(graph_nx, NODE_POINTS, TYPE)

    best_solution, best_cost = simulated_annealing(dist_matrix,
                                                   city_names,
                                                   initial_temp=1000,
                                                   cooling_rate=0.995,
                                                   min_temp=1)
    print("Best path:", best_solution)
    print("Cost of the best path:", best_cost)
