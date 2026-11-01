"""One native reference window; retained Qt pages own their reading state."""
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QSizePolicy, QLayout
from .player_window_frame import PlayerDialog
from .player_theme import apply_theme


class ToolPage(QWidget):
    finished = Signal(int)

    def __init__(self, title, content, parent, *, on_show=None, theme='dark', extra_style='', object_name='playerPopover'):
        super().__init__(parent.reference_window.pages)
        self.host = parent.reference_window
        self.setWindowTitle(title)
        self.setObjectName(object_name)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.theme = theme
        self.extra_style = extra_style.replace('QDialog#', 'QWidget#')
        apply_theme(self, theme, extra=self.extra_style)
        self.on_show = on_show
        self.prepare = lambda: True
        self.preferred_size = QSize(760, 600)
        self.header = QWidget()
        self.header_bar = QHBoxLayout(self.header)
        self.header_bar.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel(title)
        self.title_label.setObjectName('popoverTitle')
        self.header_bar.addWidget(self.title_label, 1)
        body = QVBoxLayout(self)
        body.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        body.setContentsMargins(0, 0, 0, 0)
        body.addWidget(content, 1)
        # Constructed but unregistered pages must not appear with their host.
        self.hide()

    def resize(self, *args):
        self.preferred_size = QSize(*args)
        super().resize(*args)

    def showEvent(self, event):
        super().showEvent(event)
        if self.on_show is not None:
            self.on_show()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.finished.emit(0)
        if not self.host.switching and self.host.pages.currentWidget() is self:
            self.host.hide()


class NotesPage(ToolPage):
    def closeEvent(self, event):
        if not self.panel.finish_edit():
            event.ignore()
            return
        super().closeEvent(event)


class ReferenceWindow(PlayerDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('黑流树海助手 · 资料')
        self.setObjectName('playerReferenceWindow')
        self.pages = QStackedWidget()
        self.pages.layout().setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.pages.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.headers = QStackedWidget()
        self.history = []
        self.cursor = -1
        self.switching = False
        self.presenting = False
        self.back = QPushButton('‹')
        self.forward = QPushButton('›')
        for button, label in ((self.back, '返回上一页'), (self.forward, '前往下一页')):
            button.setAccessibleName(label)
            button.setToolTip(label)
            button.setFixedSize(28, 28)
            button.setAutoDefault(False)
        self.back.clicked.connect(lambda: self.navigate(self.cursor-1))
        self.forward.clicked.connect(lambda: self.navigate(self.cursor+1))
        bar = self.titleBar.hBoxLayout
        self.titleBar.titleLabel.hide()
        bar.insertWidget(0, self.back)
        bar.insertWidget(1, self.forward)
        bar.insertWidget(2, self.headers, 1)
        body = QVBoxLayout(self)
        body.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        body.addWidget(self.pages, 1)
        self.update_navigation()

    def present(self, page, *, record=True):
        if not page.prepare():
            return False
        current = self.pages.currentWidget()
        if current is not None and current is not page:
            current.preferred_size = self.size()
            self.switching = True
            accepted = current.close()
            self.switching = False
            if not accepted:
                self.show()
                self.raise_()
                return False
        if self.pages.indexOf(page) < 0:
            self.pages.addWidget(page)
            self.headers.addWidget(page.header)
        if record and (self.cursor < 0 or self.history[self.cursor] is not page):
            del self.history[self.cursor+1:]
            self.history.append(page)
            self.cursor = len(self.history)-1
        apply_theme(self, page.theme)
        self.setWindowTitle('黑流树海助手 · '+page.windowTitle())
        self.headers.setCurrentWidget(page.header)
        self.pages.setCurrentWidget(page)
        page.show()
        self.presenting = True
        self.show()
        self.presenting = False
        if current is not page:
            area = self.screen().availableGeometry()
            size = page.preferred_size
            self.resize(min(size.width(), area.width()-24), min(size.height(), area.height()-24))
        self.update_navigation()
        self.raise_()
        return True

    def discard(self, page, *, fallback):
        """Remove an invalid source page from both navigation directions."""
        current = self.pages.currentWidget()
        removed_before = sum(p is page for p in self.history[:self.cursor+1])
        self.history = [p for p in self.history if p is not page]
        self.cursor -= removed_before
        if current is page:
            self.present(fallback)
            self.parentWidget().active_popup = fallback
        else:
            self.switching = True
            page.close()
            self.switching = False
        self.pages.removeWidget(page)
        self.headers.removeWidget(page.header)
        page.header.deleteLater()
        page.deleteLater()
        self.update_navigation()

    def showEvent(self, event):
        current = self.pages.currentWidget()
        if not self.presenting and current is not None:
            current.prepare()
        super().showEvent(event)

    def navigate(self, index):
        if 0 <= index < len(self.history) and self.present(self.history[index], record=False):
            self.cursor = index
            self.parentWidget().active_popup = self.history[index]
            self.update_navigation()

    def update_navigation(self):
        self.back.setEnabled(self.cursor > 0)
        self.forward.setEnabled(0 <= self.cursor < len(self.history)-1)

    def closeEvent(self, event):
        current = self.pages.currentWidget()
        self.switching = True
        accepted = current is None or current.close()
        self.switching = False
        if not accepted:
            event.ignore()
            return
        event.accept()

    def reject(self):
        # Escape must use the same unsaved-note guard as the close button.
        self.close()
