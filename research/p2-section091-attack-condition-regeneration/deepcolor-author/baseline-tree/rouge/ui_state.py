"""Refresh read-only text without moving the reader's cursor or viewport."""
from PySide6.QtGui import QTextCursor


def _reading_state(widget):
    cursor = widget.textCursor()
    vertical = widget.verticalScrollBar()
    return (cursor.anchor(), cursor.position(), vertical.value(),
            widget.horizontalScrollBar().value(), vertical.value() >= vertical.maximum())


def _restore_reading(widget, state, follow_tail):
    anchor, position, vertical, horizontal, at_tail = state
    # QTextCursor uses document positions (UTF-16), not Python string lengths.
    last = max(0, widget.document().characterCount() - 1)
    cursor = QTextCursor(widget.document())
    cursor.setPosition(min(anchor, last))
    cursor.setPosition(min(position, last), QTextCursor.MoveMode.KeepAnchor)
    widget.setTextCursor(cursor)
    bar = widget.verticalScrollBar()
    bar.setValue(bar.maximum() if follow_tail and at_tail else vertical)
    widget.horizontalScrollBar().setValue(horizontal)


def replace_text(widget, text, *, preserve=True, follow_tail=False):
    """Return whether text changed; a new viewed item can explicitly reset state."""
    if preserve and widget.toPlainText() == text:
        return False
    state = _reading_state(widget) if preserve else None
    widget.setPlainText(text)
    if state is not None:
        _restore_reading(widget, state, follow_tail)
    return True


def append_text(widget, text, *, follow_tail=True):
    """Append a local reply chunk, following it only while already at the bottom."""
    if not text:
        return False
    state = _reading_state(widget)
    cursor = QTextCursor(widget.document())
    cursor.movePosition(QTextCursor.MoveOperation.End)
    cursor.insertText(text)
    _restore_reading(widget, state, follow_tail)
    return True
