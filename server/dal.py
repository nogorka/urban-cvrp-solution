import datetime

from server.model import Point
from server.mongo import get_routes_collection


def save_route(route):
    routes_collection = get_routes_collection()

    json_route = [point.json() for point in route]

    entry = {
        'route': json_route,
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    ins_id = routes_collection.insert_one(entry).inserted_id
    entry['_id'] = str(ins_id)
    return entry


if __name__ == "__main__":
    point1 = Point(adress='113 к1', free_volume=211, id=10844090706, lat=60.023117, long=30.326293, purpose='Ozon',
                   total_volume=376, type='outpost')
    point2 = Point(adress='112 к1', free_volume=211, id=10844090706, lat=60.023117, long=30.326293, purpose='Ozon',
                   total_volume=376, type='outpost')
    route = [point1, point2]
    save_route(route)
