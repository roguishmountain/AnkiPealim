"""The tenses of a Pealim verb table and how they split into notes.

No Anki imports here, so this module can be tried outside Anki.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tense:
    prefix: str  # element id prefix on the verb page, e.g. "PERF" for "PERF-1s"
    label: str  # checkbox label; lowercased on cards, e.g. "(past)"
    # One note per group; each group lists the id suffixes of its forms, in line order.
    groups: tuple[tuple[str, ...], ...]
    # Some verbs (e.g. hif'il) also have a passive table,
    # with the same ids prefixed "passive-".
    has_passive: bool
    # Show the infinitive as spelled in the page title (לִקְרוֹא)
    # instead of the table's shorter spelling (לִקְרֹא).
    use_lemma: bool = False


TENSES = [
    Tense("INF", "Infinitive", (("L",),), has_passive=False, use_lemma=True),
    Tense("AP", "Present", (("ms", "fs", "mp", "fp"),), has_passive=True),
    Tense(
        "PERF",
        "Past",
        (("1s", "1p"), ("2ms", "2fs", "2mp", "2fp"), ("3ms", "3fs", "3p")),
        has_passive=True,
    ),
    Tense(
        "IMPF",
        "Future",
        (("1s", "1p"), ("2ms", "2fs", "2mp", "2fp"), ("3ms", "3fs", "3mp", "3fp")),
        has_passive=True,
    ),
    Tense("IMP", "Imperative", (("2ms", "2fs", "2mp", "2fp"),), has_passive=False),
]
