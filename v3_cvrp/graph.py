import os

import numpy as np
from tqdm import tqdm

from algorithms.graph_algorithms import get_graph, optimize_graph_nx, calculate_distance
from v2oop.graph import set_node_all_point_list
from v2oop.preprocess import read_csv_to_point_list
from v2oop.utils import fill_nn_matrix


def precompute_distances_nn_based(G, points, nn_matrix, num_neighbors=5):
    num_points = len(points)
    distances = np.zeros((num_points, num_points))

    for it in tqdm(range(len(points)), desc="Precompute Progress"):
        points[it].set_it(it)

        closest_neighbors_all = [(i, neighbor) for i, neighbor in enumerate(nn_matrix[it])]
        closest_neighbors = sorted(closest_neighbors_all, key=lambda x: x[1])[1:num_neighbors + 1]

        for n_index, _ in closest_neighbors:
            if distances[it, n_index] == 0:  # If not already computed
                distances[it, n_index] = calculate_distance(points[it].node_id, points[n_index].node_id, G)
                distances[n_index, it] = distances[it, n_index]
    return distances


def calc_dist(matrix, p1, p2, G):
    distance = calculate_distance(p1.node_id, p2.node_id, G)
    matrix[p1.it, p2.it] = distance
    matrix[p2.it, p1.it] = distance
    return distance


def get_distance_from_matrix(matrix, p1, p2, G):
    distance = matrix[p1.it][p2.it]
    if distance == 0:
        distance = calc_dist(matrix, p1, p2, G)
    return distance


if __name__ == "__main__":
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'input_dir': "../public/",
        'output_dir': "../public/result_routes/",
        'file': '50_ex.csv',
        'vehicle_capacity': 1000,
    }

    input_csv = os.path.join(config['input_dir'], config['file'])

    city_graph = get_graph(config['city_name'], config['graph_filename'])
    graph_nx = optimize_graph_nx(city_graph)

    city_points = read_csv_to_point_list(input_csv)
    set_node_all_point_list(city_points, city_graph)

    nn_matrix = fill_nn_matrix(city_points)
    print(nn_matrix[0][0])
    distance_matrix = precompute_distances_nn_based(graph_nx, city_points, nn_matrix)
