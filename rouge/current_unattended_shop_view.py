"""Unattended-shop reader; same-text followups remain individually inspectable."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QSpinBox,QComboBox,QPushButton
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_unattended_shop as model

class CurrentUnattendedShopPanel(DocumentedEventFlowPanel):
    def __init__(self,target=None,parent=None):
        self.requested_original_id=target.get('original_choice_id')if target else None
        super().__init__('shop',target.get('scene_id')if target else None,parent,reference_model=model)
        row=QHBoxLayout();row.addWidget(QLabel('仅本页对照：源石锭'));self.gold=QSpinBox();self.gold.setRange(-1,99999);self.gold.setSpecialValueText('未知');self.gold.setValue(-1);row.addWidget(self.gold);row.addWidget(QLabel('四叶草化石'));self.fossil=QComboBox()
        for label,value in(('尚未确认',None),('持有',True),('未持有',False)):self.fossil.addItem(label,value)
        row.addWidget(self.fossil);self.layout().insertLayout(1,row);self.gold.valueChanged.connect(self._condition_changed);self.fossil.currentIndexChanged.connect(self._condition_changed)
        self.gold.setAccessibleName('本页开桶源石锭对照');self.fossil.setAccessibleName('本页四叶草化石持有对照');row=QHBoxLayout();self.followup_buttons=[QPushButton(),QPushButton()]
        for button in self.followup_buttons:row.addWidget(button);button.clicked.connect(lambda _=False,b=button:self.open_documented_followup(b.property('sceneId')))
        self.layout().insertLayout(4,row)
        if target and target.get('choice_id'):
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==target['choice_id']:self.choices.setCurrentRow(i);break
        self._sync_followups()
    def _fresh_reference(self):
        gold=getattr(self,'gold',None);fossil=getattr(self,'fossil',None);return model.reference('shop',None if gold is None or gold.value()<0 else gold.value(),fossil.currentData()if fossil is not None else None,self.requested_original_id)
    def _condition_changed(self,*_):self.refresh_reference()
    def _sync_followups(self):
        if not hasattr(self,'followup_buttons'):return
        c=model.choice_reference(self.result,self.scene_id,self.choice_id)if self.result else None;ids=c['next_scene_ids']if c and len(c['next_scene_ids'])>1 else[]
        for i,button in enumerate(self.followup_buttons):
            active=i<len(ids);button.setVisible(active);button.setEnabled(active and c['listed_condition_match']is not False);button.setProperty('sceneId',ids[i]if active else None)
            if active:button.setText('查看'+model.scene_label(self.result,ids[i]))
    def _choice_changed(self,item,*args,preserve=False):super()._choice_changed(item,*args,preserve=preserve);self._sync_followups()
    def clear_reference(self):self.requested_original_id=None;super().clear_reference();self._sync_followups()
    def open_documented_followup(self,sid):
        if not self._recheck()or not model.followup_allowed(self.result,self.scene_id,self.choice_id,sid):return False
        self.scene.setCurrentIndex(self.scene.findData(sid));return True

class CurrentUnattendedShopDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('无人商店 · 持有条件、换档与报酬');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentUnattendedShopPanel(target,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
