"""Search pealim.com and read verb pages.

No Anki imports here, so this module can be tried outside Anki.
requests and BeautifulSoup come with Anki's own Python.
"""

from dataclasses import dataclass, field
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://www.pealim.com"
TIMEOUT_SECONDS = 15
# Say who is asking,
# rather than the generic "python-requests" some sites block.
HEADERS = {"User-Agent": "Pealim Verb Cards (Anki add-on)"}


@dataclass
class SearchResult:
    url: str  # full URL of the word's page
    lemma: str  # dictionary form with nikkud, e.g. לְסַפֵּר
    part_of_speech: str  # e.g. "verb – PI'EL" or "noun – ketel pattern, masculine"
    meaning: str
    # Anchors of the forms that matched the query, e.g. "INF-L" or "PERF-3ms".
    matched_forms: list[str] = field(default_factory=list)

    @property
    def is_verb(self) -> bool:
        return self.part_of_speech.lower().startswith("verb")

    @property
    def binyan(self) -> str:
        """E.g. "PI'EL" from "verb – PI'EL"."""
        return self.part_of_speech.split("–", 1)[-1].strip()

    @property
    def matched_infinitive(self) -> bool:
        return "INF-L" in self.matched_forms


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
    """Run a Pealim search and return every result, verbs or not.

    Meant for Hebrew queries.
    Latin-letter queries are treated as transliteration by Pealim,
    so English ("to read") can match an unrelated verb.
    """
    soup = _get(urljoin(BASE_URL, "/search/"), {"q": query})
    results = [_parse_result(block) for block in soup.select("div.verb-search-result")]
    # Without a link there is no page to load.
    return [result for result in results if result.url]


def verb_matches(results: list[SearchResult]) -> list[SearchResult]:
    """Keep only verbs, preferring those whose infinitive matched the query.

    E.g. לספר matches the nouns "book" and "barber" too;
    those are dropped,
    leaving "to tell" and "to count".
    """
    verbs = [result for result in results if result.is_verb]
    infinitives = [result for result in verbs if result.matched_infinitive]
    return infinitives or verbs


def fetch_verb_forms(url: str) -> dict[str, Form]:
    """Download a verb page and return its forms keyed by element id, e.g. "PERF-1s"."""
    return parse_verb_forms(_get(url))


def parse_verb_forms(soup: BeautifulSoup) -> dict[str, Form]:
    forms = {}
    for cell in soup.select("td.conj-td > div[id]"):
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

    # The binyan line starts with a "Part of speech:" label; drop it.
    if part_of_speech is not None:
        label = part_of_speech.select_one(".verb-search-label")
        if label is not None:
            label.extract()

    # Each matched form links to its cell on the word's page, e.g. "/dict/1409-lesaper/#h-INF-L".
    matched_forms = [
        str(link["href"]).split("#h-", 1)[1]
        for link in block.select(".vf-search-result a[href*='#h-']")
    ]

    return SearchResult(
        url=urljoin(BASE_URL, str(lemma_link["href"])) if lemma_link is not None else "",
        lemma=_text(block.select_one(".verb-search-lemma .menukad")),
        part_of_speech=_text(part_of_speech),
        meaning=_text(block.select_one(".verb-search-meaning")),
        matched_forms=matched_forms,
    )


def _text(tag: Tag | None, separator: str = " ") -> str:
    """A tag's text with whitespace collapsed; "" for a missing tag."""
    if tag is None:
        return ""
    return " ".join(tag.get_text(separator).split())
