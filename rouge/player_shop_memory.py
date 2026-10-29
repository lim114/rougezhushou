"""Partial shop names observed in this run; never inventory or purchase claims."""
import time
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
        if not isinstance(row,dict):return None
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

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QComboBox,QListWidgetItem,QPlainTextEdit
from pathlib import Path
from .player_catalog_grid import CatalogGrid,add_catalog_controls
class ShopMemoryPanel(QWidget):
    def __init__(self,run):
        super().__init__();self.run=run;self.signature=None;self.rows={};body=QVBoxLayout(self);self.notice=QLabel();self.notice.setWordWrap(True);body.addWidget(self.notice);self.snapshots=QComboBox();body.addWidget(self.snapshots);self.entries=CatalogGrid();body.addWidget(self.entries,1);self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1);self.details_toggle,self.icon_scale=add_catalog_controls(body,self.entries,self.detail);self.snapshots.currentIndexChanged.connect(self.show_snapshot);self.entries.currentItemChanged.connect(self.selected);self.refresh()
    def refresh(self):
        from .player_replay import observation_time
        rows=[(i,r)for i,r in enumerate(self.run.state.get('history',[]))if isinstance(r,dict)and r.get('kind')=='shop_items_read'and qualified(r)]
        signature=(self.run.state.get('id'),rows,self.run.save_issue)
        if signature==self.signature:return
        same=self.signature and self.signature[0]==signature[0];old=self.snapshots.currentData()if same else None;self.signature=deepcopy(signature);self.rows=dict(rows);self.snapshots.blockSignals(True);self.snapshots.clear()
        for i,row in reversed(rows):self.snapshots.addItem(observation_time(row.get('at'))+' · '+str(len(row['items']))+'件已读名称',i)
        self.snapshots.setCurrentIndex(self.snapshots.findData(old)if old in self.rows else 0 if rows else-1);self.snapshots.blockSignals(False);self.show_snapshot()
        self.notice.setText(('记录暂未保存到本机。'if self.run.save_issue else'')+'仅保留本局可确认的商店商品名称，可能未读全；不代表已经购买或持有。价格、剩余刷新次数及当前是否仍在售：未读。')
    def show_snapshot(self,*_):
        from .expansion_reference import packet
        public=packet();row=self.rows.get(self.snapshots.currentData())or{};old=self.entries.currentItem();keep=old.data(Qt.ItemDataRole.UserRole)if old else None;self.entries.blockSignals(True);self.entries.clear()
        if public:
            for record in row.get('items',[]):
                item=public['current']['details']['items'].get(record['id'])or{};path=Path(__file__).with_name('data')/'relic-icons'/((item.get('iconId')or'')+'.png');entry=QListWidgetItem(QIcon(str(path))if path.is_file()else QIcon(),record['name']);entry.setData(Qt.ItemDataRole.UserRole,record['id']);self.entries.addItem(entry)
                if keep==record['id']:self.entries.setCurrentItem(entry)
        self.entries.blockSignals(False);self.entries._selected(self.entries.currentItem());self.selected()
    def selected(self,*_):
        from .expansion_reference import packet,_plain
        public=packet();entry=self.entries.currentItem();identity=entry.data(Qt.ItemDataRole.UserRole)if entry else None;item=public['current']['details']['items'].get(identity)if public else None
        self.detail.setPlainText(item['name']+'\n\n资料效果\n'+_plain(item.get('usage'))+'\n\n这是当时读到的名称，不证明持有、购买或当前仍在售。'if item else'选择已读商品查看效果。')
        if not item:self.details_toggle.setChecked(False)
