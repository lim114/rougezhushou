"""Current exact enemy entry into four existing full documentary workflows."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTabWidget, QPlainTextEdit)
from . import current_boss_documents as model
from .branch_choice import BranchChoice
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentBossDocumentsPanel(QWidget):
    enemy_requested = Signal(str)

    def __init__(self, stage_id, enemy_key=None, parent=None):
        super().__init__(parent)
        self.stage_id = stage_id; self.entry_key = enemy_key
        self.result = None; self.selected_key = None; self._view_key = None
        self._initial = True; self.map_dialog = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(model.NOTICE); self.notice.setWordWrap(True); layout.addWidget(self.notice)
        self.refresh_button = QPushButton('重新核对本关完整机制资料'); layout.addWidget(self.refresh_button)
        self.enemy_combo = QComboBox(); self.enemy_combo.setAccessibleName('本关具有完整机制文献的准确敌人条目')
        self.enemies = BranchChoice(self.enemy_combo, [], overview_label='总览（本关完整文献）',
            placeholder='请选择准确敌人条目；不表示实际出现或当前形态')
        layout.addWidget(self.enemies)
        self.portrait = QLabel(); self.portrait.setFixedHeight(70); self.portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.portrait)
        self.topic = QComboBox(); self.topic.setAccessibleName('完整机制文献的阅读分支'); layout.addWidget(self.topic)
        bar = QHBoxLayout(); self.related = QComboBox(); self.related.setAccessibleName('本关明确关联的准确敌人条目')
        self.related_button = QPushButton('在本关敌人页查看'); bar.addWidget(self.related, 1); bar.addWidget(self.related_button)
        layout.addLayout(bar)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for area, title in ((self.player, '机制、条件与限制'), (self.technical, '准确来源与新旧差异')):
            area.setReadOnly(True); self.tabs.addTab(area, title)
        layout.addWidget(self.tabs, 1)
        self.map_button = QPushButton('查看这关固定地图（不标记实际首领位置）'); layout.addWidget(self.map_button)
        self.status = QLabel(); self.status.setWordWrap(True); layout.addWidget(self.status)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.enemy_combo.currentIndexChanged.connect(self._enemy_changed)
        self.topic.currentIndexChanged.connect(self._render)
        self.related_button.clicked.connect(self.follow_entity)
        self.map_button.clicked.connect(self.open_map)
        self.refresh_reference()

    def _close_map(self):
        if self.map_dialog is not None:
            self.map_dialog.panel.clear_reference(); self.map_dialog.close()
        self.map_dialog = None

    def _map_finished(self, child):
        child.panel.clear_reference()
        if self.map_dialog is child: self.map_dialog = None

    def clear_reference(self):
        self._close_map(); self.result = None; self.selected_key = None; self.entry_key = None
        self._view_key = None; self._initial = False; self.enemies.set_groups([], emit=False)
        for control in (self.topic, self.related):
            blocked = control.blockSignals(True); control.clear(); control.blockSignals(blocked)
        self.topic.setEnabled(False); self.related_button.setEnabled(False)
        self.map_button.setEnabled(False); self.portrait.clear(); self.portrait.hide()
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0); self.status.clear()

    def refresh_reference(self, *_):
        fresh = model.reference(self.stage_id, self.entry_key)
        if fresh is None: self.clear_reference(); return False
        keep = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        selected = self.enemy_combo.currentData() if keep else None
        if self._initial: selected = self.entry_key; self._initial = False
        self.result = fresh
        entries = []
        for row in fresh['rows']:
            icon = QIcon(); picture = QPixmap(); raw = model.battle.picture_bytes(row['enemy']['portrait'])
            if raw and picture.loadFromData(raw, 'PNG'): icon = QIcon(picture)
            entries.append((row['enemy']['name'], row['enemy_key'], icon))
        block = self.enemy_combo.blockSignals(True)
        self.enemies.set_groups([(model.LABELS[fresh['family']], entries)], emit=False)
        if selected is not None: self.enemies.select_value(selected, emit=False)
        else: self.enemy_combo.setCurrentIndex(0)
        self.enemy_combo.blockSignals(block); self._enemy_changed(preserve=keep)
        if self.map_dialog is not None:
            mapped = model.map_reference(fresh)
            if mapped is None: self._close_map(); self.status.setText('这关固定地图无法重新核对，旧地图已关闭；文献仍可阅读。')
            elif not self.map_dialog.panel.refresh_reference(): self._close_map()
            elif self.map_dialog.panel.result != mapped['map']:
                self._close_map(); self.status.setText('地图重新读取的资料与本关不一致，旧地图已清除；完整文献仍可阅读。')
        return True

    def _enemy_changed(self, *_, preserve=False):
        key = self.enemy_combo.currentData(); keep = preserve and key == self.selected_key
        old_topic = self.topic.currentData() if keep else None
        old_related = self.related.currentData() if keep else None
        if key != self.selected_key: self._close_map()
        self.selected_key = key
        block = self.topic.blockSignals(True); self.topic.clear()
        self.topic.addItem('完整总览（保留全部招式、条件和差异）', None)
        for row in model.topics(self.result, key): self.topic.addItem(row['name'], row['id'])
        self.topic.setCurrentIndex(max(0, self.topic.findData(old_topic))); self.topic.blockSignals(block)
        self.topic.setEnabled(key is not None)
        block = self.related.blockSignals(True); self.related.clear()
        self.related.addItem('选择本关明确列出的关联条目', None)
        for request in model.related_entities(self.result, key): self.related.addItem(request['name'], request)
        self.related.setCurrentIndex(max(0, self.related.findData(old_related))); self.related.blockSignals(block)
        self.related_button.setEnabled(self.related.count() > 1)
        self.map_button.setEnabled(self.result is not None)
        self.portrait.clear(); row = model.entity(self.result, key); self.portrait.setVisible(row is not None)
        if row is not None:
            picture = QPixmap(); raw = model.battle.picture_bytes(row['enemy']['portrait'])
            if raw and picture.loadFromData(raw, 'PNG'):
                self.portrait.setPixmap(picture.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else: self.portrait.setText('这份准确敌人条目没有可核对图片，不替换成同名图。')
        self.status.clear(); self._render()

    def _render(self, *_):
        topic = self.topic.currentData()
        identity = (self.result['source_identity'], self.selected_key, topic) if self.result else None
        keep = identity == self._view_key
        replace_text(self.player, model.player_text(self.result, self.selected_key, topic), preserve=keep)
        technical = {'stage_id': self.stage_id, 'current_source_identity': self.result['source_identity'],
            'selected_current_reference_and_authentic_legacy_document': model.entity(self.result, self.selected_key),
            'current_level_source': self.result['source'], 'complete_level_qualification': self.result['qualification'],
            'fixed_document_revisions': self.result['documents'], 'related_exact_current_references': self.result['related'],
            'actual_phase': None, 'actual_skill_time': None, 'expected_stats': None,
            'actual_server_verified': False, 'numeric_model_added': False, 'run_updated': False} if self.result else {}
        replace_text(self.technical, _technical_json(technical), preserve=keep)
        if not keep: self.tabs.setCurrentIndex(0)
        self._view_key = identity

    def follow_entity(self):
        request = model.resolve_entity(self.result, self.selected_key, self.related.currentData())
        if request is None:
            self.clear_reference(); self.status.setText('关联入口无法核对，旧内容已清除；恢复后请手动重新选择。'); return False
        self.enemy_requested.emit(request['enemy_key']); self.status.clear(); return True

    def open_map(self):
        mapped = model.map_reference(self.result); self._close_map()
        if mapped is None:
            self.status.setText('这份准确固定地图无法核对，旧地图已关闭；不借用同名或其他版本地图。'); return False
        from .current_map_position_view import CurrentMapPositionDialog
        child = CurrentMapPositionDialog(mapped['stage_id'], self)
        if child.panel.result is None or child.panel.result != mapped['map']:
            child.panel.clear_reference(); child.close(); return False
        child.finished.connect(lambda _result: self._map_finished(child))
        self.map_dialog = child; self.status.clear(); child.show(); return True

    def closeEvent(self, event):
        self.clear_reference(); super().closeEvent(event)


class CurrentBossDocumentsDialog(QDialog):
    def __init__(self, stage_id, enemy_key=None, parent=None):
        super().__init__(parent); self.setWindowTitle('本关完整机制 · 形态、循环与退场条件'); self.resize(1100, 850)
        layout = QVBoxLayout(self); self.panel = CurrentBossDocumentsPanel(stage_id, enemy_key, self); layout.addWidget(self.panel)

    def done(self, result):
        self.panel.clear_reference(); super().done(result)

    def closeEvent(self, event):
        self.panel.clear_reference(); super().closeEvent(event)
