from pathlib import Path
from PySide6.QtCore import Qt,QSize,Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QComboBox,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton
from .player_exchange_sources import exchange_links,exchange_text,exchange_label

def related_exchanges(data,version,identity):
    if not isinstance(data,dict)or not isinstance(version,str)or not isinstance(identity,str):return []
    try:return exchange_links(data,version,identity)
    except(ValueError,KeyError,TypeError,AttributeError):return []

class ExchangePanel(QWidget):
    openPool=Signal(str,str)
    def __init__(self,parent=None):
        super().__init__(parent);self.identity=None;self.version=None;self.signature=None;self.key=None;self.links=[];self.rows={};body=QVBoxLayout(self)
        self.title=QLabel('选择提供物后查看资料中的对应换入候选。');self.title.setWordWrap(True);body.addWidget(self.title)
        self.notice=QLabel('只查明确记载的对应关系，不按同名、稀有度或允许交换标记推算。');self.notice.setWordWrap(True);body.addWidget(self.notice)
        self.choices=QComboBox();body.addWidget(self.choices);self.entries=QListWidget();self.entries.setIconSize(QSize(44,44));body.addWidget(self.entries,1)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1);self.open_button=QPushButton('查看这个换入集合的完整来源与统计');body.addWidget(self.open_button)
        self.choices.currentIndexChanged.connect(self.choose);self.entries.currentItemChanged.connect(self.selected);self.open_button.clicked.connect(self.open_output)
    def bind(self,data,version,identity,signature):
        if (version,identity)!=(self.version,self.identity):self.key=None;self.choices.setCurrentIndex(-1)
        self.version=version;self.identity=identity;self.refresh_source(data,signature)
    def refresh_source(self,data,signature):
        key=(self.version,self.identity,signature)
        if key==self.key:return
        self.key=key;old=self.choices.currentData();self.links=related_exchanges(data,self.version,self.identity)if signature is not None else[]
        self.choices.blockSignals(True);self.choices.clear();self.choices.addItem('请选择一条有明确依据的交换对应关系',None)
        for link in self.links:self.choices.addItem(exchange_label(link),link['output_id'])
        index=self.choices.findData(old);self.choices.setCurrentIndex(max(0,index));self.choices.blockSignals(False)
        item=data.get('items',{}).get(self.identity,{})if isinstance(data,dict)else{}
        self.title.setText('提供物资料：'+(item.get('name')or'名称未核对'))
        self.notice.setText('当前范围未找到可核对的明确对应关系，旧候选已清除。不能据此认定本次无法交换。'if not self.links else '对应关系来自路标公开资料中的明确提供物与输出说明。当前DLC完整适用性未核验；本局资格与实际领取仍未知。')
        self.choose()
    def current_link(self):return next((link for link in self.links if link['output_id']==self.choices.currentData()),None)
    def choose(self,*_):
        link=self.current_link();old=self.entries.currentItem();identity=old.data(Qt.ItemDataRole.UserRole)if old else None;self.entries.blockSignals(True);self.entries.clear();self.rows={r['id']:r for r in link['members']}if link else{}
        for row in self.rows.values():
            icon=row.get('icon');picture=QIcon()
            if isinstance(icon,str)and Path(icon).name==icon and '/'not in icon and '\\'not in icon:
                for folder in('relic-icons','part-icons'):
                    path=Path(__file__).with_name('data')/folder/(icon+'.png')
                    if path.is_file():picture=QIcon(str(path));break
            entry=QListWidgetItem(picture,row['name']+(' · 图片待补'if picture.isNull()else''));entry.setData(Qt.ItemDataRole.UserRole,row['id']);self.entries.addItem(entry)
            if row['id']==identity:self.entries.setCurrentItem(entry)
        self.entries.blockSignals(False);self.open_button.setEnabled(link is not None);self.selected()
    def selected(self,*_):
        link=self.current_link();entry=self.entries.currentItem();row=self.rows.get(entry.data(Qt.ItemDataRole.UserRole))if entry else None
        text=exchange_text(link)if link else'请先选择明确的交换对应关系；没有假定奖励或等概率分配。'
        if row:
            from .expansion_reference import _plain
            text=row['name']+'\n\n效果资料\n'+_plain(row.get('effect'))+'\n\n'+text
        if text!=self.detail.toPlainText():self.detail.setPlainText(text)
    def open_output(self):
        link=self.current_link()
        if link:self.openPool.emit(link['version'],link['output_id'])

def input_available(panel):
    item=panel.entries.currentItem();identity=item.data(Qt.ItemDataRole.UserRole)if item else None
    return identity,bool(identity and panel.source_index and related_exchanges(panel.source_index.data,panel.version.currentData(),identity))

def update_inventory_button(panel):
    identity,available=input_available(panel);panel.exchange_button.setVisible(available);panel.exchange_button.setEnabled(available)

def request_inventory(panel):
    identity,available=input_available(panel)
    if available:panel.openExchangeReference.emit(panel.version.currentData(),identity)

