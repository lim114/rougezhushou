"""Lake-stage reader; separate result buttons never select a real random result."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QPushButton
from .documented_event_flow_view import DocumentedEventFlowPanel
from .ui_state import replace_text
from . import current_lake as model

class CurrentLakePanel(DocumentedEventFlowPanel):
    def __init__(self,target=None,parent=None):
        self.requested_choice=target.get('choice_id')if target else None
        super().__init__('lake',target.get('scene_id')if target else None,parent,reference_model=model)
        row=QHBoxLayout();self.outcome_buttons=[QPushButton(),QPushButton()]
        for button in self.outcome_buttons:row.addWidget(button);button.clicked.connect(lambda _=False,b=button:self.open_documented_outcome(b.property('sceneId')))
        self.layout().insertLayout(3,row)
        if target and target['phase_needed']:
            self.scene.setCurrentIndex(0)
            if self.result:replace_text(self.player,model.phase_prompt(self.result,self.requested_choice),preserve=False)
        else:self._select_requested()
        self._sync_outcomes()

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
            if i<len(outcomes):button.setText('查看文献结果：'+model.scene_label(self.result,outcomes[i]['scene_id']).removeprefix('随机结果：'))

    def _choice_changed(self,item,*args,preserve=False):
        super()._choice_changed(item,*args,preserve=preserve)
        self._sync_outcomes()
        if self.result is None:return
        c=model.choice_reference(self.result,self.scene_id,self.choice_id);hint=bool(c and c['has_documented_battle_link']);target=model.battle_target(self.result,self.scene_id,self.choice_id)if hint else None
        self.battle_button.setVisible(hint);self.battle_button.setEnabled(target is not None);self.battle_button.setText('查看本选项的作战配置与固定地图')
        if target is None:self._close_battle()
        if preserve and self.battle_dialog is not None and self.battle_dialog.isVisible():self.battle_dialog.panel.refresh_reference()

    def clear_reference(self):
        self.requested_choice=None;super().clear_reference();self._sync_outcomes()

    def open_documented_outcome(self,sid):
        if not self._recheck():return False
        c=model.choice_reference(self.result,self.scene_id,self.choice_id)
        if c is None or sid not in{x['scene_id']for x in c['documented_outcomes']}:return False
        self.scene.setCurrentIndex(self.scene.findData(sid));return True

    def open_battle(self):
        if not self._recheck():return False
        target=model.battle_target(self.result,self.scene_id,self.choice_id)
        if target is None:self._close_battle();self.battle_button.setEnabled(False);return False
        from .current_event_battles_view import CurrentEventBattlesDialog
        self._close_battle();self.battle_dialog=CurrentEventBattlesDialog(target['event_id'],target['choice_id'],parent=self);self.battle_dialog.show();return True

class CurrentLakeDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('湖中仙女 · 阶段、投入与两种结果');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentLakePanel(target,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
