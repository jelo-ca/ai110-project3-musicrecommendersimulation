"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from colorama import init, Fore, Style
from tabulate import tabulate
from recommender import load_songs, recommend_songs
from config import DEV

init(autoreset=True)


def print_dev_info(user_prefs: dict) -> None:
    print("[DEV] Sample User Profile:")
    print(f"  Genre    : {user_prefs['favorite_genre']}")
    print(f"  Moods    : {user_prefs['mood_weights']}")
    print(f"  Energy   : {user_prefs['target_energy']:.2f}")
    print(f"  Acoustic : {'yes' if user_prefs['likes_acoustic'] else 'no'}")
    print(f"  Valence  : {user_prefs.get('target_valence', 0.5):.2f}")
    if user_prefs.get("liked_artists"):
        print(f"  Artists  : {user_prefs['liked_artists']}")
    if user_prefs.get("listen_history"):
        print(f"  History  : {user_prefs['listen_history']}")
    if user_prefs.get("discovery_mode"):
        print(f"  Mode     : discovery")
    if user_prefs.get("prefers_instrumental"):
        print(f"  Instrum  : yes")
    if user_prefs.get("prefers_mainstream"):
        print(f"  Mainstream: yes")
    if "preferred_decade" in user_prefs:
        print(f"  Era      : {user_prefs['preferred_decade']}s")
    print("\n[DEV] Expected Outputs:")
    mood_str = "/".join(user_prefs["mood_weights"].keys())
    print(f"  - Songs tagged '{user_prefs['favorite_genre']}' or similar genres should rank highest")
    print(f"  - '{mood_str}' mood songs should score well")
    print(f"  - Energy close to {user_prefs['target_energy']:.2f} preferred")
    print(f"  - {'High' if user_prefs['likes_acoustic'] else 'Low'} acousticness favored")
    print(f"  - Valence close to {user_prefs.get('target_valence', 0.5):.2f} preferred")
    print("-" * 50)


def main() -> None:
    songs = load_songs("data/songs.csv")

    print("=" * 50)
    print("Music Recommender Simulation")
    print("=" * 50)
    print(f"Catalog : {len(songs)} songs loaded")
    print("-" * 50)

    rock_user = {
        "favorite_genre": "rock",
        "mood_weights": {"intense": 1.0},
        "target_energy": 0.90,
        "likes_acoustic": False,
        "target_valence": 0.50,
    }

    lofi_user = {
        "favorite_genre": "lofi",
        "mood_weights": {"chill": 1.0},
        "target_energy": 0.38,
        "likes_acoustic": True,
        "target_valence": 0.60,
        "prefers_instrumental": True,    # lofi is typically background/wordless
    }

    pop_user = {
        "favorite_genre": "pop",
        "mood_weights": {"happy": 1.0},
        "target_energy": 0.75,
        "likes_acoustic": False,
        "target_valence": 0.80,
        "prefers_mainstream": True,      # wants chart-toppers
        "preferred_decade": 2023,        # only cares about the latest releases
    }

    jazz_user = {
        "favorite_genre": "jazz",
        "mood_weights": {"relaxed": 1.0},
        "target_energy": 0.45,
        "likes_acoustic": True,
        "target_valence": 0.65,
        "prefers_instrumental": True,    # classic jazz is often wordless
        "preferred_decade": 2019,        # prefers older releases over new drops
    }

    edm_user = {
        "favorite_genre": "edm",
        "mood_weights": {"energetic": 1.0},
        "target_energy": 0.95,
        "likes_acoustic": False,
        "target_valence": 0.75,
    }

    sad_fan = {
        "favorite_genre": "folk",
        "mood_weights": {"melancholic": 1.0},
        "target_energy": 0.30,
        "likes_acoustic": True,
        "target_valence": 0.25,  # prefers dark/sad songs — valence now aligned, not unconditional
    }

    walking_contradiction = {
        "favorite_genre": "metal",   # not in catalog; closest is rock (similarity 0.6)
        "mood_weights": {"relaxed": 1.0},  # opposite of what metal songs carry
        "target_energy": 0.95,       # high energy...
        "likes_acoustic": True,      # ...but high-energy songs have acousticness ~0.05-0.10
        "target_valence": 0.50,
        # Edge case: every preference fights another — algorithm picks whichever song loses least
    }

    # Demonstrates multi-mood tolerance (feature 5)
    mixed_mood_user = {
        "favorite_genre": "pop",
        "mood_weights": {"happy": 0.6, "energetic": 0.4},
        "target_energy": 0.80,
        "likes_acoustic": False,
        "target_valence": 0.80,
    }

    # Demonstrates anti-repetition decay (feature 7) and artist familiarity (feature 8)
    repeat_listener = {
        "favorite_genre": "lofi",
        "mood_weights": {"chill": 1.0},
        "target_energy": 0.40,
        "likes_acoustic": True,
        "target_valence": 0.60,
        "listen_history": [2, 4, 9],              # recently heard these lofi tracks
        "liked_artists": ["LoRoom", "Paper Lanterns"],
        "prefers_instrumental": True,             # focus/work session — no lyrics
    }

    # Demonstrates discovery mode (feature 8)
    discovery_user = {
        "favorite_genre": "jazz",
        "mood_weights": {"relaxed": 0.7, "chill": 0.3},
        "target_energy": 0.45,
        "likes_acoustic": True,
        "target_valence": 0.65,
        "liked_artists": ["Slow Stereo"],
        "discovery_mode": True,                   # penalizes known artists to surface new ones
        "prefers_mainstream": False,              # also favors niche over mainstream
    }

    all_users = {
        "rock_user":            rock_user,
        "lofi_user":            lofi_user,
        "pop_user":             pop_user,
        "jazz_user":            jazz_user,
        "edm_user":             edm_user,
        "sad_fan":              sad_fan,
        "walking_contradiction": walking_contradiction,
        "mixed_mood_user":      mixed_mood_user,
        "repeat_listener":      repeat_listener,
        "discovery_user":       discovery_user,
    }

    for name, user_prefs in all_users.items():
        print(f"\n{Style.BRIGHT}{'=' * 50}{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}User: {name}{Style.RESET_ALL}")
        print("=" * 50)

        if DEV:
            print_dev_info(user_prefs)

        recommendations = recommend_songs(user_prefs, songs, k=5)

        print(f"\n{Style.BRIGHT}Top Recommendations:{Style.RESET_ALL}")
        print("-" * 50)
        for i, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"{Fore.CYAN}{i}. {song['title']}{Style.RESET_ALL} by {song['artist']}")
            print(f"   {Fore.YELLOW}Score  :{Style.RESET_ALL} {score:.2f}")
            print(f"   {Fore.GREEN}Reason :{Style.RESET_ALL} {explanation}")
            print("-" * 50)


if __name__ == "__main__":
    main()
