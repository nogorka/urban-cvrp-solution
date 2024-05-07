# если машина загружена больше чем возможно или почти не загружена, то штрафуем иначе штраф 0
def calculate_capacity_penalty(individual, vehicle_capacity,
                               over_penalty_rate=0.8, under_penalty_rate=0.5, penalty_weight=3):
    penalty = 0
    for route in individual.routes:
        route_demand = route.calculate_demand()
        if route_demand > vehicle_capacity:
            excess = route_demand - vehicle_capacity
            penalty += (excess / vehicle_capacity) ** over_penalty_rate
        elif route_demand < vehicle_capacity:
            shortage = vehicle_capacity - route_demand
            penalty += (shortage / vehicle_capacity) ** under_penalty_rate
    return penalty * penalty_weight


def calculate_route_compactness_bonus(individual, matrix,
                                      bonus_rate=0.2, bonus_weight=1, desired_threshold=250000):
    bonus = 0
    for route in individual.routes:
        distance = route.calculate_length_M(matrix)
        if distance < desired_threshold:
            bonus += bonus_weight
    return bonus * bonus_rate


def fitness(individual, matrix, vehicle_capacity):
    if not individual.routes:
        return float('inf')

    total_distance = individual.calculate_distance(matrix)
    capacity_penalty = calculate_capacity_penalty(individual, vehicle_capacity)
    compactness_bonus = calculate_route_compactness_bonus(individual, matrix)

    # print(1 / total_distance, capacity_penalty, compactness_bonus)
    fitness_value = (1 / total_distance) * (capacity_penalty - compactness_bonus)
    return fitness_value
