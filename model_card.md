# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

### Profiles Tested

Seven user profiles were run against the 20-song catalog. Each profile was inspected by hand — looking at which songs landed in the top 5, how wide the score gaps were, and whether the result "made sense" given what the user supposedly wanted.

| Profile | Genre | Mood | Energy | Acoustic |
|---|---|---|---|---|
| rock_user | rock | intense | 0.90 | no |
| lofi_user | lofi | chill | 0.38 | yes |
| pop_user | pop | happy | 0.75 | no |
| jazz_user | jazz | relaxed | 0.45 | yes |
| edm_user | edm | energetic | 0.95 | no |
| sad_fan *(edge)* | folk | melancholic | 0.30 | yes |
| walking_contradiction *(edge)* | metal | relaxed | 0.95 | yes |

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

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
