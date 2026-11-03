"""Six-fog document reader and separate exact-original views without parent guessing."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QWidget,QHBoxLayout,QLabel,QSpinBox
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_portal as model

class CurrentPortalPanel(DocumentedEventFlowPanel):
    def __init__(self,target=None,parent=None):
        self.source_request=target['source_request']if target else None
        initial=('source-scene'if self.source_request['category']=='scenes'else'source-choice')if self.source_request else None
        super().__init__('portal',initial,parent,reference_model=model)
        self.part_controls=QWidget();row=QHBoxLayout(self.part_controls);row.setContentsMargins(0,0,0,0);row.addWidget(QLabel('仅本页加工品件数（不等于零件总数）：'));self.parts=QSpinBox();self.parts.setRange(-1,99999);self.parts.setSpecialValueText('尚未确认');self.parts.setValue(-1);self.parts.setAccessibleName('仅本页加工品件数');row.addWidget(self.parts);self.layout().insertWidget(1,self.part_controls);self.parts.valueChanged.connect(self._conditions_changed)
        if self.source_request and self.source_request['category']=='choices':self.choices.setCurrentRow(0)
        self._update_controls()
    def _fresh_reference(self):
        w=getattr(self,'parts',None);return model.reference('portal',None if w is None or w.value()<0 else w.value(),self.source_request)
    def _conditions_changed(self,*_):self.refresh_reference()
    def _choice_changed(self,item,*args,preserve=False):
        super()._choice_changed(item,*args,preserve=preserve);self._update_controls()
    def clear_reference(self):super().clear_reference();self._update_controls()
    def _update_controls(self):
        if not hasattr(self,'part_controls'):return
        c=model.choice_reference(self.result,self.scene_id,self.choice_id)if self.result else None;self.part_controls.setVisible(bool(c and c['inventory_rule']))

class CurrentPortalDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('溯源 · 六种雾色、加工品与明确后续');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentPortalPanel(target,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
