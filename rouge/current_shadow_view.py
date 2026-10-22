"""Read dance outcomes without turning random references into game commands."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QWidget,QLabel
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_shadow as model
class CurrentShadowPanel(DocumentedEventFlowPanel):
    def __init__(self,target=None,parent=None):
        target=target or {};self.source_request=target.get('source_request')
        initial=('source-scene'if self.source_request['category']=='scenes'else'source-choice')if self.source_request else target.get('scene_id')
        super().__init__('shadow',initial,parent,reference_model=model)
        self.choices.setAccessibleName('资料选项或随机结果参考，不是游戏操作')
        self.reward_card=QWidget();row=QHBoxLayout(self.reward_card);row.setContentsMargins(0,0,0,0);self.reward_icon=QLabel();self.reward_icon.setAccessibleName('犬植浆准确物品图片');row.addWidget(self.reward_icon);row.addWidget(QLabel('犬植浆 · 当前固定资料（不是已领取）'));row.addStretch(1);self.layout().insertWidget(1,self.reward_card)
        if self.source_request and self.source_request['category']=='choices':self.choices.setCurrentRow(0)
        elif target.get('choice_id'):
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==target['choice_id']:self.choices.setCurrentRow(i);break
        self._update_reward()
    def _fresh_reference(self):return model.reference('shadow',self.source_request)
    def _choice_changed(self,item,*args,preserve=False):
        super()._choice_changed(item,*args,preserve=preserve);self._update_reward()
    def clear_reference(self):super().clear_reference();self._update_reward()
    def _update_reward(self):
        if not hasattr(self,'reward_card'):return
        show=bool(self.result and model.shows_reward(self.result,self.scene_id,self.choice_id));self.reward_card.setVisible(show);self.reward_icon.clear()
        if show:
            raw=model.icon_bytes();picture=QPixmap()
            if raw is not None and picture.loadFromData(raw):self.reward_icon.setPixmap(picture.scaled(52,52,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:self.reward_icon.setText('犬植浆（图片暂缺）')
class CurrentShadowDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('被歌颂的影子 · 逐圈代价、结果与离开');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentShadowPanel(target,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
