"""Add the card texts to the collection as Anki notes."""

import unicodedata
from dataclasses import dataclass

from anki.collection import AddNoteRequest, Collection, OpChanges
from anki.decks import DeckId
from anki.models import NotetypeId

from .cards import CardText

# Built-in note type: each note makes a Hebrew → English and an English → Hebrew card.
# Non-English Anki installs name it differently.
NOTE_TYPE = "Basic (and reversed card)"
TAG = "pealim"


class NoteTypeMissing(Exception):
    pass


@dataclass
class AddResult:
    changes: OpChanges  # lets Anki refresh its screens after the operation
    added: int
    duplicates: int


def add_cards(col: Collection, cards: list[CardText], deck_id: DeckId) -> AddResult:
    """Add one note per card text,
    skipping notes whose Hebrew side is already in the target deck.

    The same verb can still be added to a different deck.
    All notes go in as a single undo step.
    """
    notetype = col.models.by_name(NOTE_TYPE)
    if notetype is None:
        raise NoteTypeMissing(f'Note type "{NOTE_TYPE}" not found in this collection.')

    existing = _fronts_in_deck(col, notetype["id"], deck_id)

    requests = []
    duplicates = 0
    for card in cards:
        if _normalize(card.front) in existing:
            duplicates += 1
            continue
        # Fields by position (Front, Back),
        # so it still works if the field names are translated.
        note = col.new_note(notetype)
        note.fields[0] = card.front
        note.fields[1] = card.back
        note.tags = [TAG]
        requests.append(AddNoteRequest(note=note, deck_id=deck_id))

    changes = col.add_notes(requests) if requests else OpChanges()
    return AddResult(changes=changes, added=len(requests), duplicates=duplicates)


def _fronts_in_deck(col: Collection, notetype_id: NotetypeId, deck_id: DeckId) -> set[str]:
    """First fields of this note type's notes that have a card in the deck.

    Only that exact deck counts, not its subdecks.
    """
    assert col.db is not None  # only None once the collection is closed
    rows = col.db.list(
        "select flds from notes where mid = ? and id in (select nid from cards where did = ?)",
        notetype_id,
        deck_id,
    )
    # Fields are stored joined by the 0x1f separator; the first one is the Hebrew side.
    return {_normalize(fields.split("\x1f", 1)[0]) for fields in rows}


def _normalize(text: str) -> str:
    # Anki stores text in Unicode NFC form,
    # which can reorder nikkud marks;
    # compare both sides in the same form.
    return unicodedata.normalize("NFC", text)
