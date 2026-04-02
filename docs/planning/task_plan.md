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
| 1 | Decide scoring formula and feature weights | complete |
| 2 | Implement `load_songs` (CSV → List[Dict]) | complete |
| 3 | Implement `score_song` + `explain_song` helpers | complete |
| 4 | Implement functional `recommend_songs` (for main.py) | complete |
| 5 | Implement `Recommender.recommend` (OOP class) | pending |
| 6 | Implement `Recommender.explain_recommendation` (OOP class) | pending |
| 7 | Run tests and verify results | pending |

---

## Scoring Formula (finalized)

```
score = 3.0 * (song.genre == user.favorite_genre)
      + 2.0 * (song.mood  == user.favorite_mood)
      + 1.5 * (1 - abs(song.energy - user.target_energy))
      + 1.0 * (song.acousticness if user.likes_acoustic else 1 - song.acousticness)
      + 0.5 * song.valence
```

Weights defined as module-level constants in `src/recommender.py` (lines 4–9).

---

## Key Files

| File | Role |
|------|------|
| `src/recommender.py` | Main implementation |
| `src/main.py` | CLI runner — uses `load_songs` + `recommend_songs` |
| `src/config.py` | DEV flag for debug output |
| `tests/test_recommender.py` | Tests `Recommender` OOP class |
| `data/songs.csv` | 20-song catalog |
| `docs/scoring_logic.mmd` | Mermaid diagram of scoring flow |

---

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| `ModuleNotFoundError: recommender` when running `python -m src.main` | 1 | Run as `python src/main.py` from project root instead |
| `UnicodeEncodeError` with `rounded_outline` tabulate format | 1 | Switched to colorama; removed tabulate |
| `FileNotFoundError: data/songs.csv` when running from `src/` | 1 | Must run from project root: `python src/main.py` |
