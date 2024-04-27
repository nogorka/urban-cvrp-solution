import csv
import pandas as pd

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
