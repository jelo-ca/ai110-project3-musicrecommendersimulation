# Reflection: Comparing User Profile Outputs

This file compares pairs of user profiles side by side — what changed between them, why the algorithm behaved differently, and what that reveals about how the recommender actually works.

---

## 1. rock_user vs. lofi_user

**rock_user** wants: rock, intense, high energy (0.90), no acoustic  
**lofi_user** wants: lofi, chill, low energy (0.38), acoustic  

These two profiles are almost perfect opposites, and the results look like it. Storm Runner (high-tempo, electric guitar rock) dominates for rock_user. Library Rain and Midnight Coding (quiet, hazy, bedroom-producer tracks) lock in the top two for lofi_user. There is almost zero overlap in their top 5 lists.

Why does that make sense? The genre and mood weights are the heaviest in the formula. Storm Runner is the only song that is both "rock" AND "intense" — it gets the maximum possible bonus from both, and nothing else is close. The same is true on the other side: Library Rain and Midnight Coding are the only lofi/chill songs. When the catalog has an exact match, the algorithm rewards it clearly and decisively.

**What this tests for:** Whether the recommender can differentiate between high-energy electric and low-energy acoustic listeners. It can — cleanly — when exact catalog matches exist.

---

## 2. pop_user vs. edm_user

**pop_user** wants: pop, happy, mid-high energy (0.75), no acoustic  
**edm_user** wants: edm, energetic, very high energy (0.95), no acoustic  

Pop_user gets a strong, personalized top result: Sunrise City matches both genre and mood exactly. EDM_user gets nothing like that. There are no EDM songs in the catalog at all, so the genre bonus is zero for every single song. The algorithm falls back entirely on mood (energetic) and energy closeness. Club After Dark and Habanera Dreams end up on top — they are a hip-hop track and a latin track respectively — not because they resemble EDM, but because they happen to have the right energy and mood label.

This is a significant gap. EDM_user's top 5 is actually weaker and less relevant than pop_user's top 5, not because of anything the user did wrong, but because their genre happened to be missing from the dataset. The system does not tell the user this. It just quietly returns whatever fits best from what is available.

**What this tests for:** Whether the recommender degrades gracefully when a user's preferred genre is not in the catalog. It does not degrade gracefully — it fails silently.

---

## 3. jazz_user vs. edm_user

**jazz_user** wants: jazz, relaxed, moderate energy (0.45), acoustic  
**edm_user** wants: edm, energetic, very high energy (0.95), no acoustic  

Both profiles have something in common: only one genre match exists for jazz (Coffee Shop Stories), and zero exist for EDM. But jazz_user still gets a clearly correct top result because Coffee Shop Stories hits both genre AND mood perfectly. EDM_user gets nothing that scores on genre at all.

After the top result, jazz_user's list fills with relaxed-mood songs from soul and acoustic genres — Sunday Stroll, Blue Velvet Hours. These are soft, slow tracks, which makes intuitive sense as fallback picks for someone who likes jazz. EDM_user's fallback list is Club After Dark and Habanera Dreams — energetic and high-tempo, yes, but nothing like electronic dance music. The fallback works better for jazz_user because "relaxed" mood translates well across genres (soul, acoustic, and jazz all share that quality). "Energetic" does not translate as cleanly from EDM to hip-hop or latin.

**What this tests for:** Whether mood-based fallback is good enough when a genre is missing. It is acceptable for jazz but unconvincing for EDM.

---

## 4. sad_fan vs. pop_user — The "Gym Hero Problem" Explained

**sad_fan** wants: folk, melancholic, low energy (0.30), acoustic  
**pop_user** wants: pop, happy, mid energy (0.75), no acoustic  

Here is the plain-language version of what is going wrong.

Imagine you walk into a music store and tell the clerk: "I want something slow and sad — like a rainy day folk song." The clerk looks at their rating sheet. Hollow Mountains is there — folk, melancholic, acoustic. Perfect match. But the sheet also has a row that says "emotional depth" and every upbeat pop song scores higher on that row automatically, no matter what you asked for. So even though Hollow Mountains is the right answer, the clerk's scoring system quietly adds bonus points to cheerful songs in the background, every single time.

That is exactly what valence does in this recommender. Valence measures how "happy" or "positive" a song sounds. The formula always adds `0.5 × valence` to the score — it is treated as a bonus, not a preference. A song like Pixel Parade (hyperpop, very upbeat, valence = 0.90) gets +0.45 from valence. Hollow Mountains (the exact match sad_fan wants) gets only +0.14. That is a 0.31 point gap that favors the cheerful song on every comparison, forever, for every user — even sad_fan.

Now apply the same idea to pop_user and Gym Hero. Gym Hero is tagged "pop" — so it gets +3.0 genre points. But Gym Hero is an intense workout anthem (mood = "intense"), not the happy pop that pop_user wants. Songs that do match "happy" mood — like Rooftop Lights from indie pop, or Pixel Parade from hyperpop — cannot overcome that 3-point genre head start. Genre weight is so large that mood becomes a tiebreaker instead of an equal partner. So Gym Hero keeps showing up in the "Happy Pop" list because the algorithm sees the "pop" label and awards it full credit, without considering whether the song's emotional character actually fits.

Both of these bugs are the same kind of problem: one feature is given too much automatic weight, and it silences other signals that the user actually cares about.

**What this tests for:** Whether the scoring formula respects the emotional intent behind a user's preferences, not just the category labels. It does not — valence and genre lock-in both work against users with non-mainstream or emotionally specific tastes.

---

## 5. sad_fan vs. walking_contradiction

**sad_fan** wants: folk, melancholic, low energy (0.30), acoustic — preferences are internally consistent  
**walking_contradiction** wants: metal, relaxed, high energy (0.95), acoustic — preferences conflict with each other

Sad_fan's results are imperfect (valence bias exists) but the top result, Hollow Mountains, is genuinely the right answer. The preferences are coherent — low energy, acoustic, melancholic, folk — and the algorithm finds the matching song.

Walking_contradiction's results are almost impossible to predict without running the numbers. The profile asks for high energy (0.95) and likes acoustic, but in this catalog, high-energy songs are all electric and have acousticness near 0.05. Every song that scores well on energy scores poorly on acousticness, and vice versa. On top of that, "metal" is not in the catalog (closest is rock), and "relaxed" mood is the opposite of what metal songs carry. Every single preference the user stated pulls the score in a different direction.

The algorithm resolves this silently. It does not say "your preferences conflict." It just runs the math and returns Iron & Rust, which happens to split the difference least poorly across all four mismatches. The user might look at the results and wonder why they got a metal-adjacent intense song when they said they wanted something relaxed — the answer is that no song could satisfy all of their stated preferences at once, and the algorithm picked the song that lost the fewest total points.

**What this tests for:** How the recommender handles internally inconsistent user preferences. The result is that the algorithm never breaks — it always returns something — but it also never tells the user that their request was contradictory. A better system would flag the conflict and ask for clarification.
