"""Readable full prose and native Qt navigation after an explicit topic change."""
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat
from PySide6.QtWidgets import QTextBrowser
from .ui_state import replace_text


class MechanismTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reference_details = None

    def setPlainText(self, text):
        if self.reference_details is not None:
            self.reference_details.setText(self.reference_details.property('referenceBaseText'))
        super().setPlainText(text)
        block = self.document().firstBlock()
        while block.isValid():
            cursor = QTextCursor(block)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            style = QTextCharFormat()
            style.setAnchor(True)
            style.setAnchorNames(['mechanism-block-' + str(block.blockNumber())])
            style.setFontUnderline(False)
            style.setFontWeight(QFont.Weight.Bold if block.blockNumber() == 0 or block.text().startswith('【')
                                else QFont.Weight.Normal)
            cursor.mergeCharFormat(style)
            block = block.next()


def replace_mechanism_text(widget, text, *, preserve, follow_change, heading=None, details=None):
    notes = ''
    if details is not None:
        from .reference_copy import mechanism_copy
        widget.reference_details = details
        text, notes = mechanism_copy(text, details.property('referenceBaseText'))
    changed = replace_text(widget, text, preserve=preserve)
    if details is not None:
        base = details.property('referenceBaseText')
        details.setText(base + ('\n\n' + notes if notes else ''))
    if follow_change and not preserve and heading:
        target = widget.document().find(heading)
        if not target.isNull():
            block = target.block()
            widget.setTextCursor(QTextCursor(block))
            widget.scrollToAnchor('mechanism-block-' + str(block.blockNumber()))
    return changed
