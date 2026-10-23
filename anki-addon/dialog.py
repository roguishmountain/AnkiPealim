"""Dialog for entering a Hebrew word to look up on pealim.com."""

from aqt import AnkiQt
from aqt.deckchooser import DeckChooser
from aqt.qt import QCheckBox, QDialog, QGroupBox, QLabel, QLineEdit, QVBoxLayout, QWidget
from aqt.utils import disable_help_button, showWarning

from .pealim import is_hebrew
from .settings import Settings
from .tenses import TENSES
from .ui import ok_cancel_buttons


class AddWordDialog(QDialog):
    def __init__(self, mw: AnkiQt, settings: Settings) -> None:
        super().__init__(mw)
        self.setWindowTitle("Add Pealim word")
        disable_help_button(self)

        label = QLabel("Hebrew word, e.g. ספר:")
        self.word_input = QLineEdit()

        # Anki's own deck button, as in the Add Cards window.
        # Its popup can also create a new deck.
        # With no deck_id it starts on the current deck;
        # a deck that no longer exists falls back to Default.
        deck_row = QWidget()
        self.deck_chooser = DeckChooser(mw, deck_row, starting_deck_id=settings.deck_id)

        # The word isn't known until after the search,
        # so the tenses are always shown and only used if it turns out to be a verb.
        tenses_box = QGroupBox("Verb tenses")
        tenses_layout = QVBoxLayout(tenses_box)
        self.tense_checkboxes: dict[str, QCheckBox] = {}
        for tense in TENSES:
            checkbox = QCheckBox(tense.label)
            checkbox.setChecked(tense.prefix in settings.tenses)
            tenses_layout.addWidget(checkbox)
            self.tense_checkboxes[tense.prefix] = checkbox

        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.word_input)
        layout.addWidget(deck_row)
        layout.addWidget(tenses_box)
        layout.addWidget(ok_cancel_buttons(self))

        self.word_input.setFocus()

    def word(self) -> str:
        return self.word_input.text().strip()

    def settings(self) -> Settings:
        return Settings(
            deck_id=self.deck_chooser.selected_deck_id,
            tenses=[prefix for prefix, checkbox in self.tense_checkboxes.items() if checkbox.isChecked()],
        )

    def accept(self) -> None:
        # Keep the dialog open until the input is usable.
        # No tense check here: the word may not be a verb.
        if not is_hebrew(self.word()):
            showWarning("Type the word in Hebrew letters, e.g. לקרוא.", parent=self)
            return
        super().accept()

    def done(self, result: int) -> None:
        # Called on OK, Cancel and Esc.
        # The deck chooser registers a hook that must be removed.
        self.deck_chooser.cleanup()
        super().done(result)
