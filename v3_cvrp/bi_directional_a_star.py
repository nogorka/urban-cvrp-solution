import csv
import heapq
import math
import os
import time

import networkx as nx
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm

from algorithms.graph_algorithms import get_graph, optimize_graph_nx
from preprocessing.input_preprocess import get_all_filenames
from v2oop.graph import set_node_all_point_list
from v2oop.preprocess import read_csv_to_point_list
from v2oop.graph import precompute_distances as pre_dist


def precompute_distances(G, points):
    num_points = len(points)
    distances = np.zeros((num_points, num_points))

    for it in tqdm(range(len(points)), desc="Precompute Progress"):
        points[it].set_it(it)
        for j in range(it + 1, num_points):  # Fill only the upper triangular part
            distances[it, j] = calculate_distance(points[it].node_id, points[j].node_id, G)
            distances[j, it] = distances[it, j]
    return distances


def calculate_distance(node_id1, node_id2, G):
    path = bidirectional_a_star(G, node_id1, node_id2)
    # print("Path from A to G:", path)

    distance = 0
    for i in range(len(path) - 1):
        distance += G[path[i]][path[i + 1]]['length']
    return distance


def euclidean_distance(a, b):
    return math.sqrt((a['x'] - b['x']) ** 2 + (a['y'] - b['y']) ** 2)


def bidirectional_a_star(graph, start, goal):
    heuristic = lambda u, v: euclidean_distance(graph.nodes[u], graph.nodes[v])

    # Priority queues
    forward_pq = [(0 + heuristic(start, goal), start, 0)]
    backward_pq = [(0 + heuristic(goal, start), goal, 0)]

    forward_cost = {start: 0}
    backward_cost = {goal: 0}
    forward_parent = {start: None}
    backward_parent = {goal: None}

    visited_forward = set()
    visited_backward = set()

    while forward_pq and backward_pq:
        # Forward search
        _, current, _ = heapq.heappop(forward_pq)
        if current in visited_backward:
            return reconstruct_path(forward_parent, backward_parent, current)
        visited_forward.add(current)

        for neighbor in graph.neighbors(current):
            new_cost = forward_cost[current] + graph[current][neighbor]['length']
            if neighbor not in forward_cost or new_cost < forward_cost[neighbor]:
                forward_cost[neighbor] = new_cost
                forward_parent[neighbor] = current
                heapq.heappush(forward_pq, (new_cost + heuristic(neighbor, goal), neighbor, new_cost))

        # Backward search
        _, current, _ = heapq.heappop(backward_pq)
        if current in visited_forward:
            return reconstruct_path(forward_parent, backward_parent, current)
        visited_backward.add(current)

        for neighbor in graph.neighbors(current):
            new_cost = backward_cost[current] + graph[current][neighbor]['length']
            if neighbor not in backward_cost or new_cost < backward_cost[neighbor]:
                backward_cost[neighbor] = new_cost
                backward_parent[neighbor] = current
                heapq.heappush(backward_pq, (new_cost + heuristic(neighbor, start), neighbor, new_cost))


def reconstruct_path(forward_parent, backward_parent, meeting_point):
    path = []
    step = meeting_point
    while step is not None:
        path.append(step)
        step = forward_parent.get(step)
    path.reverse()

    step = meeting_point
    step = backward_parent.get(step)
    while step is not None:
        path.append(step)
        step = backward_parent.get(step)

    return path


def city_case(filename, config):
    input_csv = os.path.join(config['input_dir'], filename)

    city_graph = get_graph(config['city_name'], config['graph_filename'])
    graph_nx = optimize_graph_nx(city_graph)

    city_points = read_csv_to_point_list(input_csv)
    set_node_all_point_list(city_points, city_graph)

    return graph_nx, city_points


def calculate_distance_3(node1, node2, nxG):
    shortest_path = nx.astar_path(nxG, source=node1, target=node2, weight='length')
    total_distance = sum(nxG[shortest_path[i]][shortest_path[i + 1]]['length'] for i in range(len(shortest_path) - 1))
    return round(total_distance)


def score(method, G, city_points):
    start = time.time()
    _ = method(G, city_points)
    end = time.time()
    return round((end - start) * 1000)


def get_results(config):
    results = []
    for filename in get_all_filenames(config['input_dir']):
        G, city_points = city_case(filename, config)

        estimate1 = score(precompute_distances, G, city_points)
        results.append([filename, 2, estimate1])

        estimate2 = score(pre_dist, G, city_points)
        results.append([filename, 1, estimate2])
    return results


def save(results):
    out = '../public/a_star_comparing.csv'
    with open(out, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['filename', '№ directions', 'Execution Time (s)'])

        for data in results:
            [filename, directions, execution] = data
            writer.writerow([filename, directions, execution])

    print(f"\nData successfully written to {out}")


def draw_chart(data):
    df = pd.DataFrame(data, columns=['file', 'algorithm_type', 'time_ms'])

    plt.figure(figsize=(10, 6))

    subset1 = df[df['algorithm_type'] == 1]
    plt.plot(subset1['file'], subset1['time_ms'], marker='o', label='Однонаправленный A*', color='blue')

    subset2 = df[df['algorithm_type'] == 2]
    plt.plot(subset2['file'], subset2['time_ms'], marker='o', label='Двунаправленный A*', color='green')

    plt.title('Сравнение времени выполнения алгоритмов A*')
    plt.xlabel('Название файла')
    plt.ylabel('Время (мс)')
    plt.xticks(rotation=90)
    plt.legend(title='Тип алгоритма')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'input_dir': "../public/test_routes/",
        # 'output_dir': "../public/result_routes/",
        # 'file': '10_ex_1.csv',
        # 'vehicle_capacity': 1000,
    }

    results = get_results(config)
    save(results)
    print(results)

    draw_chart(results)

    # p1, p2 = city_points[0].node_id, city_points[1].node_id
    # distance = calculate_distance(p1, p2, G)
    # d2 = nx.shortest_path_length(G, p1, p2)
    # d3 = calculate_distance_3(p1, p2, G)
    # print(distance, d2, d3)

    # path = bidirectional_a_star(G, city_points[0].node_id, city_points[1].node_id)
    # print("Path from A to G:", path)