"""Scoped future-result reading with an owned exact-original conflict comparison."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QWidget,QLabel,QPushButton
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_resting as model

class CurrentRestingPanel(DocumentedEventFlowPanel):
    def __init__(self,target=None,parent=None,*,allow_original_popup=True):
        self.source_request=(target or{}).get('source_request');self.allow_original_popup=allow_original_popup;self.original_dialog=None
        initial=None if not self.source_request else'source-scene'if self.source_request['category']=='scenes'else'source-choice'
        super().__init__('resting',initial,parent,reference_model=model)
        self.choices.setAccessibleName('资料选项或结果参考，不是游戏操作')
        self.reward_card=QWidget();row=QHBoxLayout(self.reward_card);row.setContentsMargins(0,0,0,0);self.reward_icon=QLabel();self.reward_icon.setAccessibleName('源私钥同名物品资料图片');row.addWidget(self.reward_icon);row.addWidget(QLabel('源私钥 · 同名物品资料（不代表已领取）'));row.addStretch(1);self.layout().insertWidget(1,self.reward_card)
        self.original_button=QPushButton('对照99源石锭原项：它明确指向病床对话');self.layout().insertWidget(2,self.original_button);self.original_button.clicked.connect(self.open_original)
        if initial=='source-choice':self.choices.setCurrentRow(0)
        self._update_specific()
    def _fresh_reference(self):return model.reference('resting',self.source_request)
    def _close_battle(self):
        child=getattr(self,'original_dialog',None)
        if child is not None:child.close();self.original_dialog=None
        super()._close_battle()
    def _choice_changed(self,item,*args,preserve=False):
        super()._choice_changed(item,*args,preserve=preserve);self._update_specific()
    def clear_reference(self):
        super().clear_reference();self._update_specific()
    def _update_specific(self):
        if not hasattr(self,'original_button'):return
        c=model.choice_reference(self.result,self.scene_id,self.choice_id)if self.result else None
        available=bool(self.allow_original_popup and self.result and model.conflicting_original_target(self.result,self.scene_id,self.choice_id));self.original_button.setVisible(available);self.original_button.setEnabled(available)
        show=bool(self.result and model.shows_reward(self.result,self.scene_id,self.choice_id));self.reward_card.setVisible(show);self.reward_icon.clear()
        if show:
            raw=model.icon_bytes();pixmap=QPixmap()
            if raw is not None and pixmap.loadFromData(raw):self.reward_icon.setPixmap(pixmap.scaled(52,52,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:self.reward_icon.setText('源私钥（图片暂缺）')
        if c and c['explicit_next_conflict']:self.next_button.setText('查看原项明确的病床后续'if c['source_only']else'查看文献记载的离开（与原项不同）')
        else:self.next_button.setText('查看后续情景')
        if self.original_dialog is not None and(not available or not self.original_dialog.panel.refresh_reference()):self.original_dialog.close();self.original_dialog=None
    def open_original(self):
        if not self._recheck()or not self.allow_original_popup:return False
        target=model.conflicting_original_target(self.result,self.scene_id,self.choice_id)
        if target is None:return False
        self._close_battle();self.original_dialog=CurrentRestingDialog(target,self,allow_original_popup=False);self.original_dialog.show();return True

class CurrentRestingDialog(QDialog):
    def __init__(self,target=None,parent=None,*,allow_original_popup=True):
        super().__init__(parent);self.setWindowTitle('安眠一隅 · 分支、领取与来源差异');self.resize(1100,820)
        layout=QVBoxLayout(self);self.panel=CurrentRestingPanel(target,self,allow_original_popup=allow_original_popup);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
