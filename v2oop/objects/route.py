import networkx as nx
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

    def calculate_length_M(self, matrix):
        distance_bw_points = [
            matrix[self.points[i].it, self.points[i + 1].it]
            for i in range(self.size - 1)
        ]
        self.set_length(np.sum(distance_bw_points))

    def calculate_length_G(self, G):
        R = [p.node_id for p in self.points]

        distance_bw_points = [
            nx.shortest_path_length(G, source=R[i], target=R[i + 1])
            for i in range(self.size - 1)
        ]
        distance_bw_points.append(nx.shortest_path_length(G, source=R[-1], target=R[0]))
        return round(np.sum(distance_bw_points))
        self.set_length(round(np.sum(distance_bw_points)))
