"""Step-by-step reference for three documented events; owned read-only windows."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                               QListWidget, QListWidgetItem, QPlainTextEdit, QTabWidget, QPushButton)
from . import documented_event_flows as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class DocumentedEventFlowPanel(QWidget):
    def __init__(self, event_id, scene_id=None, parent=None):
        super().__init__(parent)
        self.event_id = event_id; self.result = None; self.scene_id = None; self.choice_id = None
        self.battle_dialog = None
        layout = QVBoxLayout(self)
        notice = QLabel('逐步查阅文献中的选项、结果和后续；不是本局已经走过的流程，完整出现前置仍请核对。')
        notice.setWordWrap(True); layout.addWidget(notice)
        row = QHBoxLayout(); self.scene = QComboBox(); self.scene.setAccessibleName('文献中的事件情景')
        self.refresh_button = QPushButton('重新核对流程'); row.addWidget(self.scene, 1); row.addWidget(self.refresh_button); layout.addLayout(row)
        self.choices = QListWidget(); self.choices.setAccessibleName('当前文献情景的选项'); self.choices.setMaximumHeight(115); layout.addWidget(self.choices)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for reader in (self.player, self.technical): reader.setReadOnly(True)
        self.tabs.addTab(self.player, '选项与结果'); self.tabs.addTab(self.technical, '资料与依据'); layout.addWidget(self.tabs, 1)
        row = QHBoxLayout(); self.start_button = QPushButton('回到最初情景'); self.next_button = QPushButton('查看后续情景')
        self.battle_button = QPushButton('查看灰坑固定作战资料')
        for button in (self.start_button, self.next_button, self.battle_button): row.addWidget(button)
        layout.addLayout(row)
        self.scene.currentIndexChanged.connect(self._scene_changed); self.choices.currentItemChanged.connect(self._choice_changed)
        self.refresh_button.clicked.connect(self.refresh_reference); self.start_button.clicked.connect(self.go_start)
        self.next_button.clicked.connect(self.follow_scene); self.battle_button.clicked.connect(self.open_battle)
        self.refresh_reference(initial_scene=scene_id, initial=True)

    def _close_battle(self):
        if self.battle_dialog is not None: self.battle_dialog.close()

    def clear_reference(self):
        self._close_battle(); self.result = None; self.scene_id = None; self.choice_id = None
        for widget in (self.scene, self.choices):
            blocked = widget.blockSignals(True); widget.clear(); widget.blockSignals(blocked)
        self.scene.setEnabled(False)
        for button in (self.start_button, self.next_button, self.battle_button): button.hide(); button.setEnabled(False)
        replace_text(self.player, model.UNAVAILABLE, preserve=False); replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def refresh_reference(self, *_, initial_scene=None, initial=False):
        fresh = model.reference(self.event_id)
        if fresh is None: self.clear_reference(); return False
        keep = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        selected = self.scene_id if keep else None
        if initial:
            selected = initial_scene if initial_scene in fresh['scenes'] else fresh['event']['entry_scene_id']
        if not keep: self._close_battle()
        self.result = fresh; blocked = self.scene.blockSignals(True); self.scene.clear(); self.scene.addItem('请选择情景', None)
        for sid in fresh['event']['scene_ids']: self.scene.addItem(model.scene_label(fresh, sid), sid)
        self.scene.setCurrentIndex(max(0, self.scene.findData(selected))); self.scene.setEnabled(True); self.scene.blockSignals(blocked)
        self._scene_changed(preserve=keep); return True

    def _scene_changed(self, *_, preserve=False):
        sid = self.scene.currentData(); keep = preserve and self.scene_id == sid
        selected = self.choice_id if keep else None
        if not keep: self._close_battle()
        self.scene_id = sid; blocked = self.choices.blockSignals(True); self.choices.clear()
        scene = self.result['scenes'].get(sid) if self.result else None
        for cid in scene['choice_ids'] if scene else []:
            original = self.result['data']['originals']['choices'][cid]
            item = QListWidgetItem(model.version._plain(original['title'])); item.setData(Qt.ItemDataRole.UserRole, cid); self.choices.addItem(item)
            if cid == selected: self.choices.setCurrentItem(item)
        self.choices.blockSignals(blocked)
        if selected is None: self.choices.setCurrentRow(-1)
        self._choice_changed(self.choices.currentItem(), preserve=keep)

    def _choice_changed(self, item, *_, preserve=False):
        cid = item.data(Qt.ItemDataRole.UserRole) if item else None
        keep = preserve and cid == self.choice_id
        if not keep: self._close_battle()
        self.choice_id = cid
        if self.result is None: return
        choice = model.choice_reference(self.result, self.scene_id, cid)
        replace_text(self.player, model.player_text(self.result, self.scene_id, cid), preserve=keep)
        replace_text(self.technical, _technical_json({'reference': self.result, 'scene': self.scene_id, 'choice': choice}), preserve=keep)
        self.start_button.setVisible(self.scene_id != self.result['event']['entry_scene_id']); self.start_button.setEnabled(True)
        self.next_button.setVisible(bool(choice and choice['next_scene_id'])); self.next_button.setEnabled(bool(choice and choice['next_scene_id']))
        self.battle_button.setVisible(bool(choice and choice['stage_ids'])); self.battle_button.setEnabled(bool(choice and choice['stage_ids']))
        if not keep: self.tabs.setCurrentIndex(0)

    def _recheck(self):
        if self.result is None or model.reference(self.event_id) != self.result:
            self.clear_reference(); return False
        return True

    def go_start(self):
        if not self._recheck(): return False
        self.scene.setCurrentIndex(self.scene.findData(self.result['event']['entry_scene_id'])); return True

    def follow_scene(self):
        if not self._recheck(): return False
        choice = model.choice_reference(self.result, self.scene_id, self.choice_id)
        if choice is None or choice['next_scene_id'] is None: return False
        self.scene.setCurrentIndex(self.scene.findData(choice['next_scene_id'])); return True

    def open_battle(self):
        if not self._recheck(): return False
        choice = model.choice_reference(self.result, self.scene_id, self.choice_id)
        if choice is None or choice['stage_ids'] != ['ro6_s_1']: return False
        from .current_battle_view import CurrentBattleDialog
        self._close_battle(); self.battle_dialog = CurrentBattleDialog('ro6_s_1', self); self.battle_dialog.show(); return True

    def closeEvent(self, event):
        self._close_battle(); super().closeEvent(event)


class DocumentedEventFlowDialog(QDialog):
    def __init__(self, event_id, scene_id=None, parent=None):
        super().__init__(parent); self.setWindowTitle('事件选项、奖励与后续'); self.resize(1050, 810)
        layout = QVBoxLayout(self); self.panel = DocumentedEventFlowPanel(event_id, scene_id, self); layout.addWidget(self.panel)

    def closeEvent(self, event):
        self.panel._close_battle(); super().closeEvent(event)
