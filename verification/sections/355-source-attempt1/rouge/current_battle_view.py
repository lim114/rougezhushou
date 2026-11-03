"""Manual current-version battle reader, with real category branches."""
import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap,QIcon
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QPlainTextEdit,QPushButton,QTabWidget,QSplitter,QListWidget,QListWidgetItem,QDialog
from . import current_battle_reference as model,expansion_reference as version
from .branch_choice import BranchChoice
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentBattlePanel(QWidget):
    def __init__(self,stage_id,parent=None):
        super().__init__(parent);self.stage_id=stage_id;self.result=None;self.source_identity=None;self.enemy_key=None;self.action_key=None
        layout=QVBoxLayout(self);self.notice=QLabel(model.NOTICE);self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.refresh_button=QPushButton('重新核对本关资料');layout.addWidget(self.refresh_button)
        self.tabs=QTabWidget();layout.addWidget(self.tabs,1)
        overview=QWidget();body=QVBoxLayout(overview);self.map_image=QLabel();self.map_image.setMinimumSize(300,160);self.map_image.setAlignment(Qt.AlignmentFlag.AlignCenter);body.addWidget(self.map_image)
        self.position_button=QPushButton('查看地图格子与已核对的原图位置');body.addWidget(self.position_button);self.position_button.clicked.connect(self.open_map_positions)
        self.event_origins_button=QPushButton('查看与本关对应的事件选项');body.addWidget(self.event_origins_button);self.event_origins_button.clicked.connect(self.open_event_origins)
        self.summary=QPlainTextEdit();self.summary.setReadOnly(True);body.addWidget(self.summary,1);self.tabs.addTab(overview,'地图与关卡')
        enemies=QWidget();body=QVBoxLayout(enemies);self.enemy_combo=QComboBox();self.enemy_choices=BranchChoice(self.enemy_combo,[],overview_label='总览（本关候选）',placeholder='请选择敌人或关联实体');body.addWidget(self.enemy_choices)
        self.enemy_portrait=QLabel();self.enemy_portrait.setMinimumSize(85,85);self.enemy_portrait.setAlignment(Qt.AlignmentFlag.AlignCenter);body.addWidget(self.enemy_portrait)
        self.enemy_player=QPlainTextEdit();self.enemy_player.setReadOnly(True);body.addWidget(self.enemy_player,1);self.tabs.addTab(enemies,'敌人和机制')
        wave=QWidget();body=QVBoxLayout(wave);self.queue_kind=QComboBox();self.queue_kind.addItem('总览（全部条目）',None);self.queue_kind.addItem('主波次','main');self.queue_kind.addItem('条件分支','branch');body.addWidget(self.queue_kind)
        split=QSplitter();self.actions=QListWidget();split.addWidget(self.actions);self.action_player=QPlainTextEdit();self.action_player.setReadOnly(True);split.addWidget(self.action_player);split.setSizes([350,650]);body.addWidget(split,1)
        self.action_position_button=QPushButton('在地图上查看本条位置参考');body.addWidget(self.action_position_button);self.action_position_button.clicked.connect(self.open_action_positions);self.tabs.addTab(wave,'出怪与条件')
        self.spawn_candidates_button=QPushButton('查看出怪候选与关联记录')
        body.addWidget(self.spawn_candidates_button);self.spawn_candidates_button.clicked.connect(self.open_spawn_candidates)
        self.technical=QPlainTextEdit();self.technical.setReadOnly(True);self.tabs.addTab(self.technical,'完整原值与来源')
        from .current_reward_view import CurrentRewardPanel
        self.rewards=CurrentRewardPanel(stage_id);self.tabs.addTab(self.rewards,'奖励与条件');self.rewards.actionSelected.connect(self._reward_action_selected)
        from .current_settlement_view import CurrentSettlementPanel
        self.settlement=CurrentSettlementPanel(stage_id);self.tabs.addTab(self.settlement,'通关基础奖励')
        self.refresh_button.clicked.connect(self.refresh_reference);self.enemy_combo.currentIndexChanged.connect(self._enemy_changed);self.queue_kind.currentIndexChanged.connect(self._actions_changed);self.actions.currentItemChanged.connect(self._action_changed)
        self.refresh_reference()

    def _clear(self):
        self._close_spawn_candidates();self.spawn_candidates_button.setEnabled(False)
        self._close_event_origins();self.event_origins_button.setEnabled(False);self.event_origins_button.hide()
        self._close_map_positions();self.position_button.setEnabled(False)
        self.action_position_button.setEnabled(False)
        self.result=None;self.source_identity=None;self.enemy_key=None;self.action_key=None
        self.map_image.clear();self.map_image.setText(model.UNAVAILABLE);self.enemy_portrait.clear()
        self.enemy_choices.set_groups([],emit=False);blocked=self.actions.blockSignals(True);self.actions.clear();self.actions.blockSignals(blocked)
        for widget in(self.summary,self.enemy_player,self.action_player,self.technical):replace_text(widget,'',preserve=False)
        self.rewards.clear_reference()
        self.settlement.clear_reference()

    def refresh_reference(self):
        fresh=model.stage_reference(self.stage_id)
        if fresh is None:self._clear();return False
        keep=self.result is not None and self.source_identity==fresh['source_identity']and self.result['id']==fresh['id']
        if not keep:self._close_event_origins();self._close_spawn_candidates()
        old_enemy=self.enemy_combo.currentData()if keep else None
        self.result=fresh;self.source_identity=fresh['source_identity']
        from .current_event_battles import stage_has_reference
        has_origins=stage_has_reference(self.stage_id);self.event_origins_button.setVisible(has_origins);self.event_origins_button.setEnabled(has_origins)
        origin=getattr(self,'event_origins_dialog',None)
        if keep and origin is not None and origin.isVisible():origin.panel.refresh_reference()
        self.position_button.setEnabled(True)
        self.spawn_candidates_button.setEnabled(True)
        self.settlement.refresh_reference()
        replace_text(self.summary,model.summary_text(fresh),preserve=keep);replace_text(self.technical,_technical_json(fresh),preserve=keep)
        raw=version.image_bytes(fresh['image']);pix=QPixmap()
        if raw and pix.loadFromData(raw,'PNG'):self.map_image.setPixmap(pix.scaled(760,235,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        else:self.map_image.clear();self.map_image.setText('本关固定原图无法核对，不借用同名关卡图片。')
        groups=[]
        for tier,label in [*model.TIERS.items(),(None,'类别未确认')]:
            items=[]
            for e in fresh['enemies']:
                if e['tier']!=tier:continue
                icon=QIcon();raw=model.picture_bytes(e['portrait']);picture=QPixmap()
                if raw and picture.loadFromData(raw,'PNG'):icon=QIcon(picture)
                items.append((e['name']+' · 引用资料'+str(e['reference_index']+1),e['key'],icon))
            groups.append((label,items))
        blocked=self.enemy_combo.blockSignals(True);self.enemy_choices.set_groups(groups,emit=False)
        if old_enemy is not None:self.enemy_choices.select_value(old_enemy,emit=False)
        self.enemy_combo.blockSignals(blocked);self._enemy_changed(preserve=keep);self._actions_changed(preserve=keep)
        if not keep:self.tabs.setCurrentIndex(0)
        self.rewards.refresh_reference()
        for name in ('position_dialog','action_position_dialog','spawn_candidates_dialog'):
            dialog=getattr(self,name,None)
            if dialog is not None and dialog.isVisible():dialog.panel.refresh_reference()
        return True

    def _close_spawn_candidates(self):
        dialog=getattr(self,'spawn_candidates_dialog',None)
        if dialog is not None:dialog.close()

    def _spawn_source_invalidated(self):
        dialog=getattr(self,'action_position_dialog',None)
        if dialog is not None:dialog.close()

    def _spawn_action_selected(self,key):
        dialog=getattr(self,'spawn_candidates_dialog',None)
        if self.result is None or dialog is None or dialog.panel.result is None:return False
        if dialog.panel.result['battle_source_identity']!=self.result['source_identity']:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        action=next((a for a in self.result['actions']if a['key']==key),None)
        if action is None:return False
        self.queue_kind.setCurrentIndex(self.queue_kind.findData(action['queue']['kind']))
        for i in range(self.actions.count()):
            if self.actions.item(i).data(Qt.ItemDataRole.UserRole)==key:self.actions.setCurrentRow(i);self.tabs.setCurrentIndex(2);return True
        return False

    def _spawn_position_requested(self,key):
        return self._spawn_action_selected(key) and self.open_action_positions()

    def open_spawn_candidates(self):
        if self.result is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_spawn_candidates_view import CurrentSpawnCandidatesDialog
        self._close_spawn_candidates();self.spawn_candidates_dialog=CurrentSpawnCandidatesDialog(self.stage_id,parent=self)
        panel=self.spawn_candidates_dialog.panel
        if panel.result is None:self._close_spawn_candidates();return False
        panel.actionSelected.connect(self._spawn_action_selected)
        panel.actionPositionRequested.connect(self._spawn_position_requested)
        panel.sourceInvalidated.connect(self._spawn_source_invalidated)
        self.spawn_candidates_dialog.show();return True

    def _reward_action_selected(self,key):
        if self.result is None or self.rewards.result is None or self.result['source_identity']!=self.rewards.result['battle_source_identity']:return False
        action=next((a for a in self.result['actions']if a['key']==key),None)
        if action is None:return False
        self.queue_kind.setCurrentIndex(self.queue_kind.findData(action['queue']['kind']))
        for i in range(self.actions.count()):
            if self.actions.item(i).data(Qt.ItemDataRole.UserRole)==key:self.actions.setCurrentRow(i);self.tabs.setCurrentIndex(2);return True
        return False

    def _enemy_changed(self,*_,preserve=False):
        key=self.enemy_combo.currentData();enemy=next((e for e in self.result['enemies']if e['key']==key),None)if self.result else None
        keep=preserve and key==self.enemy_key;self.enemy_key=key
        replace_text(self.enemy_player,model.enemy_text(enemy)if enemy else'请选择敌人或关联实体。',preserve=keep)
        self.enemy_portrait.clear();pix=QPixmap();raw=model.picture_bytes(enemy['portrait'])if enemy else None
        if raw and pix.loadFromData(raw,'PNG'):self.enemy_portrait.setPixmap(pix.scaled(90,90,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        else:self.enemy_portrait.setText('此精确引用未取得图片。'if enemy else'')

    def _actions_changed(self,*_,preserve=False):
        old=self.actions.currentItem();key=old.data(Qt.ItemDataRole.UserRole)if old and preserve else None
        blocked=self.actions.blockSignals(True);self.actions.clear();kind=self.queue_kind.currentData()
        for action in self.result['actions']if self.result else[]:
            if kind is not None and action['queue']['kind']!=kind:continue
            item=QListWidgetItem(model.action_label(action));item.setData(Qt.ItemDataRole.UserRole,action['key']);self.actions.addItem(item)
            if key==action['key']:self.actions.setCurrentItem(item)
        self.actions.blockSignals(blocked)
        if key is None:self.actions.setCurrentRow(-1)
        self._action_changed(self.actions.currentItem(),preserve=preserve)

    def _action_changed(self,item,*_,preserve=False):
        key=item.data(Qt.ItemDataRole.UserRole)if item else None
        action=next((a for a in self.result['actions']if a['key']==key),None)if self.result else None
        if key!=self.action_key:
            dialog=getattr(self,'action_position_dialog',None)
            if dialog is not None:dialog.close()
        keep=preserve and key==self.action_key;self.action_key=key
        replace_text(self.action_player,model.action_text(action)if action else'请选择一条出怪、装置或条件分支资料。',preserve=keep)
        self.action_position_button.setEnabled(action is not None and action['raw'].get('actionType')in('SPAWN','ACTIVATE_PREDEFINED'))

    def _close_map_positions(self):
        for name in ('position_dialog','action_position_dialog'):
            dialog=getattr(self,name,None)
            if dialog is not None:dialog.close()

    def open_action_positions(self):
        if self.result is None or self.action_key is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_action_positions_view import CurrentActionPositionsDialog
        dialog=getattr(self,'action_position_dialog',None)
        if dialog is not None:dialog.close()
        self.action_position_dialog=CurrentActionPositionsDialog(self.stage_id,self.action_key,self)
        self.action_position_dialog.show();return True

    def open_map_positions(self):
        if self.result is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_map_position_view import CurrentMapPositionDialog
        self._close_map_positions();self.position_dialog=CurrentMapPositionDialog(self.stage_id,self);self.position_dialog.show();return True

    def _close_event_origins(self):
        dialog=getattr(self,'event_origins_dialog',None)
        if dialog is not None:dialog.close()

    def open_event_origins(self):
        if self.result is None:return False
        if model.stage_reference(self.stage_id)!=self.result:self._clear();return False
        from .current_event_battles import stage_has_reference
        if not stage_has_reference(self.stage_id):self._close_event_origins();self.event_origins_button.hide();return False
        from .current_event_battles_view import CurrentEventBattlesDialog
        self._close_event_origins();self.event_origins_dialog=CurrentEventBattlesDialog(stage_id=self.stage_id,parent=self);self.event_origins_dialog.show();return True

    def closeEvent(self,event):self._close_spawn_candidates();self._close_map_positions();self._close_event_origins();super().closeEvent(event)


class CurrentBattleDialog(QDialog):
    def __init__(self,stage_id,parent=None):
        super().__init__(parent);self.setWindowTitle('固定关卡预览');self.resize(1120,820)
        layout=QVBoxLayout(self);self.panel=CurrentBattlePanel(stage_id);layout.addWidget(self.panel)

    def closeEvent(self,event):self.panel._close_spawn_candidates();self.panel._close_map_positions();self.panel._close_event_origins();super().closeEvent(event)
