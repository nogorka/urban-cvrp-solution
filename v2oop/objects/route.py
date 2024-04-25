import numpy as np


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

    def calculate_length(self, matrix):
        distance_bw_points = [
            matrix[self.points[i].it, self.points[i+1].it]
            for i in range(self.size - 1)
        ]
        self.set_length(np.sum(distance_bw_points))

