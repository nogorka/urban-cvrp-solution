import osmnx as ox


class Point:
    def __init__(self, id, lat, long):
        self.id = id
        self.node_id = None
        self.lat = float(lat)
        self.long = float(long)
        self.it = None

    def __str__(self):
        return f'(Node({self.node_id}, {self.lat}, {self.long}))'

    def __repr__(self):
        # return f'({self.id},{self.it}: Node({self.node_id}, {self.lat}, {self.long}))'
        return f'({self.id},{self.it})'

    def set_node_id(self, node_id):
        self.node_id = node_id

    def set_it(self, it):
        self.it = it

    def set_node_id_from_G(self, G):
        self.set_node_id(ox.distance.nearest_nodes(G, X=self.long, Y=self.lat))
