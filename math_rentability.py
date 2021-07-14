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

t_arr = np.arange(24)

"""
List with number of tree of each size:
    [size 0, size 1, size 2, size 3]
Starting the game with 2 trees of size 1
"""
tree_arr = np.array([0, 2, 0, 0])


### Sun Points (SP) gain per turn per tree size
income_arr = np.array([0, 1, 2, 3])

### grow cost
initial_cost_arr = np.array([1, 3, 7])

def cost_arr():
    """ Return the current cost of growing tree depending on the initial cost
    and the numbr of current tree of each size
    """
    return initial_cost_arr + tree_arr[1:]

### actions
def income():
    """ Return the income in Sun Points, at the beginning of each turn
    """
    return sum(tree_arr * income_arr)

def grow(size):
    """ Grow a tree of given size
    """
    tree_arr[size] += 1
    
SP_count = 0

for i in range(N_tour):
    SP_count += income()
    print("SP count = {}".format(SP_count))    
