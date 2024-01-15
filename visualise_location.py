import folium
import pandas as pd

# HTML разметка всплывающего сообщения для маркеров
def get_html(point):
    return f"<h3>{point.type}</h3><br>{point.adress}"

# Чтение данных из файла CSV
df = pd.read_csv('public/locations_data.csv')

# Создание карты с центром на средних координатах точек
map_center = [df['lat'].mean(), df['long'].mean()]
my_map = folium.Map(location=map_center, zoom_start=13)

# Добавление маркеров для каждой точки
for index, point in df.iterrows():
    folium.Marker(
        location=[point['lat'], point['long']],
        popup=get_html(point)
    ).add_to(my_map)


# Сохранение карты в файл HTML
my_map.save("public/map_with_points.html")
