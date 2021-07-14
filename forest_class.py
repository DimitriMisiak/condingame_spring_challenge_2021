# -*- coding: utf-8 -*-
"""
Created on Fri May  7 15:21:28 2021

@author: dimit

Modeling the challenge without board.
So no influence of the sun direction, the richness of the soil, and admitting
that ther is always room for seeds.
"""

import numpy as np
import matplotlib.pyplot as plt

N_tour = 24
t_arr = np.arange(N_tour)

class Forest():
    
    ### Sun Points (SP) gain per turn per tree size
    income_arr = np.array([0, 1, 2, 3])

    ### grow cost
    initial_cost_arr = np.array([1, 3, 7])
    
    ### complete
    complete_cost = 4
    nutrients = 20
    

    def __init__(self):
        
        # # Starting the game with 2 trees of size 1
        # self.tree_arr = np.array([0, 2, 0, 0])
        
        # Starting the game with 1 trees of size 1
        self.tree_arr = np.array([0, 1, 0, 0])
        
        self.dormant_arr = np.array([0, 0, 0, 0])
        
        self.sp_count = 0
        self.score = 0
        
    @property
    def sp_income(self):
        return sum( self.tree_arr * self.income_arr )

    @property
    def grow_cost(self):
        """ Return the current cost of growing tree depending on the initial cost
        and the numbr of current tree of each size
        """
        return self.initial_cost_arr + self.tree_arr[1:]

    @property
    def seed_cost(self):
        return self.tree_arr[0]
    
    @property
    def ready_tree_arr(self):
        return self.tree_arr - self.dormant_arr
    
    def grow_tree(self, size):
        self.sp_count -= self.grow_cost[size-1]
        self.tree_arr[size] += 1
        self.tree_arr[size-1] -= 1
        self.dormant_arr[size] += 1
    
    def seed(self, size_tree):
        self.sp_count -= self.seed_cost
        self.tree_arr[0] += 1
        self.dormant_arr[0] += 1
        self.dormant_arr[size_tree] += 1

    def complete(self):
        self.sp_count -= self.complete_cost
        self.tree_arr[-1] -= 1
        self.score += self.nutrients
        
    def sp_to_score(self):
        self.score += int(self.sp_count/3)
        self.sp_count = 0
        
    def new_turn(self):
        self.sp_count += self.sp_income
        self.dormant_arr = np.array([0, 0, 0, 0])

FD = {
    "A": Forest(),
    "B": Forest(),
    "C": Forest(),
    "D": Forest(),
    "E": Forest(),
    "F": Forest(),
}

# A = Forest()
# B = Forest()

SP_dict = {
    "A": [],
    "B": [],
    "C": [],
    "D": [],
    "E": [],
    "F": [],
}

income_dict = {
    "A": [],
    "B": [],
    "C": [],
    "D": [],
    "E": [],
    "F": [],
}

score_dict = {
    "A": [],
    "B": [],
    "C": [],
    "D": [],
    "E": [],
    "F": [],
}

seed_count_F = 0
seed_count_E = 0
seed_count_D = 0
for i in range(N_tour):
    print("Turn=", i)
    # new turn routine
    for a in FD.keys():
        f = FD[a]
        f.new_turn()
    
        """
        Strategy A: Wait
        """
        if a == 'A':
            pass
    
        """
        Strategy B: invest to size 2 as soon as possible
        """
        if a == 'B':
            while 1:
                if (f.sp_count >= f.grow_cost[1]) and (f.ready_tree_arr[1]>=1):
                    f.grow_tree(size=2)
                else:
                    break

        """
        Strategy C: invest to size 3 as soon as possible
        """
        if a == 'C':
            while 1:
                if (f.sp_count >= f.grow_cost[2]) and (f.ready_tree_arr[2]>=1):
                    f.grow_tree(size=3)
                elif (f.sp_count >= f.grow_cost[1]) and (f.ready_tree_arr[1]>=1):
                    f.grow_tree(size=2)
                else:
                    break

        """
        Strategy D: seed once and Strategy A
        """
        if a == 'D':
            while True:
                if (f.sp_count >= f.grow_cost[0]) and (f.ready_tree_arr[0]>=1):
                    f.grow_tree(size=1)
                elif (f.sp_count >= f.seed_cost) and np.any(f.ready_tree_arr[1:]>=1) and seed_count_D<1:
                    f.seed(1)
                    seed_count_D += 1
                else:
                    break

        """
        Strategy E: seed once and Strategy B
        """
        if a == 'E':
            while True:
                if (f.sp_count >= f.grow_cost[1]) and (f.ready_tree_arr[1]>=1):
                    f.grow_tree(size=2)
                elif (f.sp_count >= f.grow_cost[0]) and (f.ready_tree_arr[0]>=1):
                    f.grow_tree(size=1)
                elif (f.sp_count >= f.seed_cost) and np.any(f.ready_tree_arr[1:]>=1) and seed_count_E<1:
                    f.seed(1)
                    seed_count_E += 1
                else:
                    break

        """
        Strategy F: seed once and Strategy C
        """
        if a == 'F':
            while True:
                if (f.sp_count >= f.grow_cost[2]) and (f.ready_tree_arr[2]>=1):
                    f.grow_tree(size=3)
                elif (f.sp_count >= f.grow_cost[1]) and (f.ready_tree_arr[1]>=1):
                    f.grow_tree(size=2)
                elif (f.sp_count >= f.grow_cost[0]) and (f.ready_tree_arr[0]>=1):
                    f.grow_tree(size=1)
                if (f.sp_count >= f.seed_cost) and np.any(f.ready_tree_arr[1:]>=1) and seed_count_F<1:
                    f.seed(1)
                    seed_count_F += 1
                else:
                    break

        # # last turn conversion
        # if (i == N_tour-1):
        #     f.sp_to_score()

        SP_dict[a].append(f.sp_count)
        income_dict[a].append(f.sp_income)
        score_dict[a].append(f.score)


        

# =============================================================================
# PLOTS
plt.close('all')
# =============================================================================
SP_dict = {k:np.array(v) for k,v in SP_dict.items()}
income_dict = {k:np.array(v) for k,v in income_dict.items()}

### SP count
fig, axes = plt.subplots(nrows=2, figsize=(6.3, 6.3))

for a in FD.keys():
    axes[0].plot(
        t_arr, SP_dict[a],
        lw=1,
        marker='.', label=a
    )

    axes[1].plot(
        t_arr, SP_dict[a]-SP_dict['A'],
        lw=1,
        marker='.', label=a
    )

for ax in axes:
    ax.legend()
    ax.grid()

fig.tight_layout()

### Income
fig, axes = plt.subplots(nrows=2, figsize=(6.3, 6.3))

for a in FD.keys():
    axes[0].plot(
        t_arr, income_dict[a],
        lw=1,
        marker='.', label=a
    )

    axes[1].plot(
        t_arr, income_dict[a]-income_dict['A'],
        lw=1,
        marker='.', label=a
    )

for ax in axes:
    ax.legend()
    ax.grid()

fig.tight_layout()

# ### Score
# fig, ax = plt.subplots()

# for a in ('A', 'B'):
#     ax.plot(
#         t_arr, score_dict[a],
#         lw=1,
#         marker='.', label=a
#     )
    
# ax.legend()
# ax.grid()