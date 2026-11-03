"""Resource-direction lookup; all context of the selected choice remains visible."""
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QListWidget, QListWidgetItem, QPlainTextEdit, QTabWidget, QPushButton
from . import current_event_resources as model
from .current_event_directory_view import make_event_dialog
from .ui_state import replace_text


class CurrentEventResourcesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.result = None; self.selected_key = None; self.event_dialog = None
        layout = QVBoxLayout(self); notice = QLabel(model.NOTICE); notice.setWordWrap(True); layout.addWidget(notice)
        row = QHBoxLayout(); self.query = QLineEdit(); self.query.setPlaceholderText('搜索事件、选项或变化原文'); self.query.setAccessibleName('事件资源原文搜索')
        self.resource = QComboBox(); self.resource.setAccessibleName('想查找的资源'); self.resource.addItem('全部资源', None)
        self.kind = QComboBox(); self.kind.setAccessibleName('变化方向与物品奖励'); self.kind.addItem('全部获得与代价', None)
        for key, label in model.RESOURCES: self.resource.addItem(label, key)
        for key, label in model.KINDS: self.kind.addItem(label, key)
        row.addWidget(self.query, 2); row.addWidget(self.resource, 1); row.addWidget(self.kind, 1); layout.addLayout(row)
        self.refresh_button = QPushButton('重新核对资源原文'); layout.addWidget(self.refresh_button); self.count = QLabel(); self.count.setWordWrap(True); layout.addWidget(self.count)
        self.entries = QListWidget(); self.entries.setMaximumHeight(180); self.entries.setAccessibleName('准确事件中的资源变化记录'); layout.addWidget(self.entries)
        self.open_button = QPushButton('查看这一条的完整条件与对话'); layout.addWidget(self.open_button)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for widget, label in ((self.player, '收益与代价'), (self.technical, '完整原文与依据')):
            widget.setReadOnly(True); self.tabs.addTab(widget, label)
        layout.addWidget(self.tabs, 1)
        self.query.textChanged.connect(self._filters_changed); self.resource.currentIndexChanged.connect(self._filters_changed)
        self.kind.currentIndexChanged.connect(self._filters_changed); self.refresh_button.clicked.connect(self.refresh_reference)
        self.entries.currentItemChanged.connect(self._selected); self.open_button.clicked.connect(self.open_event); self.refresh_reference()

    def _close_event(self):
        if self.event_dialog is not None:
            self.event_dialog.panel.clear_reference(); self.event_dialog.close()
        self.event_dialog = None

    def clear_reference(self):
        self._close_event(); self.result = None; self.selected_key = None
        blocked = self.entries.blockSignals(True); self.entries.clear(); self.entries.blockSignals(blocked)
        self.open_button.setEnabled(False); self.count.setText('资料暂未核对；不沿用旧数值。')
        replace_text(self.player, model.UNAVAILABLE, preserve=False); replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def _filters(self): return {'resource': self.resource.currentData(), 'kind': self.kind.currentData(), 'query': self.query.text()}

    def refresh_reference(self, *_):
        fresh = model.reference(**self._filters())
        if fresh is None: self.clear_reference(); return False
        same = self.result is not None and model.directory.same(self.result['source_identity'], fresh['source_identity'])
        selected = self.selected_key if same else None
        if not same: self._close_event()
        self.result = fresh; blocked = self.entries.blockSignals(True); self.entries.clear()
        for row in fresh['rows']:
            text = row['event_title'] + ' · ' + row['entry']['scene_label'] + ' · ' + row['entry']['title']
            item = QListWidgetItem(text); item.setData(Qt.ItemDataRole.UserRole, row['id']); self.entries.addItem(item)
            if row['id'] == selected: self.entries.setCurrentItem(item)
        self.entries.blockSignals(blocked)
        if selected is None: self.entries.setCurrentRow(-1)
        self.count.setText('当前找到' + str(len(fresh['rows'])) + '条准确来源记录；不是本局可用数量、出现次数或总收益。')
        self._selected(self.entries.currentItem(), preserve=same)
        if same and self.event_dialog is not None and self.event_dialog.isVisible():
            if not self.event_dialog.panel.refresh_reference(): self._close_event()
        return True

    def _filters_changed(self, *_):
        self._close_event(); self.selected_key = None; self.refresh_reference()

    def _selected(self, item, *_, preserve=False):
        if self.result is None: return
        key = item.data(Qt.ItemDataRole.UserRole) if item else None; keep = preserve and key == self.selected_key
        if not keep: self._close_event()
        self.selected_key = key; row = next((r for r in self.result['rows'] if r['id'] == key), None); self.result['selected'] = row
        self.open_button.setEnabled(row is not None)
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

    def closeEvent(self, event): self._close_event(); super().closeEvent(event)


class CurrentEventResourcesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle('事件资源变化 · 收益、代价与准确条件'); self.resize(1180, 850)
        layout = QVBoxLayout(self); self.panel = CurrentEventResourcesPanel(self); layout.addWidget(self.panel)
    def closeEvent(self, event): self.panel.clear_reference(); super().closeEvent(event)
    def reject(self): self.panel.clear_reference(); super().reject()
