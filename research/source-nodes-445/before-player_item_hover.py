"""Pinnable local item reference; all navigation carries exact version and pool IDs."""
from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QComboBox,QPlainTextEdit
from .player_item_sources import pool_label,VERSION_LABELS
from .view_catalog import relic_icon,relic_icon_note

class ItemHoverCard(QDialog):
    entered=Signal()
    left=Signal()
    poolRequested=Signal(str,str)
    def __init__(self,parent):
        super().__init__(parent,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);self.setWindowTitle('藏品来源速览');self.resize(470,620)
        self.identity=None;self.version=None;self.index=None;self.pinned=False;self.signature=None
        self.setObjectName('itemHoverCard');self.setStyleSheet('#itemHoverCard{background:#1b2928;border:1px solid #56655f;border-radius:12px;} #itemHoverCard QLabel{color:#e7f5f0;} QComboBox,QPushButton{color:#e7f5f0;background:#304746;border:1px solid #617b77;border-radius:7px;padding:4px;}')
        body=QVBoxLayout(self);head=QHBoxLayout();self.picture=QLabel();self.picture.setFixedSize(48,48);head.addWidget(self.picture);self.title=QLabel();self.title.setWordWrap(True);head.addWidget(self.title,1)
        self.pin=QPushButton('固定');self.pin.setCheckable(True);self.pin.toggled.connect(self.set_pinned);head.addWidget(self.pin);close=QPushButton('×');close.clicked.connect(self.dismiss);head.addWidget(close);body.addLayout(head)
        self.notice=QLabel();self.notice.setWordWrap(True);body.addWidget(self.notice)
        from .player_source_cards import SourceCards
        self.cards=SourceCards(self);self.cards.poolChosen.connect(self.choose_card);body.addWidget(self.cards,1)
        self.show_conditions=QPushButton('展开条件与统计样本');self.show_conditions.setCheckable(True);body.addWidget(self.show_conditions)
        self.pools=QComboBox();self.pools.currentIndexChanged.connect(self.read_pool);body.addWidget(self.pools)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1);self.detail.hide();self.show_conditions.toggled.connect(self.detail.setVisible);self.pools.hide()
        self.open_button=QPushButton('查看这个池的全部物品');self.open_button.clicked.connect(self.open_pool);body.addWidget(self.open_button)
        self.map_targets=QComboBox();self.map_targets.setAccessibleName('来源明确关联的地图节点类型');body.addWidget(self.map_targets)
        self.map_button=QPushButton('在本局地图查看这类节点');self.map_button.clicked.connect(self.open_map_source);body.addWidget(self.map_button)
    def set_pinned(self,value):self.pinned=value;self.pin.setText('取消固定'if value else'固定')
    def enterEvent(self,event):self.entered.emit();super().enterEvent(event)
    def leaveEvent(self,event):self.left.emit();super().leaveEvent(event)
    def dismiss(self):self.pin.setChecked(False);self.hide();self.identity=None;self.signature=None
    def install(self,row,version,index,signature):
        if self.pinned and self.identity!=row['id']:return False
        key=(row['id'],version,signature)
        if key==self.signature:return True
        old=self.pools.currentData()if self.identity==row['id']and self.version==version else None
        self.signature=key;self.identity=row['id'];self.version=version;self.index=index
        self.title.setText(row['name']);self.picture.clear()
        self.picture.setPixmap(relic_icon(row.get('icon')or'').pixmap(46,46))
        self.notice.setText(VERSION_LABELS.get(version,'未确认资料范围')+' · 当前DLC适用性待核验。\n比例为历史候选出现频率，不是抽取权重或本局获得概率；不同来源可能重叠，不相加。仅本机查询，不上传本局。')
        note=relic_icon_note(row.get('icon')or'')
        if note:self.notice.setText(note+'\n'+self.notice.text())
        self.pools.blockSignals(True);self.pools.clear()
        for pool in index.pools(version,row['id'])if index else[]:self.pools.addItem(pool_label(pool),pool['id'])
        if old is not None and self.pools.findData(old)>=0:self.pools.setCurrentIndex(self.pools.findData(old))
        self.pools.blockSignals(False)
        from .player_source_cards import source_cards
        self.cards.install(source_cards(index,version,row['id']));self.read_pool();return True
    def read_pool(self,*_):
        pool=self.pools.currentData();self.open_button.setEnabled(pool is not None and self.index is not None)
        text=self.index.describe(self.version,self.identity,pool)if self.index and pool else'所选资料范围未列出此物品的所属池，不能据此认定无法获得。'if self.index else'公开资料暂不可用；旧池与统计已清除。'
        self.cards.select(pool)
        if self.detail.toPlainText()!=text:self.detail.setPlainText(text)
        from .player_source_map import targets,companion
        self.map_targets.clear()
        for kind in targets(self.index,self.version,self.identity,pool):self.map_targets.addItem(kind,kind)
        visible=self.map_targets.count()>0
        self.map_targets.setVisible(visible);self.map_button.setVisible(visible);self.map_button.setEnabled(visible and companion(self)is not None)
        self.map_button.setToolTip('仅标出本局记录中对应类型及候选位置；来源资料不表示当前可达、会出现此物或必掉。')
    def open_map_source(self):
        from .player_source_map import targets,companion
        kind=self.map_targets.currentData();bar=companion(self)
        if bar is None or kind not in targets(self.index,self.version,self.identity,self.pools.currentData()):return False
        if bar.open_map()is False:return False
        bar.map_popup.panel.set_type_filter(kind);return True
    def choose_card(self,identity):
        index=self.pools.findData(identity)
        if index>=0:self.pools.setCurrentIndex(index);self.show_conditions.setChecked(True)
    def open_pool(self):
        if self.index and self.pools.currentData()is not None:self.poolRequested.emit(self.version,self.pools.currentData())
