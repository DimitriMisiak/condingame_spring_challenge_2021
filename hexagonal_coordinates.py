# -*- coding: utf-8 -*-
"""
Created on Thu May 13 15:12:20 2021

@author: dimit
"""

import numpy as np

number_of_cells = 37

# for each cell: hexagonal coordinates (x,y,z)
cell_map = np.zeros((number_of_cells, 3), dtype=int)

construction_vector_dict = {}
for cycle_idx in (1,2,3):
    c_list = []
    # starter
    if cycle_idx == 1:
        c_list.append([0,])
    else:
        c_list.append([1,0])
    
    # middle and finisher
    for i in range(6):
        c_list += [[(i+2)%6],]*cycle_idx
    c_list.pop(-1)
    construction_vector_dict[cycle_idx] = c_list

direction_vector = {
    0: [1, -1, 0],
    1: [1, 0, -1],
    2: [0, 1, -1],
    3: [-1, +1, 0],
    4: [-1, 0, 1],
    5: [0, -1, 1],   
}

cell_idx = 1
for cycle_idx, c_list in construction_vector_dict.items():
    
    for vect_list in c_list:
        vector = 0
        for vect_idx in vect_list:
            vector = np.add(vector, direction_vector[vect_idx])
        
        #print(cell_map[cell_idx-1])
        #print(vector)
        cell_map[cell_idx] = cell_map[cell_idx-1] + vector
        cell_idx += 1
    
#print(cell_map)

#accessing the coordinates of the 7th cell is simply:
coords = cell_map[7]

# the distance (= norm of vector) between two cells is:
distance_map = (
    np.sum( abs(cell_map - cell_map[35]), axis=1) / 2
).astype(int)

# finding the seedable cells (up to 3 in distance, is simply
seedable_idx = np.nonzero(distance_map<=3)[0]

# finding the cell_idx upon which a shadow is cast depends on the direction of the sun
sun_dir = 3
shadow_coords = [i*np.array(direction_vector[sun_dir])+cell_map[35] for i in (1,2,3)]

# finding the idx corresponding to coords
shadow_idx = [np.flatnonzero(np.all(cell_map == s, axis=1))[0] for s in shadow_coords]

