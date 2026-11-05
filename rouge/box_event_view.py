"""Condition-aware current box-event reader; conditions stay local to this panel."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox,QDialog,QVBoxLayout,QHBoxLayout,QLabel
from . import box_event_reference as model
from .documented_event_flow_view import DocumentedEventFlowPanel


class BoxEventPanel(DocumentedEventFlowPanel):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__('box',scene_id,parent,reference_model=model, defer_initial_refresh=True)
        row=QHBoxLayout();row.addWidget(QLabel('用于本页对照：是否持有祭日之契'))
        self.covenant=QComboBox();self.covenant.setAccessibleName('本页对照的祭日之契持有状态')
        for text,value in(('尚未确认',None),('持有',True),('未持有',False)):self.covenant.addItem(text,value)
        row.addWidget(self.covenant,1);self.add_condition_row(row);self.covenant.currentIndexChanged.connect(self._condition_changed)
        self.refresh_reference(initial_scene=scene_id, initial=True)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break

    def _fresh_reference(self):
        return model.reference('box', self.covenant.currentData())

    def _condition_changed(self,*_):
        self._close_battle();self.refresh_reference()


from .player_window_frame import PlayerDialog


class BoxEventDialog(PlayerDialog):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('窥视箱中 · 条件、对话与相关作战');self.resize(760,600)
        layout=QVBoxLayout(self);self.panel=BoxEventPanel(scene_id,choice_id,self);layout.addWidget(self.panel)
        from .player_map_reader import readable
        readable(self)

    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
