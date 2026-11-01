"""A read-only public-frequency reader. Never transmits a local map or query."""
from pathlib import Path
from threading import Thread
from datetime import datetime
from PySide6.QtCore import Signal,Qt,QSignalBlocker
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,QPushButton,QTableWidget,QTableWidgetItem,QCheckBox
from . import public_node_statistics as model
class StatisticsPanel(QWidget):
    received=Signal(object)
    def __init__(self,cache,parent=None,*,source=None):
        from .node_statistics_source import NodeStatisticsSource
        super().__init__(parent);self.cache=Path(cache);self.source=source or NodeStatisticsSource(cache,self);self.busy=False;self.render_key=object();self.query_key=None
        body=QVBoxLayout(self);body.setContentsMargins(8,4,8,4);body.setSpacing(6);self.status=QLabel();self.status.setWordWrap(True);body.addWidget(self.status)
        bar=QHBoxLayout();self.floor=QComboBox()
        for key,label in [('0','第一层'),('1','第二层'),('2','第三层'),('3','第四层'),('remembrance','第四层·追忆'),('4','第五层')]:self.floor.addItem(label,key)
        self.distance=QSpinBox();self.distance.setRange(0,100);self.distance.setValue(1)
        bar.addWidget(self.floor);bar.addWidget(QLabel('距本层初始入口'));bar.addWidget(self.distance);bar.addWidget(QLabel('步'));body.addLayout(bar)
        self.context=QLabel('手动查询');self.context.setWordWrap(True);body.addWidget(self.context)
        self.table=QTableWidget(0,4);self.table.setHorizontalHeaderLabels(['节点类型','历史出现比例','出现次数','同位置样本']);self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers);self.table.horizontalHeader().setStretchLastSection(True);body.addWidget(self.table,1)
        self.notice=QLabel('统计范围：同层、距入口步数相同的历史节点。分母为该位置所有已统计节点；当前版本适用范围待核对。');self.notice.setWordWrap(True);body.addWidget(self.notice);self.notice.hide()
        buttons=QHBoxLayout();self.refresh_button=QPushButton('更新公开统计');self.website_button=QPushButton('查看数据来源');self.scope=QCheckBox('资料说明');buttons.addWidget(self.refresh_button);buttons.addWidget(self.website_button);buttons.addWidget(self.scope);body.addLayout(buttons)
        self.scope.toggled.connect(self.notice.setVisible)
        for button in(self.refresh_button,self.website_button):button.setAutoDefault(False)
        self.refresh_button.clicked.connect(self.refresh_online);self.website_button.clicked.connect(lambda:QDesktopServices.openUrl(QUrl(model.PAGE)))
        self.floor.currentIndexChanged.connect(self.manual_query);self.distance.valueChanged.connect(self.manual_query);self.received.connect(self.accept_data)
        self.source.changed.connect(self.render)
        self.render()
    @property
    def data(self):return self.source.data
    def manual_query(self,*_):
        self.context.setText('手动查询：'+self.floor.currentText()+f' · 距入口{self.distance.value()}步');self.render()
    def render(self,*_):
        query=(self.floor.currentData(),self.distance.value());key=(self.source.index.identity,*query)
        if key==self.render_key:return True
        same=query==self.query_key;current=self.table.currentItem();selected=self.table.item(current.row(),0).data(Qt.ItemDataRole.UserRole)if same and current else None
        column=current.column()if same and current else 0;vertical=self.table.verticalScrollBar().value()if same else 0;horizontal=self.table.horizontalScrollBar().value()if same else 0
        self.render_key=key;self.query_key=query
        self.table.setRowCount(0)
        if self.data is None:self.source_label='暂无公开统计，可点击更新';self.status.setText(self.source_label);return True
        rows=self.source.index.rows(*query)
        meta=self.source.index.metadata;date=datetime.fromisoformat(meta['updatedAt'].replace('Z','+00:00')).astimezone().strftime('%Y-%m-%d %H:%M')
        self.source_label=f"路标档案馆 · 更新于{date} · {meta['sampleCount']:,}条节点记录"
        for row in rows:
            i=self.table.rowCount();self.table.insertRow(i)
            for j,text in enumerate([row['name'],f"{row['frequency']:.2%}",str(row['count']),str(row['total'])]):self.table.setItem(i,j,QTableWidgetItem(text))
            self.table.item(i,0).setData(Qt.ItemDataRole.UserRole,row['type'])
            if row['type']==selected:self.table.setCurrentCell(i,column)
        self.table.resizeColumnsToContents()
        self.table.verticalScrollBar().setValue(vertical);self.table.horizontalScrollBar().setValue(horizontal)
        if not rows:self.source_label+=' · 该步数暂无统计'
        self.status.setText(self.source_label)
        return True
    def set_map_node(self,graph,node_id):
        node=next((n for n in(graph or{}).get('nodes',[])if n.get('id')==node_id),None)
        index={'zone_1':'0','zone_2':'1','zone_3':'2','zone_4':'3','zone_5':'4'}.get((graph or{}).get('zone_id'))
        if node and index is not None and type(node.get('distance'))is int and 0<=node['distance']<=100:
            with QSignalBlocker(self.floor),QSignalBlocker(self.distance):self.floor.setCurrentIndex(self.floor.findData(index));self.distance.setValue(node['distance'])
            from .map_reporting import location
            self.context.setText('查询位置：'+self.floor.currentText()+' · '+location(node,graph['grid']['rows'])+f" · 距入口{node['distance']}步");self.render();return True
        self.manual_query();return False
    def refresh_online(self):
        if self.busy:return
        self.busy=True;self.refresh_button.setEnabled(False);self.status.setText('正在更新公开统计…')
        def worker():
            try:result={'data':model.fetch()}
            except(OSError,ValueError,KeyError,TypeError)as e:result={'error':str(e)}
            self.received.emit(result)
        Thread(target=worker,daemon=True).start()
    def accept_data(self,result):
        self.busy=False;self.refresh_button.setEnabled(True)
        if 'error'in result:self.render();self.status.setText('更新失败；'+('仍显示上方日期的离线缓存。'if self.data else'没有可用统计。')+' 可稍后重试。');return
        try:
            changed=self.source.accept(result['data'])
        except(OSError,ValueError,KeyError,TypeError):self.render();self.status.setText('新数据无法核对或保存，未替换原缓存。');return
        if not changed:self.render()
        self.status.setText(self.source_label)
