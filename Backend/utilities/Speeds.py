"""
General utilities for working with speeds.
"""
import datetime
import json
import random

max_speed_mapping = {
    'motorway': 90,
    'trunk': 90,
    'primary': 90,
    'secondary': 70,
    'tertiary': 50,
    'residential': 50,
    'living_street': 30,
    'unclassified': 30
}
mean_mapping = {  # [ no traffic, low traffic, medium traffic, high traffic]
    'motorway': [87, 72, 50, 40],
    'motorway_link': [60, 55, 50, 40],
    'trunk': [87, 72, 50, 40],
    'primary': [87, 72, 50, 40],
    'secondary': [67, 60, 50, 30],
    'tertiary': [45, 37, 30, 25],
    'residential': [45, 37, 30, 25],
    'living_street': [29, 27, 25, 22],
    'unclassified': [29, 27, 25, 22]
}
std_mapping = {  # [ no traffic, low traffic, medium traffic, high traffic]
    'motorway': [3, 4, 5, 7],
    'motorway_link': [3, 4, 5, 7],
    'trunk': [3, 4, 5, 7],
    'primary': [3, 4, 5, 6],
    'secondary': [2, 3, 4, 5],
    'tertiary': [1, 2, 3, 4],
    'residential': [1, 2, 3, 4],
    'living_street': [1, 1, 1, 2],
    'unclassified': [1, 1, 1, 2]
}


def add_max_speed_to_graph(graph):
    """
    Add the max speed of each road to the graph.

    :param graph: osmnx multiDiGraph
    :return: osmnx multiDiGraph with max speed
    """

    for u, v, k, data in graph.edges(keys=True, data=True):
        highway_type = data['highway']
        if isinstance(highway_type, list):
            highway_type = highway_type[0]  # Use the first value in the list as the highway type
        if 'maxspeed' in data:
            maxspeed = data['maxspeed']
            if isinstance(maxspeed, list):
                maxspeed = maxspeed[0]
            if maxspeed.isdigit():
                data['maxspeed'] = int(maxspeed)
            else:
                data['maxspeed'] = int(fix_speed(maxspeed))
        else:
            data['maxspeed'] = max_speed_mapping.get(highway_type, 50)
    return graph


def generate_speed(highway, max_speed, day, current_time):
    """
    Generate a speed for a road based on the day and time.

    :param highway: (str) highway type
    :param max_speed: (int) max speed of the road
    :param day: (int) day of the week
    :param current_time: (datetime) current time

    :return: speed (int)
    """

    if day == 4: # friday
        if 10 < current_time.hour < 16:  # medium traffic, rush hours in friday
            traffic = 2
        elif current_time.hour == 10 or 16 == current_time.hour:  # low traffic, before and after rush hours in friday
            traffic = 1
        else:  # no traffic, night in friday
            traffic = 0
    elif day == 5: # saturday
        if 19 < current_time.hour < 22:  #medium traffic, rush hours in saturday
            traffic = 2
        elif current_time.hour == 19 or 22 == current_time.hour:  # low traffic, before and after rush hours in saturday
            traffic = 1
        else:  # no traffic, night in saturday
            traffic = 0
    else: # sunday - thursday
        if 7 < current_time.hour < 10 or 15 < current_time.hour < 19:  # high traffic, rush hours in sunday - thursday
            traffic = 3
        elif current_time.hour == 7 or 10 == current_time.hour or 15 == current_time.hour or 19 == current_time.hour:  # medium traffic, before and after rush hours in sunday - thursday
            traffic = 2
        elif current_time.hour == 6 or 11 <= current_time.hour <= 14  or 20 == current_time.hour:  # low traffic, before and after rush hours in sunday - thursday
            traffic = 1
        else:  # no traffic, night in sunday - thursday
            traffic = 0

    mean_speed = mean_mapping.get(highway, [30, 30, 30, 30])
    std = std_mapping.get(highway, [3, 3, 3, 3])
    actual_std = std[traffic]
    actual_mean_speed = mean_speed[traffic]
    speed = min(max_speed,int(random.gauss(actual_mean_speed, actual_std)))
    speed = max(0, speed)

    return speed


def generate_day_data(graph, graph_name):
    """
    Generates a dictionary of speeds for each road in the graph
    based on the day of the week and the time of day
    generates a json file with the Graphs

    :param graph: osmnx multiDiGraph
    :param graph_name: (str) name of the city

    :return: None
    """
    number_of_roads = len(graph.edges)
    roads = [str(i) for i in range(number_of_roads)]
    start_time = datetime.datetime(2023, 3, 30, 0, 0)
    end_time = datetime.datetime(2023, 3, 31, 0, 0)

    # Define the interval
    interval = datetime.timedelta(minutes=10)

    # Initialize the dictionary
    data = {}
    for day in range(7):
        data[day] = {}
        for road in roads:
            data[day][road] = {}

    # Loop over the interval and generate random speeds for each road
    current_time = start_time
    while current_time < end_time:
        time_str = current_time.strftime("%H:%M")
        for day in range(7):
            for i, edge_data in enumerate(graph.edges.items()):
                i = str(i)
                edge_data = edge_data[1]
                # highway = get_attr(edge_data, 'highway', str)
                # max_speed = get_attr(edge_data, 'maxspeed', int)
                highway = edge_data.get('highway')
                if isinstance(highway, list):
                    highway = str(highway[0])  # Use the first element of the list
                else:
                    highway = str(highway)

                max_speed = edge_data.get('maxspeed')
                if isinstance(max_speed, list):
                    max_speed = int(max_speed[0])  # Use the first element of the list
                else:
                    max_speed = int(max_speed)

                speed = generate_speed(highway, max_speed, day, current_time)
                data[day][i][time_str] = speed

        current_time += interval

    # Print the dictionary
    # print(data)
    path = "../speeds_Data/" + graph_name + "_speeds.json"
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return


def color_edges_by_speed(RN, current_time, blocked_roads):
    """
    Colors the edges of the graph according to the speed of the road at the current time
    uses the roads past speeds dictionary
    used to animate the simulation after it happened

    :param RN: (RoadNetwork)
    :param current_time: (datetime)
    :param blocked_roads: (dict) {road_id: [start_time, end_time]}

    :return: edge_colors (list)
    """
    edge_colors = []

    # we need to make sure that the minutes are rounded to the nearest 10
    rounded_minutes = current_time.minute - (current_time.minute % 10)
    current_time = current_time.replace(minute=rounded_minutes, second=0, microsecond=0)
    for road in RN.roads_array:
        if road.id in blocked_roads.keys():
            # check if the road is blocked at the start time of the simulation
            blocking_start_time = blocked_roads[road.id][0]
            blocking_end_time = blocked_roads[road.id][1]
            if blocking_start_time <= current_time <= blocking_end_time:
                # if the road is blocked at the start time of the simulation, color it black
                edge_colors.append('black')
                continue
        ratio = road.past_speeds[current_time] / road.max_speed
        if ratio < 0.4:
            edge_colors.append('red')
        elif ratio < 0.75:
            edge_colors.append('orange')

        else:
            edge_colors.append('green')
    return edge_colors

def color_edges_by_speed_json(graph_name, day_int ,RN, current_time, blocked_roads):
    """
    Colors the edges of the graph according to the speed of the road at the current time
    uses the json speed file
    used when loading a simulation from a json file

    :param graph_name: (str) name of the city
    :param day_int: (int) day of the week
    :param RN: (RoadNetwork)
    :param current_time: (datetime)
    :param blocked_roads: (dict) {road_id: [start_time, end_time]}

    :return: edge_colors (list)
    """
    file_name = "../Speeds_Data/" + graph_name + "_speeds.json"
    with open(file_name) as json_file:
        data = json.load(json_file)
    speeds = data[str(day_int)]
    edge_colors = []

    # we need to make sure that the minutes are rounded to the nearest 10
    rounded_minutes = current_time.minute - (current_time.minute % 10)
    current_time = current_time.replace(minute=rounded_minutes, second=0, microsecond=0)
    for road in RN.roads_array:

        if road.id in blocked_roads.keys():
            blocking_start_time = blocked_roads[road.id][0]
            blocking_end_time = blocked_roads[road.id][1]
            date_format = "%Y-%m-%d %H:%M:%S"  # Year, Month, Day, Hour, Minute, Second

            # Use datetime.strptime to parse the string into a datetime object
            blocking_start_time = datetime.datetime.strptime(blocking_start_time, date_format)
            blocking_end_time = datetime.datetime.strptime(blocking_end_time, date_format)
            if blocking_start_time <= current_time <= blocking_end_time:
                # if the road is blocked at the start time of the simulation, color it black
                edge_colors.append('black')
                continue
        str_id = str(road.id)
        str_time = str(current_time.strftime("%H:%M"))
        if speeds[str_id][str_time] < 25:
            edge_colors.append('red')
        elif speeds[str_id][str_time] < 37:
            edge_colors.append('orange')
        else:
            edge_colors.append('green')
    return edge_colors

def fix_speed(speed_str):
    """
    Converts a speed string to an integer

    :param speed_str: (str) speed string

    :return: speed (int)
    """
    fixed_speed_kmph = 0
    if 'knots' in speed_str:
        speed_str = speed_str.replace('knots', '')
        fixed_speed_kmph = float(speed_str) * 1.852
    elif 'mph' in speed_str:
        speed_str = speed_str.replace('mph', '')
        fixed_speed_kmph = float(speed_str) * 1.60934
    elif 'RO:urban' in speed_str:
        fixed_speed_kmph = 50
    elif 'RO:rural' in speed_str:
        fixed_speed_kmph = 90
    elif 'RO:trunk' in speed_str:
        fixed_speed_kmph = 110

    return fixed_speed_kmph