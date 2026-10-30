"""Read-only picture inventory, with held facts distinct from source descriptions."""
from pathlib import Path
from PySide6.QtCore import Qt,QSize,Signal,QTimer,QEvent
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QCheckBox,QLabel,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton,QComboBox,QGridLayout,QSlider,QSplitter,QButtonGroup
from . import expansion_reference as reference
from .record_flags import active_record

RARITIES={'NORMAL':'低稀有度 · N','RARE':'中稀有度 · R','SUPER_RARE':'高稀有度 · SR','NONE':'未分档'}

def source_nodes(public_data,version):
    result={}
    for pool in (public_data or{}).get('versions',{}).get(version,[]):
        bindings=pool.get('nodeBindings');bindings=bindings if isinstance(bindings,list)else[]
        names=list(dict.fromkeys(b['nodeName']for b in bindings if isinstance(b,dict)and isinstance(b.get('nodeName'),str)and b['nodeName'].strip()))
        for identity in pool['collectibles']:
            result.setdefault(identity,[])
            result[identity]=list(dict.fromkeys([*result[identity],*names]))
    return result

def inventory_rows(state,query='',held_only=True,*,rarity=None,exchange=None,kind=None,public_data=None,version=None,category=None,access=None,source_node=None,packet=...):
    packet=reference.packet() if packet is ... else packet
    if packet is None:return None
    from .public_compendium import resolve,effect_text
    docs=resolve(public_data,version,packet) if public_data is not None else {}
    held={key for key,row in state.get('relics',{}).items()if active_record(row,'held')}
    result=[];q=query.strip().casefold();nodes=source_nodes(public_data,version)
    for row in reference.rows('relics',changes_only=False,reference=packet):
        item=row['value'].get('item')or{}
        if item.get('type')not in ('RELIC','LEGACY'):continue
        doc=docs.get(row['id']);usage=effect_text(doc.get('effect') if doc else item.get('usage'))
        if category is not None and (doc or{}).get('category')!=category:continue
        if held_only and row['id']not in held:continue
        search_text=row['name']+' '+usage
        if doc:search_text+=' '+reference._plain(doc.get('unlockConditionText'))+' '+reference._plain(doc.get('obtainMethod'))
        if q and q not in search_text.casefold():continue
        if access=='unlock'and not(doc and(doc.get('unlockConditional')is True or reference._plain(doc.get('unlockConditionText')).strip())):continue
        if access=='special'and not(doc and(doc.get('specialAccess')is True or reference._plain(doc.get('obtainMethod')).strip())):continue
        if access=='uncovered'and doc is not None:continue
        if access not in(None,'unlock','special','uncovered'):continue
        if source_node is not None and source_node not in nodes.get(row['id'],[]):continue
        if rarity is not None and item.get('rarity')!=rarity:continue
        if exchange is not None and item.get('canSacrifice')is not exchange:continue
        if kind is not None and item.get('type')!=kind:continue
        result.append({'id':row['id'],'name':row['name'],'usage':usage,'held':row['id']in held,
            'icon':item.get('iconId'),'exchange':item.get('canSacrifice'),'rarity':item.get('rarity'),'kind':item.get('type'),'compendium':doc,'category':(doc or{}).get('category'),'source_nodes':nodes.get(row['id'],[])})
    return result

class InventoryPanel(QWidget):
    openReference=Signal(str)
    openPoolReference=Signal(str,str)
    openExchangeReference=Signal(str,str)
    def __init__(self,run,public_cache=None):
        super().__init__();self.run=run;self.rows={};self.public_cache=Path(public_cache)if public_cache is not None else None;self.source_stamp=None;self.source_signature=None;self.source_index=None;self.render_key=None;body=QVBoxLayout(self)
        bar=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('搜索藏品名称、效果或取得条件，如攻击、独活')
        self.held=QCheckBox('只看本局已确认持有');self.held.setChecked(True);bar.addWidget(self.search,1);bar.addWidget(self.held);self.more=QPushButton('更多筛选');self.more.setCheckable(True);bar.addWidget(self.more);body.addLayout(bar)
        self.filter_box=QWidget();filters=QGridLayout(self.filter_box);self.rarity=QComboBox();self.rarity.addItem('全部稀有度',None)
        for key,label in RARITIES.items():self.rarity.addItem(label,key)
        self.exchange=QComboBox();self.exchange.addItem('全部交换资格',None);self.exchange.addItem('资料允许交出',True);self.exchange.addItem('资料不允许交出',False)
        self.kind=QComboBox();self.kind.addItem('全部类别',None);self.kind.addItem('收藏品','RELIC');self.kind.addItem('开局助力','LEGACY')
        self.version=QComboBox();self.version.setToolTip('切换所属池与已核对的版本图鉴说明；未收录的条目保留固定国服说明，并逐项标明。不是本局生效证明。')
        for i,widget in enumerate((self.exchange,self.kind,self.version)):filters.addWidget(widget,i//2,i%2)
        self.category=QComboBox();self.category.addItem('全部游戏内类别',None);filters.addWidget(self.category,1,1)
        self.access=QComboBox();self.access.addItem('全部取得说明',None);self.access.addItem('资料标注解锁条件','unlock');self.access.addItem('资料标注特殊取得','special');self.access.addItem('所选图鉴未收录','uncovered')
        self.access.setToolTip('按来源标记和原文筛选，不判断本局是否已解锁或可以领取。');filters.addWidget(self.access,2,0)
        self.source_node=QComboBox();self.source_node.addItem('全部关联节点',None);self.source_node.setToolTip('所选资料明确关联的节点，不是当前地图的可取得保证；未列不表示无法取得。');filters.addWidget(self.source_node,2,1)
        body.addWidget(self.filter_box);self.filter_box.hide();self.more.toggled.connect(self.filter_box.setVisible)
        self.status=QLabel();self.status.setWordWrap(True);body.addWidget(self.status)
        from .player_catalog_grid import CatalogGrid
        self.entries=CatalogGrid();self.splitter=QSplitter(Qt.Orientation.Horizontal);self.splitter.addWidget(self.entries);body.addWidget(self.splitter,1)
        self.reader=QWidget();reader=QVBoxLayout(self.reader);reader.setContentsMargins(8,0,0,0)
        self.hide_reader=QPushButton('收起说明');reader.addWidget(self.hide_reader)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);reader.addWidget(self.detail,1)
        self.splitter.addWidget(self.reader);self.splitter.setSizes([650,310]);self.reader.hide();self.hide_reader.clicked.connect(self.reader.hide)
        bottom=QHBoxLayout();bottom.addWidget(QLabel('稀有度'));self.rarity_buttons=QButtonGroup(self);self.rarity_buttons.setExclusive(True)
        for i,label in enumerate(('全部','N','R','SR','未分档')):
            button=QPushButton(label);button.setCheckable(True);button.setChecked(i==0);self.rarity_buttons.addButton(button,i);bottom.addWidget(button)
        self.rarity_buttons.idClicked.connect(self.rarity.setCurrentIndex);self.rarity.hide()
        self.rarity.currentIndexChanged.connect(lambda i:self.rarity_buttons.button(i).setChecked(True))
        bottom.addStretch();bottom.addWidget(QLabel('图标大小'));self.icon_scale=QSlider(Qt.Orientation.Horizontal);self.icon_scale.setRange(48,104);self.icon_scale.setValue(72);self.icon_scale.setMaximumWidth(160);bottom.addWidget(self.icon_scale);self.icon_scale.valueChanged.connect(self.entries.set_tile_size);body.addLayout(bottom)
        self.reference_button=QPushButton('查看取得来源与相关查询');body.addWidget(self.reference_button)
        self.exchange_button=QPushButton('查看此提供物对应的换入候选');body.addWidget(self.exchange_button);self.exchange_button.setVisible(False)
        from .player_exchange_view import request_inventory
        self.exchange_button.clicked.connect(lambda:request_inventory(self))
        self.reference_button.clicked.connect(self.open_selected);self.entries.currentItemChanged.connect(self.selected);self.entries.itemClicked.connect(lambda _:(self.reader.show(),self.splitter.setSizes([500,310])))
        from .player_item_hover import ItemHoverCard
        self.hover_card=ItemHoverCard(self);self.hover_card.poolRequested.connect(self.openPoolReference)
        self.hover_pending=None;self.hover_timer=QTimer(self);self.hover_timer.setSingleShot(True);self.hover_timer.setInterval(180);self.hover_timer.timeout.connect(self.show_hover)
        self.leave_timer=QTimer(self);self.leave_timer.setSingleShot(True);self.leave_timer.setInterval(220);self.leave_timer.timeout.connect(self.leave_hover)
        self.entries.setMouseTracking(True);self.entries.viewport().installEventFilter(self);self.entries.itemEntered.connect(self.queue_hover)
        self.hover_card.entered.connect(self.leave_timer.stop);self.hover_card.left.connect(self.leave_timer.start)
        self.search.textChanged.connect(self.refresh);self.held.toggled.connect(self.refresh)
        for widget in(self.rarity,self.exchange,self.kind,self.version,self.category,self.access,self.source_node):widget.currentIndexChanged.connect(self.refresh)
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
        from .public_compendium import complete
        data=complete(self.source_index.data) if self.source_index else None
        packet=reference.packet()
        available=inventory_rows({},held_only=False,public_data=data,version=self.version.currentData(),packet=packet)
        nodes=list(dict.fromkeys(n for row in available or[]for n in row['source_nodes']))
        if [self.source_node.itemData(i)for i in range(1,self.source_node.count())]!=nodes:
            prior=self.source_node.currentData();self.source_node.blockSignals(True);self.source_node.clear();self.source_node.addItem('全部关联节点',None)
            for name in nodes:self.source_node.addItem(name,name)
            index=self.source_node.findData(prior)
            if prior is not None and index<0:self.source_node.addItem('原节点在此范围无资料',prior);index=self.source_node.count()-1
            self.source_node.setCurrentIndex(max(0,index));self.source_node.blockSignals(False)
        categories=list(dict.fromkeys(r['category'] for r in available or[] if r.get('category')))
        options=[self.category.itemData(i) for i in range(1,self.category.count())]
        if options!=categories:
            prior=self.category.currentData();self.category.blockSignals(True);self.category.clear();self.category.addItem('全部游戏内类别',None)
            for label in categories:self.category.addItem(label,label)
            index=self.category.findData(prior)
            if prior is not None and index<0:self.category.addItem('原类别在此范围无资料',prior);index=self.category.count()-1
            self.category.setCurrentIndex(max(0,index));self.category.blockSignals(False)
        current=self.entries.currentItem();selected=current.data(Qt.ItemDataRole.UserRole)if current else None
        rows=inventory_rows(self.run.state,self.search.text(),self.held.isChecked(),rarity=self.rarity.currentData(),exchange=self.exchange.currentData(),kind=self.kind.currentData(),public_data=data,version=self.version.currentData(),category=self.category.currentData(),access=self.access.currentData(),source_node=self.source_node.currentData(),packet=packet);self.rows={r['id']:r for r in rows or[]}
        render_key=repr(rows)
        if render_key!=self.render_key:self.render_rows(rows,selected);self.render_key=render_key
        if self.hover_card.identity not in self.rows:self.hover_card.dismiss()
        elif self.hover_card.isVisible():self.hover_card.install(self.rows[self.hover_card.identity],self.version.currentData(),self.source_index,self.source_signature)
        from .player_exchange_view import update_inventory_button
        update_inventory_button(self)
        complete=self.run.state.get('inventory_verified')is True
        self.status.setText('资料暂不可用，已清除旧列表。'if rows is None else f'找到{len(rows)}件。'+('本局收藏品已核对完整。'if complete else'本局尚未核对读全；未列出不代表没有。')+' 悬停查看所属池，点击阅读效果与取得条件。拓展一图鉴按所选范围显示；其它条目另注明固定基准。不是当前DLC完整目录或已生效证明。')
        if rows is not None and data is None:self.status.setText('公开图鉴暂不可用；下方只显示固定国服说明，未沿用旧的图鉴或掉落资料。'+self.status.text())
        if self.access.currentData()or self.source_node.currentData():self.status.setText(self.status.text()+' 当前按来源说明筛选，不判断本局解锁、可选或必掉；未收录不表示没有取得途径。')
    def render_rows(self,rows,selected):
        offset=self.entries.verticalScrollBar().value()
        self.entries.blockSignals(True);self.entries.clear()
        for row in rows or[]:
            icon=Path(__file__).parent/'data/relic-icons'/((row['icon']or'')+'.png')
            item=QListWidgetItem(QIcon(str(icon))if icon.is_file()else QIcon(),row['name'])
            item.setToolTip(row['name']+' · '+RARITIES.get(row['rarity'],'未分档')+(' · 本局已确认'if row['held']else' · 资料条目'));item.setData(Qt.ItemDataRole.UserRole,row['id']);self.entries.addItem(item)
            if row['id']==selected:self.entries.setCurrentItem(item)
        if selected not in self.rows:self.entries.setCurrentRow(-1)
        self.entries.verticalScrollBar().setValue(offset);self.entries.blockSignals(False);self.entries._selected(self.entries.currentItem());self.selected()
    def selected(self,*_):
        item=self.entries.currentItem();row=self.rows.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        self.reference_button.setEnabled(row is not None)
        from .player_exchange_view import update_inventory_button
        update_inventory_button(self)
        if not row:self.detail.clear();self.reader.hide();return
        if self.sender()is self.entries:self.reader.show();self.splitter.setSizes([500,310])
        exchange='资料允许交换'if row['exchange']is True else'资料不允许交换'if row['exchange']is False else'交换资格未确认'
        text=row['name']+' · '+RARITIES.get(row['rarity'],'未分档')+'\n\n效果说明\n'+(row['usage']or'暂无说明')+'\n\n'+exchange+'；实际能否交换仍需对应事件条件。'
        doc=row.get('compendium')
        if doc:
            text=row['name']+' · '+(row.get('category')or'未分类')+'\n\n效果说明\n'+(row['usage']or'来源未说明')
            text+='\n\n取得与解锁\n'+(reference._plain(doc.get('unlockConditionText'))or'来源未列解锁条件；不等于本局已解锁。')
            if doc.get('obtainMethod'):text+='\n'+reference._plain(doc['obtainMethod'])
            text+='\n\n'+exchange+'；实际能否交换仍需对应事件条件。'
            if doc.get('description'):text+='\n\n藏品简介\n'+reference._plain(doc['description'])
            text+='\n\n说明来源：路标档案馆 · 拓展一图鉴。列出的分档效果不代表本局当前档位；持有、解锁与生效均需另行确认。'
        else:text+='\n\n说明来源：固定国服2026年10月16日；所选图鉴未确认收录此条，不能视为该范围完整说明。'
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
