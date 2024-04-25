import numpy as np
from geopy.distance import geodesic
from tqdm import tqdm


def calculate_distance_geo(point1, point2):
    return geodesic((point1.lat, point1.long), (point2.lat, point2.long)).kilometers


def fill_nn_matrix(points):
    num_points = len(points)
    distances = np.zeros((num_points, num_points))

    # Fill only the upper triangular part because matrix is symmetric
    for it in tqdm(range(len(points)), desc="Geo distance matrix Progress"):
        for j in range(it + 1, num_points):
            distances[it, j] = calculate_distance_geo(points[it], points[j])
            distances[j, it] = distances[it, j]
    return distances


def get_distance_from_matrix(point1, point2, matrix):
    return matrix[point1.it, point2.it]
