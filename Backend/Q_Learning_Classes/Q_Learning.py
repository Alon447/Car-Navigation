import datetime
import os
import pickle
from tqdm import tqdm

from Q_Learning_Classes import Q_Agent
from Utilities.Getters import get_specific_directory, get_starting_time_of_the_day, get_simulation_speeds_file_path
from Utilities.Results import plot_results


class Q_Learning:
    """
    Class for applying the Q-learning algorithm in a road network.
    Q_Agent is a class that represents an agent in the Q-learning algorithm. and it is defined in Q_Agent.py
    Most of the functions are defined in Q_Agent.py
    This is like a main class that runs the Q-learning algorithm for all the agents
    """

    def __init__(self, road_network, eta_data, cars, num_episodes = 2000, max_steps_per_episode = 100, learning_rate = 0.1, discount_factor = 0.9, epsilon = 0.2):
        """
        Initialize the Q_Learning class.

        Args:
            road_network (Road_Network): The road network for which the Q-learning algorithm is applied.
            learning_rate (float): The learning rate for updating Q-values.
            discount_factor (float): The discount factor for future rewards in Q-learning.
            epsilon (float): The exploration-exploitation trade-off factor.

        Returns:
            None
        """
        # General
        self.road_network = road_network
        self.cars_list = cars
        self.eta_data = eta_data
        self.agent_list = []  # list of agents

        # Q Learning Parameters
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.num_episodes = num_episodes
        self.max_steps_per_episode = max_steps_per_episode

    def save_q_table(self, agent: Q_Agent, save_path):
        """
        Save the Q-value table to a file.For the Q Learning training we set the following parameters:
Number of training episodes to 2000, maximum number of number of steps in each episode to 100, learning rate to 0.05, discount factor to 0.9 and epsilon to 0.2. the parameter's values were decided by trial and error until we got it to the a sweet spot where the agent's training won't take too long but the agent will learn the optimal path.


        Args:
            agent (Q_Agent): The agent for which the Q-value table is saved.
            save_path (str): The path to save the Q-value table.

        Returns:
            None
        """
        # add the blocked roads to the filename
        blocked_roads = self.road_network.blocked_roads_dict
        blocked_roads_str = '_blocked_roads'
        if blocked_roads:
            for block_road in blocked_roads:
                if blocked_roads[block_road][0] <= agent.start_time <= blocked_roads[block_road][1]:
                    blocked_roads_str += '_' + str(block_road)
        if blocked_roads_str == '_blocked_roads':
            blocked_roads_str = ''
        # add the car's starting hour and the day of the week to the filename
        time_of_the_day = get_starting_time_of_the_day(agent.start_time.hour)

        day_of_week = agent.start_time.weekday()
        filename = os.path.join(save_path, f'q_table_{self.road_network.graph_name}_{agent.src}_{agent.dst}_{time_of_the_day}_{day_of_week}{blocked_roads_str}.pkl')
        with open(filename, 'wb') as f:
            pickle.dump(agent.q_table, f)

    def train(self, start_time: datetime, epsilon_decay_rate = 0.9995, is_plot_results = True):
        """
        Train the Q-learning agent for a source-destination pair.

        Args:
            start_time (datetime): The start time of the simulation.
            epsilon_decay_rate (float): The rate of epsilon decay.
            is_plot_results (bool): A flag indicating whether to plot the results.

        Returns:
            list: The Q-value table after training.
        """
        print("*********************************************")
        print("          Training Started                   ")
        print("*********************************************")
        # initialize the agents and the q-tables
        for car in self.cars_list:
            self.agent_list.append(Q_Agent.Q_Agent(car.source_node, car.destination_node, car.starting_time, self.road_network))
            self.agent_list[-1].initialize_q_table()

        blocked_roads = self.road_network.blocked_roads_dict
        for episode in tqdm(range(self.num_episodes), desc = "Episodes", unit = "episode"):
            for step in range(self.max_steps_per_episode):  # every car can take max_steps_per_episode steps
                if self.check_all_agents_done():
                    # if all agents are done, then move to the next episode
                    break  # Exit the episode loop

                for i, agent in enumerate(self.agent_list):
                    # for every agent we need to update the state, action, next_state, reward
                    if agent.finished or agent.blocked:
                        # if the agent is done, then move to the next agent
                        continue
                    agent.step(self.epsilon)
                    reward = agent.calculate_reward(blocked_roads)
                    agent.total_episode_reward += reward
                    agent.update_q_table(reward, self.learning_rate, self.discount_factor)
                    agent.move_to_next_road(self.max_steps_per_episode)

            for agent in self.agent_list:
                # end of episode, we need to update the agent and get him ready for the next episode
                agent.reset()

            self.epsilon *= epsilon_decay_rate

        print("*********************************************")
        print("          Training Finished                  ")
        print("*********************************************")

        # Plot mean rewards
        for agent in self.agent_list:
            print(agent.all_training_paths_nodes[-1])

            if is_plot_results:
                plot_results(agent.src, agent.dst, agent.all_training_paths_nodes, agent.all_training_times, agent.mean_rewards)
            self.save_q_table(agent, get_specific_directory("Q Tables Data"))
        return

    def check_all_agents_done(self):
        """
        Check if all agents are done.

        Returns:
            bool: True if all agents are done, False otherwise.
        """
        for agent in self.agent_list:
            if not (agent.finished or agent.blocked):
                return False
        return True
