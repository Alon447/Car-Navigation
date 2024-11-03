import datetime
import random
import numpy as np

from models import Node


class Road:
    """
    Represents a road segment in a road network.
    """

    def __init__(self, id: int, osm_id, source_node: Node, destination_node: Node, length, max_speed: int, type: str, activate_traffic_lights: bool, rain_intensity: int = 0):

        # Attributes
        self.id = id
        self.osm_id = osm_id
        self.source_node = source_node  # class Node (id, osm_id, lat, lon, street_count, traffic_lights)
        self.destination_node = destination_node  # class Node (id, osm_id, lat, lon, street_count, traffic_lights)
        self.length = length
        self.type = type
        self.max_speed = max_speed
        self.current_speed = 10
        self.estimated_time = float('inf')

        # Dicts
        self.road_speed_dict = {}  # key: time (for example "08:00"), value: speed
        self.eta_dict = {}  # key: time (for example "08:00"), value: eta

        # Past Information
        self.past_speeds = {}

        # Flags
        self.activate_traffic_lights = activate_traffic_lights
        self.rain_intensity = rain_intensity
        self.is_blocked = False

        # Adjacency
        self.adjacent_roads = []  # list of adjacent roads to this road, includes only the ids of the roads

        # Initialize
        self.calculate_time()  # initialize the estimated time

    # Functions
    def calculate_time(self):
        """
        Calculate the estimated time it takes to travel the road.

        Returns:
        float: The estimated time in seconds.
        """
        if self.current_speed is None:
            print("error")

        total_time = 3.6 * self.length / self.current_speed
        if self.destination_node.traffic_lights and self.activate_traffic_lights:  # has traffic lights
            street_count = self.destination_node.street_count  # get the street count of the destination node

            # Activate the traffic lights
            if street_count > 1:
                total_time += random.randrange(0, 20 * (street_count - 1), 1)
            else:
                total_time += random.randrange(0, 5, 1)
        self.estimated_time = round(total_time, 2)
        return self.estimated_time

    def update_speed(self, current_time: datetime, traffic_white_noise: bool = True):
        """
        Update the current speed of the road-based on the provided time and recalculate ETA.

        Args:
        current_time (str): The current time.

        Returns:
        float: The updated estimated time of arrival (ETA) in seconds.
        """
        current_hour_and_minute = current_time.strftime("%H:%M")
        projected_speed = self.road_speed_dict[current_hour_and_minute]
        if traffic_white_noise:
            # add white noise to the speed
            mean = 0  # Mean of the normal distribution (adjust as needed)
            if type == 'living_street' or type == 'residential' or type == 'unclassified':
                std_dev = 1
            else:
                std_dev = 4  # Standard deviation of the normal distribution (adjust as needed)
            noise = int(np.random.normal(mean, std_dev))
            if noise < 0:
                projected_speed = max(projected_speed + noise, 1)
            else:
                projected_speed = min(projected_speed + noise, self.max_speed)

        # check if there is rain
        if self.rain_intensity == 0:
            reduction_factor = 1.0  # No rain, no reduction
        elif self.rain_intensity == 1:
            reduction_factor = 0.95  # Light rain, 5% reduction
        elif self.rain_intensity == 2:
            reduction_factor = 0.85  # Moderate rain, 15% reduction
        else:  # self.rain_intensity == 3:
            reduction_factor = 0.70  # Heavy rain, 30% reduction

        self.current_speed = max(int(projected_speed * reduction_factor), 1)
        self.past_speeds[current_time.replace(second = 0)] = self.current_speed
        eta = self.calculate_time()
        return eta

    def update_estimated_time(self, current_time: datetime, traffic_white_noise: bool = True):
        """
        this function replaces the update_speed function, it updates the estimated time of the road for the real seoul data
        :param current_time:
        :param traffic_white_noise:
        :return:
        """
        self.estimated_time = self.eta_dict[current_time.strftime("%H:%M")]
        # get the speed from the eta data and the length of the road
        self.current_speed = int((self.length / 1000) / (self.estimated_time / 3600))
        self.past_speeds[current_time.replace(second = 0)] = self.current_speed
        return self.estimated_time

    def update_road_speed_dict(self, new_speed: dict):
        """
        Update the road speed dictionary and recalculate ETA values.

        Args:
        new_speed (dict): A dictionary containing times and corresponding road speeds.

        Returns:
        None
        """
        self.road_speed_dict = new_speed
        self.update_eta_dict()
        return

    def update_eta_dict_from_file(self, eta_data: dict):
        """
        Update the road speed dictionary and recalculate ETA values.

        Args:
        new_speed (dict): A dictionary containing times and corresponding road speeds.

        Returns:
        None
        """
        self.eta_dict = eta_data
        return

    def update_eta_dict(self):
        """
        Update the ETA dictionary based on the current road speeds.

        Returns:
        None
        """
        for key, value in self.road_speed_dict.items():
            new_val = self.calculate_eta(value)
            self.eta_dict[key] = new_val
        return

    # def update_speed_dict(self, new_speed: dict):
    #     """
    #     Update the road speed dictionary and recalculate ETA values.
    #
    #     Args:
    #     new_speed (dict): A dictionary containing times and corresponding road speeds.
    #
    #     Returns:
    #     None
    #     """
    #     for key, value in self.eta_dict.items():
    #         new_val = self.calculate_eta(value)
    #         self.eta_dict[key] = new_val
    #     return
    def calculate_eta(self, speed: int):
        """
        Calculate the estimated time of arrival (ETA) based on the provided speed.

        Args:
        speed (int): The speed of travel on the road in km/h.

        Returns:
        float: The estimated time of arrival (ETA) in seconds.
        """
        total_time = round(3.6 * self.length / speed, 2)
        if self.destination_node.traffic_lights and self.activate_traffic_lights:  # has traffic lights
            street_count = self.destination_node.street_count  # get the street count of the destination node

            # Activate the traffic lights
            if street_count > 1:
                total_time += random.randrange(0, 20 * (street_count - 1), 1)
            else:
                total_time += random.randrange(0, 5, 1)
        return total_time

    def calculate_speed(self, time):
        """
        Calculate the speed based on the provided estimated time of arrival (ETA).

        Args:
        time (str): The current time.
        Returns:
        int: The speed of travel on the road in km/h.
        """
        return int((self.length / 1000) / (self.get_eta(time) / 3600))

    def get_eta(self, time: str):
        """
        Get the estimated time of arrival (ETA) for the specified time.

        Args:
        time (str): The time for which ETA is requested.

        Returns:
        float: The estimated time of arrival (ETA) in seconds.
        """
        self.estimated_time = self.eta_dict[time]
        self.current_speed = int((self.length / 1000) / (self.estimated_time / 3600))
        return self.estimated_time

    def get_speed(self, time: str):
        """
        Get the speed for the specified time.

        Args:
        time (str): The time for which speed is requested.

        Returns:
        float: The speed in km/h.
        """
        return self.calculate_speed(time)

    def block(self):
        """
        Block the road.

        Returns:
        None
        """
        self.is_blocked = True
        self.estimated_time = float('inf')
        return

    def unblock(self):
        """
        Unblock the road.

        Returns:
        None
        """
        self.is_blocked = False
        new_eta = self.calculate_time()
        return new_eta, self.current_speed

    def __str__(self):
        return "Road id: " + str(self.id) + ", source node: " + str(self.source_node.id) + ", destination node: " + str(self.destination_node.id) + ", length: " + str(self.length) + ", max speed: " + str(self.max_speed) + ", current speed: " + str(self.current_speed) + ", is blocked: " + str(self.is_blocked)  # + ", cars on road: " + str(self.cars_on_road)

    def __repr__(self):
        return f"Road(road_id={self.id}, source_node={self.source_node.id}, destination_node={self.destination_node.id}, length={self.length}, speed={self.current_speed})"
