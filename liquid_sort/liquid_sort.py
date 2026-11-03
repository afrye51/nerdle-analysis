import re
import numpy as np
import time
import pickle
from colorama import Fore, Style
from collections import defaultdict
from functools import cache
import copy
h = 4 # bottle_height
k = 2 # num_spare_bottles
n = 10 # num_colors
colors = [Fore.BLUE, Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTRED_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTBLACK_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTCYAN_EX]

class Bottle:
    def __init__(self, bottles_array):
        self.bottles = bottles_array # (n+k, h) array
        if self.bottles.shape[0] != n+k or self.bottles.shape[1] != h:
            raise ValueError(f"Bottles array improperly sized: ({self.bottles.shape[0]}, {self.bottles.shape[1]}), but (n+k, h) is ({n+k},{h})")

    def __str__(self):
        bottle_str = Style.RESET_ALL + Style.BRIGHT + "\n"
        for row in self.bottles.T:
            for cell in row:
                if cell == -1:
                    bottle_str += Fore.WHITE + "| "
                else:
                    bottle_str += Fore.WHITE + "|" + colors[cell] + str(cell)
            bottle_str += Fore.WHITE + "|\n"
        return bottle_str[:-1] + Style.RESET_ALL


class TopColors:
    def __init__(self, bottles):
        self.empty = np.zeros((n+k), dtype=int)
        self.colors = -1*np.ones((n+k), dtype=int)
        self.heights = np.ones((n+k), dtype=int)

        for i in range(len(bottles)):
            self.empty[i] = np.count_nonzero(bottles[i] == -1)
            if self.empty[i] < h:
                self.colors[i] = bottles[i, self.empty[i]]
                for j in range(self.empty[i]+1, h):
                    if bottles[i, j] == self.colors[i]:
                        self.heights[i] += 1
                    else:
                        break
            else:
                self.colors[i] = -1
                self.heights[i] = 0

# Would you ever need to move a liquid block before it can be fully placed elsewhere?
#   1. Liquid of the same color is interchangeable, so as long as it's moving that full stack to x places, it doesn't matter which specifically goes where.
# If we're going to allow partial moves (2/1 -> 1/2 or 3/1 -> 1/3) that DON'T also move the rest of that block, how do we prevent infinite flipping?
#   1. Track moves, and disallow reverses of completed moves, by same [height, color, source, and dest]
#       Or track states, and kill it if we return to the same state we've had before?
#   2. Disallow moving liquid from one empty vial to another

def get_possible_moves(bottles):
    top_colors = TopColors(bottles)
    color_graph = np.zeros((n+k, n+k), dtype=int)
    for i in range(len(bottles)):
        for j in range(len(bottles)):
            if top_colors.colors[i] == top_colors.colors[j]:
                color_graph[i, j] = min(top_colors.heights[i], top_colors.empty[j])
            elif top_colors.colors[j] == -1:
                color_graph[i, j] = 4
    np.fill_diagonal(color_graph, 0)
    return color_graph, top_colors


def apply_move(bottles, top_colors, move):
    moving_color = bottles[move[0], top_colors.empty[move[0]]]
    moving_height = min(top_colors.heights[move[0]], top_colors.empty[move[1]])
    bottles[move[1], top_colors.empty[move[1]]-moving_height:top_colors.empty[move[1]]] = moving_color
    bottles[move[0], top_colors.empty[move[0]]:top_colors.empty[move[0]] + moving_height] = -1
    return bottles


def is_solved(bottles):
    for i in range(len(bottles)):
        if np.count_nonzero(bottles[i] == bottles[i, 0]) != h:
            return False
    return True


def solve_recursive(bottles, moves, depth, max_depth=60):
    if depth >= max_depth:
        # print(f"max depth reached: {max_depth}, is solved: {is_solved(bottles)}")
        return bottles, moves, depth

    color_graph, top_colors = get_possible_moves(bottles)
    if np.count_nonzero(color_graph) <= 0:
        return bottles, moves, depth
    for i in range(len(bottles)):
        for j in range(len(bottles)):
            if color_graph[i, j] != 0 and color_graph[i, j] >= top_colors.heights[i] and i != j:
                if top_colors.heights[i] == h or (top_colors.empty[i] + top_colors.heights[i] == h and top_colors.empty[j] == h):
                    break
                move = [i, j]
                moves_temp = copy.deepcopy(moves)
                moves_temp.append(move)
                # print(f"depth: {depth}{Bottle(bottles)}")
                bottles2, moves2, depth2 = solve_recursive(apply_move(copy.deepcopy(bottles), top_colors, move), moves_temp, depth+1)
                if is_solved(bottles2):
                    return bottles2, moves2, depth2
            # else: # loading non-full-height blocks

    return bottles, moves, depth


def main():
    # bottles = Bottle(np.array([[0, 0, 0, -1, -1],
    #                            [1, 1, 1, -1, -1],
    #                            [2, 2, 2, -1, -1],
    #                            [0, 1, 2, -1, -1]], dtype=int).T)
    # bottles = Bottle(np.array([[1, 0, 0, 0, -1, -1],
    #                            [2, 1, 1, 1, -1, -1],
    #                            [3, 2, 2, 2, -1, -1],
    #                            [0, 3, 3, 3, -1, -1]], dtype=int).T)
    bottles = Bottle(np.array([[5, 9, 5, 2, 1, 6, 0, 1, 7, 2, -1, -1],
                               [0, 6, 5, 9, 8, 4, 1, 2, 3, 3, -1, -1],
                               [6, 8, 4, 3, 3, 9, 7, 8, 1, 4, -1, -1],
                               [8, 7, 6, 7, 0, 5, 0, 4, 2, 9, -1, -1]], dtype=int).T) # Level 175

    print(f"original bottles: {bottles}")
    start_time = time.time()
    # pct = len(all_answers) // 100
    final_bottles_arr, final_moves, final_depth = solve_recursive(bottles.bottles, [], depth=0)
    final_bottles = Bottle(final_bottles_arr)

    print(f"is solved: {is_solved(final_bottles_arr)} at depth: {final_depth}, ")
    print(f"moves: {final_moves}")
    print(f"final bottles: {final_bottles}")
    print(f'took: {time.time() - start_time} seconds')
    print('')

if __name__ == "__main__":
    main()
