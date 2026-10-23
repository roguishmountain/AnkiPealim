"""Dialog for choosing between several words that match a search."""

from aqt.qt import (
    QDialog,
    QHeaderView,
    QLabel,
    Qt,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    qconnect,
)
from aqt.utils import disable_help_button

from .pealim import SearchResult
from .ui import ok_cancel_buttons


class WordPickerDialog(QDialog):
    def __init__(self, parent: QWidget, query: str, words: list[SearchResult]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Choose a word")
        disable_help_button(self)
        self.words = words

        label = QLabel(f"Several words match {query}:")
        # The query is user text; never read it as HTML.
        label.setTextFormat(Qt.TextFormat.PlainText)

        # Separate columns keep Hebrew and English apart,
        # so right-to-left and left-to-right text don't get mixed on one line.
        self.word_list = QTreeWidget()
        self.word_list.setHeaderLabels(["Word", "Part of speech", "Meaning"])
        self.word_list.setRootIsDecorated(False)
        for word in words:
            self.word_list.addTopLevelItem(
                QTreeWidgetItem([word.lemma, word.part_of_speech, word.meaning])
            )
        header = self.word_list.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.word_list.setCurrentItem(self.word_list.topLevelItem(0))
        # Double-clicking a row is the same as selecting it and clicking OK.
        qconnect(self.word_list.itemDoubleClicked, lambda *_: self.accept())

        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.word_list)
        layout.addWidget(ok_cancel_buttons(self))

        self.resize(700, 250)
        self.word_list.setFocus()

    def selected_word(self) -> SearchResult:
        return self.words[self.word_list.indexOfTopLevelItem(self.word_list.currentItem())]
