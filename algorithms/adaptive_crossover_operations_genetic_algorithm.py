import random
import numpy as np
import operator
import pandas as pd

from algorithms.graph_algorithms import get_graph, get_node_all, optimize_graph_nx, precompute_distances
from preprocessing.input_preprocess import read_csv_to_dict


class City:
    def __init__(self, node_id, coords):
        self.node_id = node_id
        self.coords = coords  # coords is a tuple (x, y)

    def distance(self, other, distance_matrix):
        return distance_matrix[self.node_id][other.node_id]

    def __repr__(self):
        return f"Node({self.node_id}) at {self.coords}"


class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.fitness = 0.0

    def routeDistance(self, distance_matrix):
        if self.distance == 0:
            pathDistance = 0
            for i in range(len(self.route)):
                fromCity = self.route[i]
                toCity = self.route[(i + 1) % len(self.route)]
                pathDistance += fromCity.distance(toCity, distance_matrix)
            self.distance = pathDistance
        return self.distance

    def routeFitness(self, distance_matrix):
        if self.fitness == 0:
            self.fitness = 1 / float(self.routeDistance(distance_matrix))
        return self.fitness


def createRoute(node_points):
    return random.sample(node_points, len(node_points))


def initialPopulation(popSize, node_points):
    population = []
    for i in range(0, popSize):
        population.append(createRoute(node_points))
    return population


def rankRoutes(population, distance_matrix):
    fitnessResults = {}
    for i in range(len(population)):
        fitnessResults[i] = Fitness(population[i]).routeFitness(distance_matrix)
    return sorted(fitnessResults.items(), key=operator.itemgetter(1), reverse=True)


def selection(popRanked, eliteSize):
    selectionResults = []
    df = pd.DataFrame(np.array(popRanked), columns=["Index", "Fitness"])
    df['cum_sum'] = df.Fitness.cumsum()
    df['cum_perc'] = 100 * df.cum_sum / df.Fitness.sum()

    for i in range(0, eliteSize):
        selectionResults.append(popRanked[i][0])
    for i in range(0, len(popRanked) - eliteSize):
        pick = 100 * random.random()
        for i in range(len(popRanked)):
            if pick <= df.iat[i, 3]:
                selectionResults.append(popRanked[i][0])
                break
    return selectionResults


def matingPool(population, selectionResults):
    matingpool = []
    for i in range(len(selectionResults)):
        index = selectionResults[i]
        matingpool.append(population[index])
    return matingpool


def breed(parent1, parent2):
    child = []
    childP1 = []
    childP2 = []

    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))

    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        childP1.append(parent1[i])

    childP2 = [item for item in parent2 if item not in childP1]

    child = childP1 + childP2
    return child


def breedPopulation(matingpool, eliteSize):
    children = []
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool))

    for i in range(eliteSize):
        children.append(matingpool[i])

    for i in range(length):
        child = breed(pool[i], pool[len(matingpool) - i - 1])
        children.append(child)
    return children


def mutate(individual, mutationRate):
    for swapped in range(len(individual)):
        if random.random() < mutationRate:
            swapWith = int(random.random() * len(individual))

            city1 = individual[swapped]
            city2 = individual[swapWith]

            individual[swapped] = city2
            individual[swapWith] = city1
    return individual


def mutatePopulation(population, mutationRate):
    mutatedPop = []

    for ind in range(len(population)):
        mutatedInd = mutate(population[ind], mutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop


def nextGeneration(currentGen, eliteSize, mutationRate, distance_matrix):
    popRanked = rankRoutes(currentGen, distance_matrix)
    selectionResults = selection(popRanked, eliteSize)
    matingpool = matingPool(currentGen, selectionResults)
    children = breedPopulation(matingpool, eliteSize)
    nextGeneration = mutatePopulation(children, mutationRate)
    return nextGeneration


def geneticAlgorithm(distance_matrix, city_list, popSize, eliteSize, mutationRate, generations):
    pop = initialPopulation(popSize, city_list)
    # print("Initial best distance: " + str(1 / rankRoutes(pop, distance_matrix)[0][1]))

    for i in range(generations):
        pop = nextGeneration(pop, eliteSize, mutationRate, distance_matrix)
        # print("Best distance in generation", i + 1, ":", str(1 / rankRoutes(pop, distance_matrix)[0][1]))

    bestRouteIndex = rankRoutes(pop, distance_matrix)[0][0]
    bestRoute = pop[bestRouteIndex]
    return bestRoute


def matrix_to_dict_with_keys(matrix, ind_dct):
    distance_dict = {}
    keys = list(ind_dct.keys())
    for i in range(matrix.shape[0]):
        row_dict = {}
        for j in range(matrix.shape[1]):
            row_dict[keys[j]] = matrix[i, j]
        distance_dict[keys[i]] = row_dict
    return distance_dict


if __name__ == "__main__":
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'data_type': 'dict',
        'input_csv': '../public/example_routes/10_ex_1.csv',
        'output_csv': '../public/result_routes/10_ex_1.csv',
    }

    city_graph = get_graph(config['city_name'], config['graph_filename'])
    points = read_csv_to_dict(config['input_csv'])
    node_points = get_node_all(points, city_graph)
    graph_nx = optimize_graph_nx(city_graph, node_points, config['data_type'])

    distance_matrix, point_index_dict = precompute_distances(graph_nx, node_points, config['data_type'])

    # required transformations
    city_list = [City(ox_id, node_data['coords']) for ox_id, node_data in node_points.items()]
    distance_matrix = matrix_to_dict_with_keys(distance_matrix, point_index_dict)

    bestRoute = geneticAlgorithm(distance_matrix, city_list, popSize=10, eliteSize=2, mutationRate=0.01, generations=10)
    route = [node.node_id for node in bestRoute]
    print("Best route found:", bestRoute, "\n", route)
