"""Search pealim.com and read word pages.

No Anki imports here, so this module can be tried outside Anki.
requests and BeautifulSoup come with Anki's own Python.
"""

from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://www.pealim.com"
TIMEOUT_SECONDS = 15
# Say who is asking,
# rather than the generic "python-requests" some sites block.
HEADERS = {"User-Agent": "Pealim Cards (Anki add-on)"}


@dataclass
class SearchResult:
    url: str  # full URL of the word's page
    lemma: str  # dictionary form with nikkud, e.g. לְסַפֵּר
    part_of_speech: str  # e.g. "verb – PI'EL" or "noun – ketel pattern, masculine"
    meaning: str

    @property
    def kind(self) -> str:
        """The part of speech without its details, e.g. "noun" from "noun – ketel pattern, masculine"."""
        return self.part_of_speech.split("–", 1)[0].strip()

    @property
    def is_verb(self) -> bool:
        return self.kind.lower() == "verb"


@dataclass
class Form:
    hebrew: str  # with nikkud, e.g. קָרָאתִי
    meaning: str  # e.g. "I read"


def is_hebrew(text: str) -> bool:
    """True if the text has letters and they are all Hebrew (U+05D0 to U+05EA).

    Nikkud, spaces and punctuation aren't letters, so they are allowed.
    """
    letters = [char for char in text if char.isalpha()]
    return bool(letters) and all("א" <= char <= "ת" for char in letters)


def search(query: str) -> list[SearchResult]:
    """Run a Pealim search and return every result, any part of speech.

    Pealim matches any form of a word,
    so e.g. ספר finds the verbs "to count" and "to tell"
    as well as the nouns "book" and "barber".

    Meant for Hebrew queries.
    Latin-letter queries are treated as transliteration by Pealim,
    so English ("to read") can match an unrelated word.
    """
    soup = _get(urljoin(BASE_URL, "/search/"), {"q": query})
    results = [_parse_result(block) for block in soup.select("div.verb-search-result")]
    # Without a link there is no page to load.
    return [result for result in results if result.url]


def fetch_forms(url: str) -> dict[str, Form]:
    """Download a word page and return its forms keyed by element id,
    e.g. "PERF-1s" on a verb page or "s" (singular) on a noun page.

    Words without a table (e.g. adverbs) have no forms.
    """
    return parse_forms(_get(url))


def parse_forms(soup: BeautifulSoup) -> dict[str, Form]:
    forms = {}
    # Each form is a div with an id and a .meaning child.
    # Most sit in table cells,
    # but some don't (e.g. a preposition's base form, or a numeral's forms).
    for cell in soup.select("div[id]:has(> div.meaning)"):
        # Some cells also hold a hidden alternative form in .aux-forms
        # (e.g. the spoken-stress קָרָאתֶם next to קְרָאתֶם);
        # only the main form is wanted.
        for aux in cell.select(".aux-forms"):
            aux.extract()
        hebrew = cell.select_one(".menukad")
        if hebrew is None:
            continue
        forms[str(cell["id"])] = Form(
            hebrew=_text(hebrew),
            # No separator: the markup already has its own spaces,
            # and "read(s)" must not become "read (s)".
            meaning=_text(cell.select_one(".meaning"), separator=""),
        )
    return forms


def _get(url: str, params: dict[str, str] | None = None) -> BeautifulSoup:
    response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def _parse_result(block: Tag) -> SearchResult:
    lemma_link = block.select_one(".verb-search-lemma a")
    part_of_speech = block.select_one(".verb-search-binyan")

    # The part-of-speech line starts with a "Part of speech:" label; drop it.
    if part_of_speech is not None:
        label = part_of_speech.select_one(".verb-search-label")
        if label is not None:
            label.extract()

    return SearchResult(
        url=urljoin(BASE_URL, str(lemma_link["href"])) if lemma_link is not None else "",
        lemma=_text(block.select_one(".verb-search-lemma .menukad")),
        # The pattern is a link, so joining the text with spaces
        # leaves "ketel pattern , masculine".
        part_of_speech=_text(part_of_speech).replace(" ,", ","),
        meaning=_text(block.select_one(".verb-search-meaning")),
    )


def _text(tag: Tag | None, separator: str = " ") -> str:
    """A tag's text with whitespace collapsed; "" for a missing tag."""
    if tag is None:
        return ""
    return " ".join(tag.get_text(separator).split())
