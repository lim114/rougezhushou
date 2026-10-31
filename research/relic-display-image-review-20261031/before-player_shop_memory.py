"""Partial shop names observed in this run; never inventory or purchase claims."""
import time
import math
from copy import deepcopy
from .player_shop_hover import canonical

def qualified(snapshot):
    from .expansion_reference import packet
    if not isinstance(snapshot,dict)or snapshot.get('source')!='fresh_shop_exact_names'or snapshot.get('complete')is not False:return None
    public=packet()
    if public is None:return None
    rows=snapshot.get('items')
    if not isinstance(rows,list)or not rows:return None
    result=[];seen=set()
    for row in rows:
        if not isinstance(row,dict)or not isinstance(row.get('id'),str)or not isinstance(row.get('name'),str):return None
        item=public['current']['details']['items'].get(row.get('id'))
        if not item or canonical(item['name'])!=canonical(row.get('name'))or row['id']in seen:return None
        seen.add(row['id']);result.append({'id':row['id'],'name':item['name']})
    return result

def remember(run,snapshot,expected_run,at):
    if run.state.get('id')!=expected_run or type(at)not in(int,float)or not 0<=time.time()-at<=2:return False
    rows=qualified(snapshot)
    if rows is None:return False
    previous=next((r for r in reversed(run.state.get('history',[]))if r.get('kind')=='shop_items_read'),None)
    if previous and previous.get('items')==rows:return False
    run.state['history'].append({'kind':'shop_items_read','at':at,'source':'fresh_shop_exact_names','items':rows,'complete':False});return run.save()

def recorded_shops(state):
    """Keep observation order; timestamps and the absence of an item prove no sale."""
    result=[]
    for position,row in enumerate(state.get('history',[])):
        if not isinstance(row,dict)or row.get('kind')!='shop_items_read':continue
        at=row.get('at')
        if type(at)not in(int,float)or not math.isfinite(at)or at<0:continue
        items=qualified(row)
        if items is not None:result.append((position,{**row,'items':items}))
    return result

def compare_shops(rows,selected):
    index=next((i for i,(key,_)in enumerate(rows)if key==selected),None)
    if index is None:return None
    current=rows[index][1]['items']
    if index==0:return {'previous':None,'first':current,'added':[],'unread':[],'both':[]}
    previous=rows[index-1][1]['items'];old={r['id']for r in previous};now={r['id']for r in current}
    return {'previous':rows[index-1][0],'first':[],
        'added':[r for r in current if r['id']not in old],
        'unread':[r for r in previous if r['id']not in now],
        'both':[r for r in current if r['id']in old]}

def comparison_text(comparison):
    if comparison is None:return '尚无可比较的商店读取记录。'
    if comparison['previous']is None:return '这是本局第一份可用商店清单，尚无前次记录可对照。'
    lines=['与前一份已读清单对照']
    for key,label in(('added','本次新读到'),('unread','前次读到、本次未读到'),('both','两次都读到')):
        lines.append(label+'：'+('、'.join(r['name']for r in comparison[key])or'无'))
    return '\n'.join(lines)+'\n\n两次清单可能没有读全，也可能来自不同商店。未读到不等于已购买或下架，变化不证明刷新。'

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QComboBox,QListWidgetItem,QPlainTextEdit,QLineEdit,QPushButton
from pathlib import Path
from .player_catalog_grid import CatalogGrid,add_catalog_controls
class ShopMemoryPanel(QWidget):
    def __init__(self,run,source_panel=None):
        super().__init__();self.run=run;self.source_panel=source_panel;self.signature=None;self.rows={};body=QVBoxLayout(self);self.notice=QLabel();self.notice.setWordWrap(True);body.addWidget(self.notice);self.snapshots=QComboBox();body.addWidget(self.snapshots)
        self.search=QLineEdit();self.search.setPlaceholderText('在这份已读清单中搜索商品');body.addWidget(self.search)
        self.comparison=QLabel();self.comparison.setWordWrap(True);body.addWidget(self.comparison)
        self.entries=CatalogGrid();body.addWidget(self.entries,1);self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1);self.details_toggle,self.icon_scale=add_catalog_controls(body,self.entries,self.detail)
        self.source_button=QPushButton('查看所选商品的取得来源与历史统计');body.addWidget(self.source_button)
        from .player_item_hover import ItemHoverCard
        self.source_card=ItemHoverCard(self)
        if source_panel is not None:self.source_card.poolRequested.connect(source_panel.openPoolReference)
        self.source_button.clicked.connect(self.open_source);self.search.textChanged.connect(self.show_snapshot);self.snapshots.currentIndexChanged.connect(self.show_snapshot);self.entries.currentItemChanged.connect(self.selected);self.refresh()
    def refresh(self):
        from .player_replay import observation_time
        rows=recorded_shops(self.run.state)
        if self.source_panel is not None:self.source_panel.reload_sources()
        source_key=(self.source_panel.source_signature,self.source_panel.version.currentData())if self.source_panel is not None else None
        signature=(self.run.state.get('id'),rows,self.run.save_issue,source_key)
        if signature==self.signature:return
        same=self.signature and self.signature[0]==signature[0];old=self.snapshots.currentData()if same else None;self.source_card.dismiss();self.signature=deepcopy(signature);self.rows=dict(rows);self.snapshots.blockSignals(True);self.snapshots.clear()
        if not same:self.search.blockSignals(True);self.search.clear();self.search.blockSignals(False)
        for i,row in reversed(rows):self.snapshots.addItem(observation_time(row.get('at'))+' · '+str(len(row['items']))+'件已读名称',i)
        self.snapshots.setCurrentIndex(self.snapshots.findData(old)if old in self.rows else 0 if rows else-1);self.snapshots.blockSignals(False);self.show_snapshot()
        self.notice.setText(('记录暂未保存到本机。'if self.run.save_issue else'')+'仅保留本局可确认的商店商品名称，可能未读全；不代表已经购买或持有。价格、剩余刷新次数及当前是否仍在售：未读。')
    def show_snapshot(self,*_):
        from .expansion_reference import packet
        public=packet();row=self.rows.get(self.snapshots.currentData())or{};old=self.entries.currentItem();keep=old.data(Qt.ItemDataRole.UserRole)if old else None;self.entries.blockSignals(True);self.entries.clear();self.source_card.dismiss()
        comparison=compare_shops(list(self.rows.items()),self.snapshots.currentData());self.comparison.setText(comparison_text(comparison));query=self.search.text().strip().casefold()
        if public:
            for record in row.get('items',[]):
                if query and query not in record['name'].casefold():continue
                item=public['current']['details']['items'].get(record['id'])or{};path=Path(__file__).with_name('data')/'relic-icons'/((item.get('iconId')or'')+'.png');entry=QListWidgetItem(QIcon(str(path))if path.is_file()else QIcon(),record['name']);entry.setData(Qt.ItemDataRole.UserRole,record['id']);self.entries.addItem(entry)
                if keep==record['id']:self.entries.setCurrentItem(entry)
        self.entries.blockSignals(False);self.entries._selected(self.entries.currentItem());self.selected()
    def selected(self,*_):
        from .expansion_reference import packet,_plain
        public=packet();entry=self.entries.currentItem();identity=entry.data(Qt.ItemDataRole.UserRole)if entry else None;item=public['current']['details']['items'].get(identity)if public else None
        self.source_button.setEnabled(item is not None)
        self.detail.setPlainText(item['name']+'\n\n资料效果\n'+_plain(item.get('usage'))+'\n\n这是当时读到的名称，不证明持有、购买或当前仍在售。'if item else'选择已读商品查看效果。')
        if not item:self.details_toggle.setChecked(False)
    def open_source(self):
        from .expansion_reference import packet
        self.refresh();entry=self.entries.currentItem();identity=entry.data(Qt.ItemDataRole.UserRole)if entry else None
        public=packet();item=public['current']['details']['items'].get(identity)if public else None
        if item is None:return
        source=self.source_panel
        if source is not None:source.reload_sources()
        self.source_card.dismiss()
        self.source_card.install({'id':identity,'name':item['name'],'icon':item.get('iconId')},source.version.currentData()if source else None,source.source_index if source else None,source.source_signature if source else None)
        self.source_card.show()
        area=self.screen().availableGeometry();point=self.mapToGlobal(self.rect().topLeft())
        self.source_card.move(max(area.left(),min(point.x(),area.right()-self.source_card.width()+1)),max(area.top(),min(point.y(),area.bottom()-self.source_card.height()+1)))
    def hideEvent(self,event):
        self.source_card.dismiss();super().hideEvent(event)
