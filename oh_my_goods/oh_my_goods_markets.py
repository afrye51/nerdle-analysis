import random
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

# Define the card distribution
cards = (
        ["white sun"] * 9 +
        ["white no"] * 8 +
        ["black sun"] * 8 +
        ["black no"] * 9 +
        ["yellow sun"] * 9 +
        ["yellow no"] * 8 +
        ["red sun"] * 8 +
        ["red no"] * 9 +
        ["green sun"] * 13 +
        ["green no"] * 13
)


# Function to simulate a single draw until two suns
def simulate_draw():
    indices = list(range(len(cards)))
    random.shuffle(indices)

    drawn_cards = []
    sun_count = 0
    color_counts = defaultdict(int)

    for index in indices:
        card = cards[index]
        drawn_cards.append(card)

        color = card.split()[0]
        if "sun" in card:
            sun_count += 1
        color_counts[color] += 1

        if sun_count >= 2:
            break

    return len(drawn_cards), dict(color_counts)


# Number of simulations
num_simulations = 100000

# Run the simulations
draw_counts = []
color_counts_list = defaultdict(list)

for _ in range(num_simulations):
    draw_count, color_counts = simulate_draw()
    draw_counts.append(draw_count)
    for color in ["white", "black", "yellow", "red", "green"]:
        color_counts_list[color].append(color_counts.get(color, 0))

# Create histograms for total draws and color counts
plt.figure(figsize=(14, 6))

# Histogram for draws until two suns
plt.subplot(1, 2, 1)
counts, bins = np.histogram(draw_counts, bins=range(min(draw_counts), max(draw_counts) + 2))
cumulative_counts = np.cumsum(counts[::-1])[::-1]
percentages = cumulative_counts / num_simulations * 100
bin_centers = bins[:-1] + np.diff(bins) / 2 - 1  # Correctly adjust bin centers

plt.step(bin_centers, percentages, where='post', color='blue')
plt.title("Histogram of Cards From One Market (≥ x)")
plt.xlabel("Number of Draws")
plt.ylabel("Percentage of Simulations")
plt.ylim(0, 100)

# Add striped lines at 10% intervals
for y in range(10, 101, 10):
    plt.axhline(y=y, color='gray', linestyle='--', alpha=0.5)

# Ensure integer x-axis labels
plt.xticks(range(2, 11))
plt.xlim(1.5, 10.5)

# Histograms for color counts
plt.subplot(1, 2, 2)
colors = ["white", "black", "yellow", "red", "green"]
for color in colors:
    counts, bins = np.histogram(color_counts_list[color], bins=range(max(color_counts_list[color]) + 2))
    cumulative_counts = np.cumsum(counts[::-1])[::-1]
    percentages = cumulative_counts / num_simulations * 100
    bin_centers = bins[:-1] + np.diff(bins) / 2 - 1  # Correctly adjust bin centers

    plt.step(bin_centers, percentages, where='post', label=color)

plt.title("Histograms of Color Counts From One Market (≥ x)")
plt.xlabel("Number of Cards of Each Color")
plt.ylabel("Percentage of Simulations")
plt.ylim(0, 100)
plt.xlim(0.5, 5.5)

# Add striped lines at 10% intervals
for y in range(10, 101, 10):
    plt.axhline(y=y, color='gray', linestyle='--', alpha=0.5)

plt.legend()

plt.tight_layout()
plt.show()
