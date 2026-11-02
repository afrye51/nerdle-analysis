import re
import numpy as np
import time

eq_len = 8
allow_multiply_add_zero = False
eql = '='
eql_pos = np.arange(4, 7)
sym = ['+', '-', '*', '/']
sym_pos = np.arange(1, 5)
num = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
# num = ['1', '2', '3']
num_pos = np.arange(0, 8)
zer = '0'
zer_pos = np.arange(1, 8)

equation_positions = [[], [], [], [], [], [], [], []]
for pos in eql_pos:
    equation_positions[pos].append(eql)
for pos in sym_pos:
    for symbol in sym:
        equation_positions[pos].append(symbol)
for pos in num_pos:
    for number in num:
        equation_positions[pos].append(number)
for pos in zer_pos:
    equation_positions[pos].append(zer)
max_len = 0
for col in equation_positions:
    if len(col) > max_len:
        max_len = len(col)
equation_positions_np = np.zeros((eq_len, max_len), dtype='U1')
for i, col in enumerate(equation_positions):
    equation_positions_np[i, :len(col)] = col

def mixed_base_iterator(bases):
    """Yields each position combination for a mixed-base counter."""
    current = np.zeros_like(bases, dtype=np.uint8)
    total = np.prod(bases)
    for _ in range(total):
        yield current.copy()
        # Increment mixed base
        for i in reversed(range(len(bases))):
            current[i] += 1
            if current[i] < bases[i]:
                break
            current[i] = 0  # rollover

# def mixed_base_iterator(bases):
#     """Generator for counting in mixed-base defined by bases."""
#     current = np.zeros_like(bases, dtype=np.uint8)
#     total = np.prod(bases)
#
#     # Increment with carry
#     for _ in range(total):
#         yield current.copy()
#         current[-1] += 1
#         while True:
#             overflow = current >= bases
#             if not np.any(overflow):
#                 break
#
#             # get the first (lowest-indexed) overflow from the right
#             i = np.where(overflow)[0][-1]  # choose the highest index overflow
#             current[i] = 0
#             current[i - 1] += 1
#     return

def is_equation_positions_eq(eq):
    return False

def fast_validity_check(eq_str):
    # No invalid operator adjacency
    if re.search(r'[+\-*/=]{2,}', eq_str):
        return False

    # Only one equal sign
    if eq_str.count('=') != 1:
        return False

    # No lone or leading zeros
    if re.search(r'\b0[/+*\-=]|[/+*\-]0|=00', eq_str):
        return False

    return True

def is_valid_equation(eq_str):
    if not fast_validity_check(eq_str):
        return False
    try:
        lhs, rhs = eq_str.split('=')
        if not lhs or not rhs:
            return False
        return eval(lhs) == eval(rhs)
    except Exception:
        return False

# Interesting regex questions:
# useless 1* \b1[/*]|[/*]1[^\d]
# useless 0+ or 0* \b0[/+*\-=]|[/+*\-]0

# Replace all digits with '_', then deduplicate
# = in position 1
# = in position 2
# = in position 3
# __*_=___
# _*__=___
# _+9_=10_
# 9_+_=10_

# __+__=__
# __-__=__
# ___/_=__
# 10_-_=9_
# _+_+_=__
# _+_-_=1_
# _+_*_=__
# _+_/_=1_
# _-_+_=__
# _-_-_=__ 0
# _-_*_=__
# _-_/_=__ 0
# _*_+_=__
# _*_-_=__
# _*_*_=__
# _*_/_=__
# _/_+_=1_
# _/_-_=__ 0
# _/_*_=__
# _/_/_=__ 0

# ___/__=_
# 10_-9_=_
# _+_-1_=_
# _+_/__=_ 0
# _-_+__=_
# _-_-__=_ 0
# _-_*__=_
# _-_/__=_ 0
# _*_-__=_
# _*_/__=_
# _/_+__=_
# _/_-__=_ 0
# _/_*__=_
# _/_/__=_ 0
# _+__-_=_
# _+__/_=_
# _-__+_=_
# _-__-_=_ 0
# _-__*_=_ 0
# _-__/_=_
# _*__-_=_
# _*__/_=_
# _/__+_=_
# _/__-_=_
# _/__*_=_
# _/__/_=_
# __+_-_=_
# __+_/_=_
# __-_+_=_
# __-_-_=_
# __-_*_=_
# __-_/_=_
# 1_*1-_=_
# __*_/_=_
# __/_+_=_
# __/_-_=_
# __/_*_=_
# __/_/_=_

# has a -
# has a +
# has a /
# has a *
# has only one symbol
# has two symbols
# has each pos as a number
# has each pos as a symbol
# has each digit
# has multiples of each digit

def index_to_eqstr(index_array):
    return ''.join(equation_positions[i][idx] for i, idx in enumerate(index_array))

def write_to_csv(equation_strings):
    with open('nerdle_eqns.csv', 'w') as outfile:
        for eqn in equation_strings:
            outfile.write(eqn + '\n')

def generate_all_eqs():

    unvalidated_equations = []
    eq_num = 0
    indexes = np.zeros(eq_len, np.uint8)  # [0, 0, 0, 0, 0, 0, 0, 0]
    pos_lengths = np.zeros(eq_len, np.uint8)  # [2, 5, 5, 5, 6, 4, 4, 3]
    for i, pos in enumerate(equation_positions):
        pos_lengths[i] = len(pos)

    valid_eqs = []
    total_count = np.prod(pos_lengths)
    count_with_useless_zero = 0
    print(f'total: {total_count}')
    start_time = time.time()
    pct = total_count // 100
    for i, combo in enumerate(mixed_base_iterator(pos_lengths)):
        eqn = index_to_eqstr(combo)
        if is_valid_equation(eqn):
            valid_eqs.append(eqn)
        if i % pct == 0 and i != 0:
            print(f'{100 * i / total_count} percent complete, {((time.time() - start_time) * (total_count - i) / i) // 60} minutes remaining')
    print(len(valid_eqs))
    print(f'took: {time.time() - start_time} seconds')
    write_to_csv(valid_eqs)

def main():
    generate_all_eqs()

if __name__ == "__main__":
    main()
