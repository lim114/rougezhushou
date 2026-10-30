"""A read-only public-frequency reader. Never transmits a local map or query."""
from pathlib import Path
from threading import Thread
from datetime import datetime
from PySide6.QtCore import Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,QPushButton,QTableWidget,QTableWidgetItem
from . import public_node_statistics as model
class StatisticsDialog(QDialog):
    received=Signal(object)
    def __init__(self,cache,parent=None,*,source=None):
        from .node_statistics_source import NodeStatisticsSource
        super().__init__(parent);self.cache=Path(cache);self.source=source or NodeStatisticsSource(cache,self);self.busy=False;self.setWindowTitle('公开节点统计 · 只读');self.resize(690,580)
        body=QVBoxLayout(self);self.status=QLabel();self.status.setWordWrap(True);body.addWidget(self.status)
        bar=QHBoxLayout();self.floor=QComboBox()
        for key,label in [('0','第一层'),('1','第二层'),('2','第三层'),('3','第四层'),('remembrance','第四层·追忆'),('4','第五层')]:self.floor.addItem(label,key)
        self.distance=QSpinBox();self.distance.setRange(0,100);self.distance.setValue(1)
        bar.addWidget(self.floor);bar.addWidget(QLabel('距本层初始入口'));bar.addWidget(self.distance);bar.addWidget(QLabel('步'));body.addLayout(bar)
        self.context=QLabel('手动查询资料；不是当前位置声明。');self.context.setWordWrap(True);body.addWidget(self.context)
        self.table=QTableWidget(0,4);self.table.setHorizontalHeaderLabels(['节点类型','历史出现比例','出现次数','同位置样本']);self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers);body.addWidget(self.table,1)
        self.notice=QLabel('这是同层、距初始入口相同步数的历史样本分布，包含已知和未知位置。不是本局节点的精确概率；没有结合本图已揭示节点、数量上限、分队、特殊区域或本次更新。0次不等于绝不出现。不会推荐或自动选路。');self.notice.setWordWrap(True);body.addWidget(self.notice)
        buttons=QHBoxLayout();self.refresh_button=QPushButton('联网更新公开统计');self.website_button=QPushButton('查看数据来源');buttons.addWidget(self.refresh_button);buttons.addWidget(self.website_button);body.addLayout(buttons)
        self.refresh_button.clicked.connect(self.refresh_online);self.website_button.clicked.connect(lambda:QDesktopServices.openUrl(QUrl(model.PAGE)))
        self.floor.currentIndexChanged.connect(self.render);self.distance.valueChanged.connect(self.render);self.received.connect(self.accept_data)
        self.source.changed.connect(self.render)
        self.render()
    @property
    def data(self):return self.source.data
    def render(self,*_):
        self.table.setRowCount(0)
        if self.data is None:self.status.setText('尚无可用公开统计；可手动联网读取。不会上传对局、截图或笔记。');return
        try:rows=self.source.index.rows(self.floor.currentData(),self.distance.value())
        except(ValueError,KeyError,TypeError):self.status.setText('统计口径无法核对，已清除旧结果。');return
        meta=self.source.index.metadata;date=datetime.fromisoformat(meta['updatedAt'].replace('Z','+00:00')).astimezone().strftime('%Y-%m-%d %H:%M')
        self.status.setText(f"来源：路标档案馆 · 数据更新 {date} · 全表{meta['sampleCount']:,}个节点记录。当前版本适用性尚未核验；以下仅供历史对照。")
        for row in rows:
            i=self.table.rowCount();self.table.insertRow(i)
            for j,text in enumerate([row['name'],f"{row['frequency']:.2%}",str(row['count']),str(row['total'])]):self.table.setItem(i,j,QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
        if not rows:self.status.setText(self.status.text()+' 此步数没有样本，概率未知。')
    def set_map_node(self,graph,node_id):
        node=next((n for n in(graph or{}).get('nodes',[])if n.get('id')==node_id),None)
        index={'zone_1':'0','zone_2':'1','zone_3':'2','zone_4':'3','zone_5':'4'}.get((graph or{}).get('zone_id'))
        if node and index is not None and type(node.get('distance'))is int:
            self.floor.setCurrentIndex(self.floor.findData(index));self.distance.setValue(node['distance'])
            from .map_reporting import location
            self.context.setText('地图位置：'+location(node,graph['grid']['rows'])+'；按模板连线距本层初始入口计步，仅查询历史分布。')
        else:self.context.setText('当前未选可映射的位置或不在统计覆盖范围；下方为手动资料查询。')
    def refresh_online(self):
        if self.busy:return
        self.busy=True;self.refresh_button.setEnabled(False);self.status.setText('正在读取公开汇总数据；请求不含本局、截图或查询条件。')
        def worker():
            try:result={'data':model.fetch()}
            except Exception as e:result={'error':str(e)}
            self.received.emit(result)
        Thread(target=worker,daemon=True).start()
    def accept_data(self,result):
        self.busy=False;self.refresh_button.setEnabled(True)
        if 'error'in result:self.render();self.status.setText('更新失败；'+('仍显示上方日期的离线缓存。'if self.data else'没有可用统计。')+' 可稍后重试。');return
        try:
            changed=self.source.accept(result['data'])
        except(OSError,ValueError,KeyError,TypeError):self.render();self.status.setText('新数据无法核对或保存，未替换原缓存。');return
        if not changed:self.render()
