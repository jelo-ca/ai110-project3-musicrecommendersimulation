# Task Plan — Music Recommender Scoring Implementation

## Goal
Implement a scoring and ranking rule using the strongest CSV features for a simple content-based music recommender.

## Scope
- `src/recommender.py`: implement `load_songs`, `Recommender.recommend`, `Recommender.explain_recommendation`, and `recommend_songs`
- No UI changes, no new files beyond what already exists
- Tests in `tests/test_recommender.py` must pass when done

---

## Phases

| # | Phase | Status |
|---|-------|--------|
| 1 | Decide scoring formula and feature weights | pending |
| 2 | Implement `load_songs` (CSV → List[Dict]) | pending |
| 3 | Implement `Recommender.recommend` (scoring + ranking) | pending |
| 4 | Implement `Recommender.explain_recommendation` | pending |
| 5 | Implement functional `recommend_songs` (for main.py) | pending |
| 6 | Run tests and verify results | pending |

---

## Scoring Formula (TBD — Phase 1 decision)

Features available in CSV:
- `genre` (categorical) — compare to `user.favorite_genre`
- `mood` (categorical) — compare to `user.favorite_mood`
- `energy` (float 0–1) — compare to `user.target_energy`
- `acousticness` (float 0–1) — compare to `user.likes_acoustic`
- `valence`, `danceability`, `tempo_bpm` — secondary features

Proposed weighted scoring approach:
```
score = w_genre * genre_match
      + w_mood  * mood_match
      + w_energy * (1 - |song.energy - user.target_energy|)
      + w_acoustic * acoustic_match
```
Weights to be finalized in Phase 1.

---

## Key Files

| File | Role |
|------|------|
| `src/recommender.py` | Main implementation |
| `src/main.py` | Uses `load_songs` + `recommend_songs` |
| `tests/test_recommender.py` | Tests `Recommender` OOP class |
| `data/songs.csv` | 10-song catalog |

---

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| — | — | — |
