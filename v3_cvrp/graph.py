import heapq
import math
import os

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm

from algorithms.graph_algorithms import get_graph, optimize_graph_nx
from v2oop.graph import set_node_all_point_list
from v2oop.preprocess import read_csv_to_point_list


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
    print("Path from A to G:", path)

    distance = 0
    for i in range(len(path) - 1):
        distance += G[path[i]][path[i + 1]]['weight']
    return distance


def euclidean_distance(a, b):
    """Calculate the Euclidean distance between two points."""
    # return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    return math.sqrt((a['x'] - b['x']) ** 2 + (a['y'] - b['y']) ** 2)


def bidirectional_a_star(graph, start, goal):
    # Heuristic function
    # heuristic = lambda u, v: euclidean_distance(graph.nodes[u]['pos'], graph.nodes[v]['pos'])
    heuristic = lambda u, v: euclidean_distance(graph.nodes[u], graph.nodes[v])

    # Priority queues initialized
    forward_pq = [(0 + heuristic(start, goal), start, 0)]
    backward_pq = [(0 + heuristic(goal, start), goal, 0)]

    # Costs and parents
    forward_cost = {start: 0}
    backward_cost = {goal: 0}
    forward_parent = {start: None}
    backward_parent = {goal: None}

    # Visited nodes
    visited_forward = set()
    visited_backward = set()

    while forward_pq and backward_pq:
        # Forward search
        _, current, _ = heapq.heappop(forward_pq)
        if current in visited_backward:
            return reconstruct_path(forward_parent, backward_parent, current)
        visited_forward.add(current)

        for neighbor in graph.neighbors(current):
            # new_cost = forward_cost[current] + graph[current][neighbor]['weight']
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
            # new_cost = backward_cost[current] + graph[current][neighbor]['weight']
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


def test_case():
    G = nx.Graph()

    nodes = {
        'A': (1, 2), 'B': (4, 1), 'C': (2, 4), 'D': (3, 3),
        'E': (5, 5), 'F': (6, 3), 'G': (7, 2)
    }
    edges = [
        ('A', 'B', 3.5), ('A', 'C', 2.1), ('B', 'D', 1.2),
        ('C', 'D', 1.5), ('D', 'E', 2.5), ('E', 'F', 1.2),
        ('F', 'G', 2.2), ('B', 'F', 4.1)
    ]
    G.add_nodes_from(nodes.keys())
    for node, pos in nodes.items():
        G.nodes[node]['pos'] = pos
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)

    path = bidirectional_a_star(G, 'A', 'G')
    print("Path from A to G:", path)
    return path


def city_case():
    config = {
        'city_name': "Saint Petersburg, Russia",
        'graph_filename': "../public/road_network_graph.pickle",
        'input_dir': "../public/example_routes/",
        'output_dir': "../public/result_routes/",
        'file': '30_ex_10.csv',
        'vehicle_capacity': 1000,
    }

    input_csv = os.path.join(config['input_dir'], config['file'])

    city_graph = get_graph(config['city_name'], config['graph_filename'])
    graph_nx = optimize_graph_nx(city_graph)
    G = nx.Graph(city_graph)

    city_points = read_csv_to_point_list(input_csv)
    set_node_all_point_list(city_points, city_graph)

    print(city_points)

    # distance_matrix = precompute_distances(graph_nx, city_points)

    path = bidirectional_a_star(G, city_points[0].node_id, city_points[1].node_id)
    print("Path from A to G:", path)
    return path


if __name__ == "__main__":
    path = city_case()
    # path = test_case()

    # Draw the whole graph
    # pos = nx.get_node_attributes(G, 'pos')
    # nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='#909090', node_size=500)
    #
    # path_edges = list(zip(path[:-1], path[1:]))
    # nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='red')
    # nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2)
    #
    # edge_labels = nx.get_edge_attributes(G, 'weight')
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    #
    # plt.title('Path from Node A to Node G')
    # plt.show()
