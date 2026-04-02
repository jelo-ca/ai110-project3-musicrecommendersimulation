"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 
    
    print("=" * 50 + "")
    print("Welcome to the Music Recommender Simulation!")
    print("=" * 50 + "")

    print(f"Loaded Songs: {len(songs)}")
    print("-" * 50 + "")
    
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

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
