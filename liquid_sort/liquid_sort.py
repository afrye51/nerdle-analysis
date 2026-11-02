import re
import numpy as np
import time
import pickle
from colorama import Fore, Style
from collections import defaultdict
from functools import cache
h = 4
k = 2
n = 3
colors = [Fore.BLUE, Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLACK_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTRED_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTCYAN_EX]

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
        return bottle_str + Style.RESET_ALL


def get_top_colors(bottles):
    top_colors = np.zeros((n+k, 2))
    top_colors[0] = bottles[0]
    for i in range(top_colors.shape[0]):
        if top_colors[i,0] == -1:
            for j in range(1, h):
                if bottles[i, j] != -1:
                    top_colors[i,0] = bottles[i, j]

    for i in range(top_colors.shape[0]):
        for j in range(h):
            if bottles[i, j] == top_colors[i]:
                top_colors[i, 1] += 1
            elif bottles[i, j] == -1:
                continue
            else: # End of that stack in that row
                break
    return top_colors


def get_possible_moves(bottles):
    possible_moves = []
    return possible_moves


def solve_recursive(bottles):
    return
    # for row in bottles:


def main():
    bottles = Bottle(np.array([[0, 0, 0, -1, -1], [1, 1, 1, -1, -1], [2, 2, 2, -1, -1], [0, 1, 2, -1, -1]]).T)

    print(f"original bottles: {bottles}")
    start_time = time.time()
    # pct = len(all_answers) // 100

    print(f"final bottles: {bottles}")
    print(f'took: {time.time() - start_time} seconds')
    print('')

if __name__ == "__main__":
    main()
