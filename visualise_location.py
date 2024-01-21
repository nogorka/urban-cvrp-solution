import folium
import pandas as pd

# HTML разметка всплывающего сообщения для маркеров
def get_html(point):
    return f"""
    <h4>{point.type}: {point.purpose}</h4>
    <p>{point.free_volume}/{point.total_volume}</p>
    {point.adress}
"""

def get_color(type):
    if type == 'outpost':
        return 'blue'
    if type == 'parcel_locker':
        return 'green'
    return 'red'


if __name__ == "__main__":
    df = pd.read_csv('public/locations_data.csv')

    # Создание карты с центром на средних координатах точек
    map_center = [df['lat'].mean(), df['long'].mean()]
    my_map = folium.Map(location=map_center, zoom_start=13)

    # Добавление маркеров для каждой точки
    for index, point in df.iterrows():
        folium.Marker(
            location=[point['lat'], point['long']],
            popup=get_html(point),
            icon=folium.Icon(color=get_color(point.type))
        ).add_to(my_map)


    # Сохранение карты в файл HTML
    my_map.save("public/locations_data_preview.html")
