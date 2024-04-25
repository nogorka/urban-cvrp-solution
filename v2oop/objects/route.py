from random import randint, sample


class Route:
    def __init__(self, points):
        self.points = points[:]
        self.len = len(points)

    def __str__(self):
        return str(self.points)

    def __repr__(self):
        return str(self.points)

    def set_points(self, points):
        self.points = points

    def create_random_specimen(self):
        self.set_points(sample(self.points, self.len))

    def create_nn_dependant_specimens(self, matrix):
        start_index = randint(0, self.len - 1)
        route = [self.points[start_index]]
        visited = {start_index}

        current_index = start_index
        for _ in range(1, self.len):
            next_index = min((idx for idx in range(self.len) if idx not in visited),
                             key=lambda idx: matrix[current_index][idx])
            visited.add(next_index)
            route.append(self.points[next_index])
            current_index = next_index

        self.set_points(route)
