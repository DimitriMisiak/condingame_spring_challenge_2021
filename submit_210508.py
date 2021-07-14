# -*- coding: utf-8 -*-
"""
Created on Thu May 13 12:17:48 2021

@author: dimit
"""

import sys
import math
import numpy as np
import random

debug_flag = True
"""
Definition of the Classes and Functions
"""

class Forest():

    def __init__(self, number_of_cells):
        self.number_of_cells = number_of_cells
        self.tiles_dict = {}

    @property
    def richness_dict(self):
        r_dict = {k:0 for k in range(4)}
        for tile in self.tiles_list:
            r_dict[tile.richness] += 1
        return r_dict

    def generate_neigh_dict(self):
        """
        For each tile of the forest:
            Generate and Save all the neighbor tiles and their distances.
        Meant to invest time at the first time, to save it in the game loop.
        """
        for tile in self.tiles_dict.values():
            tile.generate_neigh_dict()

class Tile():

    forest = None

    def __init__(self, input_str):
        input_list = [int(j) for j in input_str.split()]
        self.index = input_list[0]
        self.richness = input_list[1]
        self.neigh_list = input_list[2:]
        self._neigh_dict = None

    @property
    def valid_neigh_list(self):
        return [idx for idx in self.neigh_list if idx!=-1]

    def generate_neigh_dict(self):
        """
        Generate and Save all the neighbor tiles and their distances.
        """
        known_set = {self.index}
        d_dict = {k:set() for k in (1,2,3)}
        # 1 cell distance
        d_dict[1] = d_dict[1].union(self.valid_neigh_list)
        known_set = known_set.union(d_dict[1])
        # 2 cell distance
        for idx in d_dict[1]:
            tile = forest.tiles_dict[idx]
            novelty_set = set(tile.valid_neigh_list).difference(known_set)
            d_dict[2] = d_dict[2].union(novelty_set)
        known_set = known_set.union(d_dict[2])
        # 3 cell distance
        for idx in d_dict[2]:
            tile = forest.tiles_dict[idx]
            novelty_set = set(tile.valid_neigh_list).difference(known_set)
            d_dict[3] = d_dict[3].union(novelty_set)
        self._neigh_dict = d_dict 

    @property
    def neigh_dict(self):
        return self._neigh_dict

class State():

    forest = None
    initial_grow_cost_dict = {0:1, 1:3, 2:7}
    complete_cost = 4

    def __init__(self, day, nutrients, my_points, opp_points, number_of_trees, turn):
        self.day = day
        self.nutrients = nutrients
        self.my_sun, self.my_score = my_points
        self.opp_sun, self.opp_score, self.opp_is_waiting = opp_points
        self.number_of_trees = number_of_trees
        self.trees_list = []
        self.turn = turn

    def __str__(self):
        #msg = "Day={}, Nutrients={}, mySP={}, myScore={}".format(
        #    self.day, self.nutrients, self.my_sun, self.my_score
        #)
        t_dict = self.my_number_of_tree_of_size_dict
        msg = (
        "D | T | s0| s1| s2| s3| SP | In | Score \n"
        "{} | {} | {} | {} | {} | {} | {} | {} |{}"
        ).format(
            self.day, self.turn,
            t_dict[0],
            t_dict[1],
            t_dict[2],
            t_dict[3],
            self.my_sun,
            self.my_income,
            self.my_score
        )

        return msg

    @property
    def get_move_cost(self):
        """
        Return a dictionnary of the cost of the move for the State.
        """
        m_dict = dict()
        m_dict["WAIT"] = 0
        grow_cost_dict = self.my_grow_cost
        m_dict["GROW 0"] = grow_cost_dict[0]
        m_dict["GROW 1"] = grow_cost_dict[1]
        m_dict["GROW 2"] = grow_cost_dict[2]
        m_dict["COMPLETE"] = self.complete_cost
        m_dict["SEED"] = self.my_seed_cost

    def get_possible_moves_and_cost(self):
        """
        Return a list of the possible (moves, cost)
        Move format:
            GROW cellIdx | SEED sourceIdx targetIdx | COMPLETE cellIdx | WAIT <message>
        """
        # WAIT move is always possible
        move_cost_list = [("WAIT",0),]

        # GROW moves
        affordable_grow_size = [size for size,cost in self.my_grow_cost.items() if self.my_sun>=cost]
        # check for affordable grow move
        for k in affordable_grow_size:
            # check for non dormant tree
            valid_idx = [tree.cell_index for tree in self.my_trees_list if not tree.is_dormant and tree.size==k]
            for idx in valid_idx:
                move_cost_list.append(
                    ("GROW {}".format(idx), self.my_grow_cost[k])
                )

        # COMPLETE moves
        affordable_complete = (self.my_sun >= self.complete_cost)
        if affordable_complete:
            valid_idx = [tree.cell_index for tree in self.my_trees_list if not tree.is_dormant and tree.size==3]
            for idx in valid_idx:
                move_cost_list.append(
                    ("COMPLETE {}".format(idx), self.complete_cost)
                )

        # SEED moves
        affordable_seed = (self.my_sun >= self.my_seed_cost)
        if affordable_seed:
            for tree in self.my_trees_list:
                if not tree.is_dormant:
                    seedable_tiles = tree.get_seedable_idx()
                    for idx in seedable_tiles:
                        move_cost_list.append(
                            ("SEED {} {}".format(tree.cell_index, idx), self.my_seed_cost)
                        )

        return move_cost_list

    @property
    def occupied_tiles(self):
        return [tree.cell_index for tree in self.trees_list]

    @property
    def free_tiles(self):
        all_tiles = set(range(forest.number_of_cells))
        return list(all_tiles.difference(self.occupied_tiles))

    ### "My" method
    @property
    def my_trees_list(self):
        return [tree for tree in self.trees_list if tree.is_mine]

    def my_trees_of_size_list(self, size):
        return [tree for tree in self.my_trees_list if tree.size==size]

    @property
    def my_number_of_tree_of_size_dict(self):
        t_dict = {k:0 for k in range(4)}
        for tree in self.my_trees_list:
            t_dict[tree.size] += 1
        return t_dict

    @property
    def my_income(self):
        size_list = [tree.size for tree in self.my_trees_list]
        return sum(size_list)

    @property
    def my_seed_cost(self):
        my_seeds_list = self.my_trees_of_size_list(0)
        return len(my_seeds_list)

    @property
    def my_grow_cost(self):
        t_dict = self.my_number_of_tree_of_size_dict
        cost_dict = {}
        for k in (0,1,2):
            initial_cost = self.initial_grow_cost_dict[k]
            inflation_cost = t_dict[k+1]
            cost_dict[k] = initial_cost + inflation_cost
        return cost_dict

    ### "Opp" method
    @property
    def opp_trees_list(self):
        return [tree for tree in self.trees_list if not tree.is_mine]

    @property
    def opp_income(self):
        size_list = [tree.size for tree in self.opp_trees_list]
        return sum(size_list)

class Tree():

    forest = None

    def __init__(self, cell_index, size, is_mine, is_dormant):
        self.cell_index = cell_index
        self.size = size
        self.is_mine = is_mine
        self.is_dormant = is_dormant
        self.state = None

    def __str__(self):
        msg = "Index={}, Size={}, isMine={}, isDormant={}".format(
            self.cell_index, self.size, self.is_mine, self.is_dormant
        )
        return msg

    @property
    def neigh_dict(self):
        """
        Recover the neighbor tiles from the Tile of the Tree
        """
        tile = forest.tiles_dict[self.cell_index]
        return tile.neigh_dict

    def get_seedable_idx(self):
        """
        A tile is seedable if:(
            within range of the tree (distance = size)
            AND there is no tree placed on the tile
            AND the richness of the soil is at least 1
        )
        """
        t_list = []
        # for loop enforces the distance to the tree
        distances_within_reach = [k for k in self.neigh_dict.keys() if k<=self.size]
        for k in distances_within_reach:
            for idx in self.neigh_dict[k]:
                # enforce free tile and minimal richness
                is_free = not (idx in self.state.occupied_tiles)
                has_minimal_richness = (self.forest.tiles_dict[idx].richness >= 1)
                if is_free and has_minimal_richness:
                    t_list.append(idx)
        
        return t_list


"""
Initialization Input
"""
### forest inputs
number_of_cells = int(input())  # 37
forest = Forest(number_of_cells)
# attributing the instance of Forest to all the other classes
for cla in (Tile, State, Tree):
    cla.forest = forest

### tiles inputs
for i in range(forest.number_of_cells):
        input_str = input()
        tile = Tile(input_str)
        forest.tiles_dict[tile.index] = tile

forest.generate_neigh_dict()

### checkpoint message
#print(forest.richness_dict, file=sys.stderr, flush=True)
#print(forest.tiles_dict[0].neigh_dict, file=sys.stderr, flush=True)


"""
GAME LOOP
"""
# initializing the turn_count to 0, as the income step (would be 0th step) is automatically done,
# and the counter incrementation is at the start of the while loop
_turn_count = 0
turn_count = _turn_count
prev_day = 0
while True:

    ### state input
    day = int(input())
    if day != prev_day:
        turn_count = _turn_count
    else:
        turn_count += 1

    nutrients = int(input())
    my_points = [int(i) for i in input().split()]
    opp_points = [int(i) for i in input().split()]
    number_of_trees = int(input())

    state = State(day, nutrients, my_points, opp_points, number_of_trees, turn_count)

    ### tree input
    for i in range(state.number_of_trees):
        cell_index, size, is_mine, is_dormant = [int(i) for i in input().split()]
        tree = Tree(cell_index, size, is_mine, is_dormant)

        # linking the Trees and the State
        tree.state = state
        state.trees_list.append(tree)

    ### checkpoint messages
    if debug_flag:
        print(state, file=sys.stderr, flush=True)
        print("My GROW cost = {}".format(state.my_grow_cost), file=sys.stderr, flush=True)


    """
    Possible moves (reading CG inputs is necessary for good completion of the code, but not used by the AI)
    """
    ### possible  from CodinGame (CG)
    number_of_possible_moves = int(input())
    possible_moves_list = list()
    for i in range(number_of_possible_moves):
        possible_move = input()
        possible_moves_list.append(possible_move)
        #print(possible_move, file=sys.stderr, flush=True)

    ### possible moves from my AI
    #ai_possible_moves = state.get_possible_moves()
    #print("AI see {} possible moves:".format(len(ai_possible_moves)), file=sys.stderr, flush=True)
    #for move in ai_possible_moves:
        #print(move, file=sys.stderr, flush=True)
        #pass

    ### checking that AI and CG prediction are the same
    #if set(possible_moves_list) == set(ai_possible_moves):
    #    print(" AI predicts same thing as CD :) ", file=sys.stderr, flush=True)
    #else:
    #    print(" ////// AI and CG think differently ! ///////", file=sys.stderr, flush=True)

    """
    Strategy RANDOM: RANDOM investment with COMPLETE priority
    At each turn, do:
        COMPLETE one tree
        OR randomly one of the possible moves apart from WAIT
        OR WAIT
    """
    """
    complete_list = [move for move in possible_moves_list if 'COMPLETE' in move]
    if complete_list:
        move_strat_random = random.choice(complete_list)
    elif number_of_possible_moves != 1:
        ### cant WAIT (first object of the list) if another move is possible
        move_strat_random = random.choice(possible_moves_list[1:])
    else:
        move_strat_random = random.choice(possible_moves_list)
    """

    """
    Strategy ALPHA
    >"on last day, complete any size 3 tree"-"random"
    >"best SP income growth per turn"-"random priority on equality"
    >"free seed"-"random"
    At each turn, do:
        if: 
            last day, COMPLETE size 3 tree
        else:
            GROW tree with the lesser cost, random choice if ex aequo
            OR SEED with free cost
            OR WAIT
    """
    ai_move_cost_list = state.get_possible_moves_and_cost()

    # checkpoint print for affordable GROW moves
    if debug_flag:
        print(
            "AI has {} possible moves:".format(len(ai_move_cost_list)),
            file=sys.stderr, flush=True
        )
        for mc in ai_move_cost_list:
            move, cost = mc
            print("{} SP = {}".format(cost, move), file=sys.stderr, flush=True)

    # selecting SEED moves
    seed_move_list = []
    for mc in ai_move_cost_list:
        move, cost = mc
        if ("SEED" in move):
            seed_move_list.append(move)

    # selecting COMPLETE moves
    complete_move_list = []
    for mc in ai_move_cost_list:
        move, cost = mc
        if ("COMPLETE" in move):
            complete_move_list.append(move)

    # selecting the affordable GROW moves
    grow_move_cost_list = []
    for mc in ai_move_cost_list:
        move, cost = mc
        if ("GROW" in move):
            grow_move_cost_list.append(mc)

    ### Start the branch decision tree:

    # on the last day
    if state.day >= 23:

        # complete any tree
        if complete_move_list:
            move_strat_alpha = random.choice(complete_move_list)
        else:
            move_strat_alpha = "WAIT"
    
    else:

        # elif there exists an affordable GROW move, do
        if grow_move_cost_list:

            # selecting the GROW moves with the minimum cost
            grow_cost_list = [mc[1] for mc in grow_move_cost_list]
            min_grow_cost = min(grow_cost_list)
            min_grow_move_list = []
            for mc in grow_move_cost_list:
                move, cost = mc
                if cost == min_grow_cost:
                    min_grow_move_list.append(move)
        
            # random GROW move with minimal cost if ex aequo
            if len(min_grow_move_list)>1:
                move_strat_alpha = random.choice(min_grow_move_list)
            else:
                move_strat_alpha = min_grow_move_list[0]

        # elif free seed is possible, do it at a random spot
        elif (state.my_seed_cost == 0) and seed_move_list:
            move_strat_alpha = random.choice(seed_move_list)

        # default answer is WAIT to finish the day
        else:
            move_strat_alpha = "WAIT"

    """
    PRINTING THE MOVE and ENDING THE TURN
    """
    chosen_move = move_strat_alpha
    print(chosen_move)    
