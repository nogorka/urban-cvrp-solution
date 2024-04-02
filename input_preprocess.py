import csv
import numpy as np
import os
import csv
import pandas as pd

def get_all_filenames(directory_path):
    filenames = []
    for filename in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, filename)):
            filenames.append(filename)
    return filenames

def load_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = [row for row in csv_reader]
    return data

def get_route(dirname, filename):
    path = os.path.join('public', dirname, filename)
    df = load_csv(path)
    return np.array([row['id'] for row in df])

# Чтение точек и преобразование к формату работы { 'id': (lat, long), ....}
def read_csv_to_dict(file_path):
    data_dict = {}

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Преобразуем значения широты и долготы в кортеж
            data_dict[row['id']] = (float(row['lat']), float(row['long']))

    return data_dict

# Сопоставлении ключей и переупорядочивания строк в DataFrame
def reorder_csv(input_csv, output_csv, keys):
    df = pd.read_csv(input_csv)
    df['id'] = df['id'].astype(str)
    df_selected = df[df['id'].isin(keys)]
    df_reordered = df_selected.set_index('id').loc[keys].reset_index()
    df_reordered.to_csv(output_csv, index=False)
