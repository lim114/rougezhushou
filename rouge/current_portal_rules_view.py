"""Player-readable portal rules and separate original-region refresh tables."""
from copy import deepcopy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QListWidget, QListWidgetItem, QPlainTextEdit, QTabWidget)
from . import current_portal_rules as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentPortalRulesPanel(QWidget):
    def __init__(self, target=None, parent=None):
        super().__init__(parent)
        self.result = None; self.selected_key = None; self._view_key = None
        self.target = deepcopy(target); self._initial_target = True
        self.link_dialog = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(model.NOTICE); self.notice.setWordWrap(True); layout.addWidget(self.notice)
        bar = QHBoxLayout(); self.branch = QComboBox(); self.fog = QComboBox()
        self.branch.addItem('九种乌托邦规则', 'rules')
        self.branch.addItem('原区域的节点刷新表', 'refresh')
        self.fog.addItem('全部雾色', None)
        for fog in model.FOGS: self.fog.addItem(fog, fog)
        self.refresh_button = QPushButton('重新核对秘境规则')
        bar.addWidget(self.branch); bar.addWidget(self.fog, 1); bar.addWidget(self.refresh_button)
        layout.addLayout(bar)
        self.entries = QListWidget(); self.entries.setMaximumHeight(145)
        self.entries.setAccessibleName('规则或准确原区域条目'); layout.addWidget(self.entries)
        self.floor_controls = QWidget(); floor_row = QHBoxLayout(self.floor_controls)
        floor_row.setContentsMargins(0, 0, 0, 0)
        floor_row.addWidget(QLabel('仅本页对照：进入前的常规层'))
        self.floor = QComboBox(); self.floor.addItem('尚未确认', None)
        for value, text in enumerate(('Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ'), 1): self.floor.addItem('第' + text + '层', value)
        floor_row.addWidget(self.floor); layout.addWidget(self.floor_controls)
        self.refresh_controls = QWidget(); query = QVBoxLayout(self.refresh_controls)
        query.setContentsMargins(0, 0, 0, 0)
        query.addWidget(QLabel('仅对照全知者盲区的文字条件，不读取或改变本局节点：'))
        query_row = QHBoxLayout(); self.node_type = QComboBox(); self.node_type.addItem('节点类型未确认', None)
        self.moved = self._boolean_combo('是否已完成一次移动', '已经移动', '尚未移动')
        self.passed = self._boolean_combo('节点是否已经过', '已经过', '未经过')
        for widget in (self.node_type, self.moved, self.passed): query_row.addWidget(widget)
        query.addLayout(query_row)
        self.shop_controls = QWidget(); shop_row = QHBoxLayout(self.shop_controls)
        shop_row.setContentsMargins(0, 0, 0, 0)
        shop_row.addWidget(QLabel('诡意行商是否为“已完成”状态'))
        self.completed_shop = self._boolean_combo('商店完成状态', '已完成', '未完成')
        shop_row.addWidget(self.completed_shop); query.addWidget(self.shop_controls)
        layout.addWidget(self.refresh_controls)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for widget, text in ((self.player, '规则、条件与例外'), (self.technical, '原文与来源')):
            widget.setReadOnly(True); self.tabs.addTab(widget, text)
        layout.addWidget(self.tabs, 1)
        links = QHBoxLayout(); self.source_combo = QComboBox()
        self.source_combo.setAccessibleName('准确对应的对话、节点或标志资料')
        self.source_button = QPushButton('查看所选原资料')
        links.addWidget(self.source_combo, 1); links.addWidget(self.source_button); layout.addLayout(links)
        self.link_status = QLabel(); self.link_status.setWordWrap(True); layout.addWidget(self.link_status)
        self.branch.currentIndexChanged.connect(self._scope_changed)
        self.fog.currentIndexChanged.connect(self._scope_changed)
        self.entries.currentItemChanged.connect(self._entry_changed)
        for widget in (self.floor, self.node_type, self.moved, self.passed, self.completed_shop):
            widget.currentIndexChanged.connect(self.refresh_reference)
        self.source_combo.currentIndexChanged.connect(self._source_changed)
        self.source_button.clicked.connect(self.open_source)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.refresh_reference()

    @staticmethod
    def _boolean_combo(name, yes, no):
        control = QComboBox(); control.setAccessibleName(name)
        control.addItem(name + '：未知', None); control.addItem(yes, True); control.addItem(no, False)
        return control

    @staticmethod
    def _set(control, value):
        blocked = control.blockSignals(True)
        control.setCurrentIndex(max(0, control.findData(value)))
        control.blockSignals(blocked)

    def _close_source(self):
        if self.link_dialog is not None: self.link_dialog.close()
        self.link_dialog = None

    def clear_reference(self):
        self._close_source(); self.result = None; self.selected_key = None; self._view_key = None
        self._initial_target = False
        blocked = self.entries.blockSignals(True); self.entries.clear(); self.entries.blockSignals(blocked)
        blocked = self.source_combo.blockSignals(True); self.source_combo.clear(); self.source_combo.blockSignals(blocked)
        for control in (self.floor, self.node_type, self.moved, self.passed, self.completed_shop): self._set(control, None)
        self.floor_controls.hide(); self.refresh_controls.hide(); self.shop_controls.hide()
        self.source_button.setEnabled(False); self.link_status.clear()
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def _scope_changed(self, *_):
        self.selected_key = None; self._close_source(); self.refresh_reference()

    def _entry_changed(self, item, *_):
        key = item.data(Qt.ItemDataRole.UserRole) if item else None
        if key != self.selected_key: self._close_source()
        self.selected_key = key; self.refresh_reference()

    def refresh_reference(self, *_):
        fresh = model.reference()
        if fresh is None: self.clear_reference(); return False
        keep = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        selected = self.selected_key if keep else None
        if not keep: self._close_source()
        if self._initial_target:
            request = self.target.get('source_request') if type(self.target) is dict else None
            target = model.locate(request.get('category'), request.get('key')) if type(request) is dict else None
            if target is not None and model._same(target, self.target):
                self._set(self.branch, target['branch']); self._set(self.fog, target['fog'])
                selected = target['rule_id'] if target['branch'] == 'rules' else target['zone_id']
            self._initial_target = False
        self.result = fresh; branch = self.branch.currentData(); fog = self.fog.currentData()
        self.fog.setVisible(branch == 'rules')
        old_node = self.node_type.currentData() if keep else None
        blocked = self.node_type.blockSignals(True); self.node_type.clear(); self.node_type.addItem('节点类型未确认', None)
        for key, row in fresh['data']['original_nodes'].items(): self.node_type.addItem(row['name'], key)
        self.node_type.setCurrentIndex(max(0, self.node_type.findData(old_node))); self.node_type.blockSignals(blocked)
        blocked = self.entries.blockSignals(True); self.entries.clear()
        if branch == 'rules':
            rows = [(r['name'] + ' · ' + r['fog'], r['id']) for r in model.rows(fresh, fog)]
        else:
            rows = [(row['name'] + ' · 原区域资料' + str(i) +
                    ('（有节点原表）' if key in fresh['data']['original_roll_node_data'] else '（未列独立表）'), key)
                    for i, (key, row) in enumerate(fresh['data']['original_portal_zones'].items(), 1)]
        for text, key in rows:
            item = QListWidgetItem(text); item.setData(Qt.ItemDataRole.UserRole, key); self.entries.addItem(item)
            if key == selected: self.entries.setCurrentItem(item)
        self.entries.blockSignals(blocked)
        self.selected_key = self.entries.currentItem().data(Qt.ItemDataRole.UserRole) if self.entries.currentItem() else None
        row = fresh['data']['rules'].get(self.selected_key) if branch == 'rules' else None
        self.floor_controls.setVisible(bool(row and row['documented_main_floors']))
        self.refresh_controls.setVisible(bool(row and row['id'] == 'variation_5'))
        self.shop_controls.setVisible(bool(row and row['id'] == 'variation_5' and self.node_type.currentData() == 'BATTLE_SHOP'))
        condition = model.refresh_condition(fresh, self.node_type.currentData(), moved=self.moved.currentData(),
            passed=self.passed.currentData(), completed_shop=self.completed_shop.currentData()
            if self.node_type.currentData() == 'BATTLE_SHOP' else None) if row and row['id'] == 'variation_5' else None
        key = (deepcopy(fresh['source_identity']), branch, fog, self.selected_key, self.floor.currentData(),
               self.node_type.currentData(), self.moved.currentData(), self.passed.currentData(),
               self.completed_shop.currentData() if self.node_type.currentData() == 'BATTLE_SHOP' else None)
        preserve = keep and key == self._view_key
        text = model.player_text(fresh, self.selected_key, fog=fog, main_floor=self.floor.currentData(), condition=condition) if branch == 'rules' else model.refresh_table_text(fresh, self.selected_key)
        replace_text(self.player, text, preserve=preserve)
        technical = {'source_identity': fresh['source_identity'], 'branch': branch, 'fog_filter': fog,
                     'selected': row if branch == 'rules' else fresh['data']['original_portal_zones'].get(self.selected_key),
                     'original_refresh_table': fresh['data']['original_roll_node_data'].get(self.selected_key),
                     'condition_comparison': condition, 'all_actual_outcomes_unknown': True}
        replace_text(self.technical, _technical_json(technical), preserve=preserve)
        previous_source = self.source_combo.currentData() if preserve else None
        candidates = model.links(fresh, self.selected_key if branch == 'rules' else None,
                                 self.selected_key if branch == 'refresh' else None)
        blocked = self.source_combo.blockSignals(True); self.source_combo.clear(); self.source_combo.addItem('选择准确对应的资料入口', None)
        for source in candidates: self.source_combo.addItem(source['label'], source)
        self.source_combo.setCurrentIndex(max(0, self.source_combo.findData(previous_source))); self.source_combo.blockSignals(blocked)
        self._source_changed(); self.link_status.clear()
        if not preserve: self.tabs.setCurrentIndex(0)
        child_panel = getattr(self.link_dialog, 'panel', None)
        if keep and child_panel is not None and self.link_dialog.isVisible():
            child_panel.refresh_reference()
        self._view_key = deepcopy(key)
        return True

    def _source_changed(self, *_):
        self.source_button.setEnabled(self.result is not None and self.source_combo.currentData() is not None)

    def open_source(self):
        request = self.source_combo.currentData()
        if self.result is None or request is None: return False
        branch = self.branch.currentData()
        selected = model.resolve_link(self.result, request,
            rule_id=self.selected_key if branch == 'rules' else None,
            zone_id=self.selected_key if branch == 'refresh' else None)
        if selected is None: self.clear_reference(); return False
        self._close_source(); key = request['key']
        if request['kind'] == 'portal_fog':
            from . import current_portal
            if current_portal.reference() is None:
                self.link_status.setText('溯源对话资料暂时无法核对；没有借用其它雾色。'); return False
            from .current_portal_view import CurrentPortalDialog
            dialog = CurrentPortalDialog(parent=self)
            index = dialog.panel.scene.findData('fog:' + key)
            if index < 0: dialog.close(); return False
            dialog.panel.scene.setCurrentIndex(index)
        else:
            raw = selected['original']; dialog = QDialog(self)
            dialog.setWindowTitle(request['label']); dialog.resize(850, 620)
            layout = QVBoxLayout(dialog); tabs = QTabWidget(); layout.addWidget(tabs)
            player = QPlainTextEdit(); player.setReadOnly(True)
            if request['kind'] == 'node_type':
                text = raw['name'] + '\n\n' + raw['description'] + '\n\n这里只查看准确节点类型的原说明，不表示本局已出现、受影响或包含所有同类事件。'
            elif request['kind'] == 'item':
                text = raw['name'] + ' · 地图标志\n\n' + version_plain(raw.get('usage')) + '\n\n这是居民标志原项，不是收藏品，也不代表本局已有标志或已触发战斗。'
            else:
                text = raw['name'] + '\n\n' + raw['description'] + '\n\n' + version_plain(raw.get('endingDescription')) + '\n\n同名原区域分别保留；实际雾色、地图与当前进入情况仍未知。'
            player.setPlainText(text); tabs.addTab(player, '原说明与范围')
            technical = QPlainTextEdit(); technical.setReadOnly(True); technical.setPlainText(_technical_json(selected)); tabs.addTab(technical, '准确原项与来源')
        self.link_dialog = dialog; dialog.show(); return True

    def closeEvent(self, event):
        self._close_source(); super().closeEvent(event)


def version_plain(value):
    return model.version._plain(value)


class CurrentPortalRulesDialog(QDialog):
    def __init__(self, target=None, parent=None):
        super().__init__(parent); self.setWindowTitle('秘境乌托邦 · 雾色、规则与节点刷新')
        self.resize(1100, 840); layout = QVBoxLayout(self)
        self.panel = CurrentPortalRulesPanel(target, self); layout.addWidget(self.panel)

    def closeEvent(self, event):
        self.panel._close_source(); super().closeEvent(event)
