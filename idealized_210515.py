# -*- coding: utf-8 -*-
"""
Created on Thu May 13 12:17:48 2021

@author: dimit
"""

import sys
import math
import numpy as np
import random
from enum import Enum
import matplotlib.pyplot as plt


debug_flag = True
"""
Definition of the Classes and Functions
"""

class ActionType(Enum):
    WAIT = "WAIT"
    SEED_1 = "SEED_1"
    SEED_2 = "SEED_2"
    SEED_3 = "SEED_3"
    GROW_0 = "GROW_0"
    GROW_1 = "GROW_1"
    GROW_2 = "GROW_2"
    COMPLETE = "COMPLETE"    

    @classmethod
    def cost(cls, type, game):
        return 

class Action:
    
    def __init__(self, type, game=None):
        self.type = type
        self.game = game

    @property
    def cost(self):
        if self.type is ActionType.WAIT:
            return 0
        elif "SEED" in self.type.name:
            return self.game.trees[0]
        elif self.type is ActionType.GROW_0:
            return 1 + self.game.trees[1]
        elif self.type is ActionType.GROW_1:
            return 3 + self.game.trees[2]
        elif self.type is ActionType.GROW_2:
            return 7 + self.game.trees[3]
        elif self.type is ActionType.COMPLETE:
            return 4
        else:
            raise Exception("Action.cost")

    @property
    def req_bool(self):
        r_bool = True
        if self.type is ActionType.WAIT:
            r_bool *= True
        if "SEED" in self.type.name:
            r_bool *= bool(sum(self.game.awake_trees[1:]))
        if "_0" in self.type.name:
            r_bool *= bool(self.game.awake_trees[0])
        if "_1" in self.type.name:
            r_bool *= bool(self.game.awake_trees[1])
        if "_2" in self.type.name:
            r_bool *= bool(self.game.awake_trees[2])
        if "_3" in self.type.name:
            r_bool *= bool(self.game.awake_trees[3])
        if self.type is ActionType.COMPLETE:
            r_bool *= bool(self.game.awake_trees[3])
        return r_bool

    @property
    def is_possible(self):
        if self.cost == 0:
            cost_bool = True
        else:
            cost_bool = (self.game.my_sun >= self.cost)
        return (cost_bool and self.req_bool)
      

class Game:
    
    INCOME = np.array([0, 1, 2, 3])
    
    def __init__(
            self,
            day, turn, nutrients,
            my_sun, my_score,
            awake_trees, dormant_trees,
            parent_game=None, parent_action=None,
        ):
        self.day = day
        self.turn = turn
        self.nutrients = nutrients
        self.my_sun = my_sun
        self.my_score = my_score
        self.awake_trees = np.array(awake_trees, int)
        self.dormant_trees = np.array(dormant_trees, int)

        self.parent_game = parent_game
        self.parent_action = parent_action
        self.children = dict()

    def get_all_attr(self):
        return (
            self.day, self.turn, self.nutrients,
            self.my_sun, self.my_score,
            self.awake_trees, self.dormant_trees
        )

    @property
    def metric(self):
        metric_list = (
            self.day,
            self.turn,
            self.nutrients,
            self.my_sun,
            self.my_score,
            *(self.awake_trees),
            *(self.dormant_trees),
        )
        return metric_list
    
    def __hash__(self):
        return hash(self.metric)
    
    def __eq__(self, other):    
        if not isinstance(other, Game):
            # only equality tests to other `structure` instances are supported
            return NotImplemented
        return self.metric == other.metric

    def __str__(self):
        msg = (
        f"D={self.day}, T={self.turn}, N={self.nutrients}, SP={self.my_sun}, Sc={self.my_score}\n"
        f"Awake   = {self.awake_trees}\n"
        f"Dormant = {self.dormant_trees}\n"
        )
        return msg      

    @property
    def trees(self):
        return self.awake_trees + self.dormant_trees

    @property
    def my_income(self):
        return sum(self.trees * self.INCOME)



    def get_available_actions(self):
        return [at for at in ActionType if Action(at, self).is_possible]

    def apply(self, action_type):
        #print(action_type.name)
        
        action = Action(action_type, self)
        
        assert action.is_possible
        self.my_sun -= action.cost
        self.turn += 1
        
        if action_type is ActionType.WAIT:
            self.day += 1
            self.turn = 0
            self.awake_trees += self.dormant_trees
            self.dormant_trees = np.zeros(4, int)
            self.my_sun += self.my_income
        
        if action_type is ActionType.SEED_1:
            self.awake_trees -= [0, 1, 0, 0]
            self.dormant_trees += [1, 1, 0, 0]

        if action_type is ActionType.SEED_2:
            self.awake_trees -= [0, 0, 1, 0]
            self.dormant_trees += [1, 0, 1, 0]

        if action_type is ActionType.SEED_3:
            self.awake_trees -= [0, 0, 0, 1]
            self.dormant_trees += [1, 0, 0, 1]

        if action_type is ActionType.GROW_0:
            self.awake_trees -= [1, 0, 0, 0]
            self.dormant_trees += [0, 1, 0, 0]

        if action_type is ActionType.GROW_1:
            self.awake_trees -= [0, 1, 0, 0]
            self.dormant_trees += [0, 0, 1, 0]

        if action_type is ActionType.GROW_2:
            self.awake_trees -= [0, 0, 1, 0]
            self.dormant_trees += [0, 0, 0, 1]

        if action_type is ActionType.COMPLETE:
            self.awake_trees -= [0, 0, 0, 1]
            self.my_score += self.nutrients
            self.nutrients -= 1

    def compute_next_action(self):
        return random.choice(self.get_available_actions())
    
    
    def project(self, action_type):
        game = Game(
            *self.get_all_attr(),
            parent_game=self, parent_action=action_type)
        self.children[action_type] = game
        game.apply(action_type)
        return game
    
    def project_all(self):
        for action in self.get_available_actions():
            self.project(action)
        return list(self.children.values())



def history(x):
    operation_list = []
    if x.parent_game:
        operation_list.insert(0, x.parent_action.name)
        operation_list = history(x.parent_game) + operation_list
    return operation_list



# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# Conclusion:
# Ok, so that is quite astounding. It is possible to gain an order of magnitude on the 
# number of game state by checking for redundant state. So cutting branches for the future.
# Which could mean that we might gain 2 to 3 turns on the projection range !
# The idea now is to create an algorithm, which prune redundant branches 
# at the start of each day. And which can store the different operations paths
# for each unique game state: so that they can be sorted with additional
# manual criterion(early seed, grow older, etc..
# =============================================================================

# =============================================================================
# Notes
# ------
# 
# Manual Criterion for same game state operation path:
#     - early seed action is best
#     - seed action from older tree is best
#     (later converted to seed action to far and rich tiles)
# 
# Comparing different unique game state:
#     - pruning game state / operations which does not invest effectively
#     Explanation:
#         The earlier the investment is made, the less number of days are wasted.
#         So, in order to speed up projection, we could prune from the available actions,
#         the ones that were already available at the day earlier.
#         Indeed, the game state / operation path which did invest in the same exact
#         action the day earlier will most of the time (only exception I can think of
#         is waiting for a rich tiles to be freed by a tree completion the next day, which
#         will very rarely happen in actual plays) be better.
#         So, We could add a method in Game for getting the available *new* actions,
#         which are less numerous than all the available action.
#         --> of, after thinking a little, one might want to wait another turn
#           to avoid the extra seeding/grow cost (of 1, not much but hey)
# 
# =============================================================================

A = Game(
    day=0, turn=0, nutrients=20,
    my_sun=2, my_score=0,
    awake_trees=[0, 2, 0, 0], dormant_trees=[0, 0, 0, 0]
)

# =============================================================================
# Analysis of all the game state at day N
#   - checking for redundant branches
#   - saving the operation paths (later sorting of this operations paths)
# =============================================================================
day_limit = 4
game_counter = 0
### Game state Tree generation Algotrithm
# Breadth first until next day is reached
# Comparing game state metric and pruning redundant branches

# key is day
children_dict = {k:[] for k in range(10)}

# obtaining all the game state of day 1:
game_queue = [A, ]
while game_queue:
    a = game_queue.pop(0)
    
    if a.turn == 0:
        children_dict[a.day].append(a)
    
    game_counter += 1
    # print("Computing the {} layer, game number {}".format(d, game_counter), end="\r")
    if a.day == day_limit:
        pass
    else:
        children_list = a.project_all()
        game_queue += children_list

#%%
# plt.close('all')

# # all game state at day=4, turn=0
# gs4_list = [game for game in game_list if (game.day==4)]
# print("There are {} game state at day 4.".format(len(gs4_list)))

# # ### number of operations to reach game state
# # op_number_list = [len(history(game)) for game in gs4_list]

# # fig, ax = plt.subplots()
# # ax.grid()

# # bins = np.arange(15)-0.5
# # ax.hist(op_number_list, bins=bins, histtype='bar', rwidth=0.7)

# # ax.set_ylabel('Number of Game State at day=4')
# # ax.set_xlabel('Number of operations (from initial game state)')

# # ### sun points income
# # income_list = [game.my_income for game in gs4_list]

# # fig, ax = plt.subplots()
# # ax.grid()

# # bins = np.arange(15)-0.5
# # ax.hist(income_list, bins=bins, histtype='bar', rwidth=0.7)

# # ax.set_ylabel('Number of Game State at day=4')
# # ax.set_xlabel('Income (in Sun/Day)')

# # ### number of trees
# # tree_number_list = [sum(game.trees) for game in gs4_list]

# # fig, ax = plt.subplots()
# # ax.grid()

# # bins = np.arange(15)-0.5
# # ax.hist(tree_number_list, bins=bins, histtype='bar', rwidth=0.7)

# # ax.set_ylabel('Number of Game State at day=4')
# # ax.set_xlabel('Number of Trees')

# ### correlation graph
# corr_list = []
# for game in gs4_list:
    
#     if game.my_income < 6:
#         continue
    
#     corr = []
#     # number of operation
#     corr.append(len(history(game)))
#     # income
#     corr.append(game.my_income)
#     # my_sun
#     corr.append(game.my_sun)
#     # my_score
#     corr.append(game.my_score)
#     # number of trees
#     corr.append(sum(game.trees))
#     # number of trees size 0
#     corr.append(game.trees[0])    
#     # number of trees size 1
#     corr.append(game.trees[1])
#     # number of trees size 2
#     corr.append(game.trees[2])       
#     # number of trees size 3
#     corr.append(game.trees[3])
    
    
#     corr_list.append(corr)


# fig, ax = plt.subplots()
# ax.grid()

# xlabels= [
#     '# op',
#     'income',
#     'my_sun',
#     'my_score',
#     '# trees',
#     '# size 0',
#     '# size 1',
#     '# size 2',
#     '# size 3',
# ]
# ax.set_xticks(list(range(len(xlabels))))
# ax.set_xticklabels(xlabels, rotation=45)


# for corr in corr_list:
#     color = 'k'
#     alpha = 0.1
#     lw=1
#     if corr[1] == 6:
#         color='r'
#         alpha=0.5
#         lw=2
#     ax.plot(corr, lw=lw, alpha=alpha, color=color)

# fig.tight_layout()


# max_income_list = [game for game in gs4_list if game.my_income==6]
# best_gs4_list = [game for game in gs4_list if game.my_income==6 and game.trees[0]==1]

# best_history_arr = np.array([history(game) for game in best_gs4_list])

# ###first attempt at a metric
    
# metric_arr = np.array([game.metric for game in gs4_list])
    
# # originally 2483 game state
# unique_metric_arr = np.unique(metric_arr, axis=0)
# print("There are {} unique game state at day 4.".format(unique_metric_arr.shape[0]))
# # only 117 unique game state at day 4





