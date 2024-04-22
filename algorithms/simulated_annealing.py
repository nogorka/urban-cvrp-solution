import random
import math


def distance_matrix(nodes):
    names = list(nodes.keys())
    distances = {}
    for key1, coord1 in nodes.items():
        for key2, coord2 in nodes.items():
            if key1 not in distances:
                distances[key1] = {}
            distances[key1][key2] = math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)
    return distances, names


def simulated_annealing(dist_matrix, node_keys, initial_temp, cooling_rate, min_temp):
    current_solution = random.sample(node_keys, len(node_keys))
    current_cost = path_cost(current_solution, dist_matrix)

    temperature = initial_temp
    while temperature > min_temp:
        new_solution = neighbour_solution(current_solution)
        new_cost = path_cost(new_solution, dist_matrix)

        if new_cost < current_cost or random.uniform(0, 1) < math.exp((current_cost - new_cost) / temperature):
            current_solution, current_cost = new_solution, new_cost

        temperature *= cooling_rate

    return current_solution, current_cost


def neighbour_solution(solution):
    idx1, idx2 = random.sample(range(len(solution)), 2)
    solution[idx1], solution[idx2] = solution[idx2], solution[idx1]
    return solution


def path_cost(solution, dist_matrix):
    cost = 0
    for i in range(len(solution) - 1):
        cost += dist_matrix[solution[i]][solution[i + 1]]
    cost += dist_matrix[solution[-1]][solution[0]]  # Return to the start
    return cost


if __name__ == "__main__":
    # Example set of cities (could be latitude, longitude)
    cities = {
        'A': (0, 0),
        'B': (1, 3),
        'C': (4, 3),
        'D': (5, 1),
        'E': (7, 5)
    }

    dist_matrix, city_names = distance_matrix(cities)

    best_solution, best_cost = simulated_annealing(dist_matrix,
                                                   city_names,
                                                   initial_temp=1000,
                                                   cooling_rate=0.995,
                                                   min_temp=1)
    print("Best path:", best_solution)
    print("Cost of the best path:", best_cost)
