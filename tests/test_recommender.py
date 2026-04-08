from src.recommender import Song, UserProfile, Recommender, score_song, _diversity_rerank

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
            year=2023,
            popularity=75,
            instrumentalness=0.05,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
            year=2021,
            popularity=45,
            instrumentalness=0.85,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        mood_weights={"happy": 1.0},
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_diversity_rerank_surfaces_minority_artist():
    """
    When one artist dominates the raw score ranking, the diversity re-ranking
    pass should promote a song from a different artist into the top-k.

    Setup: Artist A has 3 near-identical high-scoring songs; Artist B has 1
    slightly lower-scoring song.  Without diversity, top-3 would be all Artist A.
    With ARTIST_DIVERSITY_PENALTY=0.4, by round 3 Artist A's third song carries
    a cumulative -0.8 effective penalty, letting Artist B's song overtake it.
    """
    user_prefs = {
        "favorite_genre": "pop",
        "mood_weights": {"happy": 1.0},
        "target_energy": 0.80,
        "likes_acoustic": False,
        "target_valence": 0.85,
    }
    songs = [
        {"id": 1, "title": "A1", "artist": "Artist A", "genre": "pop", "mood": "happy",
         "energy": 0.80, "tempo_bpm": 120, "valence": 0.85, "danceability": 0.80,
         "acousticness": 0.20, "year": 2023, "popularity": 75, "instrumentalness": 0.05},
        {"id": 2, "title": "A2", "artist": "Artist A", "genre": "pop", "mood": "happy",
         "energy": 0.79, "tempo_bpm": 118, "valence": 0.84, "danceability": 0.80,
         "acousticness": 0.20, "year": 2023, "popularity": 74, "instrumentalness": 0.05},
        {"id": 3, "title": "A3", "artist": "Artist A", "genre": "pop", "mood": "happy",
         "energy": 0.78, "tempo_bpm": 116, "valence": 0.83, "danceability": 0.80,
         "acousticness": 0.20, "year": 2023, "popularity": 73, "instrumentalness": 0.05},
        {"id": 4, "title": "B1", "artist": "Artist B", "genre": "pop", "mood": "happy",
         "energy": 0.77, "tempo_bpm": 114, "valence": 0.82, "danceability": 0.80,
         "acousticness": 0.20, "year": 2023, "popularity": 72, "instrumentalness": 0.05},
    ]

    scored = [(s, score_song(s, user_prefs)) for s in songs]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Without diversity: top-3 are all Artist A
    assert all(s["artist"] == "Artist A" for s, _ in scored[:3])

    # With diversity re-ranking: Artist B appears in the top-3
    diverse = _diversity_rerank(scored, k=3)
    artists_in_result = [s["artist"] for s, _ in diverse]
    assert "Artist B" in artists_in_result


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        mood_weights={"happy": 1.0},
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
