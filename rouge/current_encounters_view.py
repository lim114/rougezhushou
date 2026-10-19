"""Whole encounter flows; required-tool control shown only where documented."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_encounters as model

class CurrentEncountersPanel(DocumentedEventFlowPanel):
    def __init__(self,event_id,scene_id=None,choice_id=None,parent=None):
        super().__init__(event_id,scene_id,parent,reference_model=model)
        if event_id=='黑诞':
            row=QHBoxLayout();row.addWidget(QLabel('仅本页对照：是否持有笼控器'));self.controller=QComboBox();self.controller.setAccessibleName('本页笼控器持有对照')
            for text,value in(('尚未确认',None),('持有',True),('未持有',False)):self.controller.addItem(text,value)
            row.addWidget(self.controller,1);self.layout().insertLayout(1,row);self.controller.currentIndexChanged.connect(self._condition_changed)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break

    def _fresh_reference(self):
        control=getattr(self,'controller',None);return model.reference(self.event_id,control.currentData()if control is not None else None)

    def _condition_changed(self,*_):self._close_battle();self.refresh_reference()

    def _choice_changed(self,item,*args,preserve=False):
        super()._choice_changed(item,*args,preserve=preserve)
        if self.result is None:return
        choice=model.choice_reference(self.result,self.scene_id,self.choice_id);hint=bool(choice and choice['has_documented_battle_link']);target=model.battle_target(self.result,self.scene_id,self.choice_id)if hint else None
        self.battle_button.setVisible(hint);self.battle_button.setEnabled(target is not None);self.battle_button.setText('查看本选项的作战配置与固定地图')
        if target is None:self._close_battle()
        if preserve and self.battle_dialog is not None and self.battle_dialog.isVisible():self.battle_dialog.panel.refresh_reference()

    def open_battle(self):
        if not self._recheck():return False
        target=model.battle_target(self.result,self.scene_id,self.choice_id)
        if target is None:self._close_battle();self.battle_button.setEnabled(False);return False
        from .current_event_battles_view import CurrentEventBattlesDialog
        self._close_battle();self.battle_dialog=CurrentEventBattlesDialog(target['event_id'],target['choice_id'],parent=self);self.battle_dialog.show();return True

class CurrentEncountersDialog(QDialog):
    def __init__(self,event_id,scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle(event_id+' · 完整对话、条件与代价');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentEncountersPanel(event_id,scene_id,choice_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
