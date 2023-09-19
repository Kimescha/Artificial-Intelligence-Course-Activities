# -*- coding: utf-8 -*-
"""8-puzzle.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QqPF-UJha6Sb-BoBl_qtAzJe5soMA0lj
"""

EASY_INSTANCES = [
    "1,2,3,0,7,6,5,4,8",
    "0,4,1,2,5,3,7,8,6",
    "4,1,3,0,2,6,7,5,8",
    "1,2,3,0,4,8,7,6,5",
    "1,2,0,4,8,3,7,6,5",
    "1,0,2,4,6,3,7,5,8",
    "0,1,2,4,5,3,7,8,6",
    "1,2,3,0,4,5,7,8,6",
    "1,2,3,4,0,5,7,8,6",
    "1,2,3,4,5,0,7,8,6",
    "0,1,3,4,2,5,7,8,6",
    "2,3,5,1,0,4,7,8,6",
    "1,6,2,5,3,0,4,7,8",
    "1,8,2,0,4,3,7,6,5",
    "2,5,3,4,1,6,0,7,8",
    "1,2,3,4,6,8,7,5,0",
    "1,6,2,5,7,3,0,4,8",
    "0,4,1,5,3,2,7,8,6",
    "0,5,2,1,8,3,4,7,6",
    "1,2,3,0,4,6,7,5,8"
]
MEDIUM_INSTANCES = [
    "1,3,5,7,2,6,8,0,4",
    "4,1,2,3,0,6,5,7,8",
    "4,3,1,0,7,2,8,5,6",
    "5,2,1,4,8,3,7,6,0",
    "2,0,8,1,3,5,4,6,7",
    "3,5,6,1,4,8,0,7,2",
    "1,0,2,7,5,4,8,6,3",
    "5,1,8,2,7,3,4,0,6",
    "4,3,0,6,1,8,2,7,5",
    "2,4,3,1,6,5,8,0,7",
    "1,2,3,6,4,5,7,8,0",
    "3,1,2,4,5,6,7,8,0",
    "1,2,3,4,8,7,6,5,0",
    "1,3,2,5,4,6,7,8,0",
    "1,4,2,6,5,8,7,3,0"

]
HARD_INSTANCES = [
    "2,1,3,4,5,6,8,7,0",
    "2,3,1,6,5,4,8,7,0",
    "2,3,1,6,4,5,7,8,0",
    "1,2,3,6,5,4,8,7,0",
    "1,2,3,6,5,4,0,8,7",
    "4,5,3,2,8,0,6,7,1",
    "4,5,3,2,1,0,8,7,6",
    "1,2,4,3,5,0,8,7,6",
    "1,2,4,3,5,8,7,0,6",
    "2,1,3,4,5,8,7,0,6",
    "1,3,5,8,7,0,6,2,4",
    "4,3,1,6,5,8,0,2,7",
    "7,0,4,8,5,1,6,3,2",
    "8,7,2,1,5,0,4,6,3",
    "8,3,5,6,4,2,1,0,7",
    "1,6,4,0,3,5,8,2,7",
    "6,3,8,5,4,1,7,2,0",
    "5,8,7,1,4,6,3,0,2",
    "2,8,5,3,6,1,7,0,4",
    "8,7,6,5,4,3,2,1,0"

]

import enum
import numpy as np
import tracemalloc
import time
from collections import deque
import copy
import sys
import heapq

def read_input(line):
    input_2d = []
    input_array = list(map(int, line.split(",")))
    for i in range(9):
        if i%3 == 0:
            input_2d.append([input_array[i]])
        else:
            input_2d[i//3].append(input_array[i])
    return input_2d

class Direction(enum.IntEnum):
    Up = 0
    Right = 1
    Down = 2
    Left = 3
    
    @staticmethod
    def actions():
        return [Direction.Right, Direction.Down, Direction.Left, Direction.Up]

class State:
    def __init__(self, positions):
        self.positions = positions

    def __eq__(self, other):
        return np.array_equiv(self.positions, other.positions)
    
    def __hash__(self):
        return hash(tuple(np.reshape(self.positions, (1, 9))[0].tolist()))
    
    def is_goal(self):
        return np.array_equiv(self.positions, [[1, 2, 3], [4, 5, 6], [7, 8, 0]])
    
    def calculate_heuristic(self):
        sum_manhat_dist = 0
        for i in range(3):
            for j in range(3):
                current_val = self.positions[i][j]
                if current_val == 0:
                    continue
                goal_x = (current_val - 1) // 3
                goal_y = (current_val -1) % 3
                sum_manhat_dist += abs(i - goal_x) + abs(j - goal_y)
        return sum_manhat_dist
    
    def transition(self, action):
        zero_pos_x = 0
        zero_pos_y = 0
        for i in range(3):
            for j in range(3):
                if (self.positions[i][j] == 0):
                    zero_pos_x = i
                    zero_pos_y = j
        if (
            (zero_pos_x == 0 and action == Direction.Down) or
            (zero_pos_x == 2 and action == Direction.Up) or
            (zero_pos_y == 0 and action == Direction.Right) or
            (zero_pos_y == 2 and action == Direction.Left)
        ):
            return False
        new_positions = copy.deepcopy(self.positions)
        if action == Direction.Up:
            new_positions[zero_pos_x][zero_pos_y] = new_positions[zero_pos_x+1][zero_pos_y]
            new_positions[zero_pos_x+1][zero_pos_y] = 0
        elif action == Direction.Down:
            new_positions[zero_pos_x][zero_pos_y] = new_positions[zero_pos_x-1][zero_pos_y]
            new_positions[zero_pos_x-1][zero_pos_y] = 0
        elif action == Direction.Left:
            new_positions[zero_pos_x][zero_pos_y] = new_positions[zero_pos_x][zero_pos_y+1]
            new_positions[zero_pos_x][zero_pos_y+1] = 0
        elif action == Direction.Right:
            new_positions[zero_pos_x][zero_pos_y] = new_positions[zero_pos_x][zero_pos_y-1]
            new_positions[zero_pos_x][zero_pos_y-1] = 0
        return State(new_positions)

class Node:
    def __init__(
        self, _state: State, _parent, _action, _path_cost
    ):
        self.state = _state
        self.parent = _parent
        self.action = _action
        self.path_cost = _path_cost

    def __lt__(self, other):
        return self

def run(algorithm_func, start_node, *args, **kwargs):
    mem_used = 0
    tic = time.time()
    tracemalloc.start()
    final = algorithm_func(start_node, *args, **kwargs)
    mem_used = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    toc = time.time()
    if final == False:
        print("NOT POSSIBLE")
        return
    answer_actions = []
    while final is not None:
        answer_actions = [final.action] + answer_actions
        final = final.parent
    print("Actions: ", end="")
    for action in answer_actions[1:]:
        print(action.name, end=" ")
    print("Time taken: {}".format(toc - tic))
    print("Memory used: {}".format(mem_used))

def run_for_tests(algorithm_func, *args, **kwargs):
    i = 1
    for test in EASY_INSTANCES:
        print("EASY INSTANCE TEST NUMBER {}".format(i))
        i += 1
        start_node = Node(State(read_input(test)), None, None, 0)
        run(algorithm_func, start_node, *args, **kwargs)
        print("--------------------------------------------------------------------------------------------------------------------------")
    i = 1
    for test in MEDIUM_INSTANCES:
        print("MEDIUM INSTANCE TEST NUMBER {}".format(i))
        i += 1
        start_node = Node(State(read_input(test)), None, None, 0)
        run(algorithm_func, start_node, *args, **kwargs)
        print("--------------------------------------------------------------------------------------------------------------------------")        
    i = 1
    for test in HARD_INSTANCES:
        print("HARD INSTANCE TEST NUMBER {}".format(i))
        i += 1
        start_node = Node(State(read_input(test)), None, None, 0)
        run(algorithm_func, start_node, *args, **kwargs)
        print("--------------------------------------------------------------------------------------------------------------------------")

def bfs(start_node: Node):
    states_met = 0
    distinct_states_met = 0
    if start_node.state.is_goal():
        return start_node
    frontier = deque([start_node])
    frontier_state_set = set()
    frontier_state_set.add(start_node.state)
    explored = set()
    while True:
        if not frontier:
            return False
        current = frontier.pop()
        frontier_state_set.remove(current.state)      
        explored.add(current.state)
        for action in Direction.actions():
            new_state = current.state.transition(action)
            if new_state is not False:
                states_met += 1
                child = Node(new_state, current, action, current.path_cost + 1)
                if (
                    child.state not in explored
                    and child.state not in frontier_state_set
                ):
                    distinct_states_met += 1
                    if child.state.is_goal():
                        return child
                    frontier.appendleft(child)
                    frontier_state_set.add(child.state)

print("BFS:")
run_for_tests(bfs)

def dfs(start_node, depth=40):
    states_met = 0
    distinct_states_met = 0
    if start_node.state.is_goal():
        return start_node
    frontier = deque([start_node])
    explored = dict()
    while True:
        if not frontier:
            return False
        current = frontier.pop()
        if current.path_cost == depth:
            continue
        explored[current.state] = current.path_cost
        for action in Direction.actions():
            new_state = current.state.transition(action)
            if new_state is not False:
                states_met += 1
                child = Node(new_state, current, action, current.path_cost + 1)
                if (
                    child.state not in explored
                    or child.path_cost < explored[child.state]
                ):
                    distinct_states_met += 1
                    if child.state.is_goal():
                        return child
                    frontier.append(child)

print("DFS:")
run_for_tests(dfs)

def ids(start_node):
    for depth in range(sys.maxsize):
        current_states = 0
        node = dfs(start_node, depth)
        if node != False:
            return node
    return False

print("IDS:")
run_for_tests(ids)

def a_star(start_node):
    states_met = 0
    distinct_states_met = 0
    if start_node.state.is_goal():
        return start_node
    frontier = []
    heapq.heappush(
        frontier,
        (
            start_node.path_cost
            + start_node.state.calculate_heuristic(),
            start_node,
        ),
    )
    frontier_state_set = set()
    frontier_state_set.add(start_node.state)
    explored = set()
    while True:
        if not frontier:
            return False
        current = heapq.heappop(frontier)
        frontier_state_set.remove(current[1].state)
        explored.add(current[1].state)
        for action in Direction.actions():
            new_state = current[1].state.transition(action)
            if new_state is not False:
                child = Node(
                    new_state, current[1], action, current[1].path_cost + 1
                )
                states_met += 1
                if (
                    child.state not in explored
                    and child.state not in frontier_state_set
                ):
                    distinct_states_met += 1
                    if child.state.is_goal():
                        return child
                    heapq.heappush(
                        frontier,
                        (
                            child.path_cost
                            + child.state.calculate_heuristic(),
                            child,
                        ),
                    )
                    frontier_state_set.add(child.state)

run_for_tests(a_star)

def ucs(start_node):
    states_met = 0
    distinct_states_met = 0
    if start_node.state.is_goal():
        return start_node
    frontier = []
    heapq.heappush(
        frontier,
        (
            start_node.path_cost,
            start_node,
        ),
    )
    frontier_state_set = set()
    frontier_state_set.add(start_node.state)
    explored = set()
    while True:
        if not frontier:
            return False
        current = heapq.heappop(frontier)
        frontier_state_set.remove(current[1].state)
        explored.add(current[1].state)
        for action in Direction.actions():
            new_state = current[1].state.transition(action)
            if new_state is not False:
                child = Node(
                    new_state, current[1], action, current[1].path_cost + 1
                )
                states_met += 1
                if (
                    child.state not in explored
                    and child.state not in frontier_state_set
                ):
                    distinct_states_met += 1
                    if child.state.is_goal():
                        return child
                    heapq.heappush(
                        frontier,
                        (
                            child.path_cost,
                            child,
                        ),
                    )
                    frontier_state_set.add(child.state)

run_for_tests(ucs)

