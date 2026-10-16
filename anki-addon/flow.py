"""What happens after clicking Pealim: ask, search, pick, fetch, add."""

from collections.abc import Callable

from anki.decks import DeckId
from aqt import mw
from aqt.operations import CollectionOp, QueryOp
from aqt.qt import QDialog
from aqt.utils import showWarning, tooltip

from .cards import build_card_texts
from .dialog import AddVerbDialog
from .notes import AddResult, add_cards
from .pealim import Form, SearchResult, fetch_verb_forms, search, verb_matches
from .picker import VerbPickerDialog
from .settings import Settings


def add_verb() -> None:
    # Dialog choices are saved in the add-on config (meta.json),
    # starting from the defaults in config.json.
    config = mw.addonManager.getConfig(__name__)
    assert config is not None  # only None without a config.json
    settings = Settings.from_config(config)
    settings.deck_id = _starting_deck_id(settings.deck_id)
    dialog = AddVerbDialog(mw, settings)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return

    settings = dialog.settings()
    mw.addonManager.writeConfig(__name__, settings.to_config())
    _find_verb(dialog.verb(), settings)


def _starting_deck_id(saved_deck_id: DeckId | None) -> DeckId | None:
    # On a deck's page, or while studying it, use that deck;
    # otherwise the deck used last time.
    if mw.state in ("overview", "review"):
        return mw.col.decks.get_current_id()
    return saved_deck_id


def _find_verb(query: str, settings: Settings) -> None:
    def on_found(verbs: list[SearchResult]) -> None:
        if not verbs:
            showWarning(f"No verb found on Pealim for {query}.")
            return
        if len(verbs) == 1:
            verb = verbs[0]
        else:
            picker = VerbPickerDialog(mw, query, verbs)
            if picker.exec() != QDialog.DialogCode.Accepted:
                return
            verb = picker.selected_verb()
        _fetch_and_add(verb, settings)

    _run_network_op(
        lambda: verb_matches(search(query)),
        on_found,
        progress="Searching Pealim…",
        error="Couldn't search Pealim",
    )


def _fetch_and_add(verb: SearchResult, settings: Settings) -> None:
    deck_id = settings.deck_id
    assert deck_id is not None  # the dialog's deck chooser always has a deck

    def on_fetched(forms: dict[str, Form]) -> None:
        cards = build_card_texts(verb.lemma, forms, settings.tenses)
        if not cards:
            showWarning(f"No forms found on Pealim for {verb.lemma} in the chosen tenses.")
            return
        # One undoable collection change for all the notes.
        CollectionOp(parent=mw, op=lambda col: add_cards(col, cards, deck_id)).success(
            on_added
        ).failure(on_add_error).run_in_background()

    def on_added(result: AddResult) -> None:
        deck_name = mw.col.decks.name_if_exists(deck_id) or "deck"
        message = f"Added {result.added} note(s) for {verb.lemma} to {deck_name}."
        if result.duplicates:
            message += f" Skipped {result.duplicates} already in that deck."
        tooltip(message, period=5000)

    def on_add_error(error: Exception) -> None:
        showWarning(f"Couldn't add the notes:\n{error}")

    _run_network_op(
        lambda: fetch_verb_forms(verb.url),
        on_fetched,
        progress=f"Loading {verb.lemma}…",
        error=f"Couldn't load {verb.url}",
    )


def _run_network_op[T](
    op: Callable[[], T], success: Callable[[T], None], progress: str, error: str
) -> None:
    """Run op in the background with a progress window,
    then success(result) back on the main thread.

    It doesn't touch the collection,
    so it needn't wait for other operations.
    """
    QueryOp(parent=mw, op=lambda _col: op(), success=success).failure(
        lambda exception: showWarning(f"{error}:\n{exception}")
    ).without_collection().with_progress(progress).run_in_background()
