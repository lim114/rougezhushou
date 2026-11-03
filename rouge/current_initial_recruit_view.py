"""Read-only current recruitment associations, with exact two-way navigation."""
import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QListWidgetItem, QPlainTextEdit,
                               QPushButton, QTabWidget, QVBoxLayout, QWidget)

from . import current_initial_recruit as model
from .ui_state import replace_text


class CurrentInitialRecruitPanel(QWidget):
    def __init__(self, target=None, parent=None):
        super().__init__(parent)
        self.result = None
        self.selected_result = None
        self.last_target = None
        layout = QVBoxLayout(self)
        notice = QLabel(model.NOTICE)
        notice.setWordWrap(True)
        layout.addWidget(notice)
        filters = QHBoxLayout()
        self.kind = QComboBox()
        self.kind.setAccessibleName('开局资料查看分支')
        for key, label in model.KINDS:
            self.kind.addItem(label, key)
        filters.addWidget(self.kind)
        self.scope = QComboBox()
        self.scope.setAccessibleName('开局资料模式范围')
        self._populate_scopes()
        filters.addWidget(self.scope)
        self.search = QLineEdit()
        self.search.setPlaceholderText('按名称、月份、保密等级或职业查找')
        self.search.setAccessibleName('查找开局配置或招募组合')
        filters.addWidget(self.search, 1)
        self.refresh_button = QPushButton('重新核对资料')
        filters.addWidget(self.refresh_button)
        layout.addLayout(filters)
        self.entries = QListWidget()
        self.entries.setAccessibleName('开局配置或招募组合目录')
        self.entries.setMaximumHeight(175)
        layout.addWidget(self.entries)
        self.declaration_row = QWidget()
        declaration = QHBoxLayout(self.declaration_row)
        declaration.setContentsMargins(0, 0, 0, 0)
        label = QLabel('可选，仅本页对照：曾使用其它招募组合进行一次探索')
        label.setWordWrap(True)
        declaration.addWidget(label, 1)
        self.other_exploration = QComboBox()
        self.other_exploration.setAccessibleName('本页声明是否曾用其它组合进行一次探索')
        for label, value in (('未知', None), ('是', True), ('否', False)):
            self.other_exploration.addItem(label, value)
        declaration.addWidget(self.other_exploration)
        layout.addWidget(self.declaration_row)
        self.tabs = QTabWidget()
        self.player = QPlainTextEdit()
        self.technical = QPlainTextEdit()
        for reader, label in ((self.player, '招募内容与条件'), (self.technical, '原值与来源')):
            reader.setReadOnly(True)
            self.tabs.addTab(reader, label)
        layout.addWidget(self.tabs, 1)
        self.related_box = QWidget()
        related_layout = QVBoxLayout(self.related_box)
        related_layout.setContentsMargins(0, 0, 0, 0)
        self.related_label = QLabel()
        self.related_label.setWordWrap(True)
        related_layout.addWidget(self.related_label)
        self.related = QListWidget()
        self.related.setAccessibleName('原资料明确关联的配置或组合')
        self.related.setMaximumHeight(125)
        related_layout.addWidget(self.related)
        self.open_related_button = QPushButton('打开选中的关联资料')
        self.open_related_button.setEnabled(False)
        related_layout.addWidget(self.open_related_button)
        layout.addWidget(self.related_box)
        self.kind.currentIndexChanged.connect(self._kind_changed)
        self.scope.currentIndexChanged.connect(self._filters_changed)
        self.search.textChanged.connect(self._filters_changed)
        self.entries.currentItemChanged.connect(self._selected)
        self.other_exploration.currentIndexChanged.connect(self._declaration_changed)
        self.related.currentItemChanged.connect(self._related_changed)
        self.open_related_button.clicked.connect(lambda: self.open_related())
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.refresh_reference()
        if target is not None:
            self.navigate_to(target)

    def _populate_scopes(self):
        old = self.scope.blockSignals(True)
        try:
            self.scope.clear()
            for key, label in model.SCOPES:
                if key != 'unlinked' or self.kind.currentData() == 'group':
                    self.scope.addItem(label, key)
        finally:
            self.scope.blockSignals(old)

    def selected_target(self):
        item = self.entries.currentItem()
        return None if item is None else {'kind': self.kind.currentData(), 'key': item.data(Qt.ItemDataRole.UserRole)}

    def _reset_declaration(self):
        old = self.other_exploration.blockSignals(True)
        try:
            self.other_exploration.setCurrentIndex(0)
        finally:
            self.other_exploration.blockSignals(old)

    def _clear_related(self):
        self.related.clear()
        self.related_label.clear()
        self.open_related_button.setEnabled(False)
        self.related_box.hide()

    def clear_reference(self):
        self.result = self.selected_result = self.last_target = None
        old = self.entries.blockSignals(True)
        try:
            self.entries.clear()
        finally:
            self.entries.blockSignals(old)
        self._reset_declaration()
        self.declaration_row.hide()
        self._clear_related()
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False)
        self.tabs.setCurrentIndex(0)

    def refresh_reference(self, *_):
        fresh = model.catalog(self.kind.currentData(), self.scope.currentData(), self.search.text())
        if fresh is None:
            self.clear_reference()
            return False
        same = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        selected = self.selected_target() if same else None
        scroll = self.entries.verticalScrollBar().value() if same else 0
        if selected is not None and not any(r['id'] == selected['key'] for r in fresh['rows']):
            selected = None
        if not same or selected is None:
            self._reset_declaration()
            self.last_target = None
            self.tabs.setCurrentIndex(0)
        self.result = fresh
        old = self.entries.blockSignals(True)
        try:
            self.entries.clear()
            for row in fresh['rows']:
                item = QListWidgetItem(row['label'])
                item.setData(Qt.ItemDataRole.UserRole, row['id'])
                self.entries.addItem(item)
                if selected is not None and row['id'] == selected['key']:
                    self.entries.setCurrentItem(item)
            if selected is None:
                self.entries.setCurrentRow(-1)
            self.entries.verticalScrollBar().setValue(scroll)
        finally:
            self.entries.blockSignals(old)
        return self._render(self.selected_target(), preserve=same and selected is not None)

    def _render(self, target, *, preserve):
        if self.result is None:
            return False
        if target is None:
            self.selected_result = None
            self._reset_declaration()
            self.declaration_row.hide()
            self._clear_related()
            replace_text(self.player,
                         '请选择开局配置或招募组合。\n\n'
                         '开局配置可打开原资料明确列出的组合；组合可返回所有明确引用它的开局配置。\n'
                         '常规行动按保密等级分开，实践者列表按原记录的年份、月份和名称分开。\n'
                         '当前21份初始配置只引用14份组合中的10份；另外4份支援作战保留在“尚未关联”分支，不能猜作未来月份。\n\n'
                         '黑流树海的“随心所欲”说明为5星临时招募保证，通用攻略旧4星说法单独保留。实际账户解锁与随机人选仍需游戏确认。',
                         preserve=preserve)
            replace_text(self.technical, '', preserve=preserve)
            return True
        if (type(target) is not dict or set(target) != {'kind', 'key'}
                or target['kind'] != self.kind.currentData()
                or not any(r['id'] == target['key'] for r in self.result['rows'])):
            self.clear_reference()
            return False
        random = target == {'kind': 'group', 'key': model.RANDOM}
        fresh = model.detail(target['kind'], target['key'], self.other_exploration.currentData() if random else None)
        if fresh is None or fresh['source_identity'] != self.result['source_identity']:
            self.clear_reference()
            return False
        selected_related = self.related.currentItem().data(Qt.ItemDataRole.UserRole) if preserve and self.related.currentItem() else None
        related_scroll = self.related.verticalScrollBar().value() if preserve else 0
        self.selected_result = fresh
        self.declaration_row.setVisible(random)
        if not random:
            self._reset_declaration()
        replace_text(self.player, model.player_text(fresh), preserve=preserve)
        technical = {'target': fresh['target'], 'row': fresh['row'], 'related': fresh['related'],
                     'source_identity': fresh['source_identity'], 'source_scope': fresh['data']['source_scope'],
                     'actual_unlocked': fresh['actual_unlocked'], 'actual_eligible': fresh['actual_eligible'],
                     'actual_menu': fresh['actual_menu'], 'actual_recruits': fresh['actual_recruits'],
                     'listed_unlock_description_matches': fresh['listed_unlock_description_matches']}
        if random:
            technical['separate_original_documents'] = fresh['documents']
        replace_text(self.technical, json.dumps(technical, ensure_ascii=False, indent=2), preserve=preserve)
        self.related.clear()
        for row in fresh['related']:
            item = QListWidgetItem(row['label'])
            item.setData(Qt.ItemDataRole.UserRole, row['target'])
            self.related.addItem(item)
            if row['target'] == selected_related:
                self.related.setCurrentItem(item)
        self.related.verticalScrollBar().setValue(related_scroll)
        self.related_label.setText('该开局明确列出的招募组合' if target['kind'] == 'initial' else
                                   '明确引用该组合的开局配置' if fresh['related'] else '当前初始配置没有引用该组合，暂无可跳转的对应配置。')
        self.related_box.show()
        self._related_changed()
        return True

    def navigate_to(self, target):
        if type(target) is not dict or set(target) != {'kind', 'key'}:
            return False
        fresh = model.detail(target['kind'], target['key'])
        if fresh is None or fresh['target'] != target:
            return False
        old = self.kind.blockSignals(True)
        try:
            self.kind.setCurrentIndex(self.kind.findData(target['kind']))
        finally:
            self.kind.blockSignals(old)
        self._populate_scopes()
        old = self.search.blockSignals(True)
        try:
            self.search.clear()
        finally:
            self.search.blockSignals(old)
        self.clear_reference()
        if not self.refresh_reference() or self.result['source_identity'] != fresh['source_identity']:
            self.clear_reference()
            return False
        for index in range(self.entries.count()):
            if self.entries.item(index).data(Qt.ItemDataRole.UserRole) == target['key']:
                self.entries.setCurrentRow(index)
                return self.selected_result is not None and self.selected_result['target'] == target
        return False

    def open_related(self, target=None):
        if self.selected_result is None:
            return False
        if target is None:
            item = self.related.currentItem()
            target = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if type(target) is not dict or target not in [r['target'] for r in self.selected_result['related']]:
            return False
        # The source must still support this exact association at activation time.
        current = model.detail(self.selected_result['kind'], self.selected_result['row']['id'])
        if (current is None or current['source_identity'] != self.selected_result['source_identity']
                or target not in [r['target'] for r in current['related']]):
            self.clear_reference()
            return False
        return self.navigate_to(target)

    def _related_changed(self, *_):
        item = self.related.currentItem()
        self.open_related_button.setEnabled(self.selected_result is not None and item is not None
                                           and item.data(Qt.ItemDataRole.UserRole) in [r['target'] for r in self.selected_result['related']])

    def _selected(self, *_):
        target = self.selected_target()
        if target != self.last_target:
            self._reset_declaration()
            self.tabs.setCurrentIndex(0)
        self.last_target = target
        self._render(target, preserve=False)

    def _declaration_changed(self, *_):
        self._render(self.selected_target(), preserve=True)

    def _filters_changed(self, *_):
        self.clear_reference()
        self.refresh_reference()

    def _kind_changed(self, *_):
        self._populate_scopes()
        self._filters_changed()

    def closeEvent(self, event):
        self.clear_reference()
        super().closeEvent(event)


class CurrentInitialRecruitDialog(QDialog):
    def __init__(self, target=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('开局招募 · 组合、条件与对应配置')
        self.resize(1080, 880)
        layout = QVBoxLayout(self)
        self.panel = CurrentInitialRecruitPanel(target, self)
        layout.addWidget(self.panel)

    def closeEvent(self, event):
        self.panel.clear_reference()
        super().closeEvent(event)
