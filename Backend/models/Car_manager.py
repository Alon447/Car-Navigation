import datetime

from models import Car


class CarManager:
    """
    CarManager class:
    This class manages cars within a road network simulation. It adds, removes, and updates cars during the simulation.

    Attributes:

    cars_waiting_to_enter (list): List of cars waiting to enter the simulation.

    cars_in_simulation (dict): Dictionary of cars currently in the simulation.

    cars_nearest_update (list): List of cars that determine the time of the next update.

    cars_nearest_update_time (int): Time of the next update.

    cars_blocked (list): List of cars blocked in the simulation.

    cars_finished (list): List of cars that have finished their journey.

    cars_stuck (list): List of cars stuck at the end of the simulation.

    simulation_update_times (dict): Dictionary of cars that have been updated in the current time step.

    Methods:

    add_update_to_dictionary(self, time, car_id, x, y, node_id): Add car update information to the dictionary.

    add_car(self, car, time): Add a car to the simulation.

    sort_cars_in_simulation(self): Sort cars in the simulation based on the time until the next road.

    calc_nearest_update_time(self, time): Calculate the time of the nearest update.

    """

    def __init__(self, max_time):
        # Start of the simulation
        self.cars_waiting_to_enter = []  # a list of the cars that are waiting to enter the simulation, i.e their starting time has not arrived yet.

        # During the simulation
        self.cars_in_simulation = {}  # a dictionary of all the cars currently in the simulation.
        self.cars_nearest_update = []  # a list  of the cars that will determine time of the next update.
        self.cars_nearest_update_time = 0  # the time of the next update
        self.cars_blocked = []  # a list of the cars that are blocked in the simulation
        self.max_time_for_car = datetime.timedelta(hours = 4)# the maximum time for car in the simulation
        # End of the simulation
        self.cars_finished = []  # a list of the cars that have finished their journey and are waiting to be removed from the simulation
        self.cars_stuck = []  # a list of the cars that are stuck at the end of the simulation
        self.simulation_update_times = {}  # a dictionary of the cars that have been updated in the current time
        # step. key is time, value is a list of the cars that have been updated in that time step
        # along with current node

    def add_update_to_dictionary(self, time, car_id, x, y, node_id):
        """
        Add car update information to the dictionary.

        Args:
        time (datetime.datetime): Time of the update.
        car_id (int): ID of the car.
        x (float): X-coordinate of the car's position.
        y (float): Y-coordinate of the car's position.
        node_id (int): ID of the current node.

        :return:
        None
        """
        if time not in self.simulation_update_times:
            self.simulation_update_times[time] = []
        self.simulation_update_times[time].append((car_id, (x, y), node_id))

    def add_car(self, car: Car, time):
        """
        Add a car to the simulation.

        :param:
        car (Car): Car object to be added.
        time (datetime.datetime): Current time in the simulation.

        :return:
        None
        """
        car_starting_time = car.starting_time
        if car_starting_time > time:  # car is not ready to enter the simulation
            self.cars_waiting_to_enter.append(car)
            self.cars_waiting_to_enter.sort(key=lambda x: x.starting_time)

        else:  # car is ready to enter the simulation
            car.start_car()
            self.cars_in_simulation[car.id] = car
        self.sort_cars_in_simulation()
        self.calc_nearest_update_time(time)
        x, y = car.get_xy_source()
        self.add_update_to_dictionary(car_starting_time, car.id, x, y, car.source_node)
        return

    def sort_cars_in_simulation(self):
        """
        Sort cars in the simulation based on the time until the next road.
        Update the nearest update time.

        :return:
        bool: False if no cars are in simulation, True otherwise.
        """
        # sort the dict by the time until the next road
        # also update the nearest update time
        if len(self.cars_in_simulation) == 0:
            return False

        self.cars_in_simulation = dict(
            sorted(self.cars_in_simulation.items(), key=lambda item: item[1].get_time_until_next_road()))
        first_index, first_car = next(iter(self.cars_in_simulation.items()))
        self.cars_nearest_update_time = first_car.get_time_until_next_road()
        return True

    def calc_nearest_update_time(self, time: datetime.datetime):
        """
        Calculate the time of the nearest update.

        :param time :(datetime.datetime) Current time in the simulation.

        :return:
        int: The time of the nearest update.
        """
        if self.cars_waiting_to_enter:
            date_time = self.cars_waiting_to_enter[0].starting_time  # datetime object
            time1 = int((date_time - time).total_seconds())  # timedelta object
        else:
            time1 = float('inf')

        if self.cars_in_simulation:
            first_index, first_car = next(iter(self.cars_in_simulation.items()))
            time2 = first_car.get_time_until_next_road()  # int object
        else:
            time2 = float('inf')
        self.cars_nearest_update_time = min(time1, time2)
        return self.cars_nearest_update_time

    def find_earliest_waiting_car(self):

        """
        Find the earliest time that a car is waiting to enter the simulation.

        :return:
        datetime.datetime or None: The earliest starting time of a waiting car, or None if no cars are waiting.
        """
        if not self.cars_waiting_to_enter:
            return None
        starting_time = self.cars_waiting_to_enter[0].starting_time
        for car in self.cars_waiting_to_enter:
            if car.starting_time < starting_time:
                starting_time = car.starting_time
        return starting_time

    def update_cars(self, timeStamp: int, current_datetime: datetime.datetime):
        """
        Update all the cars in the simulation.

        :param:
        timeStamp (int): The simulation time step.
        current_datetime (datetime.datetime): Current time in the simulation.

        :return:
        None
        """
        cars = self.cars_in_simulation.copy()
        blocked_cars = self.cars_blocked.copy()

        for key in self.cars_in_simulation:
            car = cars[key]
            current_travel_time = car.update_travel_time(timeStamp)

            # if the car travel time is longer than 2 hours, then force finish the car
            if current_travel_time > self.max_time_for_car:
                car.force_finish()
                self.cars_stuck.append(car)
                x, y = car.get_xy_destination()
                self.add_update_to_dictionary(current_datetime, car.id, x, y, car.destination_node)
                cars.pop(car.id)

            elif car.get_time_until_next_road() == 0:
                # car is ready to move to the next road
                result = car.move_next_road()  # result is the next road the car is on

                # add update to list
                x, y = car.get_xy_current()
                self.add_update_to_dictionary(current_datetime, car.id, x, y, car.current_road.source_node.id)

                if result is None:  # car is finished or stuck
                    cars.pop(car.id)

                    if car.car_in_destination:
                        print("car", car.id, "finished his journey after", car.total_travel_time)
                        self.cars_finished.append(car)
                        x, y = car.get_xy_destination()
                        self.add_update_to_dictionary(current_datetime, car.id, x, y, car.destination_node)
                    else:
                        print("car", car.id, "is stuck")
                        self.cars_stuck.append(car)

                elif result == "blocked":  # car is blocked
                    print("car", car.id, "is blocked in road ", car.current_road.id)
                    self.cars_blocked.append(car)
                    car.is_blocked = True
                    blocked_cars.append(car)


        # after we updated all the cars, we need to handle the waiting cars
        copy_waiting_cars = self.cars_waiting_to_enter.copy()
        for car in copy_waiting_cars:
            if car.starting_time <= current_datetime:
                car.start_car()
                cars[car.id] = car
                self.cars_waiting_to_enter.remove(car)
            else:
                break

        self.cars_in_simulation = cars
        self.cars_blocked = blocked_cars
        self.sort_cars_in_simulation()
        return

    def is_car_stuck(self, car):
        """
        Check if a car is stuck.

        :param:
        car (Car): The car to check.

        :return:
        bool: True if the car is stuck, False otherwise.
        """
        return car in self.cars_stuck

    def is_car_finished(self, car):
        """
        Check if a car has finished its journey.

        :param:
        car (Car): The car to check.

        :return:
        bool: True if the car has finished, False otherwise.
        """
        return car in self.cars_finished

    def clear(self):
        """
        Clear all simulation Graphs and reset the CarManager.

        :return:
        None
        """
        self.cars_in_simulation.clear()
        self.cars_finished.clear()
        self.cars_stuck.clear()
        self.cars_nearest_update_time = 0
        for car in self.cars_blocked:
            car.is_blocked = False
        self.cars_blocked.clear()

    def get_all_cars_ids(self):
        """
        Get the IDs of all cars currently in the simulation and those blocked.

        :return:
        list[int]: List of car IDs.
        """
        return list(self.cars_in_simulation.keys()) + [car.id for car in self.cars_blocked]

    def __str__(self):
        return f'CarManager: Cars in simulation: {self.cars_in_simulation}, Cars blocked: {self.cars_blocked}, Cars finished: {self.cars_finished}, Cars stuck: {self.cars_stuck}'

    def __repr__(self):
        return self.__str__()
