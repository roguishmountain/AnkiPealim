"""Turn a word's Pealim forms into front/back text for Anki notes.

No Anki imports here, so this module can be tried outside Anki.
"""

import re
from dataclasses import dataclass
from html import escape

from .pealim import Form, SearchResult
from .tenses import TENSES

# Forms used for nouns and adjectives, by element id, in line order.
# Nouns get singular and plural only,
# not the construct or possessive forms.
NOUN_FORMS = ("s", "p")
ADJECTIVE_FORMS = ("ms-a", "fs-a", "mp-a", "fp-a")

# Forms with a person, e.g. "P-1s" (שֶׁלִּי, "of mine") or "3ms" (הוּא, "he").
PERSON_ID = re.compile(r"^(?:P-)?([123])")


@dataclass
class CardText:
    front: str  # Hebrew with nikkud, HTML
    back: str  # English, HTML


def build_card_texts(word: SearchResult, forms: dict[str, Form], tenses: list[str]) -> list[CardText]:
    """Front/back text for each note of a word.

    Verbs get notes for the chosen tenses;
    the tenses are ignored for every other part of speech.
    """
    if word.is_verb:
        return _verb_card_texts(word.lemma, forms, tenses)
    return _other_card_texts(word, forms)


def _verb_card_texts(lemma: str, forms: dict[str, Form], tenses: list[str]) -> list[CardText]:
    """Front/back text for each note of the chosen tenses,
    active and passive.

    lemma is the infinitive as Pealim spells it in the page title (e.g. לִקְרוֹא),
    used for tenses marked use_lemma.
    Forms missing from the page are left out;
    a note with no forms at all is skipped,
    so a verb without a passive table simply gets no passive notes.
    """
    cards = []
    for tense in TENSES:
        if tense.prefix not in tenses:
            continue
        voices = [("", tense.label.lower())]
        if tense.has_passive:
            voices.append(("passive-", f"passive {tense.label.lower()}"))
        for id_prefix, label in voices:
            for group in tense.groups:
                ids = [f"{id_prefix}{tense.prefix}-{suffix}" for suffix in group]
                card = _card_text(forms, ids, label, lemma=lemma if tense.use_lemma else None)
                if card is not None:
                    cards.append(card)
    return cards


def _other_card_texts(word: SearchResult, forms: dict[str, Form]) -> list[CardText]:
    """Front/back text for a noun, adjective, preposition or any other non-verb.

    The part of speech goes last on the English side, e.g. "(noun)",
    and a noun's gender last on the Hebrew side.
    Forms missing from the page are left out.
    A word without a table (e.g. an adverb) gets one note:
    the word and its meaning.
    """
    kind = word.kind.lower()
    gender = _gender_mark(word.part_of_speech) if kind == "noun" else None
    if kind == "noun":
        groups = [list(NOUN_FORMS)]
    elif kind == "adjective":
        groups = [list(ADJECTIVE_FORMS)]
    else:
        groups = _person_groups(forms)

    cards = []
    for ids in groups:
        card = _card_text(forms, ids, kind, hebrew_note=gender, merge_same_meaning=True)
        if card is not None:
            cards.append(card)
    if cards:
        return cards

    lemma_only = {"lemma": Form(hebrew=word.lemma, meaning=word.meaning)}
    card = _card_text(lemma_only, ["lemma"], kind, hebrew_note=gender)
    assert card is not None  # the one form is always there
    return [card]


def _person_groups(forms: dict[str, Form]) -> list[list[str]]:
    """Split a table into notes: forms without a person first,
    then one note each for 1st, 2nd and 3rd person.

    E.g. שֶׁל gives [b], [P-1s, P-1p], [P-2ms, …], [P-3ms, …].
    Forms keep the page's order within each note.
    """
    plain: list[str] = []
    by_person: dict[str, list[str]] = {"1": [], "2": [], "3": []}
    for form_id in forms:
        match = PERSON_ID.match(form_id)
        if match is None:
            plain.append(form_id)
        else:
            by_person[match.group(1)].append(form_id)
    return [group for group in [plain, *by_person.values()] if group]


def _gender_mark(part_of_speech: str) -> str | None:
    """"(ז׳)" for masculine, "(נ׳)" for feminine, "(ז׳/נ׳)" for both; None if not given.

    Pealim puts it in the part of speech, e.g. "noun – ketel pattern, masculine".
    """
    marks = []
    if "masculine" in part_of_speech:
        marks.append("ז׳")
    if "feminine" in part_of_speech:
        marks.append("נ׳")
    if not marks:
        return None
    return f"({'/'.join(marks)})"


def _card_text(
    forms: dict[str, Form],
    ids: list[str],
    label: str,
    lemma: str | None = None,
    hebrew_note: str | None = None,
    merge_same_meaning: bool = False,
) -> CardText | None:
    present = [form_id for form_id in ids if form_id in forms]
    if not present:
        return None
    hebrew = [lemma or forms[form_id].hebrew for form_id in present]
    if hebrew_note is not None:
        hebrew.append(hebrew_note)
    meanings = [forms[form_id].meaning for form_id in present]
    # E.g. an adjective's four forms all mean "big, large"; show it once.
    if merge_same_meaning and len(set(meanings)) == 1:
        meanings = meanings[:1]
    # The label goes last on the English side,
    # since e.g. "I read" alone could be present or past.
    english = meanings + [f"({label})"]
    return CardText(
        front='<div dir="rtl">' + "<br>".join(escape(h) for h in hebrew) + "</div>",
        back="<br>".join(escape(e) for e in english),
    )
