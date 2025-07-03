import re
import numpy as np
import time
from colorama import Fore, Style
from collections import defaultdict

def load_answers(filename):
    with open(filename, 'r') as infile:
        answers = [line.strip() for line in infile]
        return answers

# Information is: (1 point for green, 0.5 points for purple) / len
#   1 is all green
#   1 green is 0.125

# 18k solns
# 3^8 possible states (3^7? 2-6k)
# Count the total number of different answer states, and the count of each
#   The minimum maximum count of answers with the same state -> the best guess
#   Try each answer against all the others, and compute that sorted array of unknown length, vals
#       Compute an array of the colored state for each answer
#       Deduplicate, keeping a count of duplicates
#       Sort that array by duplicate count, return the sorted array
#       Rank them by the first element count

# 224/4=56
# 242-4=//
# green = [2___4=__]
# unused_syms = [2, 4, /, 5, 6]
# purple = [_42___/_]
def score_guess(guess, answer):
    colored = ['_']*len(answer)
    unused_syms = list(answer)
    for i in range(len(answer)):
        if guess[i] == answer[i]:
            colored[i] = 'g'
            unused_syms.remove(answer[i])
    for i in range(len(guess)):
        if colored[i] == '_':
            if guess[i] in unused_syms:
                colored[i] = 'p'
                unused_syms.remove(guess[i])
    return ''.join(colored)

def score_guesses(guesses, answer):
    colored_dict = {}
    for guess in guesses:
        colored = score_guess(guess, answer)
        if colored in colored_dict.keys():
            current = colored_dict[colored]
            current[0] += 1
            current[1].append(guess)
            colored_dict[colored] = current
        else:
            colored_dict[colored] = [1, [guess]]

    size_arr = []
    sorted_guesses = []
    for color in colored_dict.keys():
        size_arr.append(colored_dict[color][0])
        sorted_guesses.append([colored_dict[color][0], color, colored_dict[color][1]])
    size_arr = np.sort(np.array(size_arr))[::-1]
    sorted_guesses.sort(key=lambda x: x[0], reverse=True)
    return size_arr, sorted_guesses

def pretty_print_answer(answer, colored):
    print(Style.RESET_ALL)
    for i in range(len(answer)):
        if colored[i] == 'g':
            print(Fore.GREEN + answer[i], end='')
        elif colored[i] == 'p':
            print(Fore.MAGENTA + answer[i], end='')
        else:
            print(Fore.WHITE + answer[i], end='')
    print(Style.RESET_ALL)
    print()

def main():
    all_answers = load_answers('nerdle_eqns.csv')
    sorted_colors = []
    start_time = time.time()
    pct = len(all_answers) // 100
    # sorted_colors_trunc = np.zeros((len(all_answers), 5))
    for i, answer in enumerate(all_answers):
        sorted_color, _ = score_guesses(all_answers, answer)
        sorted_colors.append([sorted_color, answer])
        # sorted_colors_trunc[i] = sorted_color[:5]
        if i % pct == 0 and i != 0:
            print(f'{round(100 * i / len(all_answers), 0)} percent complete, {((time.time() - start_time) * (len(all_answers) - i) / i) // 60} minutes remaining')
    sorted_colors.sort(key=lambda x: x[0][0])
    # sorted_colors_trunc.sort(axis=0)
    print(sorted_colors[:5])
    print(f'took: {time.time() - start_time} seconds')
    # print(sorted_colors_trunc[0])
    # pretty_print_answer(score_guess('242-4=//', '224/4=56'))

if __name__ == "__main__":
    main()