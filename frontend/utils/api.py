import streamlit as st
import requests
from typing import List, Dict, Optional
from datetime import date


API_BASE = st.secrets["API_BASE_URL"]


def login(email: str, password: str):
    response = requests.post(
        f"{API_BASE}/auth/jwt/login",
        data={
            "username": email, 
            "password": password
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    response.raise_for_status()
    return response.json()


def get_headers():
    headers = {"Content-Type": "application/json"}
    if "access_token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    return headers


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
        json={"name": name},
        headers=get_headers()
    )
    response.raise_for_status()
    return response.json()


def create_match(match_data: Dict) -> Dict:
    response = requests.post(
        f"{API_BASE}/matches/create",
        json=match_data,
        headers=get_headers()
    )
    response.raise_for_status()
    return response.json()


def get_matches(
    status: str = "all",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Dict]:
    response = requests.get(
        f"{API_BASE}/matches/",
        params={
            "status": status,
            "start_date": str(start_date) if start_date else None,
            "end_date": str(end_date) if end_date else None
        }
    )
    response.raise_for_status()
    return response.json()


def get_match(match_id: str) -> Dict:
    response = requests.get(f"{API_BASE}/matches/{match_id}")
    response.raise_for_status()
    return response.json()


def submit_match_results(match_id: str, blue_score: int, red_score: int) -> Dict:
    response = requests.put(
        f"{API_BASE}/matches/{match_id}/results",
        json={"blue_score": blue_score, "red_score": red_score},
        headers=get_headers()
    )
    response.raise_for_status()
    return response.json()

def delete_match(match_id: int):
    response = requests.delete(
        f"{API_BASE}/matches/{match_id}",
        headers=get_headers()
    )
    response.raise_for_status()
    return response.json()

