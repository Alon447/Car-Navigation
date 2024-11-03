import datetime
import json
import time
import pandas as pd

from Q_Learning_Classes import Q_Learning
from Utilities.Getters import time_delta_to_seconds, get_simulation_speeds_file_path, Source, Destination, Reached_destination, Routing_algorithm, Time_taken, Day_of_week, Start_time, End_time, Route, Roads_used, Distance_travelled, Simulation_number, Blocked_roads, get_random_src_dst
from models import Road_Network, Car_manager, Car


class Simulation_manager:
    """
    Manages the simulation by creating and updating the road network, managing cars, and printing results.

    """

    def __init__(self, graph_name, activate_traffic_lights = False, rain_intensity = 0, traffic_white_noise = True, is_plot_results = True, max_time_for_car = datetime.timedelta(hours = 2), start_time = datetime.datetime(year = 2023, month = 6, day = 29, hour = 8, minute = 0, second = 0)):
        """
        Initialize the Simulation_manager.

        :Args:
        :param graph: The networkx graph representing the road network.
        :param time_limit :(int) The maximum time the simulation will run in seconds.
        :param activate_traffic_lights: Indicates whether traffic lights are activated. Default is False.
        :param start_time : (bool, optional) The starting datetime of the simulation. Default is June 29, 2023, 08:00:00.
        """
        # MANAGERS
        self.graph_name = graph_name
        self.road_network = Road_Network.Road_Network(graph_name, activate_traffic_lights, rain_intensity, traffic_white_noise)
        self.car_manager = Car_manager.CarManager(max_time_for_car)  # the maximum time for car in the simulation

        # TIME
        self.simulation_datetime_start = start_time
        self.simulation_datetime = start_time
        self.simulation_time = datetime.timedelta(seconds = 0)  # in seconds
        self.last_current_speed_update_time = start_time  # for updating the current speed of the roads
        self.last_speed_dict_update_time = start_time  # for updating the speed dict of the roads
        self.day_int = start_time.weekday()  # 0-6, 0 - monday, 1 - tuesday, 2 - wednesday, 3 - thursday, 4 - friday, 5 - saturday, 6 - sunday

        # RESULTS
        self.simulation_results = []  # list of dictionaries, each dictionary is a simulation result
        self.simulation_update_times = []  # list of times the simulation was updated for the animation

        # DATA
        self.speeds_file_path = None
        self.eta_data = None
        # FUNCTIONS - read speeds
        self.read_road_speeds(self.simulation_datetime_start)

        # Flags
        self.is_plot_results = is_plot_results

    def run_multiple_simulations(self, start_time, number_of_simulations = 1, num_episodes = 2000, max_steps_per_episode = 150, simulation_number_added = 0, learning_rate = 0.1, discount_factor = 0.9, epsilon = 0.2):
        """
        Run multiple simulations. generate source and destination with one q learning car and one shortest path car and comapres them.
        :param number_of_simulations:
        :param start_time:
        :param num_episodes:
        :param max_steps_per_episode:
        :param simulation_number_added:
        :param learning_rate:
        :param discount_factor:
        :param epsilon:
        :return:
        """
        results = [0, 0, 0]  # [q_learning, shortest_path, tie] - number of times each algorithm won
        for i in range(number_of_simulations):
            print("*********************************************")
            print("simulation number:", i + 1)
            print("*********************************************")
            cars = []
            src, dst = get_random_src_dst(self.road_network)
            cars.append(Car.Car(1, src, dst, start_time, self.road_network, route_algorithm = "q", use_existing_q_table = False, ))
            cars.append(Car.Car(2, src, dst, start_time, self.road_network, route_algorithm = "sp", use_existing_q_table = False))
            res = self.run_full_simulation(cars, 1, num_episodes, max_steps_per_episode, simulation_number_added, learning_rate, discount_factor, epsilon)
            print(res[1])
            print(res[2])
            if res[1]['Time_taken'] < res[2]['Time_taken']:
                results[0] += 1
            elif res[1]['Time_taken'] > res[2]['Time_taken']:
                results[1] += 1
            else:
                results[2] += 1
        return results

    def run_full_simulation(self, cars, number_of_simulations = 1, num_episodes = 2000, max_steps_per_episode = 150, simulation_number_added = 0, learning_rate = 0.1, discount_factor = 0.9, epsilon = 0.2):
        """
        Run the full simulation process including setup, execution, and result printing.

        Args:
        cars (list): List of Car objects for the simulation.
        number_of_simulations (int, optional): Number of simulations to run. Default is 1.

        Returns:
        None
        """
        for i in range(number_of_simulations):
            copy_cars = []
            # make a deep copy of the cars list
            if number_of_simulations > 1:
                for car in cars:
                    new_car = Car.Car(car.id, car.source_node, car.destination_node, car.starting_time, self.road_network, car.get_routing_algorithm())
                    copy_cars.append(new_car)
            else:
                copy_cars = cars
            # set up the simulation
            self.start_q_learning_simulation(copy_cars, num_episodes, max_steps_per_episode, learning_rate, discount_factor, epsilon)
            self.set_up_simulation(copy_cars)
            self.start_simulation()
            self.end_simulation(i)
            res = self.write_simulation_results(copy_cars, i + simulation_number_added)
        return res

    def start_q_learning_simulation(self, copy_cars, num_episodes, max_steps_per_episode, learning_rate, discount_factor, epsilon):
        """
        Start the Q-Learning simulation by training the cars that use Q-Learning.

        :param copy_cars: List of Car objects for the simulation.
        :param num_episodes: Number of episodes to train the Q-Learning agent.
        :param max_steps_per_episode: Maximum number of steps per episode.
        :param learning_rate: The learning rate for the Q-Learning agent.
        :param discount_factor: The discount factor for the Q-Learning agent.
        :param epsilon: The epsilon for the Q-Learning agent.

        :return:  None
        """
        q_learning_cars = []

        for car in copy_cars:
            if car.route_algorithm_name == "q" and car.route.q_table is None:
                q_learning_cars.append(car)
        q_learn = Q_Learning.Q_Learning(self.road_network, self.eta_data, cars = q_learning_cars, num_episodes = num_episodes, max_steps_per_episode = max_steps_per_episode, learning_rate = learning_rate, discount_factor = discount_factor, epsilon = epsilon)
        q_learn.train(self.simulation_datetime_start, is_plot_results = self.is_plot_results)
        return

    def set_up_simulation(self, cars: list):
        """
        Set up the simulation by adding cars to the car manager.

        Args:
        cars (list): List of Car objects to be added to the simulation.

        Returns:
        None
        """

        self.simulation_time = datetime.timedelta(seconds = 0)  # in seconds
        self.simulation_datetime = self.simulation_datetime_start
        self.update_block_roads()

        self.car_manager.clear()
        for car in cars:
            self.car_manager.add_car(car, self.simulation_datetime_start)
        return

    def start_simulation(self):
        """
        Start the simulation and run it until all cars finish or time limit is reached.

        Returns:
        None
        """
        # while the time limit is not reached and there are cars in the simulation or cars waiting to enter the simulation
        # while int(self.simulation_time.total_seconds()) < self.time_limit and (self.car_manager.cars_in_simulation or self.car_manager.cars_waiting_to_enter):
        while self.car_manager.cars_in_simulation or self.car_manager.cars_waiting_to_enter:

            time = self.car_manager.calc_nearest_update_time(self.simulation_datetime)
            self.update_simulation_clocks(time)
            self.update_simulation_roads_speed_dict()
            self.update_simulation_roads_current_speeds()
            self.update_block_roads()
            self.car_manager.update_cars(time, self.simulation_datetime)

            # print("simulation_time:", SM.simulation_time)  # self.car_manager.show_cars_in_simulation()

        for carInd in self.car_manager.cars_in_simulation:
            car = self.car_manager.cars_in_simulation[carInd]  # dict so we need to get the car object
            self.car_manager.cars_stuck.append(car)
        # self.car_manager.force_cars_to_finish()
        for car in self.car_manager.cars_stuck:
            car.force_finish()

        # show results
        return

    def end_simulation(self, simulation_number):
        """
        Print the results of the simulation.

        Args:
        simulation_number (int): The index of the current simulation.

        Returns:
        None
        """
        simulation_number += 1
        simulation_time_seconds = time_delta_to_seconds(self.simulation_time)
        if simulation_time_seconds >= 3600:
            if simulation_time_seconds % 3600 == 0:
                print("simulation", simulation_number, "finished after", int(simulation_time_seconds / 3600), "hours")
            else:
                print("simulation", simulation_number, "finished after", int(simulation_time_seconds / 3600), "hours and ", int(simulation_time_seconds % 60), "minutes")
        else:
            print("simulation", simulation_number, "finished after", int(simulation_time_seconds / 60), "minutes")
        print("*********************************************")
        return

    # update functions for the simulation run
    def update_simulation_clocks(self, time: int):
        """
        Update the simulation clocks.

        Args:
        time (int): The time interval to update the simulation clock in seconds.

        Returns:
        None
        """
        # update both the spesific simulation time and the datetime
        self.simulation_time += pd.Timedelta(seconds = time)  # time
        self.simulation_datetime += pd.Timedelta(seconds = time)  # time
        self.simulation_update_times.append(self.simulation_datetime)
        self.day_int = self.simulation_datetime.weekday()  # 0-6, 0 - monday, 1 - tuesday, 2 - wednesday, 3 - thursday, 4 - friday, 5 - saturday, 6 - sunday
        return

    def update_simulation_roads_speed_dict(self):
        """
        Check if a day is passed in the simulation and update the road speeds accordingly.

        Args:
        None

        Returns:
        None
        """
        last_update_day = self.last_speed_dict_update_time.weekday()
        if self.day_int != last_update_day:
            # update the road speeds according to the day
            # every day or at the next time a car will be updated (if more than a day passed)

            self.last_speed_dict_update_time = self.simulation_datetime.replace(hour = 0).replace(minute = 0).replace(second = 0).replace(microsecond = 0)
            self.read_road_speeds(self.simulation_datetime)
        return

    def update_simulation_roads_current_speeds(self):
        """

        Check if 10 minutes passed in the simulation and update the road speeds accordingly.

        Args:
        None

        Returns:
        None
        """
        time_difference = self.simulation_datetime - self.last_current_speed_update_time
        if (
                self.simulation_datetime.minute % 10 == 0 and self.simulation_datetime.minute - self.last_current_speed_update_time.minute > 0) or time_difference.seconds >= 600:
            # update the road speeds according to the time
            # every 10 minutes or at the next time a car will be updated (if more than 10 minutes passed)

            minutes = int(self.simulation_datetime.minute / 10) * 10
            self.last_current_speed_update_time = self.simulation_datetime.replace(minute = minutes).replace(second = 0).replace(microsecond = 0)

            # time_key = self.simulation_datetime.replace(minute=minutes).strftime("%H:%M")
            time_key = self.simulation_datetime.replace(minute = minutes)
            self.road_network.update_roads_speeds(time_key)  # updates the road speeds according to the current time

            print(self.simulation_datetime.strftime("%H:%M:%S"))
        return

    def update_block_roads(self):
        """

        Update all the blocked and soon to be blocked roads in the simulation,
        according to the current time.


        :return: None
        """

        copied_blocked_roads_dict = self.road_network.blocked_roads_dict.copy()

        for key, value in copied_blocked_roads_dict.items():

            road_id = key
            start_time = value[0]
            end_time = value[1]
            if start_time <= self.simulation_datetime <= end_time and self.road_network.roads_array[
                road_id].is_blocked == False:
                self.road_network.block_road(road_id)
            elif self.simulation_datetime > end_time and self.road_network.roads_array[road_id].is_blocked == True:
                self.road_network.unblock_road(road_id)

        return

    def read_road_speeds(self, datetime_obj: datetime.datetime):
        """
        Read road speeds from a JSON file and update the road network.
        The Json file supposed to be in the following format:
        {day_int: {time_key: {road_id: speed}}}
        The Json file is located at /Speeds_Data/{graph_name}_speeds.json

        Args:
        datetime_obj (datetime.datetime): The datetime for which road speeds are to be read.

        Returns:
        None
        """
        self.last_current_speed_update_time = datetime_obj.replace(second = 0, microsecond = 0)
        self.day_int = datetime_obj.weekday()
        self.speeds_file_path = get_simulation_speeds_file_path(self.road_network.graph, self.graph_name)
        with open(self.speeds_file_path, 'r') as infile:
            self.eta_data = json.load(infile)
        # day_data = data.get(str(self.day_int), {})

        # round the minutes to the nearest 10
        minutes = int(datetime_obj.minute / 10) * 10
        time_key = datetime_obj.replace(minute = minutes)
        self.road_network.set_roads_speeds_from_dict(self.eta_data, self.day_int, time_key)
        return

    def update_road_blockage(self, road_id, start_time = None, end_time = None):
        """
        Update the road blockage in the road network.

        Args:
        road_id (int): The id of the road to be blocked.
        start_time (datetime.datetime): The datetime the road is blocked.
        end_time (datetime.datetime): The datetime the road is unblocked.

        Returns:
        None
        """
        if start_time is None:
            start_time = self.simulation_datetime_start
        if end_time is None:
            end_time = self.simulation_datetime_start + datetime.timedelta(weeks = 52)
        self.road_network.plan_road_blockage(road_id, start_time, end_time)
        return

    def write_simulation_results(self, copy_cars: list, simulation_number: int):
        """
        Write simulation results to the simulation results list.

        Args:
        copy_cars (list): List of Car objects used in the simulation.
        i (int): Index of the current simulation.

        Returns:
        None
        """
        simulation_results = {}
        reached_destination = []
        for j, car in enumerate(copy_cars):
            car_reached_destination = self.car_manager.is_car_finished(car)
            if self.car_manager.is_car_finished(car):
                reached_destination.append(True)
            else:
                reached_destination.append(False)
            car_time_taken = int(car.total_travel_time.total_seconds())  # car.get_total_travel_time()
            car_starting_time = str(car.starting_time)
            car_ending_time = str(car.total_travel_time + car.starting_time)
            car_route = car.past_nodes
            car_key = car.id
            day_of_week_str = car.starting_time.strftime('%A')
            # blocked_roads = list(self.road_network.blocked_roads_dict.keys())
            blocked_roads = []
            for key, (start_datetime, end_datetime) in self.road_network.blocked_roads_dict.items():
                start_datetime_str = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
                end_datetime_str = end_datetime.strftime("%Y-%m-%d %H:%M:%S")
                block_road = [key, [start_datetime_str, end_datetime_str]]
                blocked_roads.append(block_road)
            # save the important Graphs

            simulation_results[
                car_key] = {Source: car.source_node, Destination: car.destination_node, Reached_destination: car_reached_destination, Routing_algorithm: car.get_routing_algorithm(), Time_taken: car_time_taken,
                # in seconds
                Day_of_week: day_of_week_str,  # day of the week string
                Start_time: car_starting_time,  # datetime object string
                End_time: car_ending_time,  # datetime object string
                Route: car_route, Roads_used: car.past_roads, Blocked_roads: blocked_roads, Distance_travelled: int(car.distance_traveled),
                # in meters, int
            }

        self.simulation_results.append({Simulation_number: simulation_number + 1, **simulation_results})
        return simulation_results

    def get_simulation_routes(self, cars: list, simulation_number: int):
        """
        Retrieve routes passed by cars in a simulation.

        Args:
        cars (list): List of Car objects.
        simulation_number (int): Index of the simulation.

        Returns:
        list: List of routes passed by cars in the simulation.
        """
        cars_ids = [car.id for car in cars]
        routes = []
        for carInd in cars_ids:
            if self.simulation_results[simulation_number][carInd][Route] is None:
                pass
            else:
                routes.append(self.simulation_results[simulation_number][carInd][Route])
        return routes

    def get_fixed_node_id(self, osm_id: int):
        """
        Get the fixed node id of a node.

        Args:
        node_id (int): osm_id.

        Returns:
        int: node id.
        """
        return self.road_network.get_node_from_osm_id(osm_id)
