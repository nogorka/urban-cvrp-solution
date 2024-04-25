from random import randint, sample
import numpy as np

from v2oop.utils import get_distance_from_matrix


class Route:
    def __init__(self, points):
        self.points = points[:]
        self.size = len(points)
        self.length = None

    def __str__(self):
        return str(self.points)

    def __repr__(self):
        return str(self.points)

    def set_points(self, points):
        self.points = points

    def set_length(self, length):
        self.length = length

    def create_random_specimen(self):
        self.set_points(sample(self.points, self.size))

    def create_nn_dependant_specimens(self, matrix):
        start_index = randint(0, self.size - 1)
        route = [self.points[start_index]]
        visited = {start_index}

        current_index = start_index
        for _ in range(1, self.size):
            next_index = min((idx for idx in range(self.size) if idx not in visited),
                             key=lambda idx: matrix[current_index][idx])
            visited.add(next_index)
            route.append(self.points[next_index])
            current_index = next_index

        self.set_points(route)

    def calculate_length(self, matrix):
        distance_bw_points = [
            get_distance_from_matrix(self.points[i], self.points[i + 1], matrix)
            for i in range(self.size - 1)
        ]
        self.set_length(np.sum(distance_bw_points))

