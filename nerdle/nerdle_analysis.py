import re
import numpy as np
import time
import pickle
from colorama import Fore, Style
from collections import defaultdict
from functools import cache

def load_answers(filename):
    with open(filename, 'r') as infile:
        answers = [line.strip() for line in infile]
        return answers

def write_rankings_to_csv(color_list):
    with open('nerdle_disparity_ranks_one_step.csv', 'w') as outfile:
        for color_element in color_list:
            outfile.write(f'{color_element[1]},')
            for count in color_element[0]:
                outfile.write(f'{count},')
            outfile.write('\n')

def load_rankings_from_csv(filename='nerdle_disparity_ranks_one_step.csv'):
    color_list = []
    with open(filename, 'r') as infile:
        for line in infile:
            row = line.strip()
            vals = row.split(',')
            color_list.append([vals[0], vals[1:-1]])
        color_list.sort(key=lambda x: x[0][0])
        return color_list

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
# Cache should be a maximum of 18k*18k*10*3 ~ 10GB
# Was storing ~3GB/10% of the total 36M combinations
# @cache
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

def score_guesses_old(guesses, answer, prev_step_guesses=None):
    if prev_step_guesses is not None:
        colored_dict = {}
        for guess in guesses:
            colored = score_guess(guess, answer)
            if guess in prev_step_guesses:
                if colored in colored_dict.keys():
                    current = colored_dict[colored]
                    current[0] += 1
                    current[1].append(guess)
                    colored_dict[colored] = current
                else:
                    colored_dict[colored] = [1, [guess]]
    else:
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

    gss = '24/6+5=9'
    two = '16-2-5=9'
    two = '2-9+13=6'
    two = '6*5-9=21'
    two = '8+6+6=20'
    col = 'p__pp_p_'
    size_arr = []
    sorted_guesses = []
    for color in colored_dict.keys():
        size_arr.append(colored_dict[color][0])
        sorted_guesses.append([colored_dict[color][0], color, colored_dict[color][1]])
    size_arr = np.sort(np.array(size_arr))[::-1]
    sorted_guesses.sort(key=lambda x: x[0], reverse=True)
    return size_arr, sorted_guesses

def score_guesses_compute_size_arr(guess, possible_answers, return_sorted_guesses=False):
    colored_dict = {}
    for possible_answer in possible_answers:
        colored = score_guess(guess, possible_answer)
        if colored in colored_dict.keys():
            current = colored_dict[colored]
            current[0] += 1
            current[1].append(guess)
            colored_dict[colored] = current
        else:
            colored_dict[colored] = [1, [guess]]

    if not return_sorted_guesses:
        size_arr = []
        for color in colored_dict.keys():
            size_arr.append(colored_dict[color][0])
        size_arr = np.sort(np.array(size_arr))[::-1]
        return size_arr, None
    else:
        size_arr = []
        sorted_guesses = []
        for color in colored_dict.keys():
            size_arr.append(colored_dict[color][0])
            sorted_guesses.append([colored_dict[color][0], color, colored_dict[color][1]])
        size_arr = np.sort(np.array(size_arr))[::-1]
        sorted_guesses.sort(key=lambda x: x[0], reverse=True)
        return size_arr, sorted_guesses

def score_guesses_min_max_bin(guesses, possible_answers):
    start_time = time.time()
    pct = len(guesses) // 100

    min_max_bin = np.inf
    min_max_index = 0
    for i, guess in enumerate(guesses):
        size_arr, _ = score_guesses_compute_size_arr(guess, possible_answers)
        if size_arr[0] < min_max_bin:
            min_max_bin = size_arr[0]
            min_max_index = i
        if i % pct == 0 and i != 0:
            print(f'{int(round(100 * i / len(guesses), 0))} percent complete, {int(round(((time.time() - start_time) * (len(guesses) - i) / i) / 60))} minutes remaining')

    best_guess = guesses[min_max_index]
    size_arr, sorted_guesses = score_guesses_compute_size_arr(best_guess, possible_answers, True)
    return best_guess, size_arr, sorted_guesses

def normalize_equation(answer):
    lhs, rhs = answer.split('=')
    tokens = re.findall(r'\d+|[+*/-]', lhs)
    digits = re.findall(r'\d+', lhs)
    operators = re.findall(r'[+*/-]', lhs)
    num_mult = operators.count('*')
    num_plus = operators.count('+')
    num_minus = operators.count('-')
    num_divide = operators.count('/')
    norm_eqn = answer

    # operator order: *+-/
    # Push smaller digits to the left
    # multiple *, put smallest digit first
    # 6*5+4 -> 5*6+4
    # 6*5-4 -> 5*6-4
    # 6*5/4 -> 5*6/4
    # 6+5*4 -> 4*5+6
    # 6-5*4 -> =====
    # 6/5*4 -> 4*6/5
    # 6+5-4 -> 5+6-4
    # 6+5/4 -> =====
    # 6-5+4 -> 
    # 6-5/4 ->
    # 6/5+4 ->
    # 6/5-4 ->

    if len(operators) == 2:
        if num_mult == 2:
            digits = digits.sort()
            norm_eqn = digits[0] + '*' + digits[1] + '*' + digits[2] + '=' + rhs
        elif num_plus == 2:
            digits = digits.sort()
            norm_eqn = digits[0] + '+' + digits[1] + '+' + digits[2] + '=' + rhs
        elif num_minus == 2:
            digits[1:] = digits[1:].sort()
            norm_eqn = digits[0] + '-' + digits[1] + '-' + digits[2] + '=' + rhs
        elif num_divide == 2:
            digits[1:] = digits[1:].sort()
            norm_eqn = digits[0] + '/' + digits[1] + '/' + digits[2] + '=' + rhs
    elif len(operators) == 1:
        if num_mult == 1:
            print()

    else:
        print(f'invalid equation for deduplication: {answer}')
        return None
    return norm_eqn


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

# Given:
#   All possible answers/guesses
#   an array of still possible answers
# Find the answer that splits the group with the smallest largest duplicate color stack
#
def compute_colors_step(all_answers, possible_answers):
    sorted_colors = []
    for i, guess in enumerate(all_answers):
        sorted_color, _ = score_guesses(possible_answers, guess)
        # sorted_colors.append([sorted_color, guess])
    sorted_colors.sort(key=lambda x: x[0][0])
    return sorted_colors

def simulate_solution(guess, answer, remaining_answers, depth, max_depth=5):
    feedback = score_guess(guess, answer)  # like Wordle coloring
    if feedback == 'g' * len(guess):
        return depth  # Solved!

    # if depth >= max_depth:
    #     return depth  # Truncated at 4+

    # Prune answer space
    new_remaining = [
        ans for ans in remaining_answers
        if score_guess(guess, ans) == feedback
    ]

    # Base case: if only one left, it's guaranteed next
    if len(new_remaining) == 1:
        return depth + 1

    # Try all possible next guesses and pick the one with the best expected outcome
    expected_depth = max_depth
    for next_guess in new_remaining:
        depths = []
        for possible_answer in new_remaining:
            d = simulate_solution(next_guess, possible_answer, new_remaining, depth + 1, max_depth)
            depths.append(d)
        expected_depth = max(depths)

    return expected_depth

# def compute_steps(all_answers):
#     sorted_colors = load_rankings_from_csv()
#     for
#     for i, guess in enumerate(all_answers):
#         graph_this = defaultdict(list)
#         graph_this[guess].append([])


    compute_colors_step(all_answers, all_answers)


# def loop_score_guesses_threaded(answers, j=8):
#     sorted_colors = []
#     start_time = time.time()
#     num_per_thread = len(answers) // j
#     for i in range(j):
#         if i != j-1:
#             this_thread_answers = answers[num_per_thread*i:num_per_thread*(i+1)]
#         else:
#             this_thread_answers = answers[num_per_thread * i:]
#         # sorted_colors_this_thread = []
#         # for i in range(len(this_thread_answers)):
#             # sorted_color, _ = score_guesses(this_thread_answers, answer)
#             # sorted_colors_this_thread.append([sorted_color, answer])
#             # return sorted_colors

# Data structure:
# For each word, use it as the answer (grab all commutative words)
#   Guess each word against it
#   Compute and merge all color strings, resulting in an array of [color, guesses, num_steps, future]
#   For each [word, or possible guess], do that again, storing the result in future recursively
#   A branch ends when there are only two
#       pickle.dump(array, file)
#       array = pickle.load(file)
#   When fully done with every branch, store it in pickle and break to inspect quickly
# Is there a way to use recursion and depth first search to find the maximum length of each branch,
#   then step backwards and compute the average and standard deviation at each node (including the root).

# (guesses, possible_answers)
def build_color_tree_for_answers(all_guesses, remaining_answers, depth, get_feedback_func, max_depth=2):
    if depth > max_depth:
        print(f'max depth reached, {len(remaining_answers)} remaining possibilities')
        return {"depth": depth, "probability": (1.0 / len(remaining_answers)), "branches": []}
    best_guess, _, merged_colors = get_feedback_func(all_guesses, remaining_answers)
    branches = []
    for color in merged_colors:
        if color[0] <= 2:
            if color[0] == 1:
                branches.append({"color": color, "node": {"depth": depth, "probability": 1.0, "guess": None, "branches": []}})
            elif color[0] == 2:
                future = {"depth": depth, "probability": 0.5, "guess": None, "branches": []}
                branches.append({"color": 'g'*len(all_guesses[0]), "node": future})
                future = {"depth": depth, "probability": 0.5, "guess": None, "branches": []}
                branches.append({"color": 'g'*len(all_guesses[0]), "node": future})
            else:
                print(f'{color[0]} in group?')
                branches.append({"color": color, "node": {"depth": depth, "probability": 1.0, "guess": None, "branches": []}})
        else:
            future = build_color_tree_for_answers(all_guesses, color[2], depth+1, get_feedback_func)
            branches.append({"color": color, "node": future})
    node = {"depth": depth, "probability": None, "guess": best_guess, "branches": branches}
    return node

def main():
    all_answers = load_answers('nerdle_eqns.csv')
    # all_answers = all_answers[:100]
    sorted_colors = []
    start_time = time.time()
    pct = len(all_answers) // 100
    # for i, guess in enumerate(all_answers):
    normalize_equation('3*2+4=10')
    answer = all_answers[0]
    tree = build_color_tree_for_answers(
        all_guesses=all_answers,
        remaining_answers=all_answers,
        depth=1,
        get_feedback_func=score_guesses_min_max_bin)
    filehandler = open(f'tree_{answer}.pickle', "wb")
    pickle.dump(tree, filehandler)
    # array = pickle.load(file)
    # if i % pct == 0 and i != 0:
    #     print(f'{int(round(100 * i / len(all_answers), 0))} percent complete, {int(round(((time.time() - start_time) * (len(all_answers) - i) / i) / 60))} minutes remaining')
    # sorted_colors.sort(key=lambda x: x[0][0])
    # print(sorted_colors[:5])
    # write_rankings_to_csv(sorted_colors)
    print(f'took: {time.time() - start_time} seconds')
    print('')

# def main():
#     all_answers = load_answers('nerdle_eqns.csv')
#     # all_answers = all_answers[:100]
#     sorted_colors = []
#     start_time = time.time()
#     pct = len(all_answers) // 100
#     # for i, guess in enumerate(all_answers):
#     normalize_equation('3*2+4=10')
#     guess = all_answers[0]
#     sorted_color, ranked_colors = score_guesses(all_answers, guess)
#     sorted_colors.append([sorted_color, guess])
#     for color_two in ranked_colors:
#         answers_two = color_two[2]
#         for i_2, guess_two in enumerate(answers_two):
#             sorted_color_two, ranked_colors_two = score_guesses(answers_two, guess_two)
#             for color_three in ranked_colors_two:
#                 answers_three = color_three[2]
#                 for i_3, guess_three in enumerate(answers_three):
#                     sorted_color_three, ranked_colors_three = score_guesses(answers_three, guess_three)
#                     for color_four in ranked_colors_three:
#                         answers_four = color_four[2]
#                         for i_4, guess_four in enumerate(answers_four):
#                             sorted_color_four, ranked_colors_four = score_guesses(answers_four, guess_four)
#                             print()
#     # if i % pct == 0 and i != 0:
#     #     print(f'{int(round(100 * i / len(all_answers), 0))} percent complete, {int(round(((time.time() - start_time) * (len(all_answers) - i) / i) / 60))} minutes remaining')
#     # sorted_colors.sort(key=lambda x: x[0][0])
#     print(sorted_colors[:5])
#     # write_rankings_to_csv(sorted_colors)
#     print(f'took: {time.time() - start_time} seconds')

if __name__ == "__main__":
    main()