# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

Vibefy 1.0

---

## 2. Intended Use

Vibefy recommends songs based on a user's preferred genre, mood, and energy level. It is a classroom simulation built to explore how music recommenders work, not a real app.

---

## 3. How the Model Works

Each song gets points based on how well it matches what the user likes — genre and mood are worth the most, followed by energy level, tempo, and whether the song is acoustic. The song with the highest total score is recommended first.

---

## 4. Data

**Data changes:**

- Added 55 songs to the original 5-song starter catalog
- No songs were removed

**Gaps:**

- hyperpop (1 song) and pop (2 songs) are too thin to recommend reliably
- No "sad", "romantic", or "motivational" moods
- No world music beyond latin and k-pop (e.g., Afrobeats, reggae)

60 songs across 20 genres and 8 moods.

| Genre(s)                                                                                                              | Count  |
| --------------------------------------------------------------------------------------------------------------------- | ------ |
| lofi, ambient, hip-hop                                                                                                | 4 each |
| rock, jazz, synthwave, indie pop, latin, folk, electronic, soul, metal, acoustic, classical, edm, r&b, country, k-pop | 3 each |
| pop                                                                                                                   | 2      |
| hyperpop                                                                                                              | 1      |

| Mood                             | Count  |
| -------------------------------- | ------ |
| happy, relaxed                   | 9 each |
| chill, intense, moody, energetic | 8 each |
| focused, melancholic             | 5 each |

---

## 5. Strengths

It works best when the user's preferred genre has several songs in the catalog — the top result usually feels right. Rock and lofi users in particular got results that matched exactly what you would expect.

---

## 6. Limitations and Bias

The system always gives bonus points to upbeat-sounding songs, even for users who prefer darker or sadder music. It also struggles when a user's favorite genre has very few songs in the catalog, and it never explains why a song was recommended.

---

## 7. Evaluation

### Profiles Tested

Seven user profiles were run against the 20-song catalog. Each profile was inspected by hand — looking at which songs landed in the top 5, how wide the score gaps were, and whether the result "made sense" given what the user supposedly wanted.

| Profile                         | Genre | Mood        | Energy | Acoustic |
| ------------------------------- | ----- | ----------- | ------ | -------- |
| rock_user                       | rock  | intense     | 0.90   | no       |
| lofi_user                       | lofi  | chill       | 0.38   | yes      |
| pop_user                        | pop   | happy       | 0.75   | no       |
| jazz_user                       | jazz  | relaxed     | 0.45   | yes      |
| edm_user                        | edm   | energetic   | 0.95   | no       |
| sad*fan *(edge)\_               | folk  | melancholic | 0.30   | yes      |
| walking*contradiction *(edge)\_ | metal | relaxed     | 0.95   | yes      |

### What Was Looked For

For each profile, the main question was: does the top result feel obviously correct, and does the ranking order follow logically from the weights? Secondary checks were whether songs from the wrong genre or wrong mood could still sneak into the top 5, and whether changing one preference meaningfully shifted the results.

### What the Results Showed

**rock_user and lofi_user** both worked as expected. Storm Runner was the only rock/intense song in the catalog and won by a wide margin (~7.6 vs ~4.8 for second place). Library Rain and Midnight Coding locked in the top two spots for lofi_user. These are the "clean" cases where the catalog has clear matches.

**pop_user** produced the most instructive surprise. Sunrise City (pop, happy) won cleanly, but Gym Hero (pop, intense — a high-BPM workout track) ranked second. Gym Hero shares the "pop" genre label, which is worth +3.0 points. That bonus is large enough that no amount of mood mismatch can close the gap. Songs that matched on mood but came from indie pop or hyperpop couldn't beat it. See `reflection.md` for the plain-language breakdown of why this happens.

**jazz_user** worked well for the top result — Coffee Shop Stories was the only jazz/relaxed song and won easily. The remaining four slots fell to relaxed-mood songs from soul and acoustic genres, which was reasonable fallback behavior.

**edm_user** revealed a catalog gap. There are no EDM songs in the 20-song dataset, so genre score was zero for every song. The algorithm fell back silently to mood (energetic) and energy proximity. Club After Dark and Habanera Dreams floated to the top purely on those two signals. The user got results, but they were weaker and less personalized than any profile whose genre existed in the catalog.

**sad_fan** exposed the valence bias. The profile asks for folk, melancholic, low-energy, acoustic songs — Hollow Mountains fits perfectly — but valence is always added as a bonus regardless of what the user prefers. High-valence upbeat songs receive a structural +0.31 to +0.45 advantage over dark songs, every time, for every user. Hollow Mountains still placed high on genre and acousticness, but the bias is real and measurable.

**walking_contradiction** confirmed that conflicting preferences produce silent compromise. The profile requests high energy (0.95) and likes acoustic — but high-energy songs in this catalog have acousticness near 0.05–0.10, so the two signals directly fight each other. The algorithm simply averages out the damage and returns whichever song loses least, with no warning to the user.

### Comparisons Run

- Weights were halved for genre matching (3.0 → 1.5): only 3 of 7 profiles shifted rankings at all, and most changes were minor swaps at positions 3–5. Genre weight is dominant but not the only thing holding results together.
- Energy weight was doubled (1.5 → 3.0): 4 of 7 profiles shifted slightly, mostly swapping positions 3 and 4. Energy proximity matters but is not as decisive as genre.
- These experiments confirmed that the genre+mood combination (worth up to 5.0 points) is the primary driver of results, and the remaining features act as tiebreakers.

---

## 8. Future Work

Adding a short "why this song?" note would help users understand and trust the results. Letting users rate songs and updating their profile based on feedback would also make recommendations more accurate over time.

---

## 9. Personal Reflection

Building this showed that even simple rules can produce both surprisingly good and surprisingly unfair results depending on the user. It made me realize how much work a "like" button on a real app is probably doing behind the scenes and how much data has to go to an recommendation algorithm.

I mainly used AI to structure most of the data and tests. Comparing results required me to run the program multiple times so I used Claude to run it and show me the table of the compared results.

The basic math used within the recommender did a lot for providing accurate results but there are very clear gaps especially with how the bpm points were calculated. There's a lot more math to look into to make this truly accurate since all the results is also based off of a users hard input on preference.

If I were to extend this project, I would try to explore how to automate user preference through collecting their listening history data. I think once thats solid, this could be a true music recommender algorithm used for a small music app.
