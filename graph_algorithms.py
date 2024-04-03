import osmnx as ox
import networkx as nx
import pickle
import datetime
import os
import time
import matplotlib.pyplot as plt

# Сопоставление гео координат узлу на графе
def get_node(long, lat):
    return ox.distance.nearest_nodes(CITY_GRAPH, X=long, Y=lat)

# Подсчет минимального пути по Диикстре
def calculate_distance(node1, node2):
    shortest_path = nx.shortest_path(CITY_GRAPH_NX, source=node1, target=node2, weight='length')
    total_distance = sum(CITY_GRAPH_NX[shortest_path[i]][shortest_path[i+1]]['length'] for i in range(len(shortest_path)-1))
    return round(total_distance)


# Скачивание графа в файл
def download_graph(city_name, filename):
    print("Start download")
    G = ox.graph_from_place(city_name, network_type="drive")
    with open(filename, 'wb') as file:
        pickle.dump(G, file)

# Чтение графа из файла
def read_graph(filename):
    print("Start read")
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

if __name__ == "__main__":
    start_time = time.time()

    city_name = "Saint Petersburg, Russia"
    filename = "road_network_graph.pickle"

    CITY_GRAPH = get_graph(city_name, filename)
    CITY_GRAPH_NX = nx.Graph(CITY_GRAPH)

    location1, location2 = (59.9206972,30.286013),(59.9496138,30.2264708)

    node1 = get_node(location1[1], location1[0])
    node2 = get_node(location2[1], location2[0])
    print(node1, node2)

    distance = calculate_distance(node1, node2)
    print("Distance between locations:", distance, "meters")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Elapsed time:", elapsed_time, "seconds")

    # рисование графа и двух точек на нем
    fig, ax = ox.plot_graph(CITY_GRAPH, figsize=(10, 10), show=False, close=False, edge_color='gray')

    node_positions = {node: (CITY_GRAPH.nodes[node]['x'], CITY_GRAPH.nodes[node]['y']) for node in CITY_GRAPH.nodes()}

    location1_x, location1_y = node_positions[node1]
    location2_x, location2_y = node_positions[node2]

    ax.scatter(location1_x, location1_y, c='red', label='Location 1', zorder=5)
    ax.scatter(location2_x, location2_y, c='red', label='Location 2', zorder=5)
    ax.legend()
    plt.show()


