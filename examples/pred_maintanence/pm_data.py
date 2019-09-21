from __future__ import absolute_import
from pomdpy.pomdp import HistoricalData
from .pm_action import ActionType
import numpy as np


class PMData(HistoricalData):
    """
    Used to store the probabilities that the turbine is in a certain state.
    This is the belief distribution over the set of possible states.
    For a 4-state system, you have
    """
    def __init__(self, model):
        self.model = model
        self.listen_count = 0
        ''' Initially there is an equal probability of the turbine being in either of the states'''
        self.part_condition_probabilities = [0.25, 0.25, 0.25, 0.25]
        self.legal_actions = self.generate_legal_actions

    def copy(self):
        dat = PMData(self.model)
        dat.listen_count = self.listen_count
        dat.part_condition_probabilities = self.part_condition_probabilities
        return dat

    def update(self, other_belief):
        self.part_condition_probabilities = other_belief.data.part_condition_probabilities

    def create_child(self, action, observation):
        next_data = self.copy()

        
        self.listen_count += 1
        '''
        Based on the observation, the door probabilities should change here.
        This is the key update that affects value function
        '''

        ''' ------- Bayes update of belief state -------- '''

        next_data.door_probabilities = self.model.belief_update(np.array([self.part_condition_probabilities]), action,
                                                                observation)
        return next_data

    @staticmethod
    def generate_legal_actions():
        """
        At each non-terminal state, the agent can listen or choose to open the door based on the current door probabilities
        :return:
        """
        return [ActionType.NO_REPAIR, ActionType.REPAIR]

