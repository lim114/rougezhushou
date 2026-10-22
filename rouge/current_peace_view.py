"""Only the move branch exposes the temporary completion comparison."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QWidget,QLabel,QComboBox
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_peace as model

class CurrentPeacePanel(DocumentedEventFlowPanel):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__('peace',scene_id,parent,reference_model=model)
        self.completion_controls=QWidget();row=QHBoxLayout(self.completion_controls);row.setContentsMargins(0,0,0,0);row.addWidget(QLabel('仅本页条件对照：本层居民据点作战'))
        self.completed=QComboBox();self.completed.setAccessibleName('仅本页本层完成情况对照')
        for label,value in [('尚未确认',None),('假设已完成',True),('假设未完成',False)]:self.completed.addItem(label,value)
        row.addWidget(self.completed);row.addStretch(1);self.layout().insertWidget(1,self.completion_controls);self.completed.currentIndexChanged.connect(self.refresh_reference)
        self.reward_card=QWidget();row=QHBoxLayout(self.reward_card);row.setContentsMargins(0,0,0,0)
        self.reward_icon=QLabel();self.reward_icon.setAccessibleName('悬赏收藏品参考：厄运火杆图片');row.addWidget(self.reward_icon);row.addWidget(QLabel('厄运火杆 · 收藏品说明（不代表已持有或获胜）'));row.addStretch(1);self.layout().insertWidget(2,self.reward_card)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break
        self._update_specific()
    def _fresh_reference(self):
        w=getattr(self,'completed',None);return model.reference('peace',None if w is None else w.currentData())
    def _choice_changed(self,item,*args,preserve=False):
        super()._choice_changed(item,*args,preserve=preserve);self._update_specific()
    def clear_reference(self):
        super().clear_reference();self._update_specific()
    def _update_specific(self):
        if not hasattr(self,'reward_card'):return
        c=model.choice_reference(self.result,self.scene_id,self.choice_id)if self.result else None
        self.completion_controls.setVisible(bool(c and c['role']=='move'))
        show=bool(self.result and model.shows_reward(self.result,self.scene_id,self.choice_id));self.reward_card.setVisible(show);self.reward_icon.clear()
        if show:
            raw=model.icon_bytes();pixmap=QPixmap()
            if raw is not None and pixmap.loadFromData(raw):self.reward_icon.setPixmap(pixmap.scaled(52,52,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:self.reward_icon.setText('厄运火杆（图片暂缺）')

class CurrentPeaceDialog(QDialog):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('和平守卫者 · 悬赏、前往与标记');self.resize(1100,820)
        layout=QVBoxLayout(self);self.panel=CurrentPeacePanel(scene_id,choice_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
