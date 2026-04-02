from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Scoring weights — adjust these to experiment with different ranking behavior
WEIGHT_GENRE      = 3.0
WEIGHT_MOOD       = 2.0
WEIGHT_ENERGY     = 1.5
WEIGHT_ACOUSTICS  = 1.0
WEIGHT_VALENCE    = 0.5

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def score_song(song: Dict, user_prefs: Dict) -> float:
    """
    Scores a single song against a user preference profile.
    Returns a float; higher means a better match.
    """
    genre_match    = float(song["genre"] == user_prefs["favorite_genre"])
    mood_match     = float(song["mood"]  == user_prefs["favorite_mood"])
    energy_sim     = 1 - abs(song["energy"] - user_prefs["target_energy"])
    acoustic_score = (
        song["acousticness"] if user_prefs["likes_acoustic"]
        else 1 - song["acousticness"]
    )
    return (
        WEIGHT_GENRE     * genre_match
      + WEIGHT_MOOD      * mood_match
      + WEIGHT_ENERGY    * energy_sim
      + WEIGHT_ACOUSTICS * acoustic_score
      + WEIGHT_VALENCE   * song["valence"]
    )


def explain_song(song: Dict, user_prefs: Dict) -> str:
    """
    Returns a human-readable explanation of why a song scored the way it did.
    """
    parts = []

    parts.append(f"genre: {'match' if song['genre'] == user_prefs['favorite_genre'] else song['genre']}")
    parts.append(f"mood: {'match' if song['mood'] == user_prefs['favorite_mood'] else song['mood']}")

    energy_diff = abs(song["energy"] - user_prefs["target_energy"])
    energy_label = "exact" if energy_diff <= 0.05 else "close" if energy_diff <= 0.15 else "off"
    parts.append(f"energy: {energy_label} ({song['energy']:.2f})")

    acoustic_label = "high" if song["acousticness"] >= 0.5 else "low"
    parts.append(f"acoustic: {acoustic_label}")

    parts.append(f"valence: {song['valence']:.2f}")

    return " | ".join(parts)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
            
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = [(song, score_song(song, user_prefs)) for song in songs]
    ranked = sorted(scored, key=lambda pair: pair[1], reverse=True)
    return [(song, s, explain_song(song, user_prefs)) for song, s in ranked[:k]]
