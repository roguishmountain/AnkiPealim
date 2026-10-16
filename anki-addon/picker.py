"""Dialog for choosing between several verbs that match a search."""

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


class VerbPickerDialog(QDialog):
    def __init__(self, parent: QWidget, query: str, verbs: list[SearchResult]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Choose a verb")
        disable_help_button(self)
        self.verbs = verbs

        label = QLabel(f"Several verbs match {query}:")
        # The query is user text; never read it as HTML.
        label.setTextFormat(Qt.TextFormat.PlainText)

        # Separate columns keep Hebrew and English apart,
        # so right-to-left and left-to-right text don't get mixed on one line.
        self.verb_list = QTreeWidget()
        self.verb_list.setHeaderLabels(["Verb", "Binyan", "Meaning"])
        self.verb_list.setRootIsDecorated(False)
        for verb in verbs:
            self.verb_list.addTopLevelItem(QTreeWidgetItem([verb.lemma, verb.binyan, verb.meaning]))
        header = self.verb_list.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.verb_list.setCurrentItem(self.verb_list.topLevelItem(0))
        # Double-clicking a row is the same as selecting it and clicking OK.
        qconnect(self.verb_list.itemDoubleClicked, lambda *_: self.accept())

        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.verb_list)
        layout.addWidget(ok_cancel_buttons(self))

        self.resize(600, 250)
        self.verb_list.setFocus()

    def selected_verb(self) -> SearchResult:
        return self.verbs[self.verb_list.indexOfTopLevelItem(self.verb_list.currentItem())]
