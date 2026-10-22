"""Agency-specific profession comparison; random recruitment never inherits it."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QWidget,QLabel,QComboBox
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_agency as model

class CurrentAgencyPanel(DocumentedEventFlowPanel):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__('agency',scene_id,parent,reference_model=model)
        self.offer_controls=QWidget();row=QHBoxLayout(self.offer_controls);row.setContentsMargins(0,0,0,0);row.addWidget(QLabel('仅本页职业组对照：'))
        self.offer=QComboBox();self.offer.setAccessibleName('仅本页可靠中介职业组对照');self.offer.addItem('尚未确认',None)
        for label in model.OFFER_LABELS:self.offer.addItem(label,label)
        row.addWidget(self.offer);self.pair_icons=[]
        for _ in range(2):
            label=QLabel();label.setMinimumWidth(32);row.addWidget(label);self.pair_icons.append(label)
        self.pair_label=QLabel();row.addWidget(self.pair_label);row.addStretch(1);self.layout().insertWidget(1,self.offer_controls);self.offer.currentIndexChanged.connect(self._conditions_changed)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break
        self._update_professions()
    def _fresh_reference(self):
        w=getattr(self,'offer',None);return model.reference('agency',None if w is None else w.currentData())
    def _conditions_changed(self,*_):self.refresh_reference()
    def _choice_changed(self,item,*args,preserve=False):
        super()._choice_changed(item,*args,preserve=preserve);self._update_professions()
    def clear_reference(self):
        super().clear_reference();self._update_professions()
    def _update_professions(self):
        if not hasattr(self,'offer_controls'):return
        c=model.choice_reference(self.result,self.scene_id,self.choice_id)if self.result else None
        promoted=bool(c and c['role']=='promoted');self.offer_controls.setVisible(promoted)
        for label in self.pair_icons:label.clear()
        self.pair_label.clear()
        if promoted:
            self.pair_label.setText('或'.join(c['profession_pair'])+' · 只招募一名')
            for label,profession in zip(self.pair_icons,c['profession_pair']):
                label.setAccessibleName(profession+'职业图标');raw=model.icon_bytes(profession);pixmap=QPixmap()
                if raw is not None and pixmap.loadFromData(raw):label.setPixmap(pixmap.scaled(28,28,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
                else:label.setText(profession+'（图标暂缺）')

class CurrentAgencyDialog(QDialog):
    def __init__(self,scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('临时中介所 · 职业、直升与临时招募');self.resize(1100,820)
        layout=QVBoxLayout(self);self.panel=CurrentAgencyPanel(scene_id,choice_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)
