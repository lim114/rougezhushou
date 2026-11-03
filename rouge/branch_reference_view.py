"""Self-contained read-only branch browser for the fixed battle panel."""
from copy import deepcopy
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QLabel,QPushButton,QPlainTextEdit,QCheckBox
from .branch_reference import branch_reference,branch_reference_text
from .ui_state import replace_text
from .branch_position_overview import branch_position_overview,overview_text

class BranchReferencePanel(QWidget):
    referenceCellSelected=Signal(object)
    positionsChanged=Signal()
    def __init__(self,parent=None):
        super().__init__(parent);self.stage_id=None;self.result=None;self.detail_key=None;self.technical=False
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);controls=QHBoxLayout()
        controls.addWidget(QLabel('分支'))
        self.branch=QComboBox();controls.addWidget(self.branch,2)
        controls.addWidget(QLabel('阶段'))
        self.phase=QComboBox();controls.addWidget(self.phase,1);layout.addLayout(controls)
        positions=QHBoxLayout();self.location=QComboBox();positions.addWidget(self.location,1)
        self.locate=QPushButton('标记固定图资料格');positions.addWidget(self.locate);layout.addLayout(positions)
        self.overlay=QCheckBox('总览当前分支/阶段的全部资料位置');self.overlay.setChecked(True);layout.addWidget(self.overlay)
        self.position_detail=QPlainTextEdit();self.position_detail.setReadOnly(True);self.position_detail.setMaximumHeight(120);layout.addWidget(self.position_detail)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);self.detail.setMaximumHeight(150);layout.addWidget(self.detail)
        self.branch.currentIndexChanged.connect(self._branch_changed);self.phase.currentIndexChanged.connect(self.refresh)
        self.locate.clicked.connect(self._locate);self.overlay.toggled.connect(lambda _:self.positionsChanged.emit());self.set_stage(None)

    def set_stage(self,stage_id):
        if stage_id==self.stage_id and self.result is not None:return
        self.stage_id=stage_id;self.result=branch_reference(stage_id) if stage_id else None
        self.branch.blockSignals(True);self.branch.clear();self.branch.addItem('总览：全部原件分支',None)
        for row in (self.result or {}).get('rows',[]):
            status='直接参数引用' if row['origins'] else '来源未知'
            name=' / '.join(dict.fromkeys(o.get('name') or '名称未确认' for o in row['origins'])) or '来源未知'
            self.branch.addItem(f"分支 {row['catalog_ordinal']} · {name} · {status}",row['branch_id'])
        self.branch.blockSignals(False);self.branch.setEnabled(bool(self.result));self._branch_changed()

    def _branch_changed(self,*_):
        self.phase.blockSignals(True);self.phase.clear();self.phase.addItem('全部阶段',None)
        key=self.branch.currentData()
        row=next((r for r in (self.result or {}).get('rows',[]) if r['branch_id']==key),None)
        for p in (row or {}).get('phases',[]):self.phase.addItem('阶段 '+str(p['phase']),p['phase'])
        self.phase.blockSignals(False);self.phase.setEnabled(bool(row));self.refresh()

    def refresh(self,*_):
        old=self.location.currentData();scroll=self.location.view().verticalScrollBar().value()
        result=branch_reference(self.stage_id,self.branch.currentData(),self.phase.currentData()) if self.stage_id else None
        self.location.blockSignals(True);self.location.clear()
        overview=branch_position_overview(self.stage_id,self.branch.currentData(),self.phase.currentData()) if self.stage_id else None
        marker_numbers={r['reference_id']:group['ordinal'] for group in (overview or {}).get('rows',[]) for r in group['references']}
        for row in (result or {}).get('rows',[]):
            for reference in row['map_references']:
                cell=reference['cell'];role='来源预置' if reference['source_kind']=='producer_declaration' else '激活对象'
                self.location.addItem(f"P{marker_numbers[reference['reference_id']]} · "+reference['name']+f" · {role} · 第{cell['row']+1}行、第{cell['col']+1}列",reference)
        if old:
            i=next((i for i in range(self.location.count()) if self.location.itemData(i)==old),-1)
            if i>=0:self.location.setCurrentIndex(i)
        self.location.blockSignals(False);self.location.view().verticalScrollBar().setValue(scroll)
        self.locate.setEnabled(bool(self.location.count()));key=(self.stage_id,self.branch.currentData(),self.phase.currentData())
        replace_text(self.detail,branch_reference_text(result,self.technical) if result else '请先选择固定战斗资料。',preserve=self.detail_key==key)
        self.detail_key=key
        replace_text(self.position_detail,overview_text(overview) if overview else '尚未选择固定关卡。',preserve=getattr(self,'position_detail_key',None)==key)
        self.position_detail_key=key
        self.positionsChanged.emit()

    def set_technical(self,value):
        self.technical=bool(value);self.refresh()

    def _locate(self):
        reference=self.location.currentData()
        if reference:self.referenceCellSelected.emit(deepcopy(reference))
