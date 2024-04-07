import osmnx as ox
import networkx as nx
import pickle
import datetime
import os
import time
import matplotlib.pyplot as plt
import numpy as np
from input_preprocess import read_csv_to_strct

# Сопоставление гео координат узлу на графе
def get_node(coords, G):
    return ox.distance.nearest_nodes(G, X=coords[1], Y=coords[0])

def get_node_all(coords_dct, G):
    return { id: { "node": get_node(coords, G), "coords": coords }
            for (id, coords) in coords_dct.items()}

def set_node_strct_all(strct, G):
    lat_long_tuples = np.column_stack((strct['lat'], strct['long']))
    nodes = np.apply_along_axis(lambda x: get_node(tuple(x), G), 1, lat_long_tuples)
    strct['node'] = nodes
    return strct

# Подсчет минимального пути по Диикстре
def calculate_distance(node1, node2, nxG):
    shortest_path = nx.shortest_path(nxG, source=node1, target=node2, weight='length')
    total_distance = sum(nxG[shortest_path[i]][shortest_path[i+1]]['length'] for i in range(len(shortest_path)-1))
    return round(total_distance)

# def calculate_distance(node1, node2, nxG):
#     shortest_path = nx.astar_path(nxG, source=node1, target=node2, weight='length')
#     total_distance = sum(nxG[shortest_path[i]][shortest_path[i+1]]['length'] for i in range(len(shortest_path)-1))
#     return round(total_distance)

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

def optimize_graph_nx(city_graph):
    G = nx.Graph(city_graph)
    G = nx.minimum_spanning_tree(G)
    return G

if __name__ == "__main__":

    city_name = "Saint Petersburg, Russia"
    filename = "road_network_graph.pickle"

    city_graph = get_graph(city_name, filename)
    city_graph_nx = nx.Graph(city_graph)

    init_data = read_csv_to_strct('public/example_routes/10_ex_1.csv')
    full_data = set_node_strct_all(init_data, city_graph)

    locations = {'1st':(59.9206972,30.286013),
                 '2nd':(59.9496138,30.2264708),
                 '3rd':(59.9897338,30.3682432),
                 '4th':(59.8744927,30.3870571)}
    location1, location2 = locations['1st'], locations['2nd']
    start_time = time.time()

    node1 = full_data[full_data['id'] == 2216518883]['node'][0]
    node2 = full_data[full_data['id'] == 11169616069]['node'][0]
    distance = calculate_distance(node1, node2, city_graph_nx)
    end_time = time.time()
    print("Elapsed time:", (end_time - start_time) * 1000, "milseconds")
    print("Distance between locations:", distance, "meters")

    # print(nodes_indexes[nodes_indexes['id' ] == 1234]['node'])

    optimize_graph_nx(city_graph)
    # # рисование графа и двух точек на нем
    # fig, ax = ox.plot_graph(city_graph, figsize=(10, 10), show=False, close=False, edge_color='gray')

    # node_positions = {node: (city_graph.nodes[node]['x'], city_graph.nodes[node]['y']) for node in city_graph.nodes()}

    # location1_x, location1_y = node_positions[node1]
    # location2_x, location2_y = node_positions[node2]

    # ax.scatter(location1_x, location1_y, c='red', label='Location 1', zorder=5)
    # ax.scatter(location2_x, location2_y, c='red', label='Location 2', zorder=5)
    # ax.legend()
    # plt.show()


