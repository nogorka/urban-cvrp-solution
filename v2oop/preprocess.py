import csv
import os
import networkx as nx
import pandas as pd

from algorithms.graph_algorithms import get_graph, optimize_graph_nx
from v2oop.graph import set_node_all_point_list, precompute_distances
from v2oop.objects.point import Point


def read_csv_to_point_list(file_path):
    lst = []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            d = int(row['total_volume']) - int(row['free_volume'])
            point = Point(id=row['id'], lat=row['lat'], long=row['long'], demand=d)
            lst.append(point)
    return lst


def reorder_save_to_csv(input, output, route):
    df = pd.read_csv(input)

    keys = [p.id for p in route.points]
    df['id'] = df['id'].astype(str)

    df_selected = df[df['id'].isin(keys)]
    df_reordered = df_selected.set_index('id').loc[keys].reset_index()

    df_reordered.to_csv(output, index=False)


def get_meta_data(config, filename):
    input_csv = os.path.join(config['input_dir'], filename)
    output_csv = os.path.join(config['output_dir'], filename)

    city_graph = get_graph(config['city_name'], config['graph_filename'])
    graph_nx = optimize_graph_nx(city_graph)
    G = nx.Graph(city_graph)

    city_points = read_csv_to_point_list(input_csv)
    set_node_all_point_list(city_points, city_graph)

    distance_matrix = precompute_distances(graph_nx, city_points)

    return distance_matrix, city_points, input_csv, output_csv, G