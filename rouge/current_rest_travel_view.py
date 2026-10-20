"""Player reader for rest/travel prose, retaining exact requested source."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_rest_travel as model

class CurrentRestTravelPanel(DocumentedEventFlowPanel):
    def __init__(self,event_id,target=None,parent=None):
        self.source_request=target.get('source_request')if target else None
        super().__init__(event_id,target.get('scene_id')if target else None,parent,reference_model=model)
        if target and target.get('choice_id'):
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==target['choice_id']:self.choices.setCurrentRow(i);break
    def _fresh_reference(self):return model.reference(self.event_id,self.source_request)
    def clear_reference(self):self.source_request=None;super().clear_reference()

class CurrentRestTravelDialog(QDialog):
    def __init__(self,event_id,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle(event_id+' · 选项、奖励与后续');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentRestTravelPanel(event_id,target,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
