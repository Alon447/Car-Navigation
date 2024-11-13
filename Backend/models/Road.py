import datetime
import random
import numpy as np

from models import Node


class Road:
    """
    Represents a road segment in a road network.
    """

    def __init__(self, osm_id: int, source_node: Node, destination_node: Node, length: float, max_speed: int, type: str, activate_traffic_lights: bool, rain_intensity: int = 0):

        # Attributes
        self.id = Road._generate_id()
        self.osm_id = osm_id
        self.source_node = source_node
        self.destination_node = destination_node
        self.length = length
        self.type = type
        self.max_speed = max_speed
        self.current_speed = 10
        self.estimated_time = float('inf')

        # Dicts
        self.road_speed_dict = {}  # key: time (for example "08:00"), value: speed
        self.eta_dict = {}  # key: time (for example "08:00"), value: eta

        # Past Information
        # self.past_speeds = {}

        # Flags
        self.activate_traffic_lights = activate_traffic_lights
        self.rain_intensity = rain_intensity
        self.is_blocked = False
        self.white_noise = True
        # Adjacency
        self.adjacent_roads = []  # list of adjacent roads to this road, includes only the ids of the roads

        # Initialize
        self.calculate_time()  # initialize the estimated time

    # Class variable to keep track of the last assigned id
    _last_id = -1

    @classmethod
    def _generate_id(cls):
        cls._last_id += 1
        return cls._last_id

    def calculate_time(self) -> float:
        """
        Calculate the estimated time it takes to travel the road.

        Returns:
        float: The estimated time in seconds.
        """
        if not self.current_speed:
            raise ValueError("Current speed is not set.")
        if self.white_noise:
            noise = int(np.random.normal(0, 4 if self.type not in ['living_street', 'residential',
                                                                   'unclassified'] else 1))
            self.current_speed = max(1, min(self.current_speed + noise, self.max_speed))

        rain_factors = {0: 1.0, 1: 0.95, 2: 0.85, 3: 0.70}
        self.current_speed = max(int(self.current_speed * rain_factors.get(self.rain_intensity, 1.0)), 1)
        total_time = 3.6 * self.length / self.current_speed
        if self.activate_traffic_lights and self.destination_node.traffic_lights:
            street_count = self.destination_node.street_count
            delay = random.randrange(5, 20 * (street_count - 1) + 5, 5)
            total_time += delay
        self.estimated_time = round(total_time, 2)
        return self.estimated_time

    def update_estimated_time(self, speed: int) -> float:
        # get the speed from the eta data and the length of the road
        self.current_speed = speed
        self.calculate_time()
        return self.estimated_time

    def __str__(self):
        return (f"Road id: {self.id}, Source Node: {self.source_node.id}, "
                f"Destination Node: {self.destination_node.id}, Length: {self.length}m, "
                f"Max Speed: {self.max_speed}km/h, Current Speed: {self.current_speed}km/h, "
                f"Is Blocked: {self.is_blocked}")

    def __repr__(self):
        return (f"Road(road_id={self.id}, source_node={self.source_node.id}, "
                f"destination_node={self.destination_node.id}, length={self.length}, "
                f"speed={self.current_speed})")
