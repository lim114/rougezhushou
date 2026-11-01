"""One native reference window; retained Qt pages own their reading state."""
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QSizePolicy, QLayout, QScrollArea
from .player_window_frame import PlayerDialog
from .player_theme import apply_theme


class PageHeaders(QStackedWidget):
    """Only the visible page supplies the shared title bar's size hints."""

    def sizeHint(self):
        page = self.currentWidget()
        return page.sizeHint() if page is not None else QSize(0, 0)

    def minimumSizeHint(self):
        page = self.currentWidget()
        return page.minimumSizeHint() if page is not None else QSize(0, 0)


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
        self.source_parent = None
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
        self.body_scroll = QScrollArea()
        self.body_scroll.setWidgetResizable(True)
        self.body_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.body_scroll.setWidget(content)
        body.addWidget(self.body_scroll, 1)
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
        self.headers = PageHeaders()
        self.headers.currentChanged.connect(self.headers.updateGeometry)
        self.history = []
        self.linked_pages = {}
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
            self.move(max(area.left(), min(self.x(), area.right()-self.width()+1)),
                      max(area.top(), min(self.y(), area.bottom()-self.height()+1)))
        self.update_navigation()
        self.raise_()
        return True

    def discard(self, page, *, fallback):
        """Remove an invalid source page and its dependent reading chain."""
        current = self.pages.currentWidget()
        targets = {page}
        candidates = set(self.linked_pages.values())
        while True:
            children = {p for p in candidates-targets if p.source_parent in targets}
            if not children:
                break
            targets.update(children)
        self.linked_pages = {k: p for k, p in self.linked_pages.items() if p not in targets}
        removed_before = sum(p in targets for p in self.history[:self.cursor+1])
        self.history = [p for p in self.history if p not in targets]
        self.cursor -= removed_before
        if current in targets:
            self.present(fallback)
            self.parentWidget().active_popup = fallback
        self.switching = True
        for target in targets:
            if target is not current:
                target.close()
            self.pages.removeWidget(target)
            self.headers.removeWidget(target.header)
            target.header.deleteLater()
            target.deleteLater()
        self.switching = False
        self.update_navigation()

    def open_reference(self, parent, role, context, factory, *, verify=None):
        """Retain a child reader while its exact parent source/selection matches."""
        from copy import deepcopy
        source = parent
        while not isinstance(source, ToolPage):
            source = source.parentWidget()
        expected = deepcopy(context())
        if expected is None:
            return False
        key = (source, role)
        page = self.linked_pages.get(key)
        if page is not None and page.link_context != expected:
            self.discard(page, fallback=source)
            page = None
        if page is None:
            page = factory(self.parentWidget())
            if page is None:
                return False
            page.source_parent = source
            page.link_context = expected
            self.linked_pages[key] = page
            def prepare():
                if not source.prepare():
                    if page in self.linked_pages.values():
                        self.discard(page, fallback=source)
                    return False
                if (context() != expected or page.panel.refresh_reference() is False
                        or (verify is not None and not verify(page.panel))):
                    self.discard(page, fallback=source)
                    return False
                return True
            page.prepare = prepare
        return self.parentWidget().present(page)

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
