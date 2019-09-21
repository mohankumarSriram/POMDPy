from __future__ import print_function
from builtins import str
from pomdpy.discrete_pomdp import DiscreteState


class PMState(DiscreteState):
    """
    Enumerated state for the Predictive Maintainence POMDP

    Consists of a boolean "did_fail" containing info on whether the state is terminal
    or not. Terminal states are reached after a part fails. This aspect of the state is 
    *clearly* not fully observable

    The Integer "part_condition" tells about the current state of the part
        0 -> Perfect Health
        1 -> Good Health
        2 -> Low Health
        3 -> Failing
        --------------------------------------------------------------
        Placeholder for showing that the Markov Chain has reached an absorbing state ->

        did_fail = True, part_condition = 3
    """
    def __init__(self, did_fail, part_condition):
        self.did_fail = did_fail
        self.part_condition = part_condition

    def distance_to(self, other_state):
        return self.equals(other_state)

    def copy(self):
        return PMState(self.did_fail, self.part_condition)

    def equals(self, other_state):
        if self.did_fail == other_state.did_fail and \
                self.part_condition == other_state.part_condition:
            return 1
        else:
            return 0

    def hash(self):
        pass

    def as_list(self):
        """
        Concatenate both numbers
        :return:
        """
        return self.did_fail + self.part_condition

    def to_string(self):
        if self.did_fail:
            state = 'Part has failed'
        else:
            state = 'Part is working'
        return state + ' (' + str(self.part_condition) + ')'

    def print_state(self):
        print(self.to_string())

