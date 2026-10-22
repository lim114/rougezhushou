"""Player-readable acquisition list with explicit, separately owned event windows."""
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPlainTextEdit, QTabWidget, QPushButton
from . import current_reward_origins as model
from .ui_state import replace_text

class CurrentRewardOriginsPanel(QWidget):
    def __init__(self, category, item_id, parent=None):
        super().__init__(parent); self.category = category; self.item_id = item_id; self.result = None; self.event_dialog = None
        layout = QVBoxLayout(self); self.notice = QLabel(model.NOTICE); self.notice.setWordWrap(True); layout.addWidget(self.notice)
        self.entries = QListWidget(); self.entries.setAccessibleName('物品已核对的取得选项'); layout.addWidget(self.entries)
        self.open_button = QPushButton('查看这条选项的条件与后续'); layout.addWidget(self.open_button)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for reader, label in ((self.player, '取得方式'), (self.technical, '来源原件')):
            reader.setReadOnly(True); self.tabs.addTab(reader, label)
        layout.addWidget(self.tabs, 1); self.entries.currentItemChanged.connect(self._selected); self.open_button.clicked.connect(self.open_event)
        self.refresh_reference()

    def _close_event(self):
        if self.event_dialog is not None: self.event_dialog.close()
        self.event_dialog = None

    def _clear(self):
        self._close_event(); self.result = None
        blocked = self.entries.blockSignals(True); self.entries.clear(); self.entries.blockSignals(blocked)
        self.open_button.setEnabled(False); replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def refresh_reference(self):
        fresh = model.reference(self.category, self.item_id)
        if fresh is None: self._clear(); return False
        same = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        selected = self.entries.currentItem().data(Qt.ItemDataRole.UserRole) if same and self.entries.currentItem() else None
        if not same: self._close_event()
        self.result = fresh; blocked = self.entries.blockSignals(True); self.entries.clear()
        for row in fresh['rows']:
            item = QListWidgetItem(row['event_title'] + ' · ' + row['choice']['title']); item.setData(Qt.ItemDataRole.UserRole, row['key']); self.entries.addItem(item)
            if row['key'] == selected: self.entries.setCurrentItem(item)
        self.entries.blockSignals(blocked); self._render(selected, same)
        if same and self.event_dialog is not None and self.event_dialog.isVisible(): self.event_dialog.panel.refresh_reference()
        return True

    def _render(self, key, preserve):
        self.open_button.setEnabled(key is not None)
        replace_text(self.player, model.player_text(self.result, key), preserve=preserve)
        row = next((r for r in self.result['rows'] if r['key'] == key), None)
        replace_text(self.technical, json.dumps(row or {'scope': model.NOTICE}, ensure_ascii=False, indent=2), preserve=preserve)

    def _selected(self, item, *_):
        if self.result is None: return
        self._close_event(); self._render(item.data(Qt.ItemDataRole.UserRole) if item else None, False)

    def open_event(self):
        old = self.result; selected = self.entries.currentItem()
        if old is None or selected is None: return False
        key = selected.data(Qt.ItemDataRole.UserRole); fresh = model.reference(self.category, self.item_id)
        if fresh is None or fresh != old: self._clear(); return False
        row = next((r for r in fresh['rows'] if r['key'] == key), None)
        if row is None: self._clear(); return False
        self._close_event()
        if row['reader'] == 'memory':
            from .current_memory_tree_view import CurrentMemoryTreeDialog
            self.event_dialog = CurrentMemoryTreeDialog(row['scene_id'], row['choice_id'], self)
        elif row['reader'] == 'dog':
            from .current_lone_dog_view import CurrentLoneDogDialog
            self.event_dialog = CurrentLoneDogDialog(row['scene_id'], row['choice_id'], self)
        elif row['reader'] == 'vine':
            from .current_vine_events_view import CurrentVineEventsDialog
            self.event_dialog = CurrentVineEventsDialog(row['event_id'], row['scene_id'], row['choice_id'], self)
        else: return False
        if self.event_dialog.panel.result is None: self._close_event(); self._clear(); return False
        self.event_dialog.show(); return True

    def closeEvent(self, event): self._close_event(); super().closeEvent(event)

class CurrentRewardOriginsDialog(QDialog):
    def __init__(self, category, item_id, parent=None):
        super().__init__(parent); self.setWindowTitle('物品取得方式 · 已核对的事件选项'); self.resize(1050, 780)
        layout = QVBoxLayout(self); self.panel = CurrentRewardOriginsPanel(category, item_id, self); layout.addWidget(self.panel)
    def closeEvent(self, event): self.panel._close_event(); super().closeEvent(event)
