import numpy as np


class Individual:
    def __init__(self):
        self.routes = []
        self.distance = 0
        self.size = len(self.routes)

    def __str__(self):
        return str(self.routes)

    def __repr__(self):
        return f'Individual of size {len(self.routes)}: {self.routes}'

    def add_route(self, route):
        self.routes.append(route)
        self.size = len(self.routes)

    def calculate_distance(self, matrix):
        self.distance = np.sum([route.calculate_length_M(matrix) for route in self.routes])
        return self.distance
