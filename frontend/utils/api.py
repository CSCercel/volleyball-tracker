import streamlit as st
import requests
from typing import List, Dict


API_BASE = st.secrets["API_BASE_URL"]


def get_player(name: str) -> Dict:
    response = requests.get(f"{API_BASE}/players/{name}")
    response.raise_for_status()
    return response.json()


def get_players() -> List[Dict]:
    response = requests.get(f"{API_BASE}/players")
    response.raise_for_status()
    return response.json()


def create_player(name: str) -> Dict:
    response = requests.post(
        f"{API_BASE}/players/create",
        json={"name": name}
    )
    response.raise_for_status()
    return response.json()


def delete_player(player_id: int):
    response = requests.delete(f"{API_BASE}/players/{player_id}")
    response.raise_for_status()
    return response.json()


def create_match(match_data: Dict) -> Dict:
    response = requests.post(
        f"{API_BASE}/matches/create",
        json=match_data
    )
    response.raise_for_status()
    return response.json()


def get_matches(status: str = "all") -> List[Dict]:
    response = requests.get(f"{API_BASE}/matches/", params={"status": status})
    response.raise_for_status()
    return response.json()


def get_match(match_id: str) -> Dict:
    response = requests.get(f"{API_BASE}/matches/{match_id}")
    response.raise_for_status()
    return response.json()


def submit_match_results(match_id: str, blue_score: int, red_score: int) -> Dict:
    response = requests.put(
        f"{API_BASE}/matches/{match_id}/results",
        json={"blue_score": blue_score, "red_score": red_score}
    )
    response.raise_for_status()
    return response.json()
