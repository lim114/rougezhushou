"""Scoped documentary conditions and an owned offering catalogue, never rewards."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QWidget,QLabel,QSpinBox,QPushButton
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_reconstruction as model,current_exchange_reference as offers

class CurrentReconstructionPanel(DocumentedEventFlowPanel):
    def __init__(self,target=None,parent=None):
        self.source_request=(target or{}).get('source_request');self.catalogue_dialog=None
        initial=None if not self.source_request else'source-scene'if self.source_request['category']=='scenes'else'source-choice'
        super().__init__('reconstruction',initial,parent,reference_model=model)
        self.natural_controls=QWidget();row=QHBoxLayout(self.natural_controls);row.setContentsMargins(0,0,0,0);row.addWidget(QLabel('仅本页自然物件数对照：'))
        self.naturals=QSpinBox();self.naturals.setRange(-1,999999);self.naturals.setSpecialValueText('尚未确认');self.naturals.setValue(-1);self.naturals.setAccessibleName('仅本页自然物数量');row.addWidget(self.naturals);row.addStretch(1);self.layout().insertWidget(1,self.natural_controls);self.naturals.valueChanged.connect(self.refresh_reference)
        self.reward_card=QWidget();row=QHBoxLayout(self.reward_card);row.setContentsMargins(0,0,0,0);self.reward_icon=QLabel();self.reward_icon.setAccessibleName('具名领取参考：焚毁文明图片');row.addWidget(self.reward_icon);row.addWidget(QLabel('焚毁“文明” · 领取参考（不是已持有）'));row.addStretch(1);self.layout().insertWidget(2,self.reward_card)
        self.catalogue_button=QPushButton('查阅当前收藏品能否交出（不是奖励池）');self.layout().insertWidget(3,self.catalogue_button);self.catalogue_button.clicked.connect(self.open_catalogue)
        if initial=='source-choice':self.choices.setCurrentRow(0)
        self._update_specific()
    def _fresh_reference(self):
        w=getattr(self,'naturals',None);count=None if w is None or w.value()<0 else w.value()
        return model.reference('reconstruction',count,self.source_request)
    def _close_battle(self):
        child=getattr(self,'catalogue_dialog',None)
        if child is not None:child.close();self.catalogue_dialog=None
        super()._close_battle()
    def _choice_changed(self,item,*args,preserve=False):
        super()._choice_changed(item,*args,preserve=preserve);self._update_specific()
    def clear_reference(self):
        super().clear_reference();self._update_specific()
    def _update_specific(self):
        if not hasattr(self,'catalogue_button'):return
        c=model.choice_reference(self.result,self.scene_id,self.choice_id)if self.result else None
        self.natural_controls.setVisible(bool(c and c['role']=='restore'))
        show=bool(self.result and model.shows_reward(self.result,self.scene_id,self.choice_id));self.reward_card.setVisible(show);self.reward_icon.clear()
        if show:
            raw=model.icon_bytes();pixmap=QPixmap()
            if raw is not None and pixmap.loadFromData(raw):self.reward_icon.setPixmap(pixmap.scaled(52,52,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:self.reward_icon.setText('焚毁“文明”（图片暂缺）')
        allowed=bool(self.result and model.catalogue_allowed(self.result,self.scene_id,self.choice_id));available=allowed and offers.packet()is not None;self.catalogue_button.setVisible(available);self.catalogue_button.setEnabled(available)
        if self.catalogue_dialog is not None:
            if not available or not self.catalogue_dialog.panel.refresh_reference():self.catalogue_dialog.close();self.catalogue_dialog=None
    def open_catalogue(self):
        if not self._recheck()or not model.catalogue_allowed(self.result,self.scene_id,self.choice_id)or offers.packet()is None:
            self._close_battle();return False
        from .current_exchange_view import CurrentExchangeDialog
        self._close_battle();self.catalogue_dialog=CurrentExchangeDialog(parent=self);self.catalogue_dialog.show();return True

class CurrentReconstructionDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('回滚文明 · 交出、领取与是否继续');self.resize(1100,820)
        layout=QVBoxLayout(self);self.panel=CurrentReconstructionPanel(target,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
