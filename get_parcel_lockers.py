import overpy
import csv
from geopy.geocoders import Nominatim
from tqdm import tqdm
import random
import numpy as np


# получения адреса по координатам
geolocator = Nominatim(user_agent="location_lookup")
def get_address(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language="ru")
        return location.address if location else "N/A"
    except:
        return "Location Decode Error"


# определение типа локации на основе тегов
def get_type(tags):
    return tags.get('amenity') or tags.get('shop') or tags.get('office', 'N/A')


# получение назначения локации на основе тегов
def get_purpose(tags):
    return tags.get('brand') or tags.get('name') or tags.get('operator') or tags.get('description', 'N/A')


# генерация случайного числа с нормальным распределением в заданном диапазоне
def get_number_from_gauss(lower_limit, upper_limit, mean_value, std_deviation):
    random_value = int(np.random.normal(loc=mean_value, scale=std_deviation))
    return max(lower_limit, min(random_value, upper_limit))


# определение общего объема в зависимости от типа локации
def get_total_volume(type):
    if type == 'parcel_locker':
        return random.choice([23, 32, 41])
    if type == 'outpost':
        return get_number_from_gauss(92, 640, 370, 90)
    return 0


# определение свободного объема в зависимости от общего объема
def get_free_volume(total_volume):
    if total_volume is None or total_volume == 0:
        return 0

    mean_value = total_volume / 5 * 3
    std_deviation = (total_volume - mean_value) / 3

    return get_number_from_gauss(0, total_volume, mean_value, std_deviation)



def download_locations(city="Санкт-Петербург"):
    api = overpy.Overpass()

    # Формирование запроса к Overpass API для поиска постоматов, ПВЗ и складов
    query = f"""
    area["name"="{city}"]->.a;
    (
      node["amenity"="parcel_locker"](area.a);
      way["amenity"="parcel_locker"](area.a);
      relation["amenity"="parcel_locker"](area.a);

      node["shop"="outpost"](area.a);
      way["shop"="outpost"](area.a);
      relation["shop"="outpost"](area.a);

      node["amenity"="post_depot"](area.a);
      way["amenity"="post_depot"](area.a);
      relation["amenity"="post_depot"](area.a);
    );
    out body;
    >;
    out skel qt;
    out meta;
    """
    print("Подготовка завершена")

    # Получение данных с сервера Overpass API
    result = api.query(query)

    print("Данные успешно получены")

    # Сохранение результатов в CSV файл
    with open("public/locations_data.csv", "w", encoding="utf-8", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["id", "lat", "long", "type", "adress", "total_volume", "free_volume", "purpose"])

        # Обработка результатов запроса
        for node in tqdm(result.nodes, desc="Обрабатываем полученые точки"):
            location_id = node.id
            lat = node.lat
            long = node.lon
            location_type = get_type(node.tags)
            address = get_address(node.lat, node.lon)
            total_volume = get_total_volume(location_type)
            free_volume = get_free_volume(total_volume)
            purpose = get_purpose(node.tags)

            csv_writer.writerow([location_id, lat, long, location_type, address, total_volume, free_volume, purpose])
    print("Точки успешно обработаны")


if __name__ == "__main__":
    download_locations()