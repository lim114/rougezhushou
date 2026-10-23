"""Independent read-only recruitment ticket page, suitable for an ordinary tab."""
import json
from copy import deepcopy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QLineEdit, QListWidget, QListWidgetItem,
                              QTabWidget, QPlainTextEdit, QPushButton, QSplitter)
from . import current_recruit_tickets as model
from .ui_state import replace_text


class CurrentRecruitTicketsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_identity = None
        self.result = None
        self.ticket_id = None
        self.event_dialog = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(model.NOTICE)
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        filters = QHBoxLayout()
        self.profession = QComboBox()
        self.profession.addItem('总览：全部职业', None)
        for value, label in model.PROFESSIONS:
            self.profession.addItem(label, value)
        self.family = QComboBox()
        self.family.addItem('总览：全部券种', None)
        for value, label in model.FAMILIES:
            self.family.addItem(label, value)
        self.profession.setAccessibleName('招募券适用职业')
        self.family.setAccessibleName('招募券种类')
        self.search = QLineEdit()
        self.search.setPlaceholderText('按完整中文券名搜索')
        self.refresh_button = QPushButton('重新核对资料')
        for control in (self.profession, self.family, self.search, self.refresh_button):
            filters.addWidget(control)
        layout.addLayout(filters)
        self.count = QLabel()
        layout.addWidget(self.count)
        splitter = QSplitter()
        self.entries = QListWidget()
        self.entries.setAccessibleName('招募券目录：原券与留存券按明确配对列出')
        splitter.addWidget(self.entries)
        self.tabs = QTabWidget()
        self.player = QPlainTextEdit()
        self.technical = QPlainTextEdit()
        for widget in (self.player, self.technical):
            widget.setReadOnly(True)
        self.tabs.addTab(self.player, '用途与留存规则')
        self.tabs.addTab(self.technical, '原券、留存券与来源')
        splitter.addWidget(self.tabs)
        splitter.setSizes([320, 760])
        layout.addWidget(splitter, 1)
        actions = QHBoxLayout()
        self.exit_button = QPushButton('查看险路尽头取券原文')
        self.rest_button = QPushButton('查看安全角落取券原文')
        actions.addWidget(self.exit_button)
        actions.addWidget(self.rest_button)
        layout.addLayout(actions)
        self.profession.currentIndexChanged.connect(self._filter_changed)
        self.family.currentIndexChanged.connect(self._filter_changed)
        self.search.textChanged.connect(self._filter_changed)
        self.entries.currentItemChanged.connect(self._selected)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.exit_button.clicked.connect(lambda: self.open_event('exit'))
        self.rest_button.clicked.connect(lambda: self.open_event('rest'))
        self.refresh_reference()

    def _filters(self):
        return {'profession': self.profession.currentData(),
                'ticket_family': self.family.currentData(), 'query': self.search.text()}

    def close_children(self):
        if self.event_dialog is not None:
            self.event_dialog.close()
        self.event_dialog = None

    def _unavailable(self):
        self.close_children()
        self.source_identity = None
        self.result = None
        self.ticket_id = None
        blocked = self.entries.blockSignals(True)
        try:
            self.entries.clear()
        finally:
            self.entries.blockSignals(blocked)
        replace_text(self.player, '', preserve=False)
        replace_text(self.technical, '', preserve=False)
        self.count.setText(model.UNAVAILABLE)
        self.exit_button.setEnabled(False)
        self.rest_button.setEnabled(False)

    def _filter_changed(self, *_):
        self._populate(preserve=False)

    def _populate(self, *, preserve):
        fresh = model.reference(**self._filters())
        if fresh is None:
            self._unavailable()
            return False
        same = self.source_identity == fresh['source_identity']
        selected = self.ticket_id if same and preserve else None
        self.source_identity = fresh['source_identity']
        blocked = self.entries.blockSignals(True)
        try:
            self.entries.clear()
            for row in fresh['rows']:
                item = QListWidgetItem(row['name'])
                item.setData(Qt.ItemDataRole.UserRole, row['id'])
                self.entries.addItem(item)
                if row['id'] == selected:
                    self.entries.setCurrentItem(item)
        finally:
            self.entries.blockSignals(blocked)
        self.count.setText('当前筛选列出'+str(len(fresh['rows']))+'种招募券。多职业筛选会重合，不是本局持有张数。')
        self.exit_button.setEnabled(True)
        self.rest_button.setEnabled(True)
        if self.entries.currentItem() is None:
            self.entries.setCurrentRow(-1)
            keep = same and preserve and self.ticket_id is None
            self.ticket_id = None
            if not keep:
                self.close_children()
            self._show(fresh, preserve=keep)
            if keep and self.event_dialog is not None and self.event_dialog.isVisible():
                self.event_dialog.panel.refresh_reference()
        else:
            self._selected(self.entries.currentItem(), preserve=same and preserve)
        return True

    def refresh_reference(self):
        return self._populate(preserve=True)

    def _show(self, result, *, preserve):
        self.result = deepcopy(result)
        replace_text(self.player, model.player_text(result), preserve=preserve)
        replace_text(self.technical, json.dumps(result, ensure_ascii=False, indent=2), preserve=preserve)
        if not preserve:
            self.tabs.setCurrentIndex(0)

    def _selected(self, item, *_, preserve=False):
        identity = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        fresh = model.reference(identity, **self._filters())
        if fresh is None or fresh['source_identity'] != self.source_identity:
            self._unavailable()
            return
        keep = preserve and identity == self.ticket_id
        if not keep:
            self.close_children()
        self.ticket_id = identity
        self._show(fresh, preserve=keep)
        if keep and self.event_dialog is not None and self.event_dialog.isVisible():
            self.event_dialog.panel.refresh_reference()

    def open_event(self, kind):
        if self.result is None:
            return False
        fresh = model.reference(self.ticket_id, **self._filters())
        if fresh is None or fresh != self.result:
            self._unavailable()
            return False
        link = model.destination(kind)
        if link is None:
            return False
        self.close_children()
        if kind == 'exit':
            from .current_exit_view import CurrentExitDialog
            self.event_dialog = CurrentExitDialog(link['target'], self)
        elif kind == 'rest':
            from .current_rest_travel_view import CurrentRestTravelDialog
            self.event_dialog = CurrentRestTravelDialog('金色凝滞', link['target'], self)
        else:
            return False
        if self.event_dialog.panel.result is None:
            self.close_children()
            return False
        self.event_dialog.show()
        return True

    def closeEvent(self, event):
        self.close_children()
        super().closeEvent(event)


class CurrentRecruitTicketsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('招募券 · 用途、留存与取出')
        self.resize(1100, 800)
        layout = QVBoxLayout(self)
        self.panel = CurrentRecruitTicketsPanel(self)
        layout.addWidget(self.panel)

    def closeEvent(self, event):
        self.panel.close_children()
        super().closeEvent(event)
