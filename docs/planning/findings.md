# Findings — Music Recommender Simulation

## Project Structure
- `src/recommender.py` — Song, UserProfile dataclasses + Recommender class + functional helpers
- `src/main.py` — CLI runner, imports functional `load_songs` / `recommend_songs`
- `tests/test_recommender.py` — Tests OOP `Recommender` class (imported from `src.recommender`)
- `data/songs.csv` — 10 songs, columns: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness

## CSV Catalog (data/songs.csv)
10 songs across genres: pop, lofi, rock, ambient, jazz, synthwave, indie pop
Moods: happy, chill, intense, relaxed, moody, focused

| Feature | Type | Range |
|---------|------|-------|
| genre | categorical | pop, lofi, rock, ambient, jazz, synthwave, indie pop |
| mood | categorical | happy, chill, intense, relaxed, moody, focused |
| energy | float | 0.28 – 0.93 |
| tempo_bpm | float | 60 – 152 |
| valence | float | 0.48 – 0.84 |
| danceability | float | 0.41 – 0.88 |
| acousticness | float | 0.05 – 0.92 |

## UserProfile Fields
- `favorite_genre: str`
- `favorite_mood: str`
- `target_energy: float`
- `likes_acoustic: bool`

## Test Expectations (test_recommender.py)
1. `test_recommend_returns_songs_sorted_by_score` — expects pop/happy song to rank first when user prefers pop/happy/energy=0.8/not acoustic
2. `test_explain_recommendation_returns_non_empty_string` — expects non-empty string from `explain_recommendation`

## Import Notes
- `main.py` imports from `recommender` (not `src.recommender`) — needs to be run as `python -m src.main`
- `test_recommender.py` imports from `src.recommender` — correct for pytest from project root

## Scoring Decision
**Chosen approach: weighted additive scoring**
- Genre match: weight 3.0 (binary: 1 if match, 0 otherwise)
- Mood match: weight 2.0 (binary)
- Energy similarity: weight 1.5 (1 - abs(song.energy - user.target_energy))
- Acoustic match: weight 1.0 (1.0 if likes_acoustic and acousticness > 0.5, else 1 - acousticness if likes_acoustic, else acousticness inverted)

This ensures genre/mood dominates, energy is secondary, acousticness is a tiebreaker.
