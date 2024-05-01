import networkx as nx
import numpy as np
from multiprocessing import Pool

from algorithms.graph_algorithms import read_graph


def calculate_all_pairs_shortest_paths(G):
    # Calculate shortest path distances between all pairs of nodes
    return dict(nx.all_pairs_dijkstra_path_length(G))


def calculate_reach_for_node(args):
    v, shortest_paths = args
    max_reach = 0
    for s in shortest_paths:
        for t in shortest_paths:
            if s != t != v:
                ds_v = shortest_paths[s].get(v, float('inf'))
                dv_t = shortest_paths[v].get(t, float('inf'))
                ds_t = shortest_paths[s].get(t, float('inf'))
                reach_val = ds_v + dv_t - ds_t
                max_reach = max(max_reach, reach_val)
    return (v, max_reach)


def calculate_reach(G):
    shortest_paths = calculate_all_pairs_shortest_paths(G)
    with Pool() as pool:
        results = pool.map(calculate_reach_for_node, [(v, shortest_paths) for v in G.nodes()])
    return dict(results)


def create_distance_matrix(G, reach):
    nodes = list(G.nodes())
    size = len(nodes)
    dist_matrix = np.full((size, size), np.inf)
    shortest_paths = calculate_all_pairs_shortest_paths(G)
    for i, u in enumerate(nodes):
        for j, v in enumerate(nodes):
            if i != j:
                path_length = shortest_paths[u].get(v, float('inf'))
                if path_length <= reach[u] + reach[v]:  # Simplified check for inclusion in the matrix
                    dist_matrix[i, j] = path_length
    return dist_matrix


if __name__ == '__main__':
    graph_filename = "../public/road_network_graph.pickle"

    # Usage example (to be run in an environment where the graph is defined and multiprocessing is feasible):
    G = nx.Graph(read_graph(graph_filename))

    reach = calculate_reach(G)
    matrix = create_distance_matrix(G, reach)

    print(reach, matrix)