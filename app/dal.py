import datetime

from bson import ObjectId

from app.mongo import get_routes_collection


def save_route(json_data):
    routes_collection = get_routes_collection()

    entry = {
        'route': json_data,
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    ins_id = routes_collection.insert_one(entry).inserted_id
    entry['_id'] = str(ins_id)
    return entry


def get_route(route_id):
    routes_collection = get_routes_collection()
    entry = routes_collection.find_one({'_id': ObjectId(route_id)})
    entry['_id'] = str(entry['_id'])
    return entry


def get_recent_routes(amount):
    routes_collection = get_routes_collection()
    return list(routes_collection.find().sort("date", -1).limit(amount))


if __name__ == "__main__":
    # point1 = Point(adress='113 к1', free_volume=211, id=10844090706, lat=60.023117, long=30.326293, purpose='Ozon',
    #                total_volume=376, type='outpost')
    # point2 = Point(adress='112 к1', free_volume=211, id=10844090706, lat=60.023117, long=30.326293, purpose='Ozon',
    #                total_volume=376, type='outpost')
    # route = [point1, point2]
    # save_route(route)

    print(get_route('66375db71c5477cc839c8148'))
    print(get_recent_routes(10))
