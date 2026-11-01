"""Current exact Elbert/independent Firebrand reader; no game or chat operations."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon,QPixmap
from PySide6.QtWidgets import (QWidget,QDialog,QVBoxLayout,QHBoxLayout,QLabel,
                              QComboBox,QPushButton,QPlainTextEdit,QTabWidget)
from . import current_elbert_reference as model
from .branch_choice import BranchChoice,OVERVIEW
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class CurrentElbertPanel(QWidget):
    def __init__(self,stage_id,enemy_key=None,parent=None):
        super().__init__(parent)
        self.stage_id=stage_id;self.entry_key=enemy_key;self._initial=True
        self.base=self.result=self.source_identity=self.selected_key=self._view_key=None
        self.related_request=None
        layout=QVBoxLayout(self);self.notice=QLabel(model.NOTICE);self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.refresh_button=QPushButton('重新核对本关机制资料');layout.addWidget(self.refresh_button)
        self.entity_combo=QComboBox();self.entity_combo.setAccessibleName('本关首领与独立火种')
        self.entities=BranchChoice(self.entity_combo,[],overview_label='总览（本关相关实体）',placeholder='请选择本关首领或火种')
        layout.addWidget(self.entities)
        self.portrait=QLabel();self.portrait.setFixedHeight(70);self.portrait.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(self.portrait)
        bar=QHBoxLayout();self.topic=QComboBox();self.topic.setAccessibleName('所选实体的机制分支')
        self.related_button=QPushButton('查看本关的关联实体');bar.addWidget(self.topic,1);bar.addWidget(self.related_button);layout.addLayout(bar)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.technical=QPlainTextEdit()
        for area,label in((self.player,'条件、效果与本关区别'),(self.technical,'完整机制原文与准确来源')):
            area.setReadOnly(True);self.tabs.addTab(area,label)
        layout.addWidget(self.tabs,1);self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.refresh_button.clicked.connect(self.refresh_reference);self.entity_combo.currentIndexChanged.connect(self._entity_changed)
        self.topic.currentIndexChanged.connect(self._topic_changed);self.related_button.clicked.connect(self.follow_related)
        self.refresh_reference()

    def clear_reference(self):
        self.base=self.result=self.source_identity=self.selected_key=self._view_key=None
        self.related_request=None;self.entry_key=None;self._initial=False
        self.entities.set_groups([],emit=False)
        blocked=self.topic.blockSignals(True)
        try:self.topic.clear()
        finally:self.topic.blockSignals(blocked)
        self.topic.hide();self.related_button.hide();self.related_button.setEnabled(False)
        self.portrait.clear();self.portrait.hide();self.status.clear()
        replace_text(self.player,model.UNAVAILABLE,preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)

    def refresh_reference(self,*_):
        fresh=model.reference(self.stage_id,self.entry_key if self._initial else None)
        if fresh is None:self.clear_reference();return False
        keep=self.base is not None and self.source_identity==fresh['source_identity']
        key=self.entity_combo.currentData()if keep else None
        if self._initial:key=self.entry_key;self._initial=False
        self.base=fresh;self.source_identity=fresh['source_identity']
        groups=[]
        for kind,label in(('boss','本关首领'),('fire','独立火种')):
            items=[]
            for row in fresh['entities']:
                if row['kind']!=kind:continue
                pix=QPixmap();icon=QIcon();raw=model.battle.picture_bytes(fresh['portraits'][self.stage_id].get(row['key']))
                if raw and pix.loadFromData(raw,'PNG'):icon=QIcon(pix)
                items.append((row['name'],row['key'],icon))
            groups.append((label,items))
        blocked=self.entity_combo.blockSignals(True)
        try:
            if not keep:
                self.entity_combo.clear();self.entities.select_branch(OVERVIEW)
            self.entities.set_groups(groups,emit=False)
            if key is not None:self.entities.select_value(key,emit=False)
        finally:self.entity_combo.blockSignals(blocked)
        self._entity_changed(preserve=keep);return True

    def _entity_changed(self,*_,preserve=False):
        if self.base is None:return
        key=self.entity_combo.currentData();keep=preserve and key==self.selected_key
        old_topic=self.topic.currentData()if keep else None;row=model.entity(self.base,key)
        self.selected_key=key;blocked=self.topic.blockSignals(True)
        try:
            self.topic.clear()
            for topic,label in model.CARDS[row['kind']]if row else():self.topic.addItem(label,topic)
            if old_topic is not None:self.topic.setCurrentIndex(max(0,self.topic.findData(old_topic)))
        finally:self.topic.blockSignals(blocked)
        self.topic.setVisible(row is not None)
        related=model.related_entities(self.base,key);self.related_request=related[0]if len(related)==1 else None
        self.related_button.setVisible(self.related_request is not None);self.related_button.setEnabled(self.related_request is not None)
        if self.related_request:self.related_button.setText('查看本关的'+self.related_request['name'])
        self.portrait.clear();self.portrait.setVisible(row is not None)
        if row:
            pix=QPixmap();raw=model.battle.picture_bytes(self.base['portraits'][self.stage_id].get(row['key']))
            if raw and pix.loadFromData(raw,'PNG'):self.portrait.setPixmap(pix.scaled(70,70,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:self.portrait.setText('本关这只敌人的独立图片尚未取得；不借用同名敌人或其它图标。')
        self.status.clear();self._topic_changed()

    def _topic_changed(self,*_):
        if self.base is None:return
        self.result=model.view_result(self.base,self.selected_key,self.topic.currentData())
        if self.result is None:self.clear_reference();return
        identity=(self.source_identity,self.stage_id,self.selected_key,self.topic.currentData());keep=identity==self._view_key
        replace_text(self.player,model.player_text(self.result),preserve=keep)
        row=self.result['selected'];card=model.selected_card(self.result,self.selected_key)
        original={'source_identity':self.source_identity,'battle_source_identity':self.result['battle_source_identity'],
                  'exact_stage':self.result['stage'],'exact_selected_entity':row,
                  'complete_selected_mechanism_card':card,
                  'full_original_game_and_documentary_prose_kept_separately':True,
                  'actual_fire_direction':None,'actual_staff_position':None,'actual_damage':None,
                  'actual_clock':None,'run_updated':False,'numerical_model_applied':False}
        replace_text(self.technical,_technical_json(original),preserve=keep)
        if not keep:self.tabs.setCurrentIndex(0)
        self._view_key=identity

    def follow_related(self):
        target=model.resolve_related(self.base,self.selected_key,self.related_request)
        if target is None:
            self.clear_reference();self.status.setText('关联入口不能重新核对，旧实体资料已清除；恢复后请手动重新选择。');return False
        return self.entities.select_value(target['enemy_key'])


class CurrentElbertDialog(QDialog):
    def __init__(self,stage_id,enemy_key=None,parent=None):
        super().__init__(parent);self.setWindowTitle('埃尔伯特与火种 · 本关机制');self.resize(1080,825)
        self.panel=CurrentElbertPanel(stage_id,enemy_key,self);QVBoxLayout(self).addWidget(self.panel)

    def done(self,result):
        self.panel.clear_reference();super().done(result)

    def closeEvent(self,event):
        self.panel.clear_reference();super().closeEvent(event)
