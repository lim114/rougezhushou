"""Player-facing public pool and event reader, no personal data requests."""
from pathlib import Path
from threading import Thread
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,os
from PySide6.QtCore import Signal,Qt,QUrl
from PySide6.QtGui import QDesktopServices
from .view_catalog import relic_icon,relic_icon_note
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QComboBox,QListWidget,QListWidgetItem,QTableWidget,QTableWidgetItem,QPlainTextEdit,QPushButton,QTabWidget,QCheckBox,QSizePolicy
from . import public_archive as model
from .ui_state import replace_text
class ArchivePanel(QWidget):
    received=Signal(object)
    openReference=Signal(str,str)
    def __init__(self,cache,parent=None):
        super().__init__(parent);self.cache=Path(cache);self.data=None;self.busy=False;self.pool_by_id={};self.event_by_id={};self.selection_version=None;self.source_signature=None;self.member_context=None
        self.setWindowTitle('路标资料 · 本地查询');self.resize(760,650);body=QVBoxLayout(self);body.setContentsMargins(8,4,8,4);body.setSpacing(6)
        self.status=QLabel();self.status.setWordWrap(True);body.addWidget(self.status)
        self.tabs=QTabWidget();self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Ignored);body.addWidget(self.tabs,1)
        page=QWidget();layout=QVBoxLayout(page);bar=QHBoxLayout();self.version=QComboBox();self.pool_search=QLineEdit();self.pool_search.setPlaceholderText('搜索藏品、零件、效果或藏品池');bar.addWidget(self.version);bar.addWidget(self.pool_search,1);layout.addLayout(bar)
        self.pools=QListWidget();self.pools.setMaximumHeight(155);layout.addWidget(self.pools)
        self.sources=QComboBox();layout.addWidget(self.sources);self.pool_note=QPlainTextEdit();self.pool_note.setReadOnly(True);self.pool_note.setMaximumHeight(100);layout.addWidget(self.pool_note)
        self.members=QTableWidget(0,4);self.members.setHorizontalHeaderLabels(['物品','候选出现频率','出现次数／统计分母','效果说明']);self.members.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers);self.members.horizontalHeader().setStretchLastSection(True);layout.addWidget(self.members,1)
        self.tabs.addTab(page,'藏品与掉落')
        page=QWidget();layout=QVBoxLayout(page);bar=QHBoxLayout();self.floor=QComboBox()
        for i in range(1,7):self.floor.addItem(f'第{i}层',i)
        self.treehole=QCheckBox('树洞（按进入层数）');self.event_search=QLineEdit();self.event_search.setPlaceholderText('搜索事件名称或节点类型');bar.addWidget(self.floor);bar.addWidget(self.treehole);bar.addWidget(self.event_search,1);layout.addLayout(bar)
        self.events=QListWidget();self.events.setMaximumHeight(155);layout.addWidget(self.events,1);self.event_note=QPlainTextEdit();self.event_note.setReadOnly(True);layout.addWidget(self.event_note,1)
        self.event_button=QPushButton('打开对应事件原文与作战入口');self.event_button.clicked.connect(self.open_event);layout.addWidget(self.event_button);self.tabs.addTab(page,'节点事件')
        self.scope_note=QLabel();self.scope_note.setWordWrap(True);body.addWidget(self.scope_note);self.scope_note.hide();self.pool_note.hide()
        buttons=QHBoxLayout();self.update_button=QPushButton('更新公开资料');self.source_button=QPushButton('路标来源');self.scope=QCheckBox('资料说明');buttons.addWidget(self.update_button);buttons.addWidget(self.source_button);buttons.addWidget(self.scope);body.addLayout(buttons)
        self.scope.toggled.connect(self.scope_note.setVisible);self.scope.toggled.connect(self.pool_note.setVisible)
        for button in (self.update_button,self.source_button,self.event_button):button.setAutoDefault(False)
        self.update_button.clicked.connect(self.update_online);self.source_button.clicked.connect(lambda:QDesktopServices.openUrl(QUrl(model.SITE+'/pools/rogue_6')))
        self.pool_search.textChanged.connect(self.render_pools);self.version.currentIndexChanged.connect(self.render_pools);self.pools.currentItemChanged.connect(self.select_pool);self.sources.currentIndexChanged.connect(self.render_members)
        self.floor.currentIndexChanged.connect(self.render_events);self.treehole.toggled.connect(self.render_events);self.event_search.textChanged.connect(self.render_events);self.events.currentItemChanged.connect(self.select_event);self.received.connect(self.accept_data)
        self.loaded_path=self.cache if self.cache.is_file()else model.DEFAULT
        self.reload_local()
    def reload_local(self):
        path=self.cache if self.cache.is_file()else self.loaded_path
        try:
            raw=path.read_bytes();signature=(str(path),sha256(raw).hexdigest())
            if signature==self.source_signature:return True
            from .public_compendium import complete
            self.data=complete(model.validate(json.loads(raw)));self.loaded_path=path;self.source_signature=signature
        except(OSError,ValueError,KeyError,TypeError,AttributeError):self.data=None;self.source_signature=None
        self.install()
        return True
    def install(self):
        version=self.version.currentData();self.version.blockSignals(True);self.version.clear()
        if self.data:
            for key in self.data['versions']:self.version.addItem({'base':'本体资料','dlc1':'内容拓展一'}.get(key,'来源范围 '+key),key)
            self.version.setCurrentIndex(max(0,self.version.findData(version or self.data.get('default_version'))))
            self.status.setText('路标档案馆 · 本机资料');self.scope_note.setText(self.data['version_applicability'])
        else:self.status.setText('暂无公开资料，可点击更新');self.scope_note.clear()
        self.version.blockSignals(False);self.render_pools();self.render_events()
    def render_pools(self,*_):
        current=self.pools.currentItem();selected=current.data(Qt.ItemDataRole.UserRole)if current and self.selection_version==self.version.currentData()else None
        rows=model.pool_rows(self.data,self.version.currentData(),self.pool_search.text())if self.data else[];self.pool_by_id={r['id']:r for r in rows};self.selection_version=self.version.currentData()
        self.pools.blockSignals(True);self.pools.clear()
        for row in rows:
            bindings='、'.join(b['nodeName']for b in row.get('nodeBindings',[])if b.get('nodeName'))
            item=QListWidgetItem(row['name']+(' · '+bindings if bindings else'')+f" · {len(row['collectibles'])}种资料成员");item.setData(Qt.ItemDataRole.UserRole,row['id']);self.pools.addItem(item)
            if row['id']==selected:self.pools.setCurrentItem(item)
        if selected not in self.pool_by_id:self.pools.setCurrentRow(-1)
        self.pools.blockSignals(False);self.select_pool()
    def select_pool(self,*_):
        item=self.pools.currentItem();row=self.pool_by_id.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        old=self.sources.currentData();self.sources.blockSignals(True);self.sources.clear()
        for key,label,_ in model.distributions(row)if row else[]:self.sources.addItem(label,key)
        self.sources.setCurrentIndex(max(0,self.sources.findData(old)));self.sources.blockSignals(False);self.sources.setVisible(self.sources.count()>0)
        if row and not self.busy:self.status.setText('路标档案馆 · 本机资料')
        self.render_members()
    def select_exact_pool(self,version,identity):
        self.tabs.setCurrentIndex(0)
        current=self.pools.currentItem()
        if self.version.currentData()==version and current is not None and current.data(Qt.ItemDataRole.UserRole)==identity:return True
        index=self.version.findData(version)
        if index<0:
            self.pools.setCurrentRow(-1);self.select_pool();self.status.setText('暂无所选范围的藏品池资料');return False
        self.version.setCurrentIndex(index);self.pool_search.clear();self.render_pools()
        for row in range(self.pools.count()):
            item=self.pools.item(row)
            if item.data(Qt.ItemDataRole.UserRole)==identity:self.pools.setCurrentItem(item);return True
        self.pools.setCurrentRow(-1);self.select_pool();self.status.setText('暂无所选藏品池资料');return False
    def render_members(self,*_):
        item=self.pools.currentItem();pool=self.pool_by_id.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        context=(self.version.currentData(),pool['id']if pool else None,self.sources.currentData());same=context==self.member_context
        current=self.members.currentItem();selected=self.members.item(current.row(),0).data(Qt.ItemDataRole.UserRole)if same and current else None
        column=current.column()if same and current else 0;vertical=self.members.verticalScrollBar().value()if same else 0;horizontal=self.members.horizontalScrollBar().value()if same else 0
        self.members.setRowCount(0);self.member_context=context
        if pool is None:self.pool_note.clear();return
        distribution=next((d for k,_,d in model.distributions(pool)if k==self.sources.currentData()),None)
        notes=['统计口径：候选出现频率，各来源分别展示。']
        updated=(distribution or{}).get('updatedAt')
        try:updated=datetime.fromisoformat(updated.replace('Z','+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')if updated else'来源未记录'
        except(ValueError,TypeError,AttributeError):updated='来源未记录'
        if distribution:notes += ['统计记录：'+str(distribution.get('sampleCount','未说明'))+'；更新时间：'+updated,'适用口径：'+str(distribution.get('scopeLabel')or distribution.get('observationSource')or'来源未说明'),str(distribution.get('notes')or'')]
        else:notes+=['该池暂无可核对的出现频率，概率未知。']
        replace_text(self.pool_note,'\n'.join(notes).replace('archive累计','归档累计').replace('观测边际分布','按候选出现次数统计的比例').replace('同局相关性','同一局内结果的关联'),preserve=same)
        rows=model.members(self.data,pool,distribution,version=self.version.currentData());has_statistics=any(row['rate']is not None for row in rows)
        self.members.setColumnHidden(1,not has_statistics);self.members.setColumnHidden(2,not has_statistics)
        for row in rows:
            i=self.members.rowCount();self.members.insertRow(i)
            values=[row['name'],f"{row['rate']:.2%}"if row['rate']is not None else'未知',f"{row['count']}／{row['total']}"if row['rate']is not None else'未核对',row['effect']]
            for j,value in enumerate(values):cell=QTableWidgetItem(value);cell.setToolTip(value);self.members.setItem(i,j,cell)
            icon=row.get('icon')or'';self.members.item(i,0).setIcon(relic_icon(icon))
            self.members.item(i,0).setData(Qt.ItemDataRole.UserRole,row['id'])
            if row['id']==selected:self.members.setCurrentCell(i,column)
            note=relic_icon_note(icon)
            if note:self.members.item(i,0).setToolTip(row['name']+'\n'+note)
        self.members.resizeColumnsToContents();self.members.setColumnWidth(3,280);self.members.resizeRowsToContents()
        self.members.verticalScrollBar().setValue(vertical);self.members.horizontalScrollBar().setValue(horizontal)
    def render_events(self,*_):
        current=self.events.currentItem();selected=current.data(Qt.ItemDataRole.UserRole)if current else None
        rows=model.event_rows(self.data,self.floor.currentData()or 1,self.treehole.isChecked(),self.event_search.text())if self.data else[]
        self.event_by_id={r['id']:r for r in rows};self.events.blockSignals(True);self.events.clear()
        for row in rows:
            item=QListWidgetItem(row['classification']+' · '+row['name']);item.setData(Qt.ItemDataRole.UserRole,row['id']);self.events.addItem(item)
            if row['id']==selected:self.events.setCurrentItem(item)
        if selected not in self.event_by_id:self.events.setCurrentRow(-1)
        self.events.blockSignals(False);self.select_event()
    def select_event(self,*_):
        item=self.events.currentItem();row=self.event_by_id.get(item.data(Qt.ItemDataRole.UserRole))if item else None;self.event_button.setEnabled(row is not None)
        if not row:self.event_note.clear();return
        if not self.busy:self.status.setText('路标档案馆 · 本机资料')
        lines=[row['name'],'节点：'+row['classification'],row['condition']]
        if row.get('repeatable')is True:lines.append('资料允许重复出现。')
        if row['prerequisites']:lines.append('需要前置事件，详见事件原文。')
        replace_text(self.event_note,'\n\n'.join(lines))
    def reference_context(self):
        item=self.events.currentItem();row=self.event_by_id.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        if self.data is None or self.tabs.currentIndex()!=1 or row is None:return None
        return {'event':row,'floor':self.floor.currentData(),'treehole':self.treehole.isChecked(),'source':str(self.loaded_path)}
    def open_event(self):
        item=self.events.currentItem();row=self.event_by_id.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        if row:self.openReference.emit('scenes',row['id'].split(':',1)[-1])
    def update_online(self):
        if self.busy:return
        self.busy=True;self.update_button.setEnabled(False);self.status.setText('正在更新公开资料…')
        def worker():
            try:result={'data':model.fetch()}
            except Exception as e:result={'error':str(e)}
            self.received.emit(result)
        Thread(target=worker,daemon=True).start()
    def accept_data(self,result):
        self.busy=False;self.update_button.setEnabled(True)
        if 'error'in result:self.install();self.status.setText(self.status.text()+' 更新失败，未替换离线资料。');return
        try:
            data=model.validate(result['data']);self.cache.parent.mkdir(parents=True,exist_ok=True);tmp=self.cache.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8');os.replace(tmp,self.cache)
        except(OSError,ValueError,KeyError,TypeError):self.status.setText('新资料无法核对或保存，未替换旧数据。');return
        self.reload_local()
