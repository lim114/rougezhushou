"""Cave reader; document outcomes and exact-record alternatives stay separate."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QPushButton
from .documented_event_flow_view import DocumentedEventFlowPanel
from .ui_state import replace_text
from . import current_cave as model

class CurrentCavePanel(DocumentedEventFlowPanel):
    def __init__(self,target=None,parent=None):
        self.requested_choice=target.get('choice_id')if target else None;self.source_request=target.get('source_request')if target else None
        super().__init__('cave',target.get('scene_id')if target else None,parent,reference_model=model)
        row=QHBoxLayout();self.outcome_buttons=[QPushButton()for _ in range(4)]
        for button in self.outcome_buttons:row.addWidget(button);button.clicked.connect(lambda _=False,b=button:self.open_documented_outcome(b.property('sceneId')))
        self.layout().insertLayout(3,row)
        row=QHBoxLayout();self.followup_buttons=[QPushButton(),QPushButton()]
        for button in self.followup_buttons:row.addWidget(button);button.clicked.connect(lambda _=False,b=button:self.open_reference_followup(b.property('sceneId')))
        self.layout().insertLayout(4,row)
        if target and target['phase_needed']:
            self.scene.setCurrentIndex(0)
            if self.result:replace_text(self.player,model.phase_prompt(self.result,self.requested_choice),preserve=False)
        else:self._select_requested()
        self._sync_outcomes()

    def _fresh_reference(self):return model.reference(self.event_id,self.source_request)

    def _select_requested(self):
        if self.requested_choice is None:return
        for i in range(self.choices.count()):
            if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==self.requested_choice:self.choices.setCurrentRow(i);return

    def _scene_changed(self,*args,preserve=False):
        super()._scene_changed(*args,preserve=preserve)
        if not preserve:self._select_requested()
        if self.result and self.scene_id is None and self.requested_choice in self.result['choices']:
            replace_text(self.player,model.phase_prompt(self.result,self.requested_choice),preserve=preserve)

    def _sync_outcomes(self):
        if not hasattr(self,'outcome_buttons'):return
        c=model.choice_reference(self.result,self.scene_id,self.choice_id)if self.result else None;outcomes=c['documented_outcomes']if c else[]
        for i,button in enumerate(self.outcome_buttons):
            button.setVisible(i<len(outcomes));button.setEnabled(i<len(outcomes));button.setProperty('sceneId',outcomes[i]['scene_id']if i<len(outcomes)else None)
            if i<len(outcomes):button.setText('查看文献结果：'+model.scene_label(self.result,outcomes[i]['scene_id']).removeprefix('文献结果：'))

        if not hasattr(self,'followup_buttons'):return
        followups=c['reference_followups']if c else[]
        for i,button in enumerate(self.followup_buttons):
            button.setVisible(i<len(followups));button.setEnabled(i<len(followups));button.setProperty('sceneId',followups[i]['scene_id']if i<len(followups)else None)
            if i<len(followups):button.setText(('查看文献后续：'if followups[i]['basis']=='documented_followup'else'原记录也列：')+model.scene_label(self.result,followups[i]['scene_id']).removeprefix('文献后续：'))

    def _choice_changed(self,item,*args,preserve=False):
        super()._choice_changed(item,*args,preserve=preserve)
        self._sync_outcomes()
        if self.result is None:return
        c=model.choice_reference(self.result,self.scene_id,self.choice_id);hint=bool(c and c['battle_hint_without_exact_stage']);self.battle_button.setVisible(hint);self.battle_button.setEnabled(False);self.battle_button.setText('关卡对应尚未核验，暂不能打开固定地图');self._close_battle()

    def clear_reference(self):
        self.requested_choice=None;self.source_request=None;super().clear_reference();self._sync_outcomes()

    def open_documented_outcome(self,sid):
        if not self._recheck():return False
        c=model.choice_reference(self.result,self.scene_id,self.choice_id)
        if c is None or sid not in{x['scene_id']for x in c['documented_outcomes']}:return False
        self.scene.setCurrentIndex(self.scene.findData(sid));return True

    def open_reference_followup(self,sid):
        if not self._recheck():return False
        c=model.choice_reference(self.result,self.scene_id,self.choice_id)
        if c is None or sid not in{x['scene_id']for x in c['reference_followups']}:return False
        self.scene.setCurrentIndex(self.scene.findData(sid));return True

    def open_battle(self):
        if not self._recheck():return False
        self._close_battle();return False

class CurrentCaveDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('洞中宝 · 四类结果与不同后续');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentCavePanel(target,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
