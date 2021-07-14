# -*- coding: utf-8 -*-
"""
Created on Thu May 13 11:54:13 2021

@author: dimit
"""
import sys
import math
from enum import Enum
import random
from abc import ABC, abstractmethod
import numpy as np

# =============================================================================
# HEXAGONAL COORDINATESS and related functions
# =============================================================================
DIRECTION_VECTORS = {
    0: [1, -1, 0],
    1: [1, 0, -1],
    2: [0, 1, -1],
    3: [-1, +1, 0],
    4: [-1, 0, 1],
    5: [0, -1, 1],   
}
DIRECTION_VECTORS = {k:np.array(v) for k,v in DIRECTION_VECTORS.items()}

# each index has its hex coords
CELL_COORDS = np.array([
       [ 0,  0,  0],
       [ 1, -1,  0],
       [ 1,  0, -1],
       [ 0,  1, -1],
       [-1,  1,  0],
       [-1,  0,  1],
       [ 0, -1,  1],
       [ 2, -2,  0],
       [ 2, -1, -1],
       [ 2,  0, -2],
       [ 1,  1, -2],
       [ 0,  2, -2],
       [-1,  2, -1],
       [-2,  2,  0],
       [-2,  1,  1],
       [-2,  0,  2],
       [-1, -1,  2],
       [ 0, -2,  2],
       [ 1, -2,  1],
       [ 3, -3,  0],
       [ 3, -2, -1],
       [ 3, -1, -2],
       [ 3,  0, -3],
       [ 2,  1, -3],
       [ 1,  2, -3],
       [ 0,  3, -3],
       [-1,  3, -2],
       [-2,  3, -1],
       [-3,  3,  0],
       [-3,  2,  1],
       [-3,  1,  2],
       [-3,  0,  3],
       [-2, -1,  3],
       [-1, -2,  3],
       [ 0, -3,  3],
       [ 1, -3,  2],
       [ 2, -3,  1]
])
CELL_COORDS.flags.writeable = False

def hex_norm(x, axis=None):
    """
    Norm function for the heaxagonal coordinates.
    """
    return np.sum(np.abs(x), axis=axis)/2


#%%
# =============================================================================
# ACTION RELATED CLASSES
# =============================================================================

# class ActionType(Enum):
#     WAIT = "WAIT"
#     SEED_1 = "SEED_1"
#     SEED_2 = "SEED_2"
#     SEED_3 = "SEED_3"
#     GROW_0 = "GROW_0"
#     GROW_1 = "GROW_1"
#     GROW_2 = "GROW_2"
#     COMPLETE = "COMPLETE"   

# class ActionElement():
    
#     def __init__(self, name):
#         self.name = name

#     def cost(self, state):
#         if self.name == "WAIT":
#             return 0
#         elif "SEED" in self.name:
#             return state.trees[0]
#         elif self.name == ActionType.GROW_0:
#             return 1 + state.trees[1]
#         elif self.type is ActionType.GROW_1:
#             return 3 + state.trees[2]
#         elif self.type is ActionType.GROW_2:
#             return 7 + state.trees[3]
#         elif self.type is ActionType.COMPLETE:
#             return 4
#         else:
#             raise Exception("Action.cost")

#     def is_state_ready(self, state):
#         """
#         Check for requirements at the level of the State
#         """
#         if self.type is ActionType.WAIT:
#             return True
#         elif "_0" in self.type.name:
#             return bool(state.awake_trees[0])
#         elif "_1" in self.type.name:
#             return bool(state.awake_trees[1])
#         elif "_2" in self.type.name:
#             return bool(state.awake_trees[2])
#         elif "_3" in self.type.name:
#             return bool(state.awake_trees[3])
#         elif self.type is ActionType.COMPLETE:
#             return bool(state.awake_trees[3])
#         else:
#             raise Exception("Action.is_state_ready")

#     def is_affordable(self, state):
#         return (self.cost(state) <= state.my_sun)

#     def is_state_possible(self, state):
#         return (self.is_affordable(state) and self.is_state_ready(state))

class Action(ABC):
    
    priority = 0
    
    def __init__(self):
        super().__init__()

    # def __lt__(self, other):
    #     if not issubclass(other, Action):
    #         # only equality tests to other `structure` instances are supported
    #         return NotImplemented
    #     return self.priority < other.priority

    # def __eq__(self, other):
    #     if not issubclass(other, Action):
    #         # only equality tests to other `structure` instances are supported
    #         return NotImplemented
    #     return self.priority == other.priority

    @classmethod
    @abstractmethod
    def cost(cls, state):
        pass

    @classmethod
    @abstractmethod
    def is_state_ready(cls, state):
        """
        Check for requirements at the level of the State
        """
        pass
    
    @classmethod
    def is_affordable(cls, state):
        return (cls.cost(state) <= state.my_sun)

    @classmethod
    def is_state_possible(cls, state):
        return (cls.is_affordable(state) and cls.is_state_ready(state))

    @classmethod
    def _general_result_dict(cls, state):
        result_dict = dict(state.__dict__)
        result_dict['my_sun'] -= cls.cost(state)
        result_dict['turn'] += 1
        return result_dict

    @classmethod
    @abstractmethod
    def result(cls, state):
        """
        Return the result state after the action.
        Usually increment the number of turn.
        """
        pass

    
class Wait(Action):
    
    priority = 0
    
    def __init__(self):
        super().__init__()
        
    @classmethod
    def cost(cls, state):
        return 0
    
    @classmethod
    def is_state_ready(cls, state):
        return True

    @classmethod
    def result(cls, state):
        result_dict = cls._general_result_dict(state)

        result_dict['day'] += 1
        result_dict['turn'] = 0
        result_dict['awake_trees'] = state.trees
        result_dict['dormant_trees'] = (0,) * len(state.trees)
        result_dict['my_sun'] += state.my_income
        
        return State(**result_dict)

    @classmethod
    def __str__(cls):
        return 'WAIT'

class SeedAction(Action):

    priority = 10
    
    def __init__(self, target_cell_id, origin_cell_id):
        super().__init__()
        self.target_cell_id = target_cell_id
        self.origin_cell_id = origin_cell_id

    @classmethod
    def cost(cls, state):
        return state.trees[0]   

    def __str__(self):
        return f'SEED {self.origin_cell_id} {self.target_cell_id}'

class Seed_1(SeedAction):
    
    @classmethod
    def is_state_ready(cls, state):
        return bool(state.awake_trees[1])

    @classmethod
    def result(cls, state):
        result_dict = cls._general_result_dict(state)
        
        result_dict['awake_trees'] -= np.array([0, 1, 0, 0])
        result_dict['dormant_trees'] += np.array([1, 1, 0, 0])

        return State(**result_dict)

class Seed_2(SeedAction):
    
    @classmethod
    def is_state_ready(cls, state):
        return bool(state.awake_trees[2])

    @classmethod
    def result(cls, state):
        result_dict = cls._general_result_dict(state)
        
        result_dict['awake_trees'] -= np.array([0, 0, 1, 0])
        result_dict['dormant_trees'] += np.array([1, 0, 1, 0])

        return State(**result_dict)

class Seed_3(SeedAction):
    
    @classmethod
    def is_state_ready(cls, state):
        return bool(state.awake_trees[3])

    @classmethod
    def result(cls, state):
        result_dict = cls._general_result_dict(state)
        
        result_dict['awake_trees'] -= np.array([0, 0, 0, 1])
        result_dict['dormant_trees'] += np.array([1, 0, 0, 1])

        return State(**result_dict)

class GrowAction(Action):

    priority = 5    

    def __init__(self, target_cell_id):
        super().__init__()
        self.target_cell_id = target_cell_id

    def __str__(self):
        return f'GROW {self.target_cell_id}'

class Grow_0(GrowAction):
    
    @classmethod
    def is_state_ready(cls, state):
        return bool(state.awake_trees[0])

    @classmethod
    def cost(cls, state):
        return 1 + state.trees[1]

    @classmethod
    def result(cls, state):
        result_dict = cls._general_result_dict(state)
        
        result_dict['awake_trees'] -= np.array([1, 0, 0, 0])
        result_dict['dormant_trees'] += np.array([0, 1, 0, 0])

        return State(**result_dict)

class Grow_1(GrowAction):
    
    @classmethod
    def is_state_ready(cls, state):
        return bool(state.awake_trees[1])

    @classmethod
    def cost(cls, state):
        return 3 + state.trees[2]

    @classmethod
    def result(cls, state):
        result_dict = cls._general_result_dict(state)
        
        result_dict['awake_trees'] -= np.array([0, 1, 0, 0])
        result_dict['dormant_trees'] += np.array([0, 0, 1, 0])

        return State(**result_dict)
    
class Grow_2(GrowAction):
    
    @classmethod
    def is_state_ready(cls, state):
        return bool(state.awake_trees[2])

    @classmethod
    def cost(cls, state):
        return 7 + state.trees[3]

    @classmethod
    def result(cls, state):
        result_dict = cls._general_result_dict(state)
        
        result_dict['awake_trees'] -= np.array([0, 0, 1, 0])
        result_dict['dormant_trees'] += np.array([0, 0, 0, 1])

        return State(**result_dict)

class Complete(Action):
    
    priority = 7
    
    def __init__(self, target_cell_id):
        super().__init__()
        self.target_cell_id = target_cell_id

    def __str__(self):
        return f'COMPLETE {self.target_cell_id}'
        
    @classmethod
    def cost(cls, state):
        return 4
    
    @classmethod
    def is_state_ready(cls, state):
        return bool(state.awake_trees[3])

    @classmethod
    def result(cls, state):
        result_dict = cls._general_result_dict(state)

        result_dict['awake_trees'] -= np.array([0, 0, 0, 1])
        result_dict['my_score'] += state.nutrients
        result_dict['nutrients'] -= 1
        
        return State(**result_dict)

ACTIONS = (
    Wait,
    Seed_1,
    Seed_2,
    Seed_3,
    Grow_0,
    Grow_1,
    Grow_2,
    Complete
)

#     @staticmethod
#     def parse(action_string):
#         split = action_string.split(' ')
#         if split[0] == ActionType.WAIT.name:
#             return Action(ActionType.WAIT)
#         if split[0] == ActionType.SEED.name:
#             return Action(ActionType.SEED, int(split[2]), int(split[1]))
#         if split[0] == ActionType.GROW.name:
#             return Action(ActionType.GROW, int(split[1]))
#         if split[0] == ActionType.COMPLETE.name:
#             return Action(ActionType.COMPLETE, int(split[1]))

#%%
# =============================================================================
# Game STATE related classes
# =============================================================================
class State():
    """
    Reduced State of the Game.
    Independant of the Cells.
    """
    
    INCOME_PER_SIZE = (0, 1, 2, 3)
    
    def __init__(
            self,
            day, turn, nutrients,
            my_sun, my_score,
            awake_trees, dormant_trees,
        ):
        self.day = day
        self.turn = turn
        self.nutrients = nutrients
        self.my_sun = my_sun
        self.my_score = my_score
        self.awake_trees = tuple(awake_trees)
        self.dormant_trees = tuple(dormant_trees)

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

    @staticmethod
    def parse(metric_tuple):
        assert len(metric_tuple) == 13
        awake_tree = metric_tuple[5:9]
        dormant_tree = metric_tuple[9:]
        return State(*metric_tuple[:5], awake_tree, dormant_tree)    

    def __hash__(self):
        return hash(self.metric)
    
    def __eq__(self, other):    
        if not isinstance(other, State):
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

    def __repr__(self):
        return f"<State {self.metric}>"

    @property
    def trees(self):
        return np.add(self.awake_trees, self.dormant_trees)

    @property
    def my_income(self):
        return sum([nt*inc for nt,inc in zip(self.trees, self.INCOME_PER_SIZE)])

    def get_possible_actions(self):
        return [action for action in ACTIONS if action.is_state_possible(self)]
    
    def get_next_turn_states(self):
        action_list = self.get_possible_actions()
        states_dict = {}
        for action in action_list:
            try:
                states_dict[action.result(self)] += ((action,),)
            except:
                states_dict[action.result(self)] = ((action,),)
        return states_dict

    def get_next_day_states(self):
        metrics_dict = {}
        
        queue_dict = self.get_next_turn_states()
        while queue_dict:
            state = next(iter(queue_dict.keys()))
            action_paths = queue_dict.pop(state)
            
            if state.day == self.day + 1:
                try:
                    metrics_dict[state.metric] += action_paths
                except KeyError:
                    metrics_dict[state.metric] = action_paths
            else:
                raw_next_turn_states = state.get_next_turn_states()
                for st,paths in raw_next_turn_states.items():
                    new_paths = []
                    for action_seq in action_paths:
                        for seq in paths:
                            new_paths.append(action_seq + seq)
                    new_paths = tuple(new_paths)
                    try:
                        queue_dict[st] += new_paths
                    except:
                        queue_dict[st] = new_paths
        
        states_dict = {State.parse(m):paths for m,paths in metrics_dict.items()}
        return states_dict
        
    # def get_states(self, day_forward):        
    #     metrics_dict = {}
        
    #     queue_dict = self.get_next_turn_states()
    #     while queue_dict:
    #         state = next(iter(queue_dict.keys()))
    #         action_paths = queue_dict.pop(state)
            
    #         if state.day == self.day + day_forward:
    #             try:
    #                 metrics_dict[state.metric] += action_paths
    #             except KeyError:
    #                 metrics_dict[state.metric] = action_paths
    #         else:
    #             raw_next_turn_states = state.get_next_turn_states()
    #             for st,paths in raw_next_turn_states.items():
    #                 new_paths = []
    #                 for action_seq in action_paths:
    #                     for seq in paths:
    #                         new_paths.append(action_seq + seq)
    #                 new_paths = tuple(new_paths)
    #                 try:
    #                     queue_dict[st] += new_paths
    #                 except:
    #                     queue_dict[st] = new_paths
        
    #     states_dict = {State.parse(m):paths for m,paths in metrics_dict.items()}
    #     return states_dict

    def get_future_states(self, day_forward):        
        metrics_dict = {}
        
        queue_dict = {self: (tuple(),)}
        while queue_dict:
            state = next(iter(queue_dict.keys()))
            action_paths = queue_dict.pop(state)
            
            if state.day == self.day + day_forward:
                try:
                    metrics_dict[state.metric] += action_paths
                except KeyError:
                    metrics_dict[state.metric] = action_paths
            else:
                raw_next_turn_states = state.get_next_turn_states()
                for st,paths in raw_next_turn_states.items():                    
                    new_paths = []
                    for action_seq in action_paths:
                        for seq in paths:
                            new_paths.append(action_seq + seq)
                    new_paths = tuple(new_paths)
                    try:
                        queue_dict[st] += new_paths
                    except:
                        queue_dict[st] = new_paths
        
        states_dict = {State.parse(m):paths for m,paths in metrics_dict.items()}
        return states_dict


# A = State(
#     day=0, turn=0, nutrients=20,
#     my_sun=2, my_score=0,
#     awake_trees=[0, 2, 0, 0], dormant_trees=[0, 0, 0, 0]
# )

A = State(
    day=0, turn=0, nutrients=20,
    my_sun=2, my_score=0,
    awake_trees=[0, 2, 0, 0], dormant_trees=[0, 0, 0, 0]
)

# day1_dict = A.get_next_day_states()

# l_list = []
# for i in range(5):
#     future_states = A.get_future_states(i)
#     max_redundant_paths = max([len(x) for x in future_states.values()])
#     num = len(future_states)
#     print(f"At Day {i}: {num} states")
#     print(f"Max redundant paths {max_redundant_paths}")
#     l_list.append(num)

import matplotlib.pyplot as plt
# plt.close('all')
# fig, ax = plt.subplots()
# ax.plot(l_list, marker='o')

# =============================================================================
# ANALYSIS DAY 4
# =============================================================================

# day4_states = A.get_future_states(4)
# day4_income = [state.my_income for state in day4_states.keys()]
# best_day4_states = [state for state in day4_states if state.my_income == max(day4_income)]

# states_list = day4_states


# =============================================================================
# ANALYSIS DAY 7
# =============================================================================
# B = State.parse((4, 0, 20, 6, 0, 0, 2, 2, 0, 0, 0, 0, 0))
# # C = State.parse((4, 0, 20, 6, 0, 1, 2, 2, 0, 0, 0, 0, 0))

# day7_states = B.get_future_states(3)
# day7_income = [state.my_income for state in day7_states.keys()]

# best_day7_states = []
# for state in day7_states:
#     if state.my_income == max(day7_income):
#         if state.trees[0]:
#             best_day7_states.append(state)


# =============================================================================
# ANALYSIS DAY 8
# =============================================================================
C = State.parse((7, 0, 20, 12, 0, 1, 2, 3, 1, 0, 0, 0, 0))
# C = State.parse((4, 0, 20, 6, 0, 1, 2, 2, 0, 0, 0, 0, 0))

day7_states = C.get_future_states(1)
day7_income = [state.my_income for state in day7_states.keys()]

best_day7_states = []
for state in day7_states:
    if state.my_income == max(day7_income):
        best_day7_states.append(state)

states_list = day7_states
# =============================================================================
# PLOT
# =============================================================================
import matplotlib.pyplot as plt
plt.close('all')

### correlation graph
corr_list = []
for state in states_list:
    
    # if game.my_income < 6:
    #     continue
    
    corr = []
    # income
    corr.append(state.my_income)
    # my_sun
    corr.append(state.my_sun)
    # my_score
    corr.append(state.my_score)
    # number of trees
    corr.append(sum(state.trees))
    # number of trees size 0
    corr.append(state.trees[0])    
    # number of trees size 1
    corr.append(state.trees[1])
    # number of trees size 2
    corr.append(state.trees[2])       
    # number of trees size 3
    corr.append(state.trees[3])
    
    
    corr_list.append(corr)


fig, ax = plt.subplots()
ax.grid()

xlabels= [
    'income',
    'my_sun',
    'my_score',
    '# trees',
    '# size 0',
    '# size 1',
    '# size 2',
    '# size 3',
]
ax.set_xticks(list(range(len(xlabels))))
ax.set_xticklabels(xlabels, rotation=45)


for corr in corr_list:
    color = 'k'
    alpha = 0.1
    lw=1
    if corr[0] == max(day7_income):
        color='r'
        alpha=0.5
        lw=2
    ax.plot(corr, lw=lw, alpha=alpha, color=color)

fig.tight_layout()


# max_income_list = [game for game in gs4_list if game.my_income==6]
# best_gs4_list = [game for game in gs4_list if game.my_income==6 and game.trees[0]==1]

# best_history_arr = np.array([history(game) for game in best_gs4_list])

# ###first attempt at a metric
    
# metric_arr = np.array([game.metric for game in gs4_list])
    
# # originally 2483 game state
# unique_metric_arr = np.unique(metric_arr, axis=0)
# print("There are {} unique game state at day 4.".format(unique_metric_arr.shape[0]))
# # only 117 unique game state at day 4
