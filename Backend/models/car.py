import datetime

from Utilities.Getters import time_delta_to_seconds
from models import Route
from models.Node import Node


class Car:
    """
    Car class:
    This class represents a car within a road network simulation.
    """

    def __init__(self, source_node: Node, destination_node: Node, starting_time: datetime, route_object: Route.Route, use_existing_q_table = True):

        self.id = Car._generate_id()

        # Nodes
        self.source_node = source_node
        self.destination_node = destination_node

        # Roads
        self.current_road = None  # the car's current road
        self.past_roads = []  # a list of the roads the car has been on, and his entering time to each one
        self.past_nodes = []  # a list of the nodes the car has been on, and his entering time to each one
        self.distance_traveled = 0  # the distance the car has traveled so far

        # Time
        self.starting_time = starting_time  # the time the car started its journey
        self.time_until_next_road = datetime.timedelta(seconds = 0)  # the time until the car reaches the next road *IN SECONDS*
        self.total_travel_time = datetime.timedelta(seconds = 0)  # the total travel time of the car
        self.current_road_time = datetime.timedelta(seconds = 0)  # the time the car has been on the current road

        # Flags
        self.is_finished = False  # indicates if the car has reached its destination
        self.car_in_destination = False  # indicates if the car is in the destination node
        self.is_blocked = False  # indicates if the car is blocked
        self.use_existing_q_table = use_existing_q_table

        # Route
        self.route_algorithm_name = route_object.get_route_name()
        self.route = route_object

    # Class variable to keep track of the last assigned id
    _last_id = -1

    @classmethod
    def _generate_id(cls):
        cls._last_id += 1
        return cls._last_id


    def start_car(self):
        """
        Move the car to the first road-based on the starting node and update car's time until the next road.

        Returns:
        Road object: The first road the car will travel to.
        """
        first_road = self.route.decide_first_road()
        if first_road.is_blocked:
            first_road = self.route.get_alt_road()
            if first_road is None:
                return "blocked"
        self.current_road = first_road
        self.update_time_until_next_road(self.current_road)
        self.past_nodes.append(self.source_node)
        return self.current_road

    def move_next_road(self):
        """
        Move the car to the next road, based on the route's next node.
        Update car's time until the next road.

        Args:
        time (float): The time interval.

        Returns:
        Road object or str: The next road the car will travel to, or "blocked" if the road is blocked.
        """
        # check if car is finished
        if self.check_if_finished():
            return None

        # else move to next road
        next_road = self.route.get_next_road()
        print("next road: ", next_road)

        if next_road is None or next_road.is_blocked:
            print("Car " + str(self.id) + " is blocked" + " on road " + str(self.current_road.id) + " at time " + str(self.total_travel_time))
            next_road = self.route.get_alt_road()
            if next_road is None:  # all roads are blocked
                self.is_blocked = True
                return "blocked"

        # appends and adds distance only if moved to next road
        self.distance_traveled += self.current_road.length
        self.past_nodes.append(self.current_road.destination_node.id)
        self.past_roads.append({self.current_road.id: round(time_delta_to_seconds(self.current_road_time), 2)})
        self.current_road = next_road
        self.update_time_until_next_road(self.current_road)
        self.current_road_time = datetime.timedelta(seconds = 0)
        return self.current_road

    def check_if_finished(self):
        # assuming reaching for the destination road is sufficient
        """
        Check if the car has reached its destination.

        Returns:
        bool: True if the car has reached its destination, False otherwise.
        """

        if self.current_road.destination_node.id == self.destination_node.id:
            self.past_roads.append({self.current_road.id: round(time_delta_to_seconds(self.current_road_time), 2)})
            self.past_nodes.append(self.current_road.destination_node.id)
            self.is_finished = True
            self.car_in_destination = True
        return self.is_finished

    def force_finish(self):
        """
        Force the car to finish its route prematurely.

        Returns:
        None
        """
        self.past_roads.append({self.current_road.id: round(time_delta_to_seconds(self.current_road_time), 2)})
        return

    def update_time_until_next_road(self, road):
        """
        Update the time until the car reaches the next road.

        Args:
        road (Road): Road object.

        Returns:
        None
        """
        time = road.calculate_time()
        self.time_until_next_road += datetime.timedelta(seconds = time)  # round((road.get_length() * 3.6 / road.get_current_speed()),2) # need to convert km/h to m/s
        return

    def update_travel_time(self, time):
        """
        Update the total travel time and the time until the next road.

        Args:
        time (float): The time interval.

        Returns:
        total_travel_time (datetime.timedelta): The total travel time of the car.
        """
        # used when we fast-forward the simulation
        self.current_road_time += datetime.timedelta(seconds = time)  # time for json file
        self.total_travel_time += datetime.timedelta(seconds = time)  # time for total travel time of the car
        self.time_until_next_road -= datetime.timedelta(seconds = time)  # time until the car changes road
        return self.total_travel_time

    def get_routing_algorithm(self):
        """
        Get the routing algorithm the car uses.

        Returns:
        str: The routing algorithm name.
        """
        q_learning_names = ["q learning", "Q learning", "Q Learning", "q Learning", "q", "Q", "Q_Learning_Route"]
        shortest_path_names = ["shortest_path", "shortest path", "Shortest Path", "Shortest path", "shortest",
                               "Shortest", "SP", "sp", "Shortest_path_route"]
        if self.route_algorithm_name in q_learning_names:
            return "Q Learning"
        elif self.route_algorithm_name in shortest_path_names:
            return "Shortest Path"
        else:
            return "Random Route"

    def get_time_until_next_road(self):
        """
        Get the time until the car reaches the next road.

        Returns:
        int: The time in seconds.
        """
        if self.is_blocked:
            self.time_until_next_road = datetime.timedelta(seconds = 600)
        return int(self.time_until_next_road.total_seconds())

    def __str__(self) -> str:
        """
        Return a string representation of the Car object.

        Returns:
        str: String representation.
        """
        return "Car_id: " + str(self.id) + ", " + "Travel_time: " + str(self.total_travel_time) + ", " + "Current Road: " + str(self.current_road.id) + ", " + "Length: " + str(self.current_road.length) + "," + "Time until update: " + str(self.time_until_next_road) + "\n"

    def __repr__(self):
        """
        Return a string representation of the Car object.

        Returns:
        str: String representation.
        """
        return "Car(car_id=" + str(self.id) + ", source_node=" + str(self.source_node) + ", destination_node=" + str(self.destination_node) + ", starting_time=" + str(self.starting_time) + ")"

    def __eq__(self, other):
        """
        Compare two Car objects for equality based on their attributes.

        Args:
        other (Car): Another Car object.

        Returns:
        bool: True if the objects are equal, False otherwise.
        """
        return self.id == other.id and self.source_node == other.source_node and self.destination_node == other.destination_node and self.starting_time == other.starting_time
