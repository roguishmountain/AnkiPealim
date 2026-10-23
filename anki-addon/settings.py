"""The add-word dialog's choices, as saved in the add-on config."""

from dataclasses import asdict, dataclass
from typing import Any

from anki.decks import DeckId


@dataclass
class Settings:
    deck_id: DeckId | None  # None: start on Anki's current deck
    tenses: list[str]  # Tense prefixes, e.g. ["INF", "AP", "PERF"]

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "Settings":
        return cls(deck_id=config["deck_id"], tenses=config["tenses"])

    def to_config(self) -> dict[str, Any]:
        return asdict(self)
