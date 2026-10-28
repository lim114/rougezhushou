"""Read-only picture inventory, with held facts distinct from source descriptions."""
from pathlib import Path
from PySide6.QtCore import Qt,QSize,Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QCheckBox,QLabel,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton
from . import expansion_reference as reference
from .record_flags import active_record

def inventory_rows(state,query='',held_only=True):
    packet=reference.packet()
    if packet is None:return None
    held={key for key,row in state.get('relics',{}).items()if active_record(row,'held')}
    result=[];q=query.strip().casefold()
    for row in reference.rows('relics',changes_only=False,reference=packet):
        item=row['value'].get('item')or{}
        if item.get('type')not in ('RELIC','LEGACY'):continue
        usage=reference._plain(item.get('usage'))
        if held_only and row['id']not in held:continue
        if q and q not in (row['name']+' '+usage).casefold():continue
        result.append({'id':row['id'],'name':row['name'],'usage':usage,'held':row['id']in held,
            'icon':item.get('iconId'),'exchange':item.get('canSacrifice')})
    return result

class InventoryPanel(QWidget):
    openReference=Signal(str)
    def __init__(self,run):
        super().__init__();self.run=run;self.rows={};body=QVBoxLayout(self)
        bar=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('搜索藏品名称或效果，如攻击、生命')
        self.held=QCheckBox('只看本局已确认持有');self.held.setChecked(True);bar.addWidget(self.search,1);bar.addWidget(self.held);body.addLayout(bar)
        self.status=QLabel();self.status.setWordWrap(True);body.addWidget(self.status)
        self.entries=QListWidget();self.entries.setIconSize(QSize(42,42));body.addWidget(self.entries,2)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1)
        self.reference_button=QPushButton('查看取得来源与相关查询');body.addWidget(self.reference_button)
        self.reference_button.clicked.connect(self.open_selected);self.entries.currentItemChanged.connect(self.selected)
        self.search.textChanged.connect(self.refresh);self.held.toggled.connect(self.refresh);self.refresh()
    def refresh(self,*_):
        current=self.entries.currentItem();selected=current.data(Qt.ItemDataRole.UserRole)if current else None
        rows=inventory_rows(self.run.state,self.search.text(),self.held.isChecked());self.rows={r['id']:r for r in rows or[]}
        self.entries.blockSignals(True);self.entries.clear()
        for row in rows or[]:
            icon=Path(__file__).parent/'data/relic-icons'/((row['icon']or'')+'.png')
            item=QListWidgetItem(QIcon(str(icon))if icon.is_file()else QIcon(),row['name']+(' · 本局已确认'if row['held']else''))
            item.setData(Qt.ItemDataRole.UserRole,row['id']);self.entries.addItem(item)
            if row['id']==selected:self.entries.setCurrentItem(item)
        if selected not in self.rows:self.entries.setCurrentRow(-1)
        self.entries.blockSignals(False);self.selected()
        complete=self.run.state.get('inventory_verified')is True
        self.status.setText('资料暂不可用，已清除旧列表。'if rows is None else f'找到{len(rows)}件。'+('本局收藏品已核对完整。'if complete else'本局尚未核对读全；未列出不代表没有。')+' 效果为资料说明，不等于本局全部生效或计算已支持。')
    def selected(self,*_):
        item=self.entries.currentItem();row=self.rows.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        self.reference_button.setEnabled(row is not None)
        if not row:self.detail.clear();return
        exchange='资料允许交换'if row['exchange']is True else'资料不允许交换'if row['exchange']is False else'交换资格未确认'
        self.detail.setPlainText(row['name']+'\n\n效果说明\n'+(row['usage']or'暂无说明')+'\n\n'+exchange+'；实际能否交换仍需对应事件条件。')
    def open_selected(self):
        item=self.entries.currentItem()
        if item and item.data(Qt.ItemDataRole.UserRole)in self.rows:self.openReference.emit(item.data(Qt.ItemDataRole.UserRole))
