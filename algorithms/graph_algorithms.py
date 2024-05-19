import osmnx as ox
import networkx as nx
import pickle
import datetime
import os
import time
import numpy as np
from preprocessing.input_preprocess import read_csv_to_strct, read_csv_to_dict
from tqdm import tqdm


# Сопоставление гео координат узлу на графе
def get_node(coords, G):
    return ox.distance.nearest_nodes(G, X=coords[1], Y=coords[0])


def get_node_all(coords_dct, G):
    return {id: {"node": get_node(coords, G), "coords": coords}
            for (id, coords) in coords_dct.items()}


def set_node_strct_all(strct, G):
    lat_long_tuples = np.column_stack((strct['lat'], strct['long']))
    nodes = np.apply_along_axis(lambda x: get_node(tuple(x), G), 1, lat_long_tuples)
    strct['node'] = nodes
    return strct


def calculate_route_lengths(route, G, NODE_POINTS):
    R = [NODE_POINTS[ext_id]['node'] for ext_id in route]

    distance = 0
    for i in range(len(R) - 1):
        distance += nx.shortest_path_length(G, source=R[i], target=R[i+1], weight='length')
    distance += nx.shortest_path_length(G, source=R[-1], target=R[0], weight='length')
    return round(distance)


# Подсчет минимального пути по Диикстре
# def calculate_distance(node1, node2, nxG):
#     shortest_path = nx.shortest_path(nxG, source=node1, target=node2, weight='length')
#     total_distance = sum(nxG[shortest_path[i]][shortest_path[i + 1]]['length'] for i in range(len(shortest_path) - 1))
#     return round(total_distance)


def calculate_distance(node1, node2, nxG):
    shortest_path = nx.astar_path(nxG, source=node1, target=node2, weight='length')
    total_distance = sum(nxG[shortest_path[i]][shortest_path[i+1]]['length'] for i in range(len(shortest_path)-1))
    return round(total_distance)

# def calculate_distance(node1, node2, nxG):
#     shortest_path = nx.shortest_path_length(nxG, source=node1, target=node2, weight='length')
#     return round(shortest_path)

# Скачивание графа в файл
def download_graph(city_name, filename):
    print("Downloading new map data...")
    G = ox.graph_from_place(city_name, network_type="drive")
    with open(filename, 'wb') as file:
        pickle.dump(G, file)


# Чтение графа из файла
def read_graph(filename):
    with open(filename, 'rb') as file:
        G = pickle.load(file)
    return G


# Получение актуального графа
def get_graph(city_name, filename):
    # если файл графа уже существует и ему меньше суток - читаем готовый файл
    if os.path.exists(filename):
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
        current_time = datetime.datetime.now()

        if (current_time - mod_time).days == 0:
            return read_graph(filename)

    # иначе заново скачиваем граф в файл и читаем
    download_graph(city_name, filename)
    return read_graph(filename)


def optimize_graph_nx(city_graph, node_points={}, type='strct'):
    # TODO: seems to be unfinished code
    # if type == 'strct':
    #     nodes = node_points['node']
    # else:
    #     nodes = [dct['node'] for dct in node_points.values()]

    G = nx.Graph(city_graph)
    G = nx.minimum_spanning_tree(G)
    return G


# Вычисление матрицы расстояний всех точек со всеми,
# считается диагональ, заполняется полностью
def precompute_distances(graph_nx, NODE_POINTS, type='strct'):
    num_points = len(NODE_POINTS)
    distances = np.zeros((num_points, num_points))

    if type == 'strct':
        for (it, _, node, _, _) in tqdm(NODE_POINTS, desc="Precompute Progress"):
            for j in range(it + 1, num_points):  # Fill only the upper triangular part
                node2 = NODE_POINTS[j]['node']
                distances[it, j] = calculate_distance(node, node2, graph_nx)
                distances[j, it] = distances[it, j]
        return distances, None
    else:
        point_indexes = {}
        enum_points = list(enumerate(NODE_POINTS.items()))

        for i, (id1, dct1) in tqdm(enum_points, desc="Precompute Progress"):
            point_indexes[id1] = i
            for j in range(i + 1, num_points):  # Fill only the upper triangular part
                _, dct2 = enum_points[j][1]
                distances[i, j] = calculate_distance(dct1['node'], dct2['node'], graph_nx)
                distances[j, i] = distances[i, j]
        return distances, point_indexes


if __name__ == "__main__":

    city_name = "Saint Petersburg, Russia"
    filename = "../public/road_network_graph.pickle"

    file = '10_ex_1.csv'
    input_csv = f'../public/example_routes/{file}'
    output_csv = f'../public/result_routes/{file}'

    city_graph = get_graph(city_name, filename)

    points = read_csv_to_dict(input_csv)
    NODE_POINTS = get_node_all(points, city_graph)

    init_data = read_csv_to_strct(input_csv)
    full_data = set_node_strct_all(init_data, city_graph)

    city_graph_nx = optimize_graph_nx(city_graph, full_data)

    dist, _ = precompute_distances(city_graph_nx, full_data)

    route = ['11304463470', '10844090706', '10672598289', '10763697408', '6308159165', '11169616069', '9076608902', '11169616022', '10844090935', '2216518883', '11304463470']
    length = calculate_route_lengths(route, city_graph, NODE_POINTS)
    print(length)

    start_time = time.time()
    node1 = full_data[full_data['id'] == 11169615768]['node'][0]
    node2 = full_data[full_data['id'] == 11304463593]['node'][0]
    distance = calculate_distance(node1, node2, city_graph_nx)
    end_time = time.time()
    print("Elapsed time:", (end_time - start_time) * 1000, "milseconds")
    print("Distance between locations:", distance, "meters")

    # print(nodes_indexes[nodes_indexes['id' ] == 1234]['node'])

    # # рисование графа и двух точек на нем
    # fig, ax = ox.plot_graph(city_graph, figsize=(10, 10), show=False, close=False, edge_color='gray')

    # node_positions = {node: (city_graph.nodes[node]['x'], city_graph.nodes[node]['y']) for node in city_graph.nodes()}

    # location1_x, location1_y = node_positions[node1]
    # location2_x, location2_y = node_positions[node2]

    # ax.scatter(location1_x, location1_y, c='red', label='Location 1', zorder=5)
    # ax.scatter(location2_x, location2_y, c='red', label='Location 2', zorder=5)
    # ax.legend()
    # plt.show()
