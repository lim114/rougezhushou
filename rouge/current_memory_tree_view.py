"""Read-only, event-specific resource declarations for the memory tree."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QSpinBox,QComboBox
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_memory_tree as model

class CurrentMemoryTreePanel(DocumentedEventFlowPanel):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__('memorytree',scene_id,parent,reference_model=model)
        row=QHBoxLayout();row.addWidget(QLabel('仅本页条件对照：'))
        for name,label in [('action_points','行动力'),('processed_parts','加工品数量')]:
            row.addWidget(QLabel(label));box=QSpinBox();box.setRange(-1,99999);box.setSpecialValueText('未知');box.setValue(-1);box.setAccessibleName('仅本页'+label+'对照');setattr(self,name,box);row.addWidget(box);box.valueChanged.connect(self._conditions_changed)
        self.layout().insertLayout(1,row);row=QHBoxLayout()
        for name,label in [('source_key','源私钥'),('controller','笼控器')]:
            row.addWidget(QLabel('仅本页持有：'+label));box=QComboBox();box.setAccessibleName('仅本页'+label+'持有对照')
            for text,value in [('尚未确认',None),('持有',True),('未持有',False)]:box.addItem(text,value)
            setattr(self,name,box);row.addWidget(box);box.currentIndexChanged.connect(self._conditions_changed)
        self.layout().insertLayout(2,row)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break
    def _fresh_reference(self):
        def count(name):
            w=getattr(self,name,None);return None if w is None or w.value()<0 else w.value()
        def held(name):
            w=getattr(self,name,None);return None if w is None else w.currentData()
        return model.reference(self.event_id,count('action_points'),count('processed_parts'),held('source_key'),held('controller'))
    def _conditions_changed(self,*_):self.refresh_reference()

class CurrentMemoryTreeDialog(QDialog):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('愈创之心 · 五种选项与追忆');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentMemoryTreePanel(scene_id,choice_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
