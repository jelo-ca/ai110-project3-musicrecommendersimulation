from typing import List, Dict, Tuple
from dataclasses import dataclass, field

# Scoring weights — adjust these to experiment with different ranking behavior
WEIGHT_GENRE        = 3.0
WEIGHT_MOOD         = 2.0
WEIGHT_ENERGY       = 1.5
WEIGHT_ACOUSTICS    = 1.0
WEIGHT_VALENCE      = 0.5
WEIGHT_ARTIST        = 0.5
WEIGHT_REPEAT_DECAY  = 0.5
WEIGHT_INSTRUMENTAL  = 0.75
WEIGHT_POPULARITY    = 0.5
WEIGHT_ERA           = 0.5

# Genre similarity graph — partial credit for adjacent genres
# Keys are (user_genre, song_genre) tuples; values are similarity scores 0–1
GENRE_SIMILARITY: Dict[Tuple[str, str], float] = {
    ("pop",        "indie pop"):   0.7,  ("indie pop",  "pop"):        0.7,
    ("pop",        "hyperpop"):    0.5,  ("hyperpop",   "pop"):        0.5,
    ("pop",        "electronic"):  0.4,  ("electronic", "pop"):        0.4,
    ("pop",        "latin"):       0.4,  ("latin",      "pop"):        0.4,
    ("lofi",       "jazz"):        0.4,  ("jazz",       "lofi"):       0.4,
    ("lofi",       "ambient"):     0.5,  ("ambient",    "lofi"):       0.5,
    ("jazz",       "soul"):        0.6,  ("soul",       "jazz"):       0.6,
    ("jazz",       "classical"):   0.3,  ("classical",  "jazz"):       0.3,
    ("rock",       "metal"):       0.6,  ("metal",      "rock"):       0.6,
    ("electronic", "ambient"):     0.4,  ("ambient",    "electronic"): 0.4,
    ("electronic", "synthwave"):   0.6,  ("synthwave",  "electronic"): 0.6,
    ("folk",       "acoustic"):    0.7,  ("acoustic",   "folk"):       0.7,
    ("folk",       "classical"):   0.3,  ("classical",  "folk"):       0.3,
    ("hip-hop",    "soul"):        0.4,  ("soul",       "hip-hop"):    0.4,
}


def _genre_sim(song_genre: str, user_genre: str) -> float:
    """Returns similarity between two genres (1.0 = exact match, 0.0 = unrelated)."""
    if song_genre == user_genre:
        return 1.0
    return GENRE_SIMILARITY.get((user_genre.lower(), song_genre.lower()), 0.0)


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
    year: int
    popularity: int
    instrumentalness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    mood_weights: Dict[str, float]      # e.g. {"happy": 0.7, "energetic": 0.3}
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.5         # preferred emotional tone (0=dark, 1=bright)
    listen_history: List[int] = field(default_factory=list)   # song IDs heard (oldest→newest)
    liked_artists: List[str] = field(default_factory=list)    # artists the user follows
    discovery_mode: bool = False        # if True, penalizes known artists to surface new ones
    prefers_instrumental: bool = False  # if True, rewards high instrumentalness
    prefers_mainstream: bool = False    # if True, rewards high popularity scores
    preferred_decade: int = 2020        # release era preference (e.g. 1990, 2000, 2020)


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k Song objects ranked by compatibility with the given user profile."""
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable string explaining why a song was recommended to the user."""
        # TODO: Implement explanation logic
        return "Explanation placeholder"


def score_song(song: Dict, user_prefs: Dict) -> float:
    """
    Scores a single song against a user preference profile.
    Returns a float; higher means a better match.
    """
    # 1. Genre: similarity graph (partial credit for adjacent genres)
    genre_sim = _genre_sim(song["genre"], user_prefs["favorite_genre"])

    # 2. Mood: weighted multi-mood (normalized so weights don't need to sum to 1)
    mood_weights = user_prefs["mood_weights"]
    total_weight = sum(mood_weights.values()) or 1.0
    mood_score = mood_weights.get(song["mood"], 0.0) / total_weight

    # 3. Energy: linear distance
    energy_sim = 1 - abs(song["energy"] - user_prefs["target_energy"])

    # 4. Acousticness: preference-aware
    acoustic_score = (
        song["acousticness"] if user_prefs["likes_acoustic"]
        else 1 - song["acousticness"]
    )

    # 5. Valence: user-aligned (fixes unconditional upbeat bias)
    target_valence = user_prefs.get("target_valence", 0.5)
    valence_score = 1 - abs(song["valence"] - target_valence)

    # 6. Artist familiarity bonus / discovery penalty
    liked = [a.lower() for a in user_prefs.get("liked_artists", [])]
    is_known = song["artist"].lower() in liked
    if user_prefs.get("discovery_mode", False):
        artist_bonus = -0.3 if is_known else 0.3
    else:
        artist_bonus = 1.0 if is_known else 0.0

    # 8. Instrumentalness preference
    instrumental_score = (
        song["instrumentalness"] if user_prefs.get("prefers_instrumental", False)
        else 1 - song["instrumentalness"]
    )

    # 9. Song popularity tier
    pop_norm = song["popularity"] / 100
    popularity_score = (
        pop_norm if user_prefs.get("prefers_mainstream", False)
        else 1 - pop_norm
    )

    # 10. Release era affinity
    preferred_decade = user_prefs.get("preferred_decade", 2020)
    era_score = max(0.0, 1 - abs(song["year"] - preferred_decade) / 10)

    score = (
        WEIGHT_GENRE        * genre_sim
      + WEIGHT_MOOD         * mood_score
      + WEIGHT_ENERGY       * energy_sim
      + WEIGHT_ACOUSTICS    * acoustic_score
      + WEIGHT_VALENCE      * valence_score
      + WEIGHT_ARTIST       * artist_bonus
      + WEIGHT_INSTRUMENTAL * instrumental_score
      + WEIGHT_POPULARITY   * popularity_score
      + WEIGHT_ERA          * era_score
    )

    # 7. Anti-repetition decay (subtracted after weighted sum)
    history = user_prefs.get("listen_history", [])
    if song["id"] in history:
        # Most recent = recency_rank 1 → largest penalty
        reversed_history = list(reversed(history))
        recency_rank = reversed_history.index(song["id"]) + 1
        score -= WEIGHT_REPEAT_DECAY / recency_rank

    return score


def explain_song(song: Dict, user_prefs: Dict) -> str:
    """
    Returns a human-readable explanation of why a song scored the way it did.
    """
    parts = []

    # Genre similarity
    sim = _genre_sim(song["genre"], user_prefs["favorite_genre"])
    if sim == 1.0:
        parts.append("genre: match")
    elif sim > 0:
        parts.append(f"genre: similar ({sim:.0%})")
    else:
        parts.append(f"genre: {song['genre']}")

    # Mood with weights
    mood_weights = user_prefs["mood_weights"]
    total_weight = sum(mood_weights.values()) or 1.0
    mood_score = mood_weights.get(song["mood"], 0.0) / total_weight
    if mood_score >= 1.0:
        parts.append("mood: match")
    elif mood_score > 0:
        parts.append(f"mood: partial ({mood_score:.0%})")
    else:
        parts.append(f"mood: {song['mood']}")

    # Energy
    energy_diff = abs(song["energy"] - user_prefs["target_energy"])
    energy_label = "exact" if energy_diff <= 0.05 else "close" if energy_diff <= 0.15 else "off"
    parts.append(f"energy: {energy_label} ({song['energy']:.2f})")

    # Acousticness
    acoustic_label = "high" if song["acousticness"] >= 0.5 else "low"
    parts.append(f"acoustic: {acoustic_label}")

    # Valence alignment
    target_valence = user_prefs.get("target_valence", 0.5)
    valence_diff = abs(song["valence"] - target_valence)
    valence_label = "match" if valence_diff <= 0.10 else "close" if valence_diff <= 0.25 else "off"
    parts.append(f"valence: {valence_label} ({song['valence']:.2f})")

    # Artist familiarity
    liked = [a.lower() for a in user_prefs.get("liked_artists", [])]
    is_known = song["artist"].lower() in liked
    discovery = user_prefs.get("discovery_mode", False)
    if is_known:
        parts.append("artist: known (penalized)" if discovery else "artist: known (+bonus)")
    elif discovery:
        parts.append("artist: new (+discovery)")

    # Instrumentalness
    inst = song["instrumentalness"]
    inst_label = "instrumental" if inst >= 0.5 else "vocal"
    parts.append(f"{inst_label}: {inst:.2f}")

    # Popularity tier
    pop = song["popularity"]
    pop_label = "mainstream" if pop >= 60 else "niche"
    parts.append(f"pop: {pop_label} ({pop})")

    # Release era
    preferred_decade = user_prefs.get("preferred_decade", 2020)
    era_diff = abs(song["year"] - preferred_decade)
    era_label = "match" if era_diff <= 1 else "close" if era_diff <= 4 else "off"
    parts.append(f"era: {era_label} ({song['year']})")

    # Repeat penalty
    history = user_prefs.get("listen_history", [])
    if song["id"] in history:
        reversed_history = list(reversed(history))
        recency_rank = reversed_history.index(song["id"]) + 1
        parts.append(f"repeat: -{WEIGHT_REPEAT_DECAY / recency_rank:.2f}")

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
                "year": int(row["year"]),
                "popularity": int(row["popularity"]),
                "instrumentalness": float(row["instrumentalness"]),
            })

    return songs


def score_song_vibe_match(song: Dict, user_prefs: Dict) -> float:
    """
    Vibe Match strategy: ranks by emotional and sonic feel.
    Mood, energy, valence, and acoustics dominate; genre is a light tiebreaker.
    Artist familiarity and popularity are ignored.
    """
    mood_weights = user_prefs["mood_weights"]
    total_weight = sum(mood_weights.values()) or 1.0
    mood_score = mood_weights.get(song["mood"], 0.0) / total_weight

    energy_sim = 1 - abs(song["energy"] - user_prefs["target_energy"])

    target_valence = user_prefs.get("target_valence", 0.5)
    valence_score = 1 - abs(song["valence"] - target_valence)

    acoustic_score = (
        song["acousticness"] if user_prefs["likes_acoustic"]
        else 1 - song["acousticness"]
    )

    instrumental_score = (
        song["instrumentalness"] if user_prefs.get("prefers_instrumental", False)
        else 1 - song["instrumentalness"]
    )

    genre_sim = _genre_sim(song["genre"], user_prefs["favorite_genre"])

    score = (
        5.0 * mood_score
      + 4.0 * energy_sim
      + 2.0 * valence_score
      + 2.0 * acoustic_score
      + 0.5 * instrumental_score
      + 0.5 * genre_sim
    )

    history = user_prefs.get("listen_history", [])
    if song["id"] in history:
        reversed_history = list(reversed(history))
        recency_rank = reversed_history.index(song["id"]) + 1
        score -= WEIGHT_REPEAT_DECAY / recency_rank

    return score


def score_song_trend_chaser(song: Dict, user_prefs: Dict) -> float:
    """
    Trend Chaser strategy: surfaces what's popular and recently released.
    Popularity and recency dominate; mood and energy are secondary signals.
    """
    pop_norm = song["popularity"] / 100
    # Recency anchored to 2024 — decay over 8-year window
    recency_score = max(0.0, 1 - abs(song["year"] - 2024) / 8)

    mood_weights = user_prefs["mood_weights"]
    total_weight = sum(mood_weights.values()) or 1.0
    mood_score = mood_weights.get(song["mood"], 0.0) / total_weight

    energy_sim = 1 - abs(song["energy"] - user_prefs["target_energy"])
    genre_sim = _genre_sim(song["genre"], user_prefs["favorite_genre"])

    score = (
        5.0 * pop_norm
      + 3.0 * recency_score
      + 1.5 * mood_score
      + 1.0 * energy_sim
      + 0.75 * genre_sim
    )

    history = user_prefs.get("listen_history", [])
    if song["id"] in history:
        reversed_history = list(reversed(history))
        recency_rank = reversed_history.index(song["id"]) + 1
        score -= WEIGHT_REPEAT_DECAY / recency_rank

    return score


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, strategy: str = "balanced") -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    strategy: "balanced" | "vibe_match" | "trend_chaser"
    """
    _score_fns = {
        "balanced":     score_song,
        "vibe_match":   score_song_vibe_match,
        "trend_chaser": score_song_trend_chaser,
    }
    score_fn = _score_fns.get(strategy, score_song)

    scored = [(song, score_fn(song, user_prefs)) for song in songs]
    ranked = sorted(scored, key=lambda pair: pair[1], reverse=True)
    return [(song, s, explain_song(song, user_prefs)) for song, s in ranked[:k]]
