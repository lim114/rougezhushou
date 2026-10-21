"""Read only lone-dog choices; no game movement or map marking."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_lone_dog as model
class CurrentLoneDogPanel(DocumentedEventFlowPanel):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__('dog',scene_id,parent,reference_model=model)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break
class CurrentLoneDogDialog(QDialog):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('独活 · 同行者与前往、标记的区别');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentLoneDogPanel(scene_id,choice_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
