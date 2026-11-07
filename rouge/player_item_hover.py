"""Pinnable local item reference; all navigation carries exact version and pool IDs."""
from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QComboBox,QPlainTextEdit
from .player_item_sources import VERSION_LABELS, selected_pool
from .view_catalog import relic_icon,relic_icon_note

class ItemHoverCard(QDialog):
    entered=Signal()
    left=Signal()
    poolRequested=Signal(str,str)
    def __init__(self,parent):
        super().__init__(parent,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);self.setWindowTitle('藏品来源速览');self.resize(470,620)
        self.identity=None;self.version=None;self.index=None;self.pinned=False;self.signature=None
        self.setProperty('playerVisibility','hover')
        from .player_theme import apply_theme
        self.setObjectName('itemHoverCard');apply_theme(self,'dark')
        body=QVBoxLayout(self);head=QHBoxLayout();self.picture=QLabel();self.picture.setFixedSize(48,48);head.addWidget(self.picture);self.title=QLabel();self.title.setWordWrap(True);head.addWidget(self.title,1)
        self.pin=QPushButton('固定');self.pin.setCheckable(True);self.pin.toggled.connect(self.set_pinned);head.addWidget(self.pin);close=QPushButton('×');close.clicked.connect(self.dismiss);head.addWidget(close);body.addLayout(head)
        self.notice=QLabel();self.notice.setWordWrap(True);body.addWidget(self.notice)
        from .player_source_cards import SourceCards
        self.cards=SourceCards(self);self.cards.poolChosen.connect(self.choose_card);self.cards.nodeChosen.connect(self.open_map_source);body.addWidget(self.cards,1)
        self.show_conditions=QPushButton('展开条件与统计样本');self.show_conditions.setCheckable(True);body.addWidget(self.show_conditions)
        self.pools=QComboBox();self.pools.currentIndexChanged.connect(self.read_pool);body.addWidget(self.pools)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1);self.detail.hide();self.show_conditions.toggled.connect(self.detail.setVisible);self.pools.hide()
        self.open_button=QPushButton('查看这个池的全部物品');self.open_button.clicked.connect(self.open_pool);body.addWidget(self.open_button)
        self.map_targets=QComboBox();self.map_targets.setAccessibleName('来源明确关联的地图节点类型');body.addWidget(self.map_targets)
        self.map_button=QPushButton('在本局地图查看这类节点');self.map_button.clicked.connect(lambda:self.open_map_source());body.addWidget(self.map_button)
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
        icon = row.get('icon') or ''
        self.picture.setPixmap(relic_icon(icon).pixmap(46,46))
        notice = VERSION_LABELS.get(version,'资料版本待选择') + ' · 藏品来源'
        note = relic_icon_note(icon)
        self.notice.setText(note + '\n' + notice if note else notice)

        from .player_source_cards import source_cards
        groups = source_cards(index, version, self.identity)
        self.pools.blockSignals(True)
        self.pools.clear()
        for pool in groups['pools']:
            self.pools.addItem(pool['title'], pool['id'])
        if old is not None:
            position = self.pools.findData(old)
            if position >= 0:
                self.pools.setCurrentIndex(position)
        self.pools.blockSignals(False)
        self.cards.install(groups)
        self.read_pool()
        return True
    def read_pool(self,*_):
        pool=self.pools.currentData();self.open_button.setEnabled(pool is not None and self.index is not None)
        selected = selected_pool(self.index, self.version, self.identity, pool)
        if self.index is None:
            text = '请先更新公开资料。'
        elif pool:
            text = self.index.describe_pool(self.version, self.identity, selected)
        else:
            text = '当前资料暂无来源记录。'
        self.cards.select(pool)
        if self.detail.toPlainText()!=text:self.detail.setPlainText(text)
        from .player_source_map import pool_targets, companion
        self.map_targets.clear()
        for kind in pool_targets(selected):self.map_targets.addItem(kind,kind)
        visible=self.map_targets.count()>0
        self.map_targets.setVisible(visible);self.map_button.setVisible(visible);self.map_button.setEnabled(visible and companion(self)is not None)
        self.map_button.setToolTip('在地图中标出对应类型的节点。')
    def open_map_source(self,pool_id=None,kind=None):
        from .player_source_map import targets,companion
        pool_id=self.pools.currentData()if pool_id is None else pool_id
        kind=self.map_targets.currentData()if kind is None else kind
        if kind not in targets(self.index,self.version,self.identity,pool_id):return False
        self.choose_card(pool_id);self.map_targets.setCurrentIndex(self.map_targets.findData(kind));bar=companion(self)
        if bar is None:return False
        if bar.open_map()is False:return False
        bar.map_popup.panel.set_type_filter(kind);return True
    def choose_card(self,identity):
        index=self.pools.findData(identity)
        if index>=0:self.pools.setCurrentIndex(index);self.show_conditions.setChecked(True)
    def open_pool(self):
        pool = self.pools.currentData()
        if self.index and pool is not None:
            self.poolRequested.emit(self.version, pool)
