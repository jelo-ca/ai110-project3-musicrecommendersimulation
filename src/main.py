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

    user_prefs = lofi_user  # swap to rock_user to compare

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
