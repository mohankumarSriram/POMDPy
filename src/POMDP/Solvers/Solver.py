__author__ = 'patrickemami'

import logging
import time
import MCTS
from POMDP.Statistic import Statistic
from POMDP import History
from console import *

module = "Solver"

class Results():
    time = Statistic("Total time")
    reward = Statistic("Total reward")
    discounted_return = Statistic("Discounted Reward")
    undiscounted_return = Statistic("Un-discounted Reward")

    def reset_running_totals(self):
        Results.time.running_total = 0.0
        Results.reward.running_total = 0.0
        Results.discounted_return.running_total = 0.0
        Results.undiscounted_return.running_total = 0.0

class Solver(object):

    def __init__(self, model):
        self.logger = logging.getLogger('Model.Solver')

        self.model = model
        self.action_pool = None
        self.observation_pool = None
        self.results = Results()
        self.histories = History.Histories() # Collection of history sequences

        self.initialize()

    def initialize(self):
        # reset these
        self.action_pool = self.model.create_action_pool()
        self.observation_pool = self.model.create_observation_pool(self)

    def discounted_return(self):

        console(2, module + ".discounted_return", "Main runs")

        self.logger.info("Simulations\tRuns\tUn-discounted Return\tUn-discounted Error\t"
                         + "\tDiscounted Return\tDiscounted Error\tTime\n")

        self.multi_run()

        print "Simulations = ", self.model.sys_cfg["num_sims"]
        print "Runs = ", self.results.time.count
        print "Undiscounted Return = ", self.results.undiscounted_return.mean,
        print " +- ", self.results.undiscounted_return.std_err()
        print "Discounted Return = ", self.results.discounted_return.mean,
        print " +- ", self.results.discounted_return.std_err()
        print "Time = ", self.results.time.mean

        self.logger.info(str(self.model.sys_cfg["num_sims"]) + '\t' + str(self.results.time.count) + '\t'
            + '\t' + str(self.results.undiscounted_return.mean) + '\t' + str(self.results.undiscounted_return.std_err()) + '\t'
            + '\t' + str(self.results.discounted_return.mean) + '\t' + str(self.results.discounted_return.std_err()) + '\t'
            + '\t' + str(self.results.time.mean))

    def multi_run(self):
        num_runs = self.model.sys_cfg["num_runs"]

        for i in range(num_runs):

            print "Starting run ", i+1,
            print " with ", self.model.sys_cfg["num_sims"], " simulations..."

            self.run()
            total_time = self.results.time.mean * self.results.time.count

            if total_time > self.model.sys_cfg["time_out"]:
                print "Timed out after ", i,
                print " runs in ", total_time,
                print " seconds"
                break

    def run(self, num_steps=None):
        run_start_time = time.time()
        discount = 1.0

        if num_steps is None:
            num_steps = self.model.sys_cfg["num_steps"]

        # Reset the running total for each statistic for this run
        self.results.reset_running_totals()

        # Monte-Carlo start state
        state = self.model.sample_an_init_state()

        console(2, module + ".run", "Initial search state: " + state.to_string())

        # Create a new MCTS solver
        mcts = MCTS.MCTS(self, self.model)

        console(2, module + ".run", "num of particles generated = " + str(mcts.policy.root.state_particles.__len__()))

        for i in range(num_steps):
            start_time = time.time()
            # action will be of type Discrete Action
            action = mcts.select_action()

            '''
            if state.position in self.model.rock_positions:
                for entry in mcts.policy.root.action_map.get_all_entries():
                    print "Action = ", entry.bin_number
                    print "Visit count = ", entry.visit_count
                    print "Mean Q Value = ", entry.mean_q_value
                    print "is legal = ", entry.is_legal
            '''
            step_result, is_legal = self.model.generate_step(state, action)

            self.results.reward.add(step_result.reward)
            self.results.undiscounted_return.running_total += step_result.reward
            self.results.discounted_return.running_total += (step_result.reward * discount)

            discount *= self.model.sys_cfg["discount"]
            state = step_result.next_state

            print "======================================================"
            console(2, module + ".run", "Step Result.Action = " + step_result.action.to_string())
            console(2, module + ".run", "Step Result.Observation = " + step_result.observation.to_string())
            console(2, module + ".run", "Step Result.Next_State = " + step_result.next_state.to_string())
            console(2, module + ".run", "Step Result.Reward = " + str(step_result.reward))

            if step_result.is_terminal:
                new_hist_entry = mcts.history.add_entry()
                new_hist_entry.reward = step_result.reward
                new_hist_entry.action = step_result.action
                new_hist_entry.observation = step_result.observation
                new_hist_entry.register_entry(new_hist_entry, None, step_result.next_state)
                print "Terminated after episode step " + str(i)
                break

            out_of_particles = mcts.update(step_result)

            if out_of_particles:
                print "Out of particles, finishing sequence with random actions"
                while i < num_steps:
                    action = self.model.get_random_action()
                    step_result, is_legal = self.model.generate_step(state, action)

                    self.results.reward.add(step_result.reward)
                    self.results.undiscounted_return.running_total += step_result.reward
                    self.results.discounted_return.running_total += (step_result.reward * discount)
                    discount *= self.model.sys_cfg["discount"]
                    state = step_result.next_state

                    console(2, module + ".run", "Step Result.Action = " + step_result.action.to_string())
                    console(2, module + ".run", "Step Result.Observation = " + step_result.observation.to_string())
                    console(2, module + ".run", "Step Result.Next_State = " + step_result.next_state.to_string())
                    console(2, module + ".run", "Step Result.Reward = " + str(step_result.reward))

                    if step_result.is_terminal:
                        print "Terminated"
                        break

                    new_entry = mcts.history.add_entry()
                    new_entry.reward = step_result.reward
                    new_entry.action = step_result.action
                    new_entry.observation = step_result.observation
                    new_entry.register_entry(new_entry, None, step_result.next_state)
                    i += 1
                break
            else:
                print "num of particles pushed over to new root = ", mcts.policy.root.state_particles.__len__()

            elapsed_time = time.time() - start_time
            print "MCTS Step Forward took ", elapsed_time

            if elapsed_time > self.model.sys_cfg["time_out"]:
                print "Timed out after ", i,
                print " runs in ", elapsed_time,
                print " seconds"
                break

        self.results.time.add(time.time() - run_start_time)
        self.results.discounted_return.add(self.results.discounted_return.running_total)
        self.results.undiscounted_return.add(self.results.undiscounted_return.running_total)
        print "Discounted Return statistics"
        print "============================"
        self.results.discounted_return.show()
        print "Un-discounted Return statistics"
        print "=============================="
        self.results.undiscounted_return.show()
        print "Time"
        print "===="
        print self.results.time.show()

        mcts.history.show()








