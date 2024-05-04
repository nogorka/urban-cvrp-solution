import networkx as nx
import numpy as np

from v3_cvrp.graph import get_distance_from_matrix


class Route:
    def __init__(self, points):
        self.points = points[:]
        self.size = len(points)
        self.length = None
        self.demand = None

    def __str__(self):
        return str(self.points)

    def __repr__(self):
        return str(self.points)

    def set_points(self, points):
        self.points = points

    def set_length(self, length):
        self.length = length

    def set_demand(self, demand):
        self.demand = demand

    def calculate_length_M(self, matrix):
        distance_bw_points = [
            matrix[self.points[i].it, self.points[i + 1].it]
            for i in range(self.size - 1)
        ]
        self.set_length(np.sum(distance_bw_points))
        return self.length

    def calculate_length_M_G(self, matrix, G):
        distance_bw_points = [
            get_distance_from_matrix(matrix, self.points[i], self.points[i + 1], G)
            for i in range(self.size - 1)
        ]
        self.set_length(np.sum(distance_bw_points))
        return self.length

    def calculate_length_G(self, G):
        R = [p.node_id for p in self.points]

        distance_bw_points = [
            nx.shortest_path_length(G, source=R[i], target=R[i + 1])
            for i in range(self.size - 1)
        ]
        distance_bw_points.append(nx.shortest_path_length(G, source=R[-1], target=R[0]))
        self.set_length(round(np.sum(distance_bw_points)))
        return self.length

    def calculate_demand(self):
        total_demand = np.sum([p.demand for p in self.points])
        self.set_demand(total_demand)
        return total_demand

    def add_point(self, point):
        self.points.append(point)
        self.size = len(self.points)

    def pop_point(self, index=-1):
        point = self.points.pop(index)
        self.size = len(self.points)
        return point

    def get_point(self, index=-1):
        return self.points[index]
