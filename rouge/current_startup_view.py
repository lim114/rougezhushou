from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_startup as model

class CurrentStartupPanel(DocumentedEventFlowPanel):
    def __init__(self,target=None,parent=None):
        super().__init__('startup',model.SCENE,parent,reference_model=model)
        controls=QHBoxLayout();self.group=QComboBox()
        for text,value in [('总览（资料目录，不是本次菜单）','all'),('常规支援候选','regular'),('继承的额外支援','inherited')]:self.group.addItem(text,value)
        self.mode=QComboBox()
        for text,value in [('模式未知',None),('常规行动','NORMAL'),('其它模式','OTHER')]:self.mode.addItem(text,value)
        self.previous=QSpinBox();self.previous.setRange(-1,999);self.previous.setSpecialValueText('未知');self.previous.setValue(-1)
        self.previous.setAccessibleName('上一局已通过区域数');self.mode.setAccessibleName('探索模式');self.group.setAccessibleName('支援资料分类')
        for widget in(self.group,self.mode,QLabel('上一局通过区域'),self.previous):controls.addWidget(widget)
        self.layout().insertLayout(1,controls)
        self.cost_row=QHBoxLayout();self.cost_label=QLabel('仅本页源石锭');self.gold=QSpinBox();self.gold.setRange(-1,99999);self.gold.setSpecialValueText('未知');self.gold.setValue(-1)
        self.cost_row.addWidget(self.cost_label);self.cost_row.addWidget(self.gold);self.layout().insertLayout(2,self.cost_row)
        self.inheritance_row=QHBoxLayout();self.inheritance_label=QLabel('上一局明确继承的额外支援');self.inherited=QComboBox();self.inherited.addItem('未知（当前持有不作证明）',None);self.inherited.addItem('明确未继承','none')
        fresh=model.packet()
        for cid in fresh['data']['inherited_ids']if fresh else[]:self.inherited.addItem(fresh['data']['choices'][cid]['title'],cid)
        self.inheritance_row.addWidget(self.inheritance_label);self.inheritance_row.addWidget(self.inherited);self.layout().insertLayout(3,self.inheritance_row)
        self.reward_icon=QLabel();self.reward_icon.setFixedSize(64,64);self.reward_name=QLabel();self.reward_card=QHBoxLayout();self.reward_card.addWidget(self.reward_icon);self.reward_card.addWidget(self.reward_name,1);self.layout().insertLayout(4,self.reward_card)
        for widget in(self.group,self.mode,self.inherited):widget.currentIndexChanged.connect(self.refresh_reference)
        self.previous.valueChanged.connect(self.refresh_reference);self.gold.valueChanged.connect(self.refresh_reference)
        self.refresh_reference()
        if target:
            if target==model.locate('choices',target.get('choice_id'))or target==model.locate('scenes',target.get('scene_id')):
                self.scene.setCurrentIndex(self.scene.findData(model.SCENE))
                cid=target.get('choice_id')
                for i in range(self.choices.count()):
                    if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid:self.choices.setCurrentRow(i);break

    def _fresh_reference(self):
        def number(name):
            w=getattr(self,name,None);return None if w is None or w.value()<0 else w.value()
        def value(name,default=None):
            w=getattr(self,name,None);return default if w is None else w.currentData()
        return model.reference('startup',number('previous'),value('mode'),number('gold'),value('inherited'),value('group','all'))

    def _choice_changed(self,*args,**kwargs):
        super()._choice_changed(*args,**kwargs)
        if not hasattr(self,'gold'):return
        row=self.result['choices'].get(self.choice_id)if self.result else None
        inherited=bool(row and row['kind']=='inherited')
        for w in(self.cost_label,self.gold):w.setVisible(self.choice_id=='choice_ro6_startbuff_3')
        if not hasattr(self,'inherited'):return
        for w in(self.inheritance_label,self.inherited):w.setVisible(inherited)
        if not hasattr(self,'reward_icon'):return
        self.reward_icon.clear();self.reward_name.clear();self.reward_icon.setVisible(inherited);self.reward_name.setVisible(inherited)
        if inherited:
            item=self.result['data']['originals']['items'][row['item_id']];path=model.ROOT/'rouge/data/relic-icons'/ (item['iconId']+'.png');pixmap=QPixmap(str(path))
            if not pixmap.isNull():self.reward_icon.setPixmap(pixmap.scaled(64,64,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            self.reward_name.setText(item['name']+' · 只查阅原说明，是否生效未知')

    def clear_reference(self):
        super().clear_reference()
        if hasattr(self,'reward_icon'):self.reward_icon.clear();self.reward_name.clear();self.reward_icon.hide();self.reward_name.hide()
        for name in('cost_label','gold','inheritance_label','inherited'):
            w=getattr(self,name,None)
            if w is not None:w.hide()

class CurrentStartupDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('行动奖励 · 常规候选与继承支援');self.resize(1100,820)
        layout=QVBoxLayout(self);self.panel=CurrentStartupPanel(target,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
