# Qwixx dice game

## Rules

### Rules

4x lines of the digits 1-12 in 4 colors, `Y` and `R` 1->12, `G` and `B` 12->1. You can only fill out boxes from left to right; you can't go backwards. Each turn, the roller rolls 2x white and one of each color (4 more). Sum the white dice, and add each player cna choose to add that to their card. Then the roller may add a white and a color and add that to the matching row of their card. The roller is forced cross off at least one of these numbers, or must take a 5-point penalty (maximum of 4). 

Once any player has five or more crosses in any row, AND they roll the ending number (either 2 or 12 based on color), they may "lock" out that row (if during action 1, other players may do it simultaneously). This removes that colored die from play, and grants an additional mark on that row (the lock counts as a mark too). Other players may no longer cross off number in this color?

The game ends at the end of a round when any player crosses off their 4th penalty, or any two dice are removed from the game

### Scoring

Scoring is computed for each color, as the sum of the counts of crosses below and including it; `n*(n+1)/2`: 

1x: 1
2x: 3
3x: 6
4x: 10
5x: 15
6x: 21
7x: 28
8x: 36
9x: 45
10x: 55
11x: 66
12x: 78

Which are added together, minus any penalties, for the final score

## Analysis

Start from the end, and work backwards computing possible score depending on dice rolls. 

### Human and adversarial strategy

Probably start isolated from the other player(s)'s actions, maybe later inform from them?
- Matching minimum lock quantity to be able to lock with them (+1 cross)
- Locking with them
- Locking out a row early to block their progress

Human strategies
- One "good" and one "bad" row of each direction, to better spread out the available field

### Basics and board states

Game states:
- Which rows are locked
- Furthest out cross on each row
  - Also how many crosses
- Penalty count

Total count of board states:
- rows (of 4)
  - Furthest cross (of 11)
  - Number of crosses (of 11)
- Locked? (of 4*3)
  - Did I lock it? (of 4)
- Penalties (of 5)
- Is it my turn? (of 2)

Total: `4*(11*11) * (4*3*4) * 5 * 2 = 232320`

Max turns: `4 + 4*11 = 48` (plus 4 per player)

Active: `2x6/2 * 1x6x4`
`6*6/2 * 6*6*6*6 = 23328`

Passive: `11`

### Stepping backwards. 

Decisions to make each turn:
If active player: Penalty or crossing one or two, inc. locking a row
`4*4*4`
`23328 * 64=`

If passive player: crossing a box or not
`11*4=44` * n_players

### Methodology

### 2-player 

### 4-player

## Conclusion

Thanks!
