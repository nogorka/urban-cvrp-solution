import overpy
import csv
from geopy.geocoders import Nominatim
from tqdm import tqdm  # Добавлен импорт tqdm

geolocator = Nominatim(user_agent="location_lookup")
def get_address(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language="ru")
        return location.address if location else "N/A"
    except:
        return "Location Decode Error"

def get_type(tags):
    print(tags)
    return tags.get('amenity') or tags.get('shop') or tags.get('office', 'N/A')

def get_total_volume(type):
    pass

def get_free_volume(total_volume):
    pass


def download_locations(city="Санкт-Петербург"):
    api = overpy.Overpass()

    # Формируем запрос для поиска постоматов, ПВЗ и складов
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

    result = api.query(query)

    print(api.parse_json(result))

    print("Данные успешно получены")

   # Сохраняем результат в CSV файл
    with open("public/locations_data.csv", "w", encoding="utf-8", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["id", "lat", "long", "type", "adress", "total_volume", "free_volume"])

        # Обработка результатов запроса
        for node in tqdm(result.nodes, desc="Обрабатываем полученые точки"):
            location_id = node.id
            lat = node.lat
            long = node.lon
            location_type = get_type(node.tags)
            address = get_address(node.lat, node.lon)
            total_volume = get_total_volume(location_type)
            free_volume = get_free_volume(total_volume)
            # purpose (назначение)

            csv_writer.writerow([location_id, lat, long, location_type, address, total_volume, free_volume])
    print("Точки успешно обработаны")

if __name__ == "__main__":
    download_locations()