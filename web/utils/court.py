import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import List, Tuple, Union
import random
import numpy as np
import pandas as pd

# Volleyball court dimensions
COURT_WIDTH = 9
COURT_LENGTH = 18

# Function to plot volleyball court
def plot_volleyball_court() -> Tuple[Figure, Axes]:
    fig, ax = plt.subplots(figsize = (10, 6))

    # Set the background color
    fig.patch.set_facecolor('bisque')
    ax.set_facecolor('bisque')

    # Create the court (rectangular)
    ax.plot([0, COURT_WIDTH], [0, 0], color = 'darkred', lw = 3)  # Bottom boundary
    ax.plot([COURT_WIDTH, COURT_WIDTH], [0, COURT_LENGTH], color = 'darkred', lw = 3)  # Right boundary
    ax.plot([COURT_WIDTH, 0], [COURT_LENGTH, COURT_LENGTH], color = 'darkred', lw = 3)  # Top boundary
    ax.plot([0, 0], [COURT_LENGTH, 0], color = 'darkred', lw = 3)  # Left boundary

    # Centerline
    ax.plot([COURT_WIDTH / 2, COURT_WIDTH / 2], [0, COURT_LENGTH], color = 'black', lw = 3, linestyle = '--')

    # Add the attack lines (for each team side)
    ax.plot([3, 3], [0, COURT_LENGTH], color = 'darkred', lw = 2, linestyle = '--', alpha = 0.5)  # Red team's attack line
    ax.plot([6, 6], [0, COURT_LENGTH], color = 'darkred', lw = 2, linestyle = '--', alpha = 0.5)  # Blue team's attack line

    # Set the court limits
    ax.set_xlim([0, COURT_WIDTH])
    ax.set_ylim([0, COURT_LENGTH])

    # Hide axes
    ax.set_xticks([])
    ax.set_yticks([])

    return fig, ax

# Function to assign positions based on team size
def assign_positions(team: List[str], side: str) -> Tuple[List[int], Union[List[int], None]]:
    # Dictionary for positions
    positions = {
        1: [1],
        2: [1, 3],
        3: [1, 3, 5],
        4: [1, 2, 3, 5],
        5: [1, 2, 3, 4, 5],
        6: [1, 2, 3, 4, 5, 6]
    }

    # Shuffle team
    random.shuffle(team)

    # Split the teams between on_court and bench
    on_court = team[:6]
    bench = team[6:]

    # Get the assigned positions based on the number of players
    if len(team) < 1:
        raise ValueError("Team must have at least one player")
    else:
        assigned_positions = positions[len(on_court)]

    # Adjust for the side of the court
    if side == "blue":
        # Blue team is on the left side (positions 1, 2, 3, etc.)
        return assigned_positions, bench
    elif side == "red":
        # Red team is on the right side (positions 1, 2, 3, etc. shifted)
        return [pos + 6 for pos in assigned_positions], bench
    
# Function to map positions to coordinates on the court
def position_to_coordinates(position: int, side: str) -> Tuple[float, float]:
    # Coordinates mapping based on positions
    if side == "blue":
        # Blue team (left side of the court)
        if position == 1:
            return (1, 2)  # pos 1
        elif position == 2:
            return (3.5, 2)  # pos 2
        elif position == 3:
            return (3.5, 9)  # pos 3
        elif position == 4:
            return (3.5, 16)  # pos 4
        elif position == 5:
            return (1, 16)  # pos 5
        elif position == 6:
            return (1, 9)  # pos 6
    elif side == "red":
        # Red team (right side of the court)
        if position == 7:
            return (8, 16)  # pos 1
        elif position == 8:
            return (5.5, 16)  # pos 2
        elif position == 9:
            return (5.5, 9)  # pos 3
        elif position == 10:
            return (5.5, 2)  # pos 4
        elif position == 11:
            return (8, 2)  # pos 5
        elif position == 12:
            return (8, 9)  # pos 6
         
# Plot the volleyball court for a match
def plot_match_court(blue_team: List[str], red_team: List[str]) -> Figure:
    fig, ax = plot_volleyball_court()

    # Assign positions
    blue_team_positions, blue_bench = assign_positions(blue_team, "blue")
    red_team_positions, red_bench = assign_positions(red_team, "red")

   # Plot the positions for blue team
    for i, position in enumerate(blue_team_positions):
        x, y = position_to_coordinates(position, "blue")
        ax.scatter(x, y, color='blue', s = 500, zorder = 5, alpha = 0.25)
        ax.text(x, y, blue_team[i], fontsize = 12, ha = 'center', va = 'center', color = 'black', zorder = 6, weight = "bold")

        # Plot the positions for red team
        for i, position in enumerate(red_team_positions):
            x, y = position_to_coordinates(position, "red")
            ax.scatter(x, y, color = 'red', s = 500, zorder = 5, alpha = 0.25)
            ax.text(x, y, red_team[i], fontsize = 12, ha = 'center', va = 'center', color = 'black', zorder = 6, weight = "bold")

    # Set ball for Service
    first_serve = random.choice(["blue", "red"])

    if first_serve == "blue":
        ball_x, ball_y = (0.2, 2)
    else:
        ball_x, ball_y = (8.8, 16)

    ax.scatter(ball_x, ball_y, color = "yellow", edgecolors = "darkblue", zorder = 6, s = 300)

    # Show the Bench
    if len(blue_bench) > 0:
        bench_x = np.linspace(start = 0, stop = 2.5, num = len(blue_bench))
        for player_name, x_i in zip(blue_bench, bench_x):
            x = x_i
            y = -1
            ax.text(x, y, player_name, fontsize = 12, ha = 'center', va = 'center', color = 'blue', zorder = 6, weight = "bold")

    if len(red_bench) > 0:
        bench_x = np.linspace(start = 6.5, stop = 9, num = len(red_bench))
        for player_name, x_i in zip(red_bench, bench_x):
            x = x_i
            y = -1
            ax.text(x, y, player_name, fontsize = 12, ha = 'center', va = 'center', color = 'red', zorder = 6, weight = "bold")

    return fig
