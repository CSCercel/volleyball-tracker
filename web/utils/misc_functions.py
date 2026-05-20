import random
from typing import Tuple, List, Dict

# Function to shuffle players when drafting
def shuffle_players(players: Dict) -> Tuple[List[Dict], List[Dict]]:
    random.shuffle(players)
    midpoint = len(players) // 2

    # Randomly select where the extra player will go
    if len(players) % 2 == 1:
        if random.choice([True, False]):
            midpoint += 1
        
    blue_team = players[: midpoint]
    red_team = players[midpoint:]

    return blue_team, red_team


# Functions to calculate ranks
def calculate_mmr(avg_points: float, efficiency: float) -> float:
    return avg_points * efficiency


def get_rank(mmr: float, matches_played: int) -> str:
    ranks = {
        "Iron I": [0, 0.1],
        "Iron II": [0.1, 0.2],
        "Iron III": [0.2, 0.3],
        "Bronze I": [0.3, 0.4],
        "Bronze II": [0.4, 0.5],
        "Bronze III": [0.5, 0.6],
        "Silver I": [0.6, 0.7],
        "Silver II": [0.7, 0.8],
        "Silver III": [0.8, 0.9],
        "Gold I": [0.9, 1.0],
        "Gold II": [1.0, 1.1],
        "Gold III": [1.1, 1.2],
        "Platinum I": [1.2, 1.3],
        "Platinum II": [1.3, 1.4],
        "Platinum III": [1.4, 1.5],
        "Diamond I": [1.5, 1.6],
        "Diamond II": [1.6, 1.7],
        "Diamond III": [1.7, 1.8],
        "Spiker": [1.8, 1.9],
        "Ace": [1.9, 2],
        "Sensei": [2, 9999]
    }
    
    if matches_played < 10:
        return "Unranked"
    else:
        for rank_name, bounds in ranks.items():
            if mmr >= bounds[0] and mmr < bounds[1]:
                return rank_name
