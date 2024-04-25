import numpy as np
from tqdm import tqdm

from algorithms.graph_algorithms import calculate_distance


def set_node_all_point_list(lst, G):
    for point in lst:
        point.set_node_id_from_G(G)


def precompute_distances(G, points):
    num_points = len(points)
    distances = np.zeros((num_points, num_points))

    for it in tqdm(range(len(points)), desc="Precompute Progress"):
        points[it].set_it(it)
        for j in range(it + 1, num_points):  # Fill only the upper triangular part
            distances[it, j] = calculate_distance(points[it].node_id, points[j].node_id, G)
            distances[j, it] = distances[it, j]
    return distances