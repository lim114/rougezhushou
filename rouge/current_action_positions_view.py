"""Manual action-to-map reader, using only explicit nominal cell references."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QSplitter, QTabWidget, QPlainTextEdit
from . import current_action_positions as model
from .current_map_position_view import CurrentTileGrid, CurrentOriginalCenters
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentActionPositionsPanel(QWidget):
    def __init__(self, stage_id, action_key, parent=None):
        super().__init__(parent); self.stage_id = stage_id; self.action_key = action_key
        self.result = None; self.entry_key = None; self.image_raw = None
        body = QVBoxLayout(self)
        notice = QLabel('选择本条记录的一处位置查看；只显示名义格及有依据的原图中心，不模拟实际出怪或寻路。')
        notice.setWordWrap(True); body.addWidget(notice)
        bar = QHBoxLayout(); self.combo = QComboBox(); self.refresh_button = QPushButton('重新核对本条位置')
        bar.addWidget(self.combo, 1); bar.addWidget(self.refresh_button); body.addLayout(bar)
        split = QSplitter(); self.grid = CurrentTileGrid(); self.original = CurrentOriginalCenters()
        split.addWidget(self.grid); split.addWidget(self.original); split.setSizes([500, 650]); body.addWidget(split, 2)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for widget in (self.player, self.technical): widget.setReadOnly(True)
        self.tabs.addTab(self.player, '位置和出现条件'); self.tabs.addTab(self.technical, '原始位置与来源'); body.addWidget(self.tabs, 1)
        self.combo.currentIndexChanged.connect(self._selected); self.refresh_button.clicked.connect(self.refresh_reference)
        self.refresh_reference()

    def clear_reference(self):
        self.result = None; self.entry_key = None; self.image_raw = None
        self.grid.set_result(None); self.original.set_image(None)
        blocked = self.combo.blockSignals(True); self.combo.clear(); self.combo.blockSignals(blocked); self.combo.setEnabled(False)
        replace_text(self.player, model.UNAVAILABLE, preserve=False); replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def set_reference(self, stage_id, action_key):
        if (stage_id, action_key) != (self.stage_id, self.action_key):
            self.clear_reference()
        self.stage_id = stage_id; self.action_key = action_key
        return self.refresh_reference()

    def refresh_reference(self):
        fresh = model.reference(self.stage_id, self.action_key)
        raw = model.positions.battle.version.image_bytes(fresh['grid']['image']) if fresh else None
        if fresh is None or raw is None: self.clear_reference(); return False
        keep = (self.result is not None and self.result['source_identity'] == fresh['source_identity']
                and self.result['stage_id'] == fresh['stage_id'] and self.result['action_key'] == fresh['action_key'])
        key = self.entry_key if keep else None; self.result = fresh; self.image_raw = raw
        blocked = self.combo.blockSignals(True); self.combo.clear(); self.combo.addItem('选择本条记录的位置', None)
        for entry in fresh['entries']: self.combo.addItem(model.entry_label(entry), entry['key'])
        self.combo.setEnabled(bool(fresh['entries'])); self.combo.setCurrentIndex(max(0, self.combo.findData(key))); self.combo.blockSignals(blocked)
        self._selected(preserve=keep); return self.result is not None

    def _selected(self, *_, preserve=False):
        if self.result is None: return
        key = self.combo.currentData(); keep = preserve and self.entry_key == key; self.entry_key = key
        entry = next((e for e in self.result['entries'] if e['key'] == key), None)
        cell = entry['cell'] if entry else None
        self.grid.set_result(self.result['grid'], (cell['row'], cell['col']) if cell else None)
        if not self.original.set_image(self.image_raw, entry['center'] if entry else None): self.clear_reference(); return
        replace_text(self.player, model.player_text(self.result, entry), preserve=keep)
        replace_text(self.technical, _technical_json({'reference': self.result, 'selected': entry}), preserve=keep)
        if not keep: self.tabs.setCurrentIndex(0)


class CurrentActionPositionsDialog(QDialog):
    def __init__(self, stage_id, action_key, parent=None):
        super().__init__(parent); self.setWindowTitle('出怪或装置 · 地图位置参考'); self.resize(1150, 800)
        layout = QVBoxLayout(self); self.panel = CurrentActionPositionsPanel(stage_id, action_key, self); layout.addWidget(self.panel)
