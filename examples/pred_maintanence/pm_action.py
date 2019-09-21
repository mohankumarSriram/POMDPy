from __future__ import print_function
from builtins import object
from pomdpy.discrete_pomdp import DiscreteAction

class ActionType(object):
    """
    Lists the possible actions and attributes an integer code to each for the Rock sample problem
    """
    NO_REPAIR = 0
    REPAIR = 1

class PMAction(DiscreteAction):
    """
    -The Predictive Maintanence problem Action class
    -Handles pretty printing
    """
    def __init__(self, action_type):
        super(PMAction, self).__init__(action_type)
        self.bin_number = action_type

    def copy(self):
        return PMAction(self.bin_number)

    def print_action(self):
        if self.bin_number is ActionType.REPAIR:
            action = "Repairing"
        elif self.bin_number is ActionType.NO_REPAIR:
            action = "Not Repairing"
        return action

    def to_string(self):
        if self.bin_number is ActionType.REPAIR:
            action = "Repairing"
        elif self.bin_number is ActionType.NO_REPAIR:
            action = "Not Repairing"
        else:
            action = "UNDEFINED ACTION"
        return action

    def distance_to(self, other_point):
        pass
 