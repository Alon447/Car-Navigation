
class Node:
    """
    Represents a node in a road network.
    """
    def __init__(self, osm_id, x, y, traffic_lights, street_count):
        self.id = Node._generate_id()
        self.osm_id = osm_id
        self.x = x
        self.y = y
        self.traffic_lights = traffic_lights
        self.street_count = street_count
        self.connected_nodes = []

    # Class variable to keep track of the last assigned id
    _last_id = -1

    @classmethod
    def _generate_id(cls):
        cls._last_id += 1
        return cls._last_id

    def __str__(self):
        return f'Id: {self.id}, Osm_Id: {self.osm_id}, X: {self.x}, Y: {self.y}, Traffic_Lights: {self.traffic_lights}, Street_Count: {self.street_count}'
    def __repr__(self):
        return self.__str__()