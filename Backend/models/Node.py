
class Node:
    """
    Represents a node in a road network.

    Attributes:
    id (int): The unique identifier of the node.
    osm_id (int): The OpenStreetMap identifier of the node.
    x (float): The x-coordinate (longitude) of the node's location.
    y (float): The y-coordinate (latitude) of the node's location.
    traffic_lights (bool): Indicates whether the node has traffic lights (True) or not (False).
    street_count (int): The number of streets connected to this node.
    """
    def __init__(self, id, osm_id, x, y, traffic_lights, street_count):
        self.id = id
        self.osm_id = osm_id
        self.x = x
        self.y = y
        self.traffic_lights = traffic_lights
        self.street_count = street_count
        self.connected_nodes = []

    def __str__(self):
        return f'Id: {self.id}, Osm_Id: {self.osm_id}, X: {self.x}, Y: {self.y}, Traffic_Lights: {self.traffic_lights}, Street_Count: {self.street_count}'
    def __repr__(self):
        return self.__str__()