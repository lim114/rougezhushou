"""Departure reading and branch-specific return item; never a recruitment action."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QWidget,QLabel
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_scout as model

class CurrentScoutPanel(DocumentedEventFlowPanel):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__('scout',scene_id,parent,reference_model=model)
        self.return_card=QWidget();row=QHBoxLayout(self.return_card);row.setContentsMargins(0,0,0,0)
        self.return_icon=QLabel();self.return_icon.setAccessibleName('探索源头归来参考：怦然信标图片');row.addWidget(self.return_icon)
        self.return_label=QLabel('探索源头归来参考 · 怦然信标（不是已领取）');row.addWidget(self.return_label);row.addStretch(1);self.layout().insertWidget(1,self.return_card)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break
        self._update_return_card()
    def _choice_changed(self,item,*args,preserve=False):
        super()._choice_changed(item,*args,preserve=preserve);self._update_return_card()
    def clear_reference(self):
        super().clear_reference();self._update_return_card()
    def _update_return_card(self):
        if not hasattr(self,'return_card'):return
        show=bool(self.result and model.shows_return_item(self.result,self.scene_id,self.choice_id));self.return_card.setVisible(show);self.return_icon.clear()
        if show:
            raw=model.icon_bytes();pixmap=QPixmap()
            if raw is not None and pixmap.loadFromData(raw):self.return_icon.setPixmap(pixmap.scaled(52,52,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:self.return_icon.setText('怦然信标（图片暂缺）')

class CurrentScoutDialog(QDialog):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('未涉足之树 · 派出、确认与归来');self.resize(1100,820)
        layout=QVBoxLayout(self);self.panel=CurrentScoutPanel(scene_id,choice_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
