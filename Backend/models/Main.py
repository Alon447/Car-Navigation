import datetime
import Simulation_manager
from Utilities.Getters import get_random_src_dst
from Utilities.Results import save_results_to_JSON, read_results_from_JSON, car_times_bar_chart, print_simulation_results, plot_simulation_overview, get_simulation_times
from models import Car

# initializes
START_TIME1 = datetime.datetime(year = 2023, month = 10, day = 4, hour = 8, minute = 0, second = 0)
START_TIME2 = datetime.datetime(year = 2023, month = 10, day = 4, hour = 14, minute = 0, second = 0)

# Constants for time intervals
WEEK = 604800
DAY = 86400
HOUR = 3600
MINUTE = 60

# Simulation parameters
NUMBER_OF_SIMULATIONS = 1
TRAFFIC_LIGHTS = False
TRAFFIC_WHITE_NOISE = False
Rain_intensity = 0  # 0-3 (0 = no rain, 1 = light rain, 2 = moderate rain, 3 = heavy rain)

# Q-Learning parameters
USE_ALREADY_GENERATED_Q_TABLE = True
NUM_EPISODES = 2000

# Animation parameters
ANIMATE_SIMULATION = True
REPEAT = True
SIMULATION_SPEED = 5  # X30 faster than one second interval

PLOT_RESULTS = True

# Initialize Simulation Manager
PLACE_NAME = 'TLV'
SM = Simulation_manager.Simulation_manager(PLACE_NAME, TRAFFIC_LIGHTS, Rain_intensity, TRAFFIC_WHITE_NOISE, PLOT_RESULTS, START_TIME1)
# CM = SM.car_manager
RN = SM.road_network

# Block roads
# SM.update_road_blockage(1097 ,start_time = START_TIME1,  end_time = START_TIME1 + datetime.timedelta(hours=1))

# Initialize cars
cars = []

src1, dst1 = 719, 665
src2, dst2 = 200, 300
src3, dst3 = 300, 400
cars.append(Car.Car(1, src1, dst1, START_TIME1, RN, route_algorithm = "sp", use_existing_q_table = USE_ALREADY_GENERATED_Q_TABLE))
cars.append(Car.Car(2, src2, dst2, START_TIME1, RN, route_algorithm = "sp", use_existing_q_table = USE_ALREADY_GENERATED_Q_TABLE))
cars.append(Car.Car(3, src3, dst3, START_TIME1, RN, route_algorithm = "sp", use_existing_q_table = USE_ALREADY_GENERATED_Q_TABLE))

#
# # Run simulations
# SM.run_full_simulation(cars, NUMBER_OF_SIMULATIONS, num_episodes=3000, max_steps_per_episode=100)
# routes = SM.get_simulation_routes(cars, 0)
#
# # Initialize Animation
# ASS = AS.Animate_Simulation(animation_speed=SIMULATION_SPEED, repeat=REPEAT)
#
# json_name = save_results_to_JSON(SM.graph_name, SM.simulation_results)
# # SM.simulation_results = read_results_from_JSON(SM.graph_name)
# times = get_simulation_times(SM)
#
# print_simulation_results(SM)
#
# plot_simulation_overview(json_name)
# # car_times_bar_chart(SM, 2)
# # car_times_bar_chart(SM, 1)
# # car_times_bar_chart(SM, 3)
#
# # Manage and display simulation results
# # Plot and display simulation results
# if ANIMATE_SIMULATION:
#     ASS.plot_simulation(SM, routes, cars)
#
