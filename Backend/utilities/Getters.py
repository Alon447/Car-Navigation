import os
import random
import networkx as nx
import osmnx as ox

import Utilities.Speeds as Speeds

# Simulation results dictionary keys
Simulation_number = 'Simulation_number'
Source = 'Source'
Destination = 'Destination'
Reached_destination = 'Reached_destination'
Routing_algorithm = 'Routing_algorithm'
Time_taken = 'Time_taken'
Day_of_week = 'Day_of_week'
Start_time = 'Start_time'
End_time = 'End_time'
Route = 'Route'
Roads_used = 'Roads_used'
Blocked_roads = 'Blocked_roads'
Distance_travelled = 'Distance_travelled'
Number_of_episodes = 'Number_of_episodes'
Max_steps_per_episode = 'Max_steps_per_episode'

Hours_key = "Hours"
Minutes_key = "Minutes"
Seconds_key = "Seconds"
Days_label_text = "Days"

# times
minute_in_seconds = 60
hour_in_seconds = 60 * minute_in_seconds
day_in_seconds = 24 * hour_in_seconds
week_in_seconds = 7 * day_in_seconds

hours = [i for i in range(0, 24)]
minutes = [i for i in range(0, 60)]
seconds = [i for i in range(0, 60)]

days = [i for i in range(0, 7)]
weeks = [i for i in range(0, 4)]
months = [i for i in range(0, 12)]


# for simulation
rain_intensity_values = ["None", "Light", "Moderate", "Heavy"]
rain_intensity_dict= {"None":0, "Light":1, "Moderate":2, "Heavy":3}

# Json keys
SP = "Shortest Path"
Q = "Q Learning"


# for statistics and for general use

Start_key = "Start_title"
End_key = "End_title"
Starting_time_title = "Enter simulation earliest starting time:"
Ending_time_title = "Enter simulation latest starting time:"

run_time_data_file_name = "run_time_data.json"
cars_times_file_name = "cars_times.json"

Average_key = "Average"
Standard_deviation_key = "Standard deviation"

Cars = "Cars Driving Times"
Run_Times = "Run Times"
Variables_for_statistics = [Cars, Run_Times]

#   directories
Route_comparisons_results_directory = "Route_comparisons_results"
Q_Tables_directory = "Q Tables Data"
Results_directory = "Results"
Speeds_Data_directory = "Speeds_Data"
Graphs_directory = "Graphs"


# paths

# Route_comparisons_results_path = get_specific_directory(Route_comparisons_results_directory)
# Q_Tables_path = os.path.join(os.getcwd(), Q_Tables_directory)


# for testing and statistics in TLV map:

top_right_nodes = [714,428,963,720,242,969,677,319,206,653,404,970,964,406,684,870]
bottom_left_nodes = [650,604,651,652,135,602,647,803,480,637,644,640,872,884,497,166]

top_left_nodes = [991,989,749,115,113,107,731,730,0,1,9,877,992,704,762]
bottom_right_nodes = [866,443,912,898,960,819,829,506,203,865,505,508,627,658,99,597]
#

day_mapping = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

routing_algorithms = [
    "Q Learning",
    "Shortest Path",
    "Random Path"

]

routing_learning_algorithms = [
    "Q Learning"
]

def get_graph(graph_name: str):
    """
    Load an OSMnx MultiDiGraph from a graphml file.
    If the file does not exist, download the graph from OSMnx and save it as a graphml file.
    The donwloaded graph will be saved in the Graphs folder.

    :param graph_name: the name of the graph file, without the extension

    :returns:
    osmnx multiDiGraph
    """
    cur = os.getcwd()
    parent = os.path.dirname(cur)
    data = os.path.join(parent, "Graphs")
    path = data + "\\" + graph_name + ".graphml"
    GRAPH_DISTANCE = 2500
    if not os.path.exists(path):
        graph = ox.graph_from_address(graph_name, network_type='drive', dist = GRAPH_DISTANCE, simplify = True)
        modified_graph = Speeds.add_max_speed_to_graph(graph) # add max speed to the graph
        ox.save_graphml(modified_graph, filepath=path)

    return ox.load_graphml(path),path

def get_specific_directory(dir_name):
    """
    get the path of a directory in the project, works only if the directory is in the main directory of the project

    :return:
    (str): the updated path
    """
    cur = os.getcwd()
    parent = os.path.dirname(cur)
    path = os.path.join(parent, dir_name)
    return path
def get_simulation_speeds_file_path(graph, graph_name):
    """
    Load a dictionary of speeds for each road in the graph.

    :param graph: the graph
    :param graph_name: the name of the graph file, without the extension


    :return: dictionary of speeds for each road in the graph
    """
    cur = os.getcwd()
    parent = os.path.dirname(cur)
    Speeds_Data = os.path.join(parent, "Speeds_Data")
    path = Speeds_Data + "/" + graph_name + "_speeds.json"
    if not os.path.exists(path):
        Speeds.generate_day_data(graph, graph_name)
        print("file created")
    return path

def time_delta_to_seconds(time):
    """
    transform a time delta to seconds
    :param time: timedelta
    :return:
    """
    return int(time.total_seconds())

def node_route_to_osm_route(road_network, node_route):
    """
    :param node_route: a list of nodes in the route
    :param road_network: the road network
    :return: a list of roads in the route
    """
    osm_route = []
    for i, node in enumerate(node_route):
        osm_route.append(road_network.nodes_array[node].osm_id)
    return osm_route

def get_random_src_dst(RN):
    """
    get a random source and destination from the road network that have a path between them
    :param RN: the road network
    :return: a random source and destination
    """
    src = RN.nodes_array[random.randint(0, len(RN.nodes_array) - 1)]
    dst = RN.nodes_array[random.randint(0, len(RN.nodes_array) - 1)]
    while not nx.has_path(RN.nx_graph, src.id, dst.id) and src.id != dst.id:
        src = RN.nodes_array[random.randint(0, len(RN.nodes_array) - 1)]
        dst = RN.nodes_array[random.randint(0, len(RN.nodes_array) - 1)]

    return src.id, dst.id

def get_results_directory_path():
    current_directory = os.getcwd()
    current_directory = os.path.dirname(current_directory)
    directory_path = os.path.join(current_directory, "Results")
    return directory_path

def check_if_path_exist(src,dst,RN):
    try:
        RN.get_shortest_path(src, dst)
        return True
    except:
        return False

def get_starting_time_of_the_day(hour):
    """
    converts the hour into a string that represents the time of the day
    7AM-11AM: morning
    12PM-3PM: noon
    4PM-7PM: evening
    8PM-6AM: night
    :param hour: int that represents the starting hour
    :return: string of the start of the day

    """
    if 7 <= hour <= 11:
        return "morning"
    elif 12 <= hour <= 15:
        return "noon"
    elif 16 <= hour <= 19:
        return "evening"
    else:
        return "night"