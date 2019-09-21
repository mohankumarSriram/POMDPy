from __future__ import print_function
from pomdpy.discrete_pomdp import DiscreteObservation
import numpy as np


class PMObservation(DiscreteObservation):
    """
    3 dimensional observation
    """
    def __init__(self, observations):
        self.observations = observations
        self.bin_number = 0

    def copy(self):
        return PMObservation(self.observations)

    def equals(self, other_observation):
        return self.observations == other_observation.observations

    def distance_to(self, other_observation):
        return sum((self.observations - other_observation.observations)**2)

    def hash(self):
        return self.bin_number

    def print_observation(self):
        print(self.observations)

    def to_string(self):
        return 'All values in numpy'



