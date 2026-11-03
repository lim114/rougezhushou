"""Manual exact guest-boss reader with owned state and separate source text."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QPlainTextEdit, QTabWidget)
from . import current_guest_crystals as model
from .branch_choice import BranchChoice
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentGuestCrystalsPanel(QWidget):
    def __init__(self, stage_id, enemy_key=None, parent=None):
        super().__init__(parent)
        self.stage_id = stage_id; self.entry_key = enemy_key; self.result = None
        self.selected_key = None; self._view_key = None; self._initial = True
        layout = QVBoxLayout(self)
        self.notice = QLabel(model.NOTICE); self.notice.setWordWrap(True); layout.addWidget(self.notice)
        self.refresh_button = QPushButton('重新核对本关机制资料'); layout.addWidget(self.refresh_button)
        self.entity_combo = QComboBox()
        self.entity_combo.setAccessibleName('本关准确首领')
        self.entities = BranchChoice(self.entity_combo, [], overview_label='总览（本关相关首领）',
                                     placeholder='请选择本关的准确首领')
        layout.addWidget(self.entities)
        self.portrait = QLabel(); self.portrait.setFixedHeight(74)
        self.portrait.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.portrait)
        bar = QHBoxLayout(); self.topic = QComboBox(); self.topic.setAccessibleName('当前实体的机制分支')
        self.related = QComboBox(); self.related.setAccessibleName('本关独立关联实体')
        self.related_button = QPushButton('查看这份关联实体')
        bar.addWidget(self.topic, 1); bar.addWidget(self.related, 1); bar.addWidget(self.related_button); layout.addLayout(bar)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for area, label in ((self.player, '怎样触发、效果与限制'), (self.technical, '准确来源与完整文献')):
            area.setReadOnly(True); self.tabs.addTab(area, label)
        layout.addWidget(self.tabs, 1)
        self.map_dialog=None
        self.map_button=QPushButton('查看本关固定地图与格子');layout.addWidget(self.map_button);self.map_button.clicked.connect(self.open_map)
        self.status = QLabel(); self.status.setWordWrap(True); layout.addWidget(self.status)
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.entity_combo.currentIndexChanged.connect(self._entity_changed)
        self.topic.currentIndexChanged.connect(self._topic_changed)
        self.related_button.clicked.connect(self.follow_related)
        self.refresh_reference()

    def clear_reference(self):
        self.close_owned_map();self.map_button.setEnabled(False)
        self.result = None; self.selected_key = None; self._view_key = None
        self.entry_key = None; self._initial = False
        self.entities.set_groups([], emit=False)
        for control in (self.topic, self.related):
            block = control.blockSignals(True); control.clear(); control.blockSignals(block)
        self.related_button.setEnabled(False); self.portrait.clear(); self.portrait.hide(); self.status.clear()
        replace_text(self.player, model.UNAVAILABLE, preserve=False)
        replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def refresh_reference(self, *_):
        fresh = model.reference(self.stage_id, self.entry_key)
        if fresh is None: self.clear_reference(); return False
        keep = self.result is not None and self.result['source_identity'] == fresh['source_identity']
        key = self.entity_combo.currentData() if keep else None
        if self._initial: key = self.entry_key; self._initial = False
        self.result = fresh
        map_target=model.map_target(fresh);self.map_button.setEnabled(map_target is not None)
        child=getattr(self,'map_dialog',None)
        if map_target is None:self.close_owned_map()
        elif child is not None and child.isVisible():
            child.panel.refresh_reference()
            if child.panel.result is None or child.panel.result.get('current_level_key')!=fresh['level_key']:self.close_owned_map()
        groups = []
        for actor_kind, label in (('boss', '本关首领'),):
            items = []
            for row in fresh['rows']:
                icon = QIcon(); picture = QPixmap(); raw = model.battle.picture_bytes(row['enemy']['portrait'])
                if raw and picture.loadFromData(raw, 'PNG'): icon = QIcon(picture)
                items.append((row['enemy']['name'] + ' · 引用' + str(row['reference_index'] + 1), row['key'], icon))
            groups.append((label, items))
        block = self.entity_combo.blockSignals(True); self.entities.set_groups(groups, emit=False)
        if key is not None: self.entities.select_value(key, emit=False)
        self.entity_combo.blockSignals(block)
        self._entity_changed(preserve=keep)
        return True

    def _entity_changed(self, *_, preserve=False):
        key = self.entity_combo.currentData(); keep = preserve and key == self.selected_key
        old_topic = self.topic.currentData() if keep else None
        old_related = self.related.currentData() if keep else None
        self.selected_key = key
        for control in (self.topic, self.related): control.blockSignals(True); control.clear()
        self.topic.addItem('先看要点与适用限制', None)
        for topic, label in model.topics(self.result, key): self.topic.addItem(label, topic)
        self.topic.setCurrentIndex(max(0, self.topic.findData(old_topic)))
        self.related.addItem('选择本关的另一份准确实体', None)
        for request in model.related_entities(self.result, key): self.related.addItem(request['name'], request)
        self.related.setCurrentIndex(max(0, self.related.findData(old_related)))
        for control in (self.topic, self.related): control.blockSignals(False)
        self.related_button.setEnabled(key is not None and self.related.count() > 1)
        row = model.entity(self.result, key); self.portrait.clear(); self.portrait.setVisible(row is not None)
        if row:
            picture = QPixmap(); raw = model.battle.picture_bytes(row['enemy']['portrait'])
            if raw and picture.loadFromData(raw, 'PNG'):
                self.portrait.setPixmap(picture.scaled(74, 74, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else: self.portrait.setText('此准确引用的图片无法核对；不借用同名或其它关卡的图片。')
        self.status.clear(); self._topic_changed()

    def _topic_changed(self, *_):
        row = model.entity(self.result, self.selected_key); topic = self.topic.currentData()
        identity = (self.result['source_identity'], self.stage_id, self.selected_key, topic) if self.result else None
        keep = identity == self._view_key
        replace_text(self.player, model.player_text(self.result, self.selected_key, topic), preserve=keep)
        technical = {'stage_id': self.stage_id, 'level_key': self.result['level_key'],
                     'source_identity': self.result['source_identity'], 'current_reference': row,
                     'current_complete_stage': self.result['data']['originals']['stages'][self.stage_id],
                     'selected_document_card': model.selected_card(self.result, self.selected_key, topic),
                     'complete_actor_source_cards': self.result['data']['materials'].get(row['actor']) if row else None,
                     'retained_documentary_scope':model.technical_scope_notes(self.result,self.selected_key,topic),
                     'actual_form':None,'actual_shield':None,'actual_partner_retired':None, 'actual_skill_time': None, 'numeric_model_added': False} if self.result else {}
        replace_text(self.technical, _technical_json(technical), preserve=keep)
        if not keep: self.tabs.setCurrentIndex(0)
        self._view_key = identity

    def close_owned_map(self):
        child=getattr(self,'map_dialog',None)
        if child is not None:child.panel.clear_reference();child.close()
        self.map_dialog=None

    def open_map(self):
        target=model.map_target(self.result)
        if target is None:self.clear_reference();return False
        from .current_map_position_view import CurrentMapPositionDialog
        class OwnedMapDialog(CurrentMapPositionDialog):
            def closeEvent(self,event):self.panel.clear_reference();super().closeEvent(event)
            def reject(self):self.panel.clear_reference();super().reject()
        self.close_owned_map();self.map_dialog=OwnedMapDialog(target['stage_id'],self)
        result=self.map_dialog.panel.result
        if result is None or result.get('current_level_key')!=self.result['level_key']:
            self.close_owned_map();return False
        self.map_dialog.show();return True

    def follow_related(self):
        request = self.related.currentData()
        target = model.resolve_related(self.result, self.selected_key, request)
        if target is None:
            self.clear_reference(); self.status.setText('关联入口无法重新核对，旧实体和招式已清除；恢复后请手动选择。'); return False
        if not self.entities.select_value(target['enemy_key']): return False
        return True


class CurrentGuestCrystalsDialog(QDialog):
    def __init__(self, stage_id, enemy_key=None, parent=None):
        super().__init__(parent); self.setWindowTitle('晶矿惊蝗 · 双晶兽的护盾与捕杀'); self.resize(1060, 840)
        layout = QVBoxLayout(self); self.panel = CurrentGuestCrystalsPanel(stage_id, enemy_key, self); layout.addWidget(self.panel)

    def closeEvent(self,event):
        self.panel.clear_reference();super().closeEvent(event)

    def reject(self):
        self.panel.clear_reference();super().reject()
