
from deap import base, creator, tools, algorithms
import random
import numpy as np

# Problem specifics
VEHICLE_CAPACITY = 100  # Example capacity
DISTANCES = np.array([
    [0, 2, 3, 2, 3],
    [2, 0, 4, 1, 3],
    [3, 4, 0, 5, 2],
    [2, 1, 5, 0, 3],
    [3, 3, 2, 3, 0]
])  # Example symmetric distance matrix for 5 nodes (depot + 4 customers)

# Define a fitness function to minimize the total distance while respecting vehicle capacity constraints
def evaluate(individual):
    total_distance = 0
    current_load = 0
    current_route_distance = 0
    last_customer = individual[0]
    
    for customer in individual:
        current_load += 1  # Simplified load, replace with actual demands
        current_route_distance += DISTANCES[last_customer][customer]
        if current_load > VEHICLE_CAPACITY:
            return (float('inf'),)  # Invalid route due to capacity constraint
        last_customer = customer
        
    total_distance += current_route_distance + DISTANCES[customer][individual[0]]  # Return to depot
    return (total_distance,)

# Setting up the DEAP framework
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("indices", random.sample, range(len(DISTANCES)), len(DISTANCES))
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("mate", tools.cxOrdered)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)

# Run the genetic algorithm
def run_ga():
    pop = toolbox.population(n=50)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)
    
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=40, 
                                   stats=stats, halloffame=hof, verbose=True)
    return pop, log, hof

# This line is commented out to prevent automatic execution; uncomment to run the algorithm
# run_ga()
