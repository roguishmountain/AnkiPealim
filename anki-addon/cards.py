"""Turn a verb's Pealim forms into front/back text for Anki notes.

No Anki imports here, so this module can be tried outside Anki.
"""

from dataclasses import dataclass
from html import escape

from .pealim import Form
from .tenses import TENSES


@dataclass
class CardText:
    front: str  # Hebrew with nikkud, HTML
    back: str  # English, HTML


def build_card_texts(lemma: str, forms: dict[str, Form], tenses: list[str]) -> list[CardText]:
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
                card = _card_text(forms, ids, label, lemma if tense.use_lemma else None)
                if card is not None:
                    cards.append(card)
    return cards


def _card_text(
    forms: dict[str, Form], ids: list[str], label: str, lemma: str | None
) -> CardText | None:
    present = [form_id for form_id in ids if form_id in forms]
    if not present:
        return None
    hebrew = [lemma or forms[form_id].hebrew for form_id in present]
    # The tense goes last on the English side,
    # since e.g. "I read" alone could be present or past.
    english = [forms[form_id].meaning for form_id in present] + [f"({label})"]
    return CardText(
        front='<div dir="rtl">' + "<br>".join(escape(h) for h in hebrew) + "</div>",
        back="<br>".join(escape(e) for e in english),
    )
