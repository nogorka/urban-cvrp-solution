import uuid


def save_route(route):
    id = uuid.uuid4()
    entry = {'id': id, 'route': route}
    print("Save Route", entry)
    return entry
