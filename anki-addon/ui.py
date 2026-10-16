"""Small pieces shared by the add-on's dialogs."""

from aqt.qt import QDialog, QDialogButtonBox, qconnect


def ok_cancel_buttons(dialog: QDialog) -> QDialogButtonBox:
    """OK and Cancel buttons wired to the dialog's accept and reject."""
    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    qconnect(buttons.accepted, dialog.accept)
    qconnect(buttons.rejected, dialog.reject)
    return buttons
