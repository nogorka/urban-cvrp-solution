# если машина загружена больше чем возможно или почти не загружена, то штрафуем иначе штраф 0
def calculate_capacity_penalty(individual, vehicle_capacity, tuning=None):
    if tuning is None:
        tuning = {}
    over_penalty_rate = tuning.get('over_penalty_rate', 0.8)
    under_penalty_rate = tuning.get('under_penalty_rate', 0.5)
    penalty_weight = tuning.get('penalty_weight', 3)

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


def calculate_route_compactness_bonus(individual, matrix, tuning=None):
    if tuning is None:
        tuning = {}
    bonus_rate = tuning.get('bonus_rate', 1)
    bonus_weight = tuning.get('bonus_weight', 0.2)
    desired_threshold = tuning.get('desired_threshold', 2.7e5)

    bonus = 0
    for route in individual.routes:
        distance = route.calculate_length_M(matrix)
        if distance < desired_threshold:
            bonus += bonus_rate
    return bonus * bonus_weight


def fitness(individual, matrix, vehicle_capacity, tuning):
    if not individual.routes:
        return float('inf')

    total_distance = individual.calculate_distance(matrix)
    capacity_penalty = calculate_capacity_penalty(individual, vehicle_capacity, tuning)
    compactness_bonus = calculate_route_compactness_bonus(individual, matrix, tuning)

    # print(1 / total_distance, capacity_penalty, compactness_bonus)
    fitness_value = (1 / total_distance) * (capacity_penalty - compactness_bonus)
    return fitness_value
