from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from past.utils import old_div
from builtins import str
from builtins import map
from builtins import hex
from builtins import range
from past.utils import old_div
import logging
import json
import numpy as np
from pomdpy.util import console, config_parser
from .pm_state import PMState
from .pm_action import *
from .pm_observation import PMObservation
from .pm_data import PMData
from pomdpy.discrete_pomdp import DiscreteActionPool, DiscreteObservationPool
from pomdpy.pomdp import Model, StepResult

module = "PMModel"

class PMModel(Model):
    def __init__(self, args):
        print('creating predictive maintanence model')
        super(PMModel, self).__init__(args)
        print('args', args)
        self.observations = np.load(args['data_dir'])
        self.cur_idx = 0
        self.end_idx = len(self.observations)-1
        print('Obtained observations:', self.observations.shape,'for predictive maintanence')
        self.num_states = 4
        self.num_actions = 2
        self.num_observations = 3 # Dataframe column size

    def start_scenario(self):
        self.tiger_door = np.random.randint(0, self.num_doors) + 1

    ''' --------- Abstract Methods --------- '''

    def is_terminal(self, state):
        if state.did_fail:
            return True
        else:
            return False

    def sample_an_init_state(self):
        return self.sample_state_uninformed()

    def create_observation_pool(self, solver):
        return DiscreteObservationPool(solver)

    def sample_state_uninformed(self):
        possible_states = [0, 1, 2, 3]
        return PMState(False, np.random.choice(possible_states))

    def sample_state_informed(self, belief): # TODO
        """

        :param belief:
        :return:
        """
        return belief.sample_particle()

    def get_all_states(self):
        """
        Did part fail + current condition of the part.
        :return:
        """
        return [[False, 0], [False, 1], [False, 2], [True, 3]]

    def get_all_actions(self):
        """
        Two unique actions
        :return:
        """
        return [PMAction(ActionType.NO_REPAIR), PMAction(ActionType.REPAIR)]

    def get_all_observations(self):
        """
        Returning the mean for all the 3 observations
        :return:
        """
        return [0.5, 0.5, 0.5]

    def get_legal_actions(self, _):
        return self.get_all_actions()

    def is_valid(self, _):
        return True

    def reset_for_simulation(self): # TO BE CHANGED
        self.start_scenario()

    # Reset every "episode"
    def reset_for_epoch(self):
        self.start_scenario()

    def update(self, step_result):
        pass

    def get_max_undiscounted_return(self):
        return 10

    @staticmethod
    def get_transition_matrix():
        """
        |A| x |S| x |S'| matrix, for predictive maintanence problem this is 2 x 4 x 4
        :return:
        """
        return np.array([
            [[0.5, 0.5, 0.0, 0.0], [0.0, 0.5, 0.5, 0.0], [0.0, 0.0, 0.5, 0.5], [0.0, 0.0, 0.0, 1.0]],   # When no repair, equal transition probabilities
            [[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]] # After repair, all states except for terminal state return to perfect health condition
        ])

    @staticmethod
    def get_observation_matrix():
        '''
        Maybe not required for our use case
        '''
        """
        |A| x |S| x |O| matrix
        :return:
        """
        return np.array([
            [[0.25, 0.25, 0.75], [0.5, 0.50, 0.75], [0.5, 0.75, 0.5], [0.75, 0.75, 0.25]],   # When no repair, equal transition probabilities
            [[0.25, 0.25, 0.75], [0.25, 0.25, 0.75], [0.25, 0.25, 0.75], [0.25, 0.25, 0.75]] # After repair, all states except for terminal state return to perfect health condition
        ])

    @staticmethod
    def get_reward_matrix():
        """
        |A| x |S| matrix
        :return:
        """
        return np.array([
            [100, 50., 0, -50],     # Taking no repair action for different part conditions
            [-50.0, 0.0, 50, 100],  # Taking repair action for different part conditions
        ])

    @staticmethod
    def get_initial_belief_state():
        return np.array([0.25, 0.25, 0.25, 0.25])

    ''' Factory methods '''

    def create_action_pool(self):
        return DiscreteActionPool(self)

    def create_root_historical_data(self, agent):
        return PMData(self)

    ''' --------- BLACK BOX GENERATION --------- '''

    def generate_step(self, action, state=None):
        if action is None:
            print("ERROR: Tried to generate a step with a null action")
            return None
        elif not isinstance(action, PMAction):
            action = PMAction(action)

        result = model.StepResult()
        result.is_terminal = self.make_next_state(action)
        result.action = action.copy()
        result.observation = self.make_observation(action)
        result.reward = self.make_reward(action, result.is_terminal)

        return result

    def make_next_state(self, action):
        # Check if next observation is terminal and then decide.
        if action.bin_number == ActionType.NO_REPAIR:
            return self.cur_idx == self.end_idx-1 # Check if my current observation has reached the end of all possible observations

    def make_reward(self, action, is_terminal):
        """
        :param action:
        :param is_terminal:
        :return: reward
        """

        

    def make_observation(self, action):
        """
        :param action:
        :return:
        """
        if action.bin_number == ActionType.REPAIR:
            # Go back to the first observation
            self.cur_idx = 0
        else:
            self.cur_idx += 1

        return self.observations[cur_idx]


    def belief_update(self, old_belief, action, observation):
        """
        Belief is a 2-element array, with element in pos 0 signifying probability that the tiger is behind door 1

        :param old_belief:
        :param action:
        :param observation:
        :return:
        """
        b_new_nonnormalized = []
        L = len(self.get_all_states())
        Z = self.get_observation_matrix()
        T = self.get_transition_matrix()
        
        for s_prime in range(L):
            p_o_prime = Z[action][s_prime]
            summation = 0.0
            for s in range(L):
                p_s_prime = self.T[action][s][s_prime]
                b_s = float(old_belief[s])
                summation = summation + p_s_prime * b_s
            b_new_nonnormalized.append(p_o_prime * summation)

        # normalize
        b_new = []
        total = sum(b_new_nonnormalized)
        for b_s in b_new_nonnormalized:
            b_new.append([b_s/total])
        return np.array(b_new)