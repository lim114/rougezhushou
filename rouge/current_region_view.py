"""Current exact-region reference; all declarations stay inside this panel."""
import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QSpinBox, QListWidget, QListWidgetItem, QPlainTextEdit,
                               QTabWidget, QPushButton, QComboBox)

from . import current_region_reference as model
from .ui_state import replace_text


def _truth_combo(name):
    combo = QComboBox()
    combo.setAccessibleName(name)
    for label, value in (('未知', None), ('是', True), ('否', False)):
        combo.addItem(label, value)
    return combo


class CurrentRegionPanel(QWidget):
    def __init__(self, target=None, parent=None):
        super().__init__(parent)
        self.result = None
        self.selected_result = None
        self.last_id = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(model.NOTICE)
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        filters = QHBoxLayout()
        filters.addWidget(QLabel('按区域目标查看'))
        self.group = QComboBox()
        for key, title in model.GROUPS:
            self.group.addItem(title, key)
        filters.addWidget(self.group, 1)
        self.refresh_button = QPushButton('重新核对资料')
        filters.addWidget(self.refresh_button)
        layout.addLayout(filters)
        self.entries = QListWidget()
        self.entries.setAccessibleName('当前固定资料中的区域')
        self.entries.setMaximumHeight(170)
        layout.addWidget(self.entries)
        self.declarations = QWidget()
        declarations = QVBoxLayout(self.declarations)
        declarations.setContentsMargins(0, 0, 0, 0)
        self.ap_row = QWidget()
        ap = QHBoxLayout(self.ap_row)
        ap.setContentsMargins(0, 0, 0, 0)
        ap.addWidget(QLabel('可选，仅本页：当前剩余行动力'))
        self.action_points = QSpinBox()
        self.action_points.setRange(-1, 2147483647)
        self.action_points.setSpecialValueText('未知')
        self.action_points.setValue(-1)
        self.action_points.setSuffix(' 点')
        self.action_points.setAccessibleName('本页声明的当前剩余行动力')
        ap.addWidget(self.action_points, 1)
        declarations.addWidget(self.ap_row)
        self.goal_row = QWidget()
        goal = QHBoxLayout(self.goal_row)
        goal.setContentsMargins(0, 0, 0, 0)
        self.goal_label = QLabel()
        self.goal_label.setWordWrap(True)
        goal.addWidget(self.goal_label)
        self.goal_completed = _truth_combo('本页声明的区域目标是否完成')
        goal.addWidget(self.goal_completed, 1)
        declarations.addWidget(self.goal_row)
        self.wings_row = QWidget()
        wings = QHBoxLayout(self.wings_row)
        wings.setContentsMargins(0, 0, 0, 0)
        wings.addWidget(QLabel('仅第一层对照：“翅膀”科技是否生效'))
        self.wings = _truth_combo('本页声明的翅膀科技是否生效')
        wings.addWidget(self.wings, 1)
        declarations.addWidget(self.wings_row)
        layout.addWidget(self.declarations)
        self.tabs = QTabWidget()
        self.player = QPlainTextEdit()
        self.technical = QPlainTextEdit()
        for widget, title in ((self.player, '行动力与区域目标'), (self.technical, '完整原值与来源')):
            widget.setReadOnly(True)
            self.tabs.addTab(widget, title)
        layout.addWidget(self.tabs, 1)
        self.group.currentIndexChanged.connect(self._group_changed)
        self.entries.currentItemChanged.connect(self._selected)
        self.action_points.valueChanged.connect(self._declaration_changed)
        self.goal_completed.currentIndexChanged.connect(self._declaration_changed)
        self.wings.currentIndexChanged.connect(self._declaration_changed)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.refresh_reference()
        if type(target) is dict and set(target) == {'zone_id'}:
            if model.locate('regions', target['zone_id']) == target:
                self.select_region(target['zone_id'])

    def selected_id(self):
        item = self.entries.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item is not None else None

    def select_region(self, zone_id):
        if type(zone_id) is not str or self.result is None:
            return False
        for index in range(self.entries.count()):
            if self.entries.item(index).data(Qt.ItemDataRole.UserRole) == zone_id:
                self.entries.setCurrentRow(index)
                return True
        return False

    def _reset_declarations(self):
        for widget, value in ((self.action_points, -1), (self.goal_completed, 0), (self.wings, 0)):
            previous = widget.blockSignals(True)
            try:
                if widget is self.action_points:
                    widget.setValue(value)
                else:
                    widget.setCurrentIndex(value)
            finally:
                widget.blockSignals(previous)

    def _declaration_values(self, row):
        return {'action_points': None if self.action_points.value() < 0 else self.action_points.value(),
                'goal_completed': self.goal_completed.currentData() if row['group'] != 'return' else None,
                'wings': self.wings.currentData() if row['wings_applicable_reference'] else None}

    def clear_reference(self):
        self.result = None
        self.selected_result = None
        self.last_id = None
        previous = self.entries.blockSignals(True)
        try:
            self.entries.clear()
        finally:
            self.entries.blockSignals(previous)
        self._reset_declarations()
        self.declarations.hide()
        self.goal_row.hide()
        self.wings_row.hide()
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False)
        self.tabs.setCurrentIndex(0)

    def refresh_reference(self, *_):
        fresh = model.catalog(self.group.currentData())
        if fresh is None:
            self.clear_reference()
            return False
        same = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        selected = self.selected_id() if same else None
        if not same:
            self._reset_declarations()
            self.last_id = None
            self.tabs.setCurrentIndex(0)
        self.result = fresh
        previous = self.entries.blockSignals(True)
        try:
            self.entries.clear()
            for row in fresh['rows']:
                title = model.label(row) + ' · 资料入区数值 ' + str(row['entry_grant']['amount']) + ' 点'
                item = QListWidgetItem(title)
                item.setData(Qt.ItemDataRole.UserRole, row['id'])
                self.entries.addItem(item)
                if row['id'] == selected:
                    self.entries.setCurrentItem(item)
            if selected is None:
                self.entries.setCurrentRow(-1)
        finally:
            self.entries.blockSignals(previous)
        return self._render(self.selected_id(), preserve=same)

    def _render(self, zone_id, *, preserve):
        if self.result is None:
            return False
        row = next((r for r in self.result['rows'] if r['id'] == zone_id), None)
        if zone_id is not None and row is None:
            self.clear_reference()
            return False
        if row is None:
            self.selected_result = None
            self.declarations.hide()
            self.goal_row.hide()
            self.wings_row.hide()
            text = ('当前固定资料包含27份区域记录：4份以抵达险路尽头为目标，4份要求击败险路恶敌，'
                    '19份秘境记录在行动力耗尽后返回。\n\n'
                    '请选择区域，查看其入区行动力资料分项、文献印证与耗尽条件。\n'
                    '同名区域以“资料序号”区分；这不是地图层数，也不是自动识别到的当前区域。\n\n'
                    '资料数值不等于完整实际入区行动力。不会替换现有预算器，也不会改变本局记录或选择路线。')
            replace_text(self.player, text, preserve=preserve)
            replace_text(self.technical, json.dumps(self.result, ensure_ascii=False, indent=2), preserve=preserve)
            return True
        fresh = model.reference(zone_id, **self._declaration_values(row))
        if fresh is None or fresh['source_identity'] != self.result['source_identity']:
            self.clear_reference()
            return False
        self.selected_result = fresh
        self.declarations.show()
        self.goal_row.setVisible(row['group'] != 'return')
        self.goal_label.setText('仅本页：已击败险路恶敌' if row['group'] == 'boss' else '仅本页：已抵达险路尽头')
        self.wings_row.setVisible(row['wings_applicable_reference'])
        replace_text(self.player, model.player_text(fresh), preserve=preserve)
        replace_text(self.technical, json.dumps(fresh, ensure_ascii=False, indent=2), preserve=preserve)
        return True

    def _selected(self, item, *_):
        zone_id = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if zone_id != self.last_id:
            self._reset_declarations()
        self.last_id = zone_id
        self._render(zone_id, preserve=False)

    def _declaration_changed(self, *_):
        self._render(self.selected_id(), preserve=True)

    def _group_changed(self, *_):
        # A different branch never carries a declaration to another region.
        self.clear_reference()
        self.refresh_reference()

    def closeEvent(self, event):
        self.clear_reference()
        super().closeEvent(event)


class CurrentRegionDialog(QDialog):
    def __init__(self, target=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('区域资料 · 入区行动力与耗尽条件')
        self.resize(1060, 840)
        layout = QVBoxLayout(self)
        self.panel = CurrentRegionPanel(target, self)
        layout.addWidget(self.panel)

    def closeEvent(self, event):
        self.panel.clear_reference()
        super().closeEvent(event)
