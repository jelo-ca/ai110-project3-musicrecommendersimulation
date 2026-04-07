"""
Interactive CLI runner for the Music Recommender Simulation.
Use arrow keys to select a user profile and ranking strategy, then press Enter.
"""

import re
import sys
import questionary

sys.stdout.reconfigure(encoding='utf-8')
from questionary import Choice
from questionary import Style as QStyle
from colorama import init, Fore, Style
from tabulate import tabulate
from recommender import load_songs, recommend_songs
from config import DEV

init(autoreset=True)

# ── Color palette ─────────────────────────────────────────────────────────────

CYAN    = Fore.CYAN    + Style.BRIGHT
YELLOW  = Fore.YELLOW  + Style.BRIGHT
MAGENTA = Fore.MAGENTA + Style.BRIGHT
GREEN   = Fore.GREEN   + Style.BRIGHT
WHITE   = Style.BRIGHT
DIM     = Style.DIM
RESET   = Style.RESET_ALL

# Arrow-key prompt styling
QSTYLE = QStyle([
    ("qmark",       "fg:cyan bold"),
    ("question",    "fg:white bold"),
    ("answer",      "fg:yellow bold"),
    ("pointer",     "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("selected",    "fg:yellow"),
    ("instruction", "fg:gray"),
])

# ── Box-drawing helpers ───────────────────────────────────────────────────────

_ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')
_W = 52  # visible inner width between border chars

def _vlen(s: str) -> int:
    return len(_ANSI_RE.sub('', s))

def _pad(s: str) -> str:
    return s + ' ' * max(0, _W - _vlen(s))

def _double_top() -> str:
    return CYAN + '╔' + '═' * _W + '╗' + RESET

def _double_mid() -> str:
    return CYAN + '╠' + '═' * _W + '╣' + RESET

def _double_bot() -> str:
    return CYAN + '╚' + '═' * _W + '╝' + RESET

def _drow(content: str) -> str:
    return CYAN + '║' + RESET + _pad(content) + CYAN + '║' + RESET

def _single_top() -> str:
    return CYAN + '┌' + '─' * _W + '┐' + RESET

def _single_bot() -> str:
    return CYAN + '└' + '─' * _W + '┘' + RESET

def _srow(content: str) -> str:
    return CYAN + '│' + RESET + _pad(content) + CYAN + '│' + RESET

# ── Ranking strategy definitions ────────────────────────────────────────────

STRATEGY_CHOICES = [
    Choice(
        title="Balanced      — Weighs genre, mood, energy, and all factors equally",
        value="balanced",
    ),
    Choice(
        title="Vibe Match    — Prioritizes mood and audio feel over genre labels",
        value="vibe_match",
    ),
    Choice(
        title="Trend Chaser  — Surfaces popular and recently-released songs",
        value="trend_chaser",
    ),
]

STRATEGY_LABELS = {
    "balanced":     "Balanced",
    "vibe_match":   "Vibe Match",
    "trend_chaser": "Trend Chaser",
}

# ── User profiles ────────────────────────────────────────────────────────────

ALL_USERS = {
    "rock_user": {
        "favorite_genre": "rock",
        "mood_weights": {"intense": 1.0},
        "target_energy": 0.90,
        "likes_acoustic": False,
        "target_valence": 0.50,
    },
    "lofi_user": {
        "favorite_genre": "lofi",
        "mood_weights": {"chill": 1.0},
        "target_energy": 0.38,
        "likes_acoustic": True,
        "target_valence": 0.60,
        "prefers_instrumental": True,
    },
    "pop_user": {
        "favorite_genre": "pop",
        "mood_weights": {"happy": 1.0},
        "target_energy": 0.75,
        "likes_acoustic": False,
        "target_valence": 0.80,
        "prefers_mainstream": True,
        "preferred_decade": 2023,
    },
    "jazz_user": {
        "favorite_genre": "jazz",
        "mood_weights": {"relaxed": 1.0},
        "target_energy": 0.45,
        "likes_acoustic": True,
        "target_valence": 0.65,
        "prefers_instrumental": True,
        "preferred_decade": 2019,
    },
    "edm_user": {
        "favorite_genre": "edm",
        "mood_weights": {"energetic": 1.0},
        "target_energy": 0.95,
        "likes_acoustic": False,
        "target_valence": 0.75,
    },
    "sad_fan": {
        "favorite_genre": "folk",
        "mood_weights": {"melancholic": 1.0},
        "target_energy": 0.30,
        "likes_acoustic": True,
        "target_valence": 0.25,
    },
    "walking_contradiction": {
        "favorite_genre": "metal",
        "mood_weights": {"relaxed": 1.0},
        "target_energy": 0.95,
        "likes_acoustic": True,
        "target_valence": 0.50,
    },
    "mixed_mood_user": {
        "favorite_genre": "pop",
        "mood_weights": {"happy": 0.6, "energetic": 0.4},
        "target_energy": 0.80,
        "likes_acoustic": False,
        "target_valence": 0.80,
    },
    "repeat_listener": {
        "favorite_genre": "lofi",
        "mood_weights": {"chill": 1.0},
        "target_energy": 0.40,
        "likes_acoustic": True,
        "target_valence": 0.60,
        "listen_history": [2, 4, 9],
        "liked_artists": ["LoRoom", "Paper Lanterns"],
        "prefers_instrumental": True,
    },
    "discovery_user": {
        "favorite_genre": "jazz",
        "mood_weights": {"relaxed": 0.7, "chill": 0.3},
        "target_energy": 0.45,
        "likes_acoustic": True,
        "target_valence": 0.65,
        "liked_artists": ["Slow Stereo"],
        "discovery_mode": True,
        "prefers_mainstream": False,
    },
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_user_choices() -> list:
    choices = []
    for name, prefs in ALL_USERS.items():
        genre  = prefs["favorite_genre"]
        mood   = "/".join(prefs["mood_weights"].keys())
        energy = prefs["target_energy"]
        label  = f"{name:<24}  {genre:<12} | {mood:<17} | energy {energy:.2f}"
        choices.append(Choice(title=label, value=name))
    choices.append(Choice(title="Exit", value="__exit__"))
    return choices


def _print_dev_info(user_prefs: dict) -> None:
    print("[DEV] Sample User Profile:")
    print(f"  Genre    : {user_prefs['favorite_genre']}")
    print(f"  Moods    : {user_prefs['mood_weights']}")
    print(f"  Energy   : {user_prefs['target_energy']:.2f}")
    print(f"  Acoustic : {'yes' if user_prefs['likes_acoustic'] else 'no'}")
    print(f"  Valence  : {user_prefs.get('target_valence', 0.5):.2f}")
    if user_prefs.get("liked_artists"):
        print(f"  Artists  : {user_prefs['liked_artists']}")
    if user_prefs.get("listen_history"):
        print(f"  History  : {user_prefs['listen_history']}")
    if user_prefs.get("discovery_mode"):
        print(f"  Mode     : discovery")
    if user_prefs.get("prefers_instrumental"):
        print(f"  Instrum  : yes")
    if user_prefs.get("prefers_mainstream"):
        print(f"  Mainstream: yes")
    if "preferred_decade" in user_prefs:
        print(f"  Era      : {user_prefs['preferred_decade']}s")
    print("\n[DEV] Expected Outputs:")
    mood_str = "/".join(user_prefs["mood_weights"].keys())
    print(f"  - Songs tagged '{user_prefs['favorite_genre']}' or similar genres should rank highest")
    print(f"  - '{mood_str}' mood songs should score well")
    print(f"  - Energy close to {user_prefs['target_energy']:.2f} preferred")
    print(f"  - {'High' if user_prefs['likes_acoustic'] else 'Low'} acousticness favored")
    print(f"  - Valence close to {user_prefs.get('target_valence', 0.5):.2f} preferred")
    print("-" * 50)


def _show_recommendations(name: str, user_prefs: dict, songs: list, strategy: str) -> None:
    label  = STRATEGY_LABELS[strategy]
    genre  = user_prefs["favorite_genre"]
    mood   = "/".join(user_prefs["mood_weights"].keys())
    energy = user_prefs["target_energy"]

    left  = f"  {YELLOW}▶ {name}{RESET}"
    right = f"[{MAGENTA}{label}{RESET}]  "
    gap   = ' ' * max(1, _W - _vlen(left) - _vlen(right))
    meta  = f"    {DIM}{genre}  ·  {mood}  ·  energy {energy:.2f}{RESET}"

    print()
    print(_single_top())
    print(_srow(left + gap + right))
    print(_srow(meta))
    print(_single_bot())

    if DEV:
        _print_dev_info(user_prefs)

    recommendations = recommend_songs(user_prefs, songs, k=5, strategy=strategy)

    print(f"\n  {GREEN}♪ Top Recommendations{RESET}  {CYAN}{'─' * 28}{RESET}")
    rows = []
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = explanation.replace(" | ", "\n")
        rows.append([i, song["title"], song["artist"], f"{score:.2f}", reasons])

    headers = ["#", "Title", "Artist", "Score", "Reasons"]
    print(tabulate(rows, headers=headers, tablefmt="grid", maxcolwidths=[3, 22, 18, 6, 42]))


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    songs = load_songs("data/songs.csv")

    title = f"  {YELLOW}♫  Music Recommender Simulation{RESET}"
    stats = f"  {DIM}{len(songs)} songs  ·  3 strategies  ·  {len(ALL_USERS)} profiles{RESET}"
    hint  = f"  {DIM}Use {RESET}{WHITE}↑ ↓{RESET}{DIM} to navigate,{RESET} {WHITE}Enter{RESET}{DIM} to select{RESET}"
    print()
    print(_double_top())
    print(_drow(title))
    print(_double_mid())
    print(_drow(stats))
    print(_drow(hint))
    print(_double_bot())
    print()

    user_choices = _make_user_choices()

    while True:
        # ── Step 1: pick a user profile ──────────────────────────────────────
        user_name = questionary.select(
            "Select a user profile:",
            choices=user_choices,
            style=QSTYLE,
        ).ask()

        if user_name is None or user_name == "__exit__":
            print(f"\n{CYAN}Goodbye!{RESET}\n")
            break

        # ── Step 2: pick a ranking strategy ──────────────────────────────────
        strategy = questionary.select(
            "Select a ranking strategy:",
            choices=STRATEGY_CHOICES,
            style=QSTYLE,
        ).ask()

        if strategy is None:
            continue

        # ── Step 3: display results ───────────────────────────────────────────
        _show_recommendations(user_name, ALL_USERS[user_name], songs, strategy)

        # ── Step 4: continue? ─────────────────────────────────────────────────
        again = questionary.confirm(
            "\nTry another profile or strategy?",
            default=True,
            style=QSTYLE,
        ).ask()

        if not again:
            print(f"\n{CYAN}Goodbye!{RESET}\n")
            break


if __name__ == "__main__":
    main()
