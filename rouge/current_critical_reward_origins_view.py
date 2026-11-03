"""Only the selected item's relevant conditions; no inventory or game actions."""
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QSpinBox, QTabWidget, QPlainTextEdit, QPushButton)
from . import current_critical_reward_origins as model
from .ui_state import replace_text


class CurrentCriticalRewardPanel(QWidget):
    def __init__(self, item_id, parent=None):
        super().__init__(parent)
        self.item_id = item_id; self.result = None; self.flow_dialog = None; self.controls = {}
        layout = QVBoxLayout(self)
        notice = QLabel('以下只用于对照本物品的取得条件；默认未知，不表示本局已读到，也不会写入本局。')
        notice.setWordWrap(True); layout.addWidget(notice)
        initial = model.reference('relics', item_id)
        self.event_id = initial['rows'][0]['event_id'] if initial else None
        specifications = []
        if self.event_id == 'entry':
            specifications = [('floor', '主层', [('未知', None)] + [(str(n), n) for n in range(1, 7)]),
                              ('node_type', '节点', [('未知', 'unknown'), ('险路尽头', '险路尽头'), ('不期而遇', '不期而遇')]),
                              ('post_update_clear', '更新后已通关并解锁', [('未知', None), ('是', True), ('否', False)])]
        elif self.event_id == 'revive':
            specifications = [('node_type', '节点', [('未知', 'unknown'), ('不期而遇', '不期而遇'), ('险路尽头', '险路尽头')]),
                              ('next_unmarked_after_first_down', '首次倒下后的下个无标记不期而遇', [('未知', None), ('是', True), ('否', False)]),
                              ('rescue_used', '本局救援机会已使用', [('未知', None), ('是', True), ('否', False)])]
        for key, label, options in specifications:
            row = QHBoxLayout(); row.addWidget(QLabel(label)); control = QComboBox(); control.setAccessibleName(label)
            for text, value in options: control.addItem(text, value)
            self.controls[key] = control; row.addWidget(control, 1); layout.addLayout(row)
            control.currentIndexChanged.connect(self.refresh_reference)
        if self.event_id == 'entry':
            row = QHBoxLayout(); row.addWidget(QLabel('源石锭')); self.gold = QSpinBox(); self.gold.setRange(-1, 99999)
            self.gold.setSpecialValueText('未知'); self.gold.setValue(-1); self.gold.setAccessibleName('仅本页源石锭对照')
            row.addWidget(self.gold, 1); layout.addLayout(row); self.gold.valueChanged.connect(self.refresh_reference)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for reader, label in ((self.player, '取得条件'), (self.technical, '完整来源')):
            reader.setReadOnly(True); self.tabs.addTab(reader, label)
        layout.addWidget(self.tabs, 1)
        self.flow_button = QPushButton('查看准确领取选项的流程原文'); layout.addWidget(self.flow_button)
        self.flow_button.clicked.connect(self.open_flow); self.refresh_reference()

    def values(self):
        values = {k: c.currentData() for k, c in self.controls.items()}
        if hasattr(self, 'gold'): values['gold'] = self.gold.value() if self.gold.value() >= 0 else None
        return values

    def _close_flow(self):
        if self.flow_dialog is not None: self.flow_dialog.close()
        self.flow_dialog = None

    def _clear(self):
        self._close_flow(); self.result = None; self.flow_button.setEnabled(False)
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def refresh_reference(self, *_):
        fresh = model.reference('relics', self.item_id, self.values())
        if fresh is None: self._clear(); return False
        same = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        if not same: self._close_flow()
        self.result = fresh; checked = fresh['condition_reference']; row = fresh['rows'][0]
        lines = [model.player_text(fresh, row['key']), '', '【本页条件对照】']
        checks = checked['event_checks'] + checked['choice_checks'].get(row['choice_id'], [])
        for check in checks:
            lines.append(check['label'] + '：' + ('未知' if check['matches'] is None else '相符' if check['matches'] else '不符'))
        if not checks: lines.append('完整条件尚未有依据，保留未知。')
        lines += checked['notes']
        replace_text(self.player, '\n'.join(lines), preserve=same)
        replace_text(self.technical, json.dumps(fresh, ensure_ascii=False, indent=2), preserve=same)
        self.flow_button.setEnabled(True)
        if same and self.flow_dialog is not None and self.flow_dialog.isVisible():
            self.flow_dialog.panel.refresh_reference()
        return True

    def open_flow(self):
        fresh = model.reference('relics', self.item_id, self.values())
        if self.result is None or fresh != self.result: self._clear(); return False
        self._close_flow(); row = fresh['rows'][0]; target = row['target']
        if row['event_id'] == 'entry':
            from .current_exit_view import CurrentExitDialog
            dialog = CurrentExitDialog(target, self)
        else:
            from .documented_event_flow_view import DocumentedEventFlowDialog
            dialog = DocumentedEventFlowDialog(target['event_id'], target['scene_id'], self)
            for i in range(dialog.panel.choices.count()):
                if dialog.panel.choices.item(i).data(Qt.ItemDataRole.UserRole) == row['choice_id']:
                    dialog.panel.choices.setCurrentRow(i); break
        if (dialog.panel.result is None
                or (dialog.panel.scene_id, dialog.panel.choice_id) != (row['reader_target']['scene_id'], row['reader_target']['choice_id'])):
            dialog.close(); self._clear(); return False
        self.flow_dialog = dialog; dialog.show(); return True

    def closeEvent(self, event): self._close_flow(); super().closeEvent(event)


class CurrentCriticalRewardDialog(QDialog):
    def __init__(self, item_id, parent=None):
        super().__init__(parent); self.setWindowTitle('关键藏品 · 取得条件与准确原文'); self.resize(1020, 780)
        layout = QVBoxLayout(self); self.panel = CurrentCriticalRewardPanel(item_id, self); layout.addWidget(self.panel)
    def closeEvent(self, event): self.panel._close_flow(); super().closeEvent(event)


def make_event_dialog(row, parent=None):
    if type(row) is not dict or type(row.get('item_id')) is not str: return None
    fresh = model.reference('relics', row['item_id'])
    if fresh is None or not any(row == r for r in fresh['rows']): return None
    return CurrentCriticalRewardDialog(row['item_id'], parent)
