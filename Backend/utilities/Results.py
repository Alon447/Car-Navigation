from datetime import datetime
import json
import os

import networkx as nx
import matplotlib.patches as mpatches
import osmnx as ox
from Utilities.Getters import Time_taken, Reached_destination, Simulation_number, Route, Distance_travelled, node_route_to_osm_route, Source, Destination, Blocked_roads, Route_comparisons_results_directory, get_specific_directory
import matplotlib.pyplot as plt

from models.Road_Network import Road_Network


def save_results_to_JSON(graph_name, results):
    """
    Save simulation results to a JSON file.

    Args:
    graph_name (str): Name of the graph.
    results (dict): Dictionary containing simulation results.

    Returns:
    None
    """
    # self.simulation_results.append(results)
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    json_name = f'simulation_results_{graph_name}_{current_time}'
    with open(f'../Results/{json_name}.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)
    return json_name


def read_results_from_JSON(graph_name):
    """
    Read simulation results from a JSON file.

    Returns:
    dict: Dictionary containing the loaded simulation results.
    """
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    with open(f'../Results/simulation_results_{graph_name}_{current_time}.json', 'r') as infile:
        new_simulation_results = json.load(infile)
    return new_simulation_results

def print_simulation_results(SM):
    """
    simulation_results follow the format:
    all_simulations : [ simulation_1:{simulation_number, car_1_info:{..},car_2_info:{..} }, { {},{} }, { {},{} } ]
    the function prints the results of the simulation in a readable format

    :param SM: Simulation_Manager object

    :return: None
    """
    for result in SM.simulation_results:
        for array_index, result_dict in result.items():
            if array_index != Simulation_number:
                print("*******************************************")
                print("Simulation number: ", result[Simulation_number])

                print(array_index, ": ")
                for key, value in result_dict.items():
                    if key != Route and key != Time_taken and key != Distance_travelled:
                        print(key, ": ", value)
                    elif key == Time_taken:
                        print(key, ": ", int(value / 60), "minutes")
                    elif key == Distance_travelled:
                        print(key, ": ", round(value / 1000, 1), "km")
                    else:
                        print("Route length: ", len(value), "roads")

    return

def plot_simulation_overview(past_result_json_name):
    """
    This function plots the past result of the simulation.

    :param past_result_json_name: The name of the JSON file containing the past result of the simulation.

    :return: None
    """
    global ax, fig, origin_x, dest_x, origin_y, dest_y
    substring_to_remove = "simulation_results_"
    # get the city name from the json name and create a road network object of the city
    graph_name_with_extra = past_result_json_name.replace(substring_to_remove, "")
    graph_name_parts = graph_name_with_extra.split('_')
    graph_name = graph_name_parts[0]  # Get the first part as the base graph name
    RN = Road_Network(graph_name)
    # Load the past result
    with open(f'../Results/{past_result_json_name}.json') as json_file:
        past_result = json.load(json_file)

    origins = []
    destinations = []
    route_labels = []  # List to store labels for each route
    first_simulation = past_result[0]
    routes = []
    edge_colors = ['grey' for edge_id in range(len(RN.roads_array))]

    for key in first_simulation.keys():
        if key != Simulation_number: # Ignore the simulation number
            # get the source and destination and the route of the car
            car_results = first_simulation[key]
            car_source = car_results[Source]
            blocked_roads = car_results[Blocked_roads]
            for road in blocked_roads:
                edge_colors[road[0]] = 'black'
            car_destination = car_results[Destination]
            origin_x, origin_y = RN.get_xy_from_node_id(car_source)
            origins.append((origin_x, origin_y))
            dest_x, dest_y = RN.get_xy_from_node_id(car_destination)
            destinations.append((dest_x, dest_y))
            car_route = car_results[Route]
            routes.append(car_route)
            route_labels.append(f"Route {key}")  # Add a label for the current route
    colors = ['red','blue','green', 'purple','orange']  # Add more colors as needed
    fig, ax = ox.plot_graph(RN.graph, figsize=(10, 10), show=False, close=False,bgcolor = 'white', node_color = 'grey', node_size = 0, edge_color = edge_colors)
    for i,route in enumerate(routes):
        route_osm = node_route_to_osm_route(RN, route)
        color = colors[i%len(colors)]
        ox.plot_graph_route(RN.graph, route_osm, route_color = color, route_linewidth = 2, node_size = 0,
            bgcolor = 'white', show = False, close = False, labal = f"Route {i}", ax = ax)

    plt.title('Past Result of Simulation')
    for i in range(len(origins)):
        orig_x, orig_y = origins[i]
        dest_x, dest_y = destinations[i]
        ax.scatter(orig_x, orig_y, color='black', s=50, label='Start')
        ax.scatter(dest_x, dest_y, color='yellow', s=50, label='End')
    ax.legend()

    plt.show(block=True)
    # plt.pause(2)
    # plt.close()
    return

def plot_simulation_overview_seoul(past_result_json_name, RN, original_routes):
    """
    This function plots the past result of the simulation.

    :param past_result_json_name: The name of the JSON file containing the past result of the simulation.

    :return: None
    """
    global ax, fig, origin_x, dest_x, origin_y, dest_y

    substring_to_remove = "simulation_results_"
    graph_name_with_extra = past_result_json_name.replace(substring_to_remove, "")
    graph_name_parts = graph_name_with_extra.split('_')
    graph_name = graph_name_parts[0]  # Get the first part as the base graph name
    with open(f'../Results/{past_result_json_name}.json') as json_file:
        past_result = json.load(json_file)

    origins = []
    destinations = []
    route_labels = []  # List to store labels for each route
    first_simulation = past_result[0]
    routes = []
    edge_colors = ['grey' for edge_id in range(len(RN.roads_array))]

    for key in first_simulation.keys():
        if key != Simulation_number: # Ignore the simulation number
            # get the source and destination and the route of the car
            car_results = first_simulation[key]
            car_source = car_results[Source]
            blocked_roads = car_results[Blocked_roads]
            for road in blocked_roads:
                edge_colors[road[0]] = 'black'
            car_destination = car_results[Destination]
            origin_x, origin_y = RN.get_xy_from_node_id(car_source)
            origins.append((origin_x, origin_y))
            dest_x, dest_y = RN.get_xy_from_node_id(car_destination)
            destinations.append((dest_x, dest_y))
            car_route = car_results[Route]
            routes.append(car_route)
            route_labels.append(f"Route {key}")  # Add a label for the current route
    colors = ['red','blue','green', 'purple','orange']  # Add more colors as needed
    plt.figure(figsize = (10, 10))
    ax = plt.gca()
    edges_of_interest = []
    for i,node in enumerate(original_routes[0][:-1]):
        u = node
        v = original_routes[0][i+1]
        edges_of_interest.append((u+1,v+1,0))
    # Draw the graph edges and nodes
    G = RN.graph.edge_subgraph(edges_of_interest)

    pos = nx.spring_layout(G )
    nx.draw(G , pos, with_labels = True, node_size = 50, edge_color = edge_colors, ax = ax)

    # Draw the graph edges and nodes
    pos = nx.spring_layout(RN.graph)
    nx.draw(G, pos, with_labels = True, node_size = 50, edge_color = edge_colors, ax = ax)
    plt.title('Graph Visualization')
    plt.show()

    fig, ax = ox.plot_graph(RN.graph, figsize=(10, 10), show=False, close=False,bgcolor = 'white', node_color = 'grey', node_size = 0, edge_color = edge_colors)
    for i,route in enumerate(routes):
        route_osm = node_route_to_osm_route(RN, route)
        color = colors[i%len(colors)]
        ox.plot_graph_route(RN.graph, route_osm, route_color = color, route_linewidth = 2, node_size = 0,
            bgcolor = 'white', show = False, close = False, labal = f"Route {i}", ax = ax)

    plt.title('Past Result of Simulation')
    for i in range(len(origins)):
        orig_x, orig_y = origins[i]
        dest_x, dest_y = destinations[i]
        ax.scatter(orig_x, orig_y, color='black', s=50, label='Start')
        ax.scatter(dest_x, dest_y, color='yellow', s=50, label='End')
    ax.legend()

    plt.show(block=True)
    # plt.pause(2)
    # plt.close()
    return

def car_times_bar_chart(SM, car_number):
        """
        This function plots a bar chart of the times of a specific car in the simulation.

        :param SM: Simulation_Manager object
        :param car_number: The car number for which the chart will be plotted.
        """
        times = []
        colors = []

        for result in SM.simulation_results:
            car_key = f'{car_number}'
            times.append(result[car_key][Time_taken])
            if result[car_key][Reached_destination]:
                colors.append('green')
            else:
                colors.append('red')
        # time_seconds = [td.total_seconds() for td in times]
        plt.bar((range(1, len(times) + 1)), times, color=colors)

        # Add labels and title
        plt.xlabel('Simulation Number')
        plt.ylabel('Time taken [seconds] by Car {}'.format(car_number))
        plt.title('Bar Chart: Times of Car {} in Simulation'.format(car_number))
        legend_labels = ['Reached Destination', 'Not Reached Destination']
        legend_colors = ['green', 'red']
        legend_patches = [mpatches.Patch(color=color, label=label) for color, label in
                          zip(legend_colors, legend_labels)]

        plt.legend(handles=legend_patches, title='Legend', loc='upper right')
        plt.show()
        return


def get_simulation_times(SM):
    """
    This function returns the times of all cars in the simulation in a list.
    :param SM:
    :return: (list): all the times of the cars in the simulation
    """
    times = []
    for result in SM.simulation_results:
        for array_index, result_dict in result.items():
            if array_index != Simulation_number:
                times.append(result_dict[Time_taken])
    return times

# plot q learning results
def car_times_bar_chart_Q_agent(src, dst, all_training_paths_nodes, all_training_times, ax=None):

    if ax is None:
        ax = plt.gca()
    colors = []

    for path in all_training_paths_nodes:
        if path[-1] == dst:
            colors.append('green')
        else:
            colors.append('red')
    # time_seconds = [td.total_seconds() for td in times]
    ax.bar((range(1, len(all_training_times) + 1)), all_training_times, color=colors)

    # Add labels and title
    ax.set_xlabel('Simulation Number')
    ax.set_ylabel('Time taken [seconds] by Q Agent')
    ax.set_title('Bar Chart: Times of Q Agent in Simulation, Source: {}, Destination: {}'.format(src, dst))
    legend_labels = ['Reached Destination', 'Not Reached Destination']
    legend_colors = ['green', 'red']
    legend_patches = [mpatches.Patch(color=color, label=label) for color, label in
                      zip(legend_colors, legend_labels)]

    ax.legend(handles=legend_patches, title='Legend', loc='upper right')

def plot_rewards(src, dst, var:list, ax=None):
    """
    Plot the mean rewards over training episodes.

    Args:
        var (list): List of mean rewards.

    Returns:
        None
    """
    if ax is None:
        ax = plt.gca()

    ax.plot(range(1, len(var) + 1), var)
    ax.set_xlabel('Interval (Every 50 Episodes)')
    ax.set_ylabel('Mean Episode Reward')
    ax.set_title('Mean Rewards over Training, Source: {}, Destination: {}'.format(src, dst))

def plot_results(src, dst, all_training_paths_nodes, all_training_times, mean_rewards):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))  # Create a 2-row, 1-column subplot layout

    car_times_bar_chart_Q_agent(src, dst, all_training_paths_nodes, all_training_times, ax1)
    plot_rewards(src, dst, mean_rewards, ax2)

    plt.tight_layout()  # Adjust layout for better spacing
    plt.show(block=True)
    # plt.pause(5)
    # plt.close()
    return

def get_results_files(*filters):
    if len(filters) == 0:
        filters = [".json"]
    results_files = {}
    for filter in filters:
        results_files[filter] = []
    for file in os.listdir(get_specific_directory(Route_comparisons_results_directory)):
        for filter in filters:
            if file.endswith(filter):
                results_files[filter].append(file)
    return results_files