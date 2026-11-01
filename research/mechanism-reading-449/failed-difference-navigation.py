"""Readable full prose and native Qt navigation after an explicit topic change."""
from os.path import commonprefix
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat
from PySide6.QtWidgets import QTextBrowser
from .ui_state import replace_text


class MechanismTextBrowser(QTextBrowser):
    def setPlainText(self, text):
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


def replace_mechanism_text(widget, text, *, preserve, follow_change):
    previous = widget.toPlainText() if follow_change and not preserve else None
    changed = replace_text(widget, text, preserve=preserve)
    if previous is not None:
        current = widget.toPlainText()
        if previous != current:
            position = len(commonprefix((previous, current)).encode('utf-16-le')) // 2
            block = widget.document().findBlock(position)
            widget.setTextCursor(QTextCursor(block))
            widget.scrollToAnchor('mechanism-block-' + str(block.blockNumber()))
    return changed
