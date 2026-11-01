"""Sand-event reader with optional, explicitly local condition comparison."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QGridLayout,QHBoxLayout,QGroupBox,QLabel,QComboBox,QSpinBox,QPushButton
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_sand_reference as model

class CurrentSandPanel(DocumentedEventFlowPanel):
    def __init__(self,event_id='informer',scene_id=None,choice_id=None,parent=None):
        self.related_dialog=None;self.controls={}
        super().__init__(event_id,scene_id,parent,reference_model=model)
        group=QGroupBox('可选条件对照 · 只用于本页，不改本局记录');grid=QGridLayout(group)
        definitions=[('scope','查看范围',[('当前条件','current'),('历史资料','history')]),('floor','层数',[('未知',None)]+[(str(n),n)for n in range(1,7)]),('node_type','节点',[('未知','unknown'),('不期而遇','不期而遇'),('命运所指','命运所指'),('其它','other')]),('cleared_reboot','强制重启是否已通关',None),('has_alpha','持有沙盘α',None),('has_beta','持有沙盘β',None),('target_marked','窥视箱中已标记',None)]
        for i,(key,label,values)in enumerate(definitions):
            control=QComboBox();control.setAccessibleName('本页对照：'+label)
            for text,value in values or[('未确认',None),('是',True),('否',False)]:control.addItem(text,value)
            self.controls[key]=control;row,col=divmod(i,3);grid.addWidget(QLabel(label),row,col*2);grid.addWidget(control,row,col*2+1);control.currentIndexChanged.connect(self._context_changed)
        self.gold=QSpinBox();self.gold.setRange(-1,99999);self.gold.setSpecialValueText('未知');self.gold.setValue(-1);self.gold.setAccessibleName('本页对照：源石锭');grid.addWidget(QLabel('源石锭'),2,2);grid.addWidget(self.gold,2,3);self.gold.valueChanged.connect(self._context_changed)
        self.layout().insertWidget(1,group);self.related_button=QPushButton('查看窥视箱中：条件与相关作战');self.layout().insertWidget(4,self.related_button);self.related_button.clicked.connect(self.open_related)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break
        self._sync_related()

    def _fresh_reference(self):
        if not hasattr(self,'gold'):return model.reference(self.event_id)
        values={k:v.currentData()for k,v in self.controls.items()};values['gold']=None if self.gold.value()<0 else self.gold.value();return model.reference(self.event_id,values)

    def _close_related(self):
        if self.related_dialog is not None:self.related_dialog.close()

    def _sync_related(self):
        if not hasattr(self,'related_button'):return
        self.related_button.setVisible(self.result is not None);self.related_button.setEnabled(self.result is not None)

    def clear_reference(self):
        self._close_related();super().clear_reference();self._sync_related()

    def refresh_reference(self,*args,**kw):
        ok=super().refresh_reference(*args,**kw);self._sync_related()
        if ok and self.related_dialog is not None and self.related_dialog.isVisible():self.related_dialog.panel.refresh_reference()
        return ok

    def _context_changed(self,*_):
        self._close_related();self.refresh_reference()

    def _choice_changed(self,item,*args,preserve=False):
        cid=item.data(Qt.ItemDataRole.UserRole)if item else None
        if not(preserve and cid==self.choice_id):self._close_related()
        super()._choice_changed(item,*args,preserve=preserve);self._sync_related()

    def open_related(self):
        if not self._recheck():return False
        from .box_event_reference import locate
        target=locate('scenes','scene_ro6_end2_enter')
        if target is None:self._close_related();return False
        from .box_event_view import BoxEventDialog
        self._close_related();self.related_dialog=BoxEventDialog(target['scene_id'],None,self);self.related_dialog.show();return True

    def closeEvent(self,event):self._close_related();super().closeEvent(event)

class CurrentSandDialog(QDialog):
    def __init__(self,event_id='informer',scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('线人 · 沙盘与奖励'if event_id=='informer'else'好奇心与死 · 标记、奖励与条件');self.resize(1100,860)
        layout=QVBoxLayout(self);self.panel=CurrentSandPanel(event_id,scene_id,choice_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_related();self.panel._close_battle();super().closeEvent(event)
