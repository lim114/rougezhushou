"""Resource-event flow with gold controls only on fixed-gold events."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QSpinBox
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_resource_events as model

class CurrentResourceEventsPanel(DocumentedEventFlowPanel):
    def __init__(self,event_id,scene_id=None,choice_id=None,parent=None):
        super().__init__(event_id,scene_id,parent,reference_model=model)
        if event_id in model.GOLD_EVENTS:
            row=QHBoxLayout();row.addWidget(QLabel('仅本页对照：源石锭'));self.gold=QSpinBox();self.gold.setRange(-1,99999);self.gold.setSpecialValueText('未知');self.gold.setValue(-1);self.gold.setAccessibleName('仅本页源石锭支付对照');row.addWidget(self.gold);self.layout().insertLayout(1,row);self.gold.valueChanged.connect(self._gold_changed)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break
    def _fresh_reference(self):
        control=getattr(self,'gold',None);return model.reference(self.event_id,None if control is None or control.value()<0 else control.value())
    def _gold_changed(self,*_):self.refresh_reference()

class CurrentResourceEventsDialog(QDialog):
    def __init__(self,event_id,scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle(event_id+' · 选项、代价与奖励');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentResourceEventsPanel(event_id,scene_id,choice_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
