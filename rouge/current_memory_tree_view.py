"""Read-only, event-specific resource declarations for the memory tree."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QSpinBox,QComboBox
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_memory_tree as model

class CurrentMemoryTreePanel(DocumentedEventFlowPanel):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__('memorytree',scene_id,parent,reference_model=model, defer_initial_refresh=True)
        row=QHBoxLayout();row.addWidget(QLabel('仅本页条件对照：'))
        for name,label in [('action_points','行动力'),('processed_parts','加工品数量')]:
            row.addWidget(QLabel(label));box=QSpinBox();box.setRange(-1,99999);box.setSpecialValueText('未知');box.setValue(-1);box.setAccessibleName('仅本页'+label+'对照');setattr(self,name,box);row.addWidget(box);box.valueChanged.connect(self._conditions_changed)
        self.add_condition_row(row);row=QHBoxLayout()
        for name,label in [('source_key','源私钥'),('controller','笼控器')]:
            row.addWidget(QLabel('仅本页持有：'+label));box=QComboBox();box.setAccessibleName('仅本页'+label+'持有对照')
            for text,value in [('尚未确认',None),('持有',True),('未持有',False)]:box.addItem(text,value)
            setattr(self,name,box);row.addWidget(box);box.currentIndexChanged.connect(self._conditions_changed)
        self.add_condition_row(row)
        self.refresh_reference(initial_scene=scene_id, initial=True)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break
    def _fresh_reference(self):
        ap,parts=self.action_points.value(),self.processed_parts.value()
        return model.reference(self.event_id, None if ap<0 else ap, None if parts<0 else parts,
                               self.source_key.currentData(),self.controller.currentData())
    def _conditions_changed(self,*_):self.refresh_reference()

from .player_window_frame import PlayerDialog


class CurrentMemoryTreeDialog(PlayerDialog):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('愈创之心 · 五种选项与追忆');self.resize(760,600);layout=QVBoxLayout(self);self.panel=CurrentMemoryTreePanel(scene_id,choice_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
