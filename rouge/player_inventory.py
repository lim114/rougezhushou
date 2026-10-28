"""Read-only picture inventory, with held facts distinct from source descriptions."""
from pathlib import Path
from PySide6.QtCore import Qt,QSize,Signal,QTimer,QEvent
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QCheckBox,QLabel,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton,QComboBox
from . import expansion_reference as reference
from .record_flags import active_record

RARITIES={'NORMAL':'低稀有度 · N','RARE':'中稀有度 · R','SUPER_RARE':'高稀有度 · SR','NONE':'未分档'}

def inventory_rows(state,query='',held_only=True,*,rarity=None,exchange=None,kind=None):
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
        if rarity is not None and item.get('rarity')!=rarity:continue
        if exchange is not None and item.get('canSacrifice')is not exchange:continue
        if kind is not None and item.get('type')!=kind:continue
        result.append({'id':row['id'],'name':row['name'],'usage':usage,'held':row['id']in held,
            'icon':item.get('iconId'),'exchange':item.get('canSacrifice'),'rarity':item.get('rarity'),'kind':item.get('type')})
    return result

class InventoryPanel(QWidget):
    openReference=Signal(str)
    openPoolReference=Signal(str,str)
    openExchangeReference=Signal(str,str)
    def __init__(self,run,public_cache=None):
        super().__init__();self.run=run;self.rows={};self.public_cache=Path(public_cache)if public_cache is not None else None;self.source_stamp=None;self.source_signature=None;self.source_index=None;self.render_key=None;body=QVBoxLayout(self)
        bar=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('搜索藏品名称或效果，如攻击、生命')
        self.held=QCheckBox('只看本局已确认持有');self.held.setChecked(True);bar.addWidget(self.search,1);bar.addWidget(self.held);body.addLayout(bar)
        filters=QHBoxLayout();self.rarity=QComboBox();self.rarity.addItem('全部稀有度',None)
        for key,label in RARITIES.items():self.rarity.addItem(label,key)
        self.exchange=QComboBox();self.exchange.addItem('全部交换资格',None);self.exchange.addItem('资料允许交出',True);self.exchange.addItem('资料不允许交出',False)
        self.kind=QComboBox();self.kind.addItem('全部类别',None);self.kind.addItem('收藏品','RELIC');self.kind.addItem('开局助力','LEGACY')
        self.version=QComboBox();self.version.setToolTip('只切换所属池的资料范围；效果说明仍使用旁边标明的固定国服基准。')
        for widget in(self.rarity,self.exchange,self.kind,self.version):filters.addWidget(widget)
        body.addLayout(filters)
        self.status=QLabel();self.status.setWordWrap(True);body.addWidget(self.status)
        self.entries=QListWidget();self.entries.setIconSize(QSize(42,42));body.addWidget(self.entries,2)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1)
        self.reference_button=QPushButton('查看取得来源与相关查询');body.addWidget(self.reference_button)
        self.exchange_button=QPushButton('查看此提供物对应的换入候选');body.addWidget(self.exchange_button);self.exchange_button.setVisible(False)
        from .player_exchange_view import request_inventory
        self.exchange_button.clicked.connect(lambda:request_inventory(self))
        self.reference_button.clicked.connect(self.open_selected);self.entries.currentItemChanged.connect(self.selected)
        from .player_item_hover import ItemHoverCard
        self.hover_card=ItemHoverCard(self);self.hover_card.poolRequested.connect(self.openPoolReference)
        self.hover_pending=None;self.hover_timer=QTimer(self);self.hover_timer.setSingleShot(True);self.hover_timer.setInterval(180);self.hover_timer.timeout.connect(self.show_hover)
        self.leave_timer=QTimer(self);self.leave_timer.setSingleShot(True);self.leave_timer.setInterval(220);self.leave_timer.timeout.connect(self.leave_hover)
        self.entries.setMouseTracking(True);self.entries.viewport().installEventFilter(self);self.entries.itemEntered.connect(self.queue_hover)
        self.hover_card.entered.connect(self.leave_timer.stop);self.hover_card.left.connect(self.leave_timer.start)
        self.search.textChanged.connect(self.refresh);self.held.toggled.connect(self.refresh)
        for widget in(self.rarity,self.exchange,self.kind,self.version):widget.currentIndexChanged.connect(self.refresh)
        self.refresh()
    def reload_sources(self):
        from . import public_archive
        from .player_item_sources import ItemSourceIndex,VERSION_LABELS
        path=getattr(self,'source_path',self.public_cache if self.public_cache is not None else public_archive.DEFAULT)
        # An explicitly installed cache becoming unavailable is not replaced by an older pack.
        if self.source_stamp is None and not path.is_file():path=public_archive.DEFAULT
        elif self.public_cache is not None and self.public_cache.is_file():path=self.public_cache
        self.source_path=path
        try:
            stat=path.stat();stamp=(str(path),stat.st_mtime_ns,stat.st_size)
        except OSError:stamp=('unavailable',str(path))
        if stamp==self.source_stamp:return
        self.source_stamp=stamp;self.hover_card.dismiss();self.source_index=None;self.source_signature=None
        try:
            from hashlib import sha256
            raw=path.read_bytes();data=public_archive.validate(__import__('json').loads(raw));self.source_index=ItemSourceIndex(data);self.source_signature=sha256(raw).hexdigest()
        except(OSError,ValueError,TypeError,KeyError,AttributeError):data=None
        selected=self.version.currentData();self.version.blockSignals(True);self.version.clear()
        if data:
            for version in data['versions']:self.version.addItem(VERSION_LABELS.get(version,'来源范围 '+version),version)
            target=selected or data.get('default_version');index=self.version.findData(target)
            if index<0 and selected is not None:self.version.addItem('原资料范围已不可用',selected);index=self.version.count()-1
            self.version.setCurrentIndex(max(0,index))
        self.version.blockSignals(False)
    def refresh(self,*_):
        self.reload_sources()
        current=self.entries.currentItem();selected=current.data(Qt.ItemDataRole.UserRole)if current else None
        rows=inventory_rows(self.run.state,self.search.text(),self.held.isChecked(),rarity=self.rarity.currentData(),exchange=self.exchange.currentData(),kind=self.kind.currentData());self.rows={r['id']:r for r in rows or[]}
        render_key=repr(rows)
        if render_key!=self.render_key:self.render_rows(rows,selected);self.render_key=render_key
        if self.hover_card.identity not in self.rows:self.hover_card.dismiss()
        elif self.hover_card.isVisible():self.hover_card.install(self.rows[self.hover_card.identity],self.version.currentData(),self.source_index,self.source_signature)
        from .player_exchange_view import update_inventory_button
        update_inventory_button(self)
        complete=self.run.state.get('inventory_verified')is True
        self.status.setText('资料暂不可用，已清除旧列表。'if rows is None else f'找到{len(rows)}件。'+('本局收藏品已核对完整。'if complete else'本局尚未核对读全；未列出不代表没有。')+' 悬停查看所属池，点击阅读效果。说明基准：国服2026年10月16日；不是当前DLC完整目录或已生效证明。')
    def render_rows(self,rows,selected):
        offset=self.entries.verticalScrollBar().value()
        self.entries.blockSignals(True);self.entries.clear()
        for row in rows or[]:
            icon=Path(__file__).parent/'data/relic-icons'/((row['icon']or'')+'.png')
            item=QListWidgetItem(QIcon(str(icon))if icon.is_file()else QIcon(),row['name']+(' · 本局已确认'if row['held']else'')+' · '+RARITIES.get(row['rarity'],'未分档'))
            item.setData(Qt.ItemDataRole.UserRole,row['id']);self.entries.addItem(item)
            if row['id']==selected:self.entries.setCurrentItem(item)
        if selected not in self.rows:self.entries.setCurrentRow(-1)
        self.entries.verticalScrollBar().setValue(offset);self.entries.blockSignals(False);self.selected()
    def selected(self,*_):
        item=self.entries.currentItem();row=self.rows.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        self.reference_button.setEnabled(row is not None)
        from .player_exchange_view import update_inventory_button
        update_inventory_button(self)
        if not row:self.detail.clear();return
        exchange='资料允许交换'if row['exchange']is True else'资料不允许交换'if row['exchange']is False else'交换资格未确认'
        text=row['name']+' · '+RARITIES.get(row['rarity'],'未分档')+'\n\n效果说明\n'+(row['usage']or'暂无说明')+'\n\n'+exchange+'；实际能否交换仍需对应事件条件。'
        if self.detail.toPlainText()!=text:self.detail.setPlainText(text)
    def open_selected(self):
        item=self.entries.currentItem()
        if item and item.data(Qt.ItemDataRole.UserRole)in self.rows:self.openReference.emit(item.data(Qt.ItemDataRole.UserRole))
    def queue_hover(self,item):
        self.leave_timer.stop();self.hover_pending=item.data(Qt.ItemDataRole.UserRole);self.hover_timer.start()
    def show_hover(self):
        row=self.rows.get(self.hover_pending)
        if row is None or not self.isVisible():return
        if not self.hover_card.install(row,self.version.currentData(),self.source_index,self.source_signature):return
        self.hover_card.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,bool(self.window().windowFlags()&Qt.WindowType.WindowStaysOnTopHint));self.hover_card.show()
        rect=self.entries.visualItemRect(next(self.entries.item(i)for i in range(self.entries.count())if self.entries.item(i).data(Qt.ItemDataRole.UserRole)==row['id']))
        point=self.entries.viewport().mapToGlobal(rect.topRight());area=self.screen().availableGeometry()
        self.hover_card.move(max(area.left(),min(point.x()+10,area.right()-self.hover_card.width()+1)),max(area.top(),min(point.y(),area.bottom()-self.hover_card.height()+1)))
    def leave_hover(self):
        if not self.hover_card.pinned and not self.hover_card.underMouse():self.hover_card.hide()
    def eventFilter(self,obj,event):
        if event.type()==QEvent.Type.Leave:self.hover_timer.stop();self.leave_timer.start()
        return super().eventFilter(obj,event)
    def hideEvent(self,event):
        self.hover_timer.stop();self.leave_timer.stop();self.hover_card.hide();super().hideEvent(event)
    def closeEvent(self,event):self.hover_card.dismiss();super().closeEvent(event)
