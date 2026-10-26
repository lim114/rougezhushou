"""Resource-direction lookup; all context of the selected choice remains visible."""
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QListWidget, QListWidgetItem, QPlainTextEdit, QTabWidget, QPushButton
from . import current_event_item_uses as model
from .current_event_directory_view import make_event_dialog
from .ui_state import replace_text


class CurrentEventItemUsesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.result = None; self.selected_key = None; self.event_dialog = None; self.origins_dialog = None
        layout = QVBoxLayout(self); notice = QLabel(model.NOTICE); notice.setWordWrap(True); layout.addWidget(notice)
        row = QHBoxLayout(); self.query = QLineEdit(); self.query.setPlaceholderText('搜索物品、事件或用途原文'); self.query.setAccessibleName('具名物品与用途原文搜索')
        self.item = QComboBox(); self.item.setAccessibleName('要查看的具名物品'); self.item.addItem('全部已证物品', None)
        self.role = QComboBox(); self.role.setAccessibleName('原文说明的使用方式'); self.role.addItem('全部使用方式', None)
        self.item.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        for key, label in model.ROLES: self.role.addItem(label, key)
        row.addWidget(self.query, 2); row.addWidget(self.item, 1); row.addWidget(self.role, 1); layout.addLayout(row)
        self.refresh_button = QPushButton('重新核对物品用途'); layout.addWidget(self.refresh_button); self.count = QLabel(); self.count.setWordWrap(True); layout.addWidget(self.count)
        self.entries = QListWidget(); self.entries.setMaximumHeight(180); self.entries.setAccessibleName('具名物品的准确事件用途'); layout.addWidget(self.entries)
        self.open_button = QPushButton('查看这一条的完整条件与对话'); layout.addWidget(self.open_button)
        self.origins_button = QPushButton('查看这件物品已有的已证取得方式'); self.origins_button.hide(); layout.addWidget(self.origins_button)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for widget, label in ((self.player, '用途与条件'), (self.technical, '完整原文与依据')):
            widget.setReadOnly(True); self.tabs.addTab(widget, label)
        layout.addWidget(self.tabs, 1)
        self.query.textChanged.connect(self._filters_changed); self.item.currentIndexChanged.connect(self._filters_changed)
        self.role.currentIndexChanged.connect(self._filters_changed); self.refresh_button.clicked.connect(self.refresh_reference)
        self.entries.currentItemChanged.connect(self._selected); self.open_button.clicked.connect(self.open_event); self.origins_button.clicked.connect(self.open_origins); self.refresh_reference()

    def _close_event(self):
        if self.event_dialog is not None:
            self.event_dialog.panel.clear_reference(); self.event_dialog.close()
        self.event_dialog = None

    @staticmethod
    def _clear_origins(dialog):
        child = getattr(dialog.panel, 'event_dialog', None)
        if child is not None: child.panel.clear_reference(); child.close()
        dialog.panel._clear()

    def _close_origins(self):
        if self.origins_dialog is not None:
            self._clear_origins(self.origins_dialog); self.origins_dialog.close()
        self.origins_dialog = None

    def clear_reference(self):
        self._close_event(); self._close_origins(); self.result = None; self.selected_key = None
        blocked = self.entries.blockSignals(True); self.entries.clear(); self.entries.blockSignals(blocked)
        self.open_button.setEnabled(False); self.count.setText('资料暂未核对；不沿用旧数值。')
        self.origins_button.hide(); self.origins_button.setEnabled(False)
        replace_text(self.player, model.UNAVAILABLE, preserve=False); replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def _filters(self): return {'item_id': self.item.currentData(), 'role': self.role.currentData(), 'query': self.query.text()}

    def refresh_reference(self, *_):
        fresh = model.reference(**self._filters())
        if fresh is None: self.clear_reference(); return False
        same = self.result is not None and model.directory.same(self.result['source_identity'], fresh['source_identity'])
        selected = self.selected_key if same else None
        if not same: self._close_event(); self._close_origins()
        if self.item.count() == 1:
            blocked = self.item.blockSignals(True); seen = set()
            for row in fresh['data']['rows']:
                if row['item_id'] in seen: continue
                seen.add(row['item_id']); self.item.addItem(row['item']['name'], row['item_id'])
            self.item.blockSignals(blocked)
        self.result = fresh; blocked = self.entries.blockSignals(True); self.entries.clear()
        for row in fresh['rows']:
            text = row['item']['name'] + ' · ' + dict(model.ROLES)[row['role']] + ' · ' + row['event_title'] + ' · ' + row['entry']['title']
            item = QListWidgetItem(text); item.setData(Qt.ItemDataRole.UserRole, row['id']); self.entries.addItem(item)
            if row['id'] == selected: self.entries.setCurrentItem(item)
        self.entries.blockSignals(blocked)
        if selected is None: self.entries.setCurrentRow(-1)
        self.count.setText('当前找到' + str(len(fresh['rows'])) + '条具名用途记录；不是库存、消耗次数或完整用途表。')
        self._selected(self.entries.currentItem(), preserve=same)
        if same and self.event_dialog is not None and self.event_dialog.isVisible():
            if not self.event_dialog.panel.refresh_reference(): self._close_event()
        if same and self.origins_dialog is not None and self.origins_dialog.isVisible():
            if not self.origins_dialog.panel.refresh_reference(): self._close_origins()
        return True

    def _filters_changed(self, *_):
        self._close_event(); self._close_origins(); self.selected_key = None; self.refresh_reference()

    def _selected(self, item, *_, preserve=False):
        if self.result is None: return
        key = item.data(Qt.ItemDataRole.UserRole) if item else None; keep = preserve and key == self.selected_key
        if not keep: self._close_event(); self._close_origins()
        self.selected_key = key; row = next((r for r in self.result['rows'] if r['id'] == key), None); self.result['selected'] = row
        self.open_button.setEnabled(row is not None)
        target = model.acquisition_target(self.result) if row else None
        self.origins_button.setVisible(target is not None); self.origins_button.setEnabled(target is not None)
        if target is None: self._close_origins()
        replace_text(self.player, model.player_text(self.result), preserve=keep)
        replace_text(self.technical, json.dumps(row or {'scope': model.NOTICE}, ensure_ascii=False, indent=2), preserve=keep)
        if not keep: self.tabs.setCurrentIndex(0)

    def open_event(self):
        target = model.destination(self.result)
        if target is None: self.clear_reference(); return False
        self._close_event(); self.event_dialog = make_event_dialog(target, self)
        if self.event_dialog is None: self.clear_reference(); return False
        self.event_dialog.finished.connect(lambda _result, child=self.event_dialog: child.panel.clear_reference())
        self.event_dialog.show(); return True

    def open_origins(self):
        target = model.acquisition_target(self.result)
        if target is None: self._close_origins(); self.origins_button.hide(); return False
        from .current_reward_origins_view import CurrentRewardOriginsDialog
        self._close_origins(); self.origins_dialog = CurrentRewardOriginsDialog(target['category'], target['item_id'], self)
        if self.origins_dialog.panel.result is None: self._close_origins(); self.origins_button.hide(); return False
        self.origins_dialog.finished.connect(lambda _result, child=self.origins_dialog: self._clear_origins(child))
        self.origins_dialog.show(); return True

    def closeEvent(self, event): self._close_event(); self._close_origins(); super().closeEvent(event)


class CurrentEventItemUsesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle('物品用途 · 持有条件、交付与消耗'); self.resize(1180, 850)
        layout = QVBoxLayout(self); self.panel = CurrentEventItemUsesPanel(self); layout.addWidget(self.panel)
    def closeEvent(self, event): self.panel.clear_reference(); super().closeEvent(event)
    def reject(self): self.panel.clear_reference(); super().reject()
