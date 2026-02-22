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
