"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from colorama import init, Fore, Style
from recommender import load_songs, recommend_songs
from config import DEV

init(autoreset=True)


def print_dev_info(user_prefs: dict) -> None:
    print("[DEV] Sample User Profile:")
    print(f"  Genre    : {user_prefs['favorite_genre']}")
    print(f"  Mood     : {user_prefs['favorite_mood']}")
    print(f"  Energy   : {user_prefs['target_energy']:.2f}")
    print(f"  Acoustic : {'yes' if user_prefs['likes_acoustic'] else 'no'}")
    print("\n[DEV] Expected Outputs:")
    print(f"  - Songs tagged '{user_prefs['favorite_genre']}' should rank highest")
    print(f"  - '{user_prefs['favorite_mood']}' mood songs should score well")
    print(f"  - Energy close to {user_prefs['target_energy']:.2f} preferred")
    print(f"  - {'High' if user_prefs['likes_acoustic'] else 'Low'} acousticness favored")
    print("-" * 50)


def main() -> None:
    songs = load_songs("data/songs.csv") 
    
    print("=" * 50)
    print("Music Recommender Simulation")
    print("=" * 50)
    print(f"Catalog : {len(songs)} songs loaded")
    print("-" * 50)
    
    # Two contrasting profiles to test differentiation
    rock_user = {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.90,
        "likes_acoustic": False,
    }

    lofi_user = {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.38,
        "likes_acoustic": True,
    }

    pop_user = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.75,
        "likes_acoustic": False,
    }

    jazz_user = {
        "favorite_genre": "jazz",
        "favorite_mood": "relaxed",
        "target_energy": 0.45,
        "likes_acoustic": True,
    }

    edm_user = {
        "favorite_genre": "edm",
        "favorite_mood": "energetic",
        "target_energy": 0.95,
        "likes_acoustic": False,
    }

    sad_fan = {
        "favorite_genre": "folk",
        "favorite_mood": "melancholic",
        "target_energy": 0.30,
        "likes_acoustic": True,
        # Edge case: valence is unconditionally additive — no target_valence in the
        # scoring formula, so upbeat songs always score higher than dark ones all else equal.
    }

    walking_contradiction = {
        "favorite_genre": "metal",   # not in catalog; closest is rock
        "favorite_mood": "relaxed",  # opposite of what metal songs carry
        "target_energy": 0.95,       # high energy...
        "likes_acoustic": True,      # ...but high-energy songs have acousticness ~0.05-0.10
        # Edge case: every preference fights another — the algorithm silently picks
        # whichever song loses least across all contradictions.
    }

    all_users = {
        "rock_user": rock_user,
        "lofi_user": lofi_user,
        "pop_user": pop_user,
        "jazz_user": jazz_user,
        "edm_user": edm_user,
        "sad_fan": sad_fan,
        "walking_contradiction": walking_contradiction,
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
