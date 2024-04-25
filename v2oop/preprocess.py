import csv

from v2oop.objects import Point


def read_csv_to_point_list(file_path):
    lst = []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            point = Point(id=row['id'], lat=row['lat'], long=row['long'])
            lst.append(point)
    return lst
