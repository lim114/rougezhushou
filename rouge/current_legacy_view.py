"""Cross-exploration original links and plain-language two-run condition checks."""
from copy import deepcopy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QListWidget, QListWidgetItem, QPlainTextEdit, QTabWidget)
from . import current_legacy as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentLegacyPanel(QWidget):
    def __init__(self, target=None, parent=None):
        super().__init__(parent)
        self.result = None; self.selected_key = None; self._view_key = None
        self.target = deepcopy(target); self._initial_target = True
        self.link_dialog = None; self._open_request = None; self._open_legacy = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(model.NOTICE); self.notice.setWordWrap(True); layout.addWidget(self.notice)
        bar = QHBoxLayout(); self.group = QComboBox()
        self.group.setAccessibleName('跨局助力分支')
        for key, label in model.GROUPS: self.group.addItem(label, key)
        self.refresh_button = QPushButton('重新核对助力资料')
        bar.addWidget(self.group, 1); bar.addWidget(self.refresh_button); layout.addLayout(bar)
        self.entries = QListWidget(); self.entries.setMaximumHeight(145)
        self.entries.setAccessibleName('准确跨局物品与同名原变体'); layout.addWidget(self.entries)
        self.conditions = QWidget(); conditions = QVBoxLayout(self.conditions)
        conditions.setContentsMargins(0, 0, 0, 0)
        conditions.addWidget(QLabel('开局助力专用；以下均为仅本页声明，不读取或改写本局：'))
        origin = QHBoxLayout(); origin.addWidget(QLabel('产生助力的那局'))
        self.origin_mode = self._mode('产生助力的那局模式')
        self.origin_grade = self._grade('产生助力的那局保密等级')
        self.origin_failed = self._boolean('是否确实探索失败', '明确探索失败', '明确没有失败')
        for widget in (self.origin_mode, self.origin_grade, self.origin_failed): origin.addWidget(widget)
        conditions.addLayout(origin)
        receipt = QHBoxLayout(); receipt.addWidget(QLabel('下次开始'))
        self.next_mode = self._mode('下次开始模式'); self.next_grade = self._grade('下次保密等级')
        self.next_started = self._boolean('下次是否已开始', '已开始', '尚未开始')
        for widget in (self.next_mode, self.next_grade, self.next_started): receipt.addWidget(widget)
        conditions.addLayout(receipt)
        claim = QHBoxLayout(); claim.addWidget(QLabel('不要由当前持有影像反推：'))
        self.prior_claim_consumed = self._boolean('这次收取判定是否已消耗', '已消耗', '未消耗')
        claim.addWidget(self.prior_claim_consumed, 1); conditions.addLayout(claim)
        layout.addWidget(self.conditions)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for widget, text in ((self.player, '用途、条件与提醒'), (self.technical, '准确原文与来源')):
            widget.setReadOnly(True); self.tabs.addTab(widget, text)
        layout.addWidget(self.tabs, 1)
        links = QHBoxLayout(); self.source_combo = QComboBox()
        self.source_combo.setAccessibleName('准确培育、后续支援、藏品与难度资料入口')
        self.source_button = QPushButton('查看所选资料')
        links.addWidget(self.source_combo, 1); links.addWidget(self.source_button); layout.addLayout(links)
        self.link_status = QLabel(); self.link_status.setWordWrap(True); layout.addWidget(self.link_status)
        self.group.currentIndexChanged.connect(self._scope_changed)
        self.entries.currentItemChanged.connect(self._entry_changed)
        for widget in self._declaration_controls(): widget.currentIndexChanged.connect(self._declaration_changed)
        self.source_combo.currentIndexChanged.connect(self._source_changed)
        self.source_button.clicked.connect(self.open_source)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.refresh_reference()

    def _declaration_controls(self):
        return (self.origin_mode, self.origin_grade, self.origin_failed, self.next_mode,
                self.next_grade, self.next_started, self.prior_claim_consumed)

    @staticmethod
    def _boolean(label, yes, no):
        control = QComboBox(); control.setAccessibleName(label)
        for text, value in ((label + '：未知', None), (yes, True), (no, False)): control.addItem(text, value)
        return control

    @staticmethod
    def _mode(label):
        control = QComboBox(); control.setAccessibleName(label)
        for text, value in (('模式未知', None), ('常规行动', 'NORMAL'), ('其它模式', 'OTHER')): control.addItem(text, value)
        return control

    @staticmethod
    def _grade(label):
        control = QComboBox(); control.setAccessibleName(label); control.addItem('保密等级未知', None)
        return control

    @staticmethod
    def _set(control, value):
        block = control.blockSignals(True); control.setCurrentIndex(max(0, control.findData(value))); control.blockSignals(block)

    def _reset_declarations(self):
        for control in self._declaration_controls(): self._set(control, None)

    def _close_source(self):
        if self.link_dialog is not None: self.link_dialog.close()
        self.link_dialog = None; self._open_request = None; self._open_legacy = None

    def clear_reference(self):
        self._close_source(); self.result = None; self.selected_key = None; self._view_key = None
        self._initial_target = False
        block = self.entries.blockSignals(True); self.entries.clear(); self.entries.blockSignals(block)
        block = self.source_combo.blockSignals(True); self.source_combo.clear(); self.source_combo.blockSignals(block)
        self._reset_declarations(); self.conditions.hide(); self.source_button.setEnabled(False); self.link_status.clear()
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def _scope_changed(self, *_):
        self.selected_key = None; self._reset_declarations(); self._close_source(); self.refresh_reference()

    def _entry_changed(self, item, *_):
        key = item.data(Qt.ItemDataRole.UserRole) if item else None
        if key != self.selected_key: self._reset_declarations(); self._close_source()
        self.selected_key = key; self.refresh_reference()

    def _declaration_changed(self, *_):
        if self.origin_mode.currentData() == 'OTHER': self._set(self.origin_grade, None)
        if self.next_mode.currentData() == 'OTHER': self._set(self.next_grade, None)
        self.refresh_reference()

    def _source_changed(self, *_):
        self._close_source(); self.link_status.clear()

    def refresh_reference(self, *_):
        fresh = model.reference()
        if fresh is None: self.clear_reference(); return
        previous_identity = self.result['source_identity'] if self.result else None
        if previous_identity is not None and previous_identity != fresh['source_identity']:
            self.clear_reference()
        self.result = fresh
        if self._initial_target:
            target = self.target; self._initial_target = False
            source = target.get('source_request') if type(target) is dict else None
            if (type(source) is dict and target == model.locate(source.get('category'), source.get('key'))):
                self._set(self.group, target['group']); self.selected_key = target['legacy_id']
        for control in (self.origin_grade, self.next_grade):
            selected = control.currentData(); block = control.blockSignals(True); control.clear(); control.addItem('保密等级未知', None)
            for row in fresh['data']['originals']['difficulties']:
                if row['modeDifficulty'] == 'NORMAL': control.addItem('保密等级' + str(row['grade']), row['grade'])
            control.setCurrentIndex(max(0, control.findData(selected))); control.blockSignals(block)
        selected = self.selected_key; scope = self.group.currentData()
        block = self.entries.blockSignals(True); self.entries.clear()
        for row in model.rows(fresh, scope):
            pointer = row['startup_pointer']; name = row['name']
            if pointer: name += ' → ' + pointer['title']
            elif row['group'] in ('cat', 'dog'):
                position = fresh['data']['groups'][row['group']]['ids'].index(row['id']) + 1
                name += ' · 原资料' + str(position)
            item = QListWidgetItem(name); item.setData(Qt.ItemDataRole.UserRole, row['id']); self.entries.addItem(item)
            if row['id'] == selected: self.entries.setCurrentItem(item)
        self.entries.blockSignals(block)
        if self.entries.currentItem() is None: self.selected_key = None
        key = self.selected_key; self.conditions.setVisible(key == model.HIDDEN)
        self.origin_grade.setVisible(self.origin_mode.currentData() != 'OTHER')
        self.next_grade.setVisible(self.next_mode.currentData() != 'OTHER')
        condition = None
        if key == model.HIDDEN:
            condition = model.compare_failure_support(fresh, **{
                name: getattr(self, name).currentData() for name in
                ('origin_mode', 'origin_grade', 'origin_failed', 'next_mode', 'next_grade', 'next_started', 'prior_claim_consumed')})
        view_key = (fresh['source_identity'], scope, key)
        replace_text(self.player, model.player_text(fresh, key, condition), preserve=self._view_key == view_key)
        row = fresh['data']['rows'].get(key)
        technical = {'source_identity': fresh['source_identity'], 'row': row, 'condition': condition,
                     'public_documentation': fresh['data']['failure_support_documentation'] if key == model.HIDDEN else None,
                     'actual_received': None, 'run_updated': False}
        replace_text(self.technical, _technical_json(technical), preserve=self._view_key == view_key)
        if self._view_key != view_key: self.tabs.setCurrentIndex(0)
        self._view_key = view_key
        old = self.source_combo.currentData(); block = self.source_combo.blockSignals(True); self.source_combo.clear()
        self.source_combo.addItem('请选择准确资料入口', None)
        for link in model.links(fresh, key): self.source_combo.addItem(link['label'], link)
        self.source_combo.setCurrentIndex(max(0, self.source_combo.findData(old))); self.source_combo.blockSignals(block)
        self.source_button.setEnabled(key is not None)
        if self.link_dialog is not None:
            resolved = model.resolve_link(fresh, self._open_request, legacy_id=self._open_legacy)
            if resolved is None: self._close_source(); self.link_status.setText('已打开的来源无法核对，旧窗口已关闭。')
            elif self._open_request['kind'] == 'seed': self.link_dialog.refresh()
            elif self._open_request['kind'] == 'startup': self.link_dialog.panel.refresh_reference()

    def open_source(self):
        request = self.source_combo.currentData()
        resolved = model.resolve_link(self.result, request, legacy_id=self.selected_key)
        self._close_source()
        if resolved is None:
            self.link_status.setText('该入口与当前原资料无法对应，旧窗口已关闭；请重新选择。'); return False
        kind = request['kind']
        if kind == 'seed':
            from .seed_cultivation_view import SeedCultivationPanel
            child = SeedCultivationPanel(self); child.set_reference(resolved['target']['item_id'])
        elif kind == 'startup':
            from .current_startup_view import CurrentStartupDialog
            child = CurrentStartupDialog(resolved['target'], self)
        else:
            child = QDialog(self); child.setWindowTitle(request['label']); child.resize(860, 650)
            layout = QVBoxLayout(child); tabs = QTabWidget(); layout.addWidget(tabs)
            original = resolved['original']
            if kind == 'difficulty':
                text = ('【保密等级' + str(original['grade']) + ' · 原条件】\n' +
                        model.version._plain(original['ruleDesc']) +
                        '\n\n这里只读这一档的原文；不把该档自动填为失败局或下次开始，也不将haveLegacy等字段当作实际领取证明。')
            else:
                item = original['item']; text = ('【' + item['name'] + '】\n' +
                    model.version._plain(item.get('usage')) + '\n\n' + model.version._plain(item.get('description')) +
                    '\n\n准确原物品资料；不代表已持有、继承或领取，不向本局添加效果。')
            for label, value in (('用途与适用范围', text), ('原文与来源', _technical_json(resolved))):
                area = QPlainTextEdit(); area.setReadOnly(True); area.setPlainText(value); tabs.addTab(area, label)
        self.link_dialog = child; self._open_request = deepcopy(request); self._open_legacy = self.selected_key
        self.link_status.clear(); child.show(); return True

    def closeEvent(self, event):
        self._close_source(); super().closeEvent(event)


class CurrentLegacyDialog(QDialog):
    def __init__(self, target=None, parent=None):
        super().__init__(parent); self.setWindowTitle('跨局助力 · 失败与下次开始分开核对'); self.resize(1100, 840)
        layout = QVBoxLayout(self); self.panel = CurrentLegacyPanel(target, self); layout.addWidget(self.panel)

    def closeEvent(self, event):
        self.panel._close_source(); super().closeEvent(event)
