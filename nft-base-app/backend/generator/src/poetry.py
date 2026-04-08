"""
poetry.py – Random poetry generator.

Supported forms:
  haiku      – three lines (5 / 7 / 5 syllables)
  couplet    – two rhyming lines
  free_verse – four to six lines of free-form verse
  limerick   – five lines with AABBA rhyme scheme

Usage
-----
    from src.poetry import PoetryGenerator, generate_poem

    # Single poem with optional seed for reproducibility
    print(generate_poem("haiku", seed=42))

    # Generator instance for multiple poems
    gen = PoetryGenerator(seed=0)
    for form in ("haiku", "limerick", "couplet", "free_verse"):
        print(gen.generate(form))
"""

from __future__ import annotations

import re
import random

# ---------------------------------------------------------------------------
# Exported constants
# ---------------------------------------------------------------------------

FORMS: tuple[str, ...] = ("haiku", "couplet", "free_verse", "limerick")

# ---------------------------------------------------------------------------
# Word banks indexed by syllable count
# ---------------------------------------------------------------------------

_NOUNS: dict[int, list[str]] = {
    1: [
        "moon", "star", "tree", "bird", "rain", "wind", "sea", "dream",
        "stone", "fire", "leaf", "light", "cloud", "wave", "snow", "brook",
        "sky", "mist", "dew", "dawn", "dusk", "frost", "fog", "tide", "bloom",
    ],
    2: [
        "river", "mountain", "garden", "flower", "forest", "summer", "winter",
        "heaven", "silence", "morning", "evening", "shadow", "petal", "meadow",
        "ocean", "thunder", "valley", "willow", "sunset", "lantern", "ember",
        "autumn", "twilight", "rainfall", "snowfall", "sunlight",
    ],
    3: [
        "butterfly", "waterfall", "horizon", "universe", "afternoon",
        "melody", "harmony", "memory", "solitude", "eternity",
    ],
}

_ADJECTIVES: dict[int, list[str]] = {
    1: [
        "cold", "bright", "dark", "soft", "deep", "still", "old", "pale",
        "vast", "pure", "lost", "lone", "fierce", "calm", "clear", "swift",
        "bold", "high", "blue", "gold", "grey",
    ],
    2: [
        "gentle", "ancient", "lonely", "silver", "golden", "endless",
        "fallen", "hidden", "frozen", "broken", "quiet", "hollow",
        "crimson", "tender", "azure", "fleeting", "fading", "drifting",
        "empty", "secret",
    ],
    3: [
        "wandering", "beautiful", "glimmering", "shimmering", "radiant",
        "delicate", "whispering",
    ],
}

_VERBS: dict[int, list[str]] = {
    1: [
        "falls", "blooms", "drifts", "glows", "sleeps", "waits", "fades",
        "flows", "sings", "soars", "hides", "melts", "calls", "stirs",
        "burns", "bends", "gleams", "breaks",
    ],
    2: [
        "whispers", "wanders", "gathers", "lingers", "shimmers", "dissolves",
        "unfolds", "reveals", "glistens", "ripples", "descends", "reflects",
        "scatters",
    ],
    3: [
        "remembers", "disappears", "surrenders", "awakening", "scattering",
    ],
}

_BANKS: dict[str, dict[int, list[str]]] = {
    "adj": _ADJECTIVES,
    "noun": _NOUNS,
    "verb": _VERBS,
}

# ---------------------------------------------------------------------------
# Rhyme groups – used for couplets
# ---------------------------------------------------------------------------

_RHYME_GROUPS: list[list[str]] = [
    ["light", "night", "bright", "sight", "flight", "might"],
    ["sea", "free", "tree", "glee", "spree"],
    ["dream", "stream", "gleam", "beam", "seem"],
    ["stone", "alone", "known", "tone", "throne"],
    ["rain", "plain", "vain", "grain", "lane"],
    ["moon", "soon", "tune", "bloom", "gloom"],
    ["snow", "flow", "glow", "below", "grow"],
    ["sky", "fly", "high", "sigh", "cry"],
    ["spring", "sing", "ring", "wing", "sting"],
    ["deep", "sleep", "keep", "weep", "sweep"],
    ["old", "cold", "bold", "gold", "fold"],
    ["still", "fill", "hill", "will", "thrill"],
    ["day", "way", "say", "play", "stay"],
    ["fire", "higher", "desire", "inspire"],
]

# ---------------------------------------------------------------------------
# Haiku line templates
#
# Each template is a list of (pos, syllables) pairs whose syllable counts
# sum to the target (5 or 7).  pos is one of "adj", "noun", "verb".
# ---------------------------------------------------------------------------

_LineTemplate = list[tuple[str, int]]

_HAIKU_TEMPLATES: dict[int, list[_LineTemplate]] = {
    5: [
        [("adj", 1), ("noun", 2), ("verb", 2)],              # 1+2+2 = 5
        [("adj", 2), ("noun", 3)],                            # 2+3   = 5
        [("noun", 2), ("verb", 3)],                           # 2+3   = 5
        [("adj", 2), ("verb", 1), ("noun", 2)],               # 2+1+2 = 5
        [("adj", 1), ("noun", 1), ("adj", 1), ("noun", 2)],   # 1+1+1+2 = 5
    ],
    7: [
        [("adj", 2), ("noun", 2), ("verb", 3)],               # 2+2+3 = 7
        [("adj", 1), ("noun", 2), ("verb", 1), ("noun", 3)],  # 1+2+1+3 = 7
        [("adj", 2), ("noun", 2), ("verb", 1), ("noun", 2)],  # 2+2+1+2 = 7
        [("adj", 3), ("noun", 1), ("verb", 3)],               # 3+1+3   = 7
        [("adj", 1), ("noun", 3), ("verb", 3)],               # 1+3+3   = 7
    ],
}

# ---------------------------------------------------------------------------
# Couplet frames
#
# Each frame is a (line1, line2) pair.  Slots:
#   {adj}   – 1-syllable adjective
#   {noun}  – 1-syllable noun
#   {noun2} – 2-syllable noun
#   {verb2} – 2-syllable verb
#   {rhyme_1}, {rhyme_2} – two words from the same rhyme group (injected at
#                           run-time); always the last token in each line.
# ---------------------------------------------------------------------------

_COUPLET_FRAMES: list[tuple[str, str]] = [
    (
        "The {adj} {noun} rests in the {rhyme_1},",
        "As all the world fades into {rhyme_2}.",
    ),
    (
        "A {noun} once {verb2} toward the {rhyme_1},",
        "And found itself lost in the {rhyme_2}.",
    ),
    (
        "The {adj} sky fills with the {rhyme_1},",
        "While silence {verb2} with the {rhyme_2}.",
    ),
    (
        "Where {adj} {noun2}s end and the world grows {rhyme_1},",
        "A new journey begins in the {rhyme_2}.",
    ),
    (
        "The {noun} carries a memory of {rhyme_1},",
        "And drifts like a leaf toward the {rhyme_2}.",
    ),
    (
        "Beneath the pale {noun2} there is only {rhyme_1},",
        "And nothing endures but the {rhyme_2}.",
    ),
]

# ---------------------------------------------------------------------------
# Limerick skeletons
#
# Pre-written five-line frames with fixed end-rhymes (AABBA).
# Slots follow the same naming convention as couplet frames.
# ---------------------------------------------------------------------------

_LIMERICK_SKELETONS: list[list[str]] = [
    [
        "There was a {adj} {noun} in a dream,",
        "Who {verb2} by the side of the stream,",
        "  It {verb} through rain,",
        "  Through glory and pain,",
        "Till the {noun2} forgot what things seem.",
    ],
    [
        "A {adj} {noun} lived by the sea,",
        "Who longed to forever be free,",
        "  It {verb} up high,",
        "  Beneath the grey sky,",
        "And {verb2} into the old tree.",
    ],
    [
        "The {adj} {noun} glowed in the night,",
        "And filled all the world with its light,",
        "  It {verb} through rain,",
        "  Across the dark plain,",
        "And vanished with morning so bright.",
    ],
    [
        "A {adj} {noun} grew ancient and old,",
        "Its heart made of silence and cold,",
        "  The {noun2} fell deep,",
        "  In fathomless sleep,",
        "And {verb2} a story untold.",
    ],
    [
        "The {adj} {noun} faded with the day,",
        "And wandered a far distant way,",
        "  The night lasted long,",
        "  Without any song,",
        "Till the {noun2} had nothing to say.",
    ],
    [
        "A {adj} {noun} arrived with the spring,",
        "And taught all the {noun2}s how to sing,",
        "  The world grew so still,",
        "  On top of the hill,",
        "As the {noun3} began to ring.",
    ],
    [
        "The {adj} {noun} {verb} in the snow,",
        "With rivers that constantly flow,",
        "  The {noun2} lit a spark,",
        "  Against the deep dark,",
        "And the {noun3} began to glow.",
    ],
    [
        "A {adj} {noun} sang under the moon,",
        "And promised the world it would soon,",
        "  Grow quiet and still,",
        "  On that faraway hill,",
        "And bloom like an old-fashioned tune.",
    ],
]

# ---------------------------------------------------------------------------
# Free-verse line pool
# ---------------------------------------------------------------------------

_FREE_VERSE_LINES: list[str] = [
    "The {adj} {noun} {verb} in silence.",
    "Beneath the {adj} sky, a {noun} {verb}.",
    "A {noun} {verb} through the {adj} {noun2}.",
    "In the shadow of the {adj} {noun}, something {verb}.",
    "The {noun} carries the weight of {noun2}.",
    "Time {verb} like a {adj} {noun}.",
    "Where {noun}s end, the {adj} {noun2} begins.",
    "The {adj} {noun} remembers nothing.",
    "Light {verb} across the {noun2}.",
    "A {noun} dreams of {adj} {noun2}s.",
    "The {noun2} has forgotten the name of the {noun}.",
    "Once, the {adj} {noun} held everything.",
    "Nothing {verb}s longer than a {adj} {noun}.",
    "Even the {adj} {noun} must {verb} away.",
    "The {noun} is also a kind of {noun2}.",
]


# ---------------------------------------------------------------------------
# PoetryGenerator
# ---------------------------------------------------------------------------


def _capitalize_first(s: str) -> str:
    """Uppercase only the very first character, leaving the rest untouched."""
    return s[:1].upper() + s[1:] if s else s


class PoetryGenerator:
    """Generate random poems in several forms.

    Parameters
    ----------
    seed:
        Optional integer seed for the internal random-number generator.
        Identical seeds produce identical output, which is useful for
        testing and for minting reproducible NFT poems.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _word(self, pos: str, syllables: int) -> str:
        """Return a random word for *pos* with the given *syllables*."""
        return self._rng.choice(_BANKS[pos][syllables])

    def _fill_frame(
        self,
        frame: str,
        *,
        rhyme_words: dict[str, str] | None = None,
    ) -> str:
        """Replace ``{slot}`` placeholders in *frame* with random words.

        Slot syntax:
        * ``{noun}``  → 1-syllable noun
        * ``{noun2}`` → 2-syllable noun
        * ``{noun3}`` → 3-syllable noun  (same pattern for adj / verb)
        * ``{rhyme_1}``, ``{rhyme_2}`` → supplied via *rhyme_words*
        """

        def _replace(m: re.Match) -> str:  # type: ignore[type-arg]
            slot = m.group(1)
            if rhyme_words and slot in rhyme_words:
                return rhyme_words[slot]
            match = re.match(r"^(adj|noun|verb)(\d?)$", slot)
            if match:
                pos = match.group(1)
                syl = int(match.group(2)) if match.group(2) else 1
                return self._word(pos, syl)
            return m.group(0)  # leave unrecognised slots untouched

        return re.sub(r"\{(\w+)\}", _replace, frame)

    def _fill_haiku_line(self, syllable_target: int) -> str:
        template = self._rng.choice(_HAIKU_TEMPLATES[syllable_target])
        parts = [self._word(pos, syl) for pos, syl in template]
        return " ".join(parts)

    # ------------------------------------------------------------------
    # Public poem generators
    # ------------------------------------------------------------------

    def haiku(self) -> str:
        """Return a haiku with 5 / 7 / 5 syllable lines."""
        lines = [self._fill_haiku_line(n) for n in (5, 7, 5)]
        return "\n".join(_capitalize_first(ln) for ln in lines)

    def couplet(self) -> str:
        """Return a two-line rhyming couplet."""
        rhyme_group = self._rng.choice(_RHYME_GROUPS)
        rhyme_1, rhyme_2 = self._rng.sample(rhyme_group, 2)
        frame1, frame2 = self._rng.choice(_COUPLET_FRAMES)
        rw = {"rhyme_1": rhyme_1, "rhyme_2": rhyme_2}
        line1 = _capitalize_first(self._fill_frame(frame1, rhyme_words=rw))
        line2 = _capitalize_first(self._fill_frame(frame2, rhyme_words=rw))
        return f"{line1}\n{line2}"

    def free_verse(self) -> str:
        """Return a free-verse poem with four to six lines."""
        n_lines = self._rng.randint(4, 6)
        templates = self._rng.sample(_FREE_VERSE_LINES, n_lines)
        lines = [_capitalize_first(self._fill_frame(t)) for t in templates]
        return "\n".join(lines)

    def limerick(self) -> str:
        """Return a limerick with AABBA rhyme scheme."""
        skeleton = self._rng.choice(_LIMERICK_SKELETONS)
        lines = [_capitalize_first(self._fill_frame(ln)) for ln in skeleton]
        return "\n".join(lines)

    def generate(self, form: str = "haiku") -> str:
        """Generate a poem of the requested *form*.

        Parameters
        ----------
        form:
            One of ``"haiku"``, ``"couplet"``, ``"free_verse"``,
            ``"limerick"``, or ``"random"`` (picks a form at random).

        Raises
        ------
        ValueError
            If *form* is not a recognised form name.
        """
        if form == "random":
            form = self._rng.choice(FORMS)
        dispatch = {
            "haiku": self.haiku,
            "couplet": self.couplet,
            "free_verse": self.free_verse,
            "limerick": self.limerick,
        }
        if form not in dispatch:
            raise ValueError(
                f"Unknown form {form!r}. Choose from: {', '.join(FORMS)}"
            )
        return dispatch[form]()


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------


def generate_poem(form: str = "random", seed: int | None = None) -> str:
    """Generate and return a single poem.

    Parameters
    ----------
    form:
        Poem form – ``"haiku"``, ``"couplet"``, ``"free_verse"``,
        ``"limerick"``, or ``"random"``.
    seed:
        Optional integer seed for reproducible output.
    """
    return PoetryGenerator(seed=seed).generate(form)
