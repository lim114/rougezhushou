"""Readable source cards; observations remain per-pool, never merged by node name."""
from . import public_archive

def source_cards(index,version,identity):
    from .player_item_sources import pool_label
    pools=[];nodes=[]
    for pool in index.pools(version,identity)if index else[]:
        observations=public_archive.distributions(pool)
        summary=next((d for key,_,d in observations if key=='summary'),None)
        frequency='暂无可核对统计';counts=''
        if summary:
            row=next((r for r in public_archive.members(index.data,pool,summary,version=version)if r['id']==identity),None)
            if row and row['rate']is not None:frequency=f"历史候选频率 {row['rate']:.2%}";counts=f"来源汇总：{row['count']}／{row['total']}次候选出现"
        elif observations:frequency='有分组统计，展开查看'
        if pool['name'].startswith('失与得：')and pool['name'].endswith('输入'):
            frequency='可作为交换提供物，并非奖励池';counts='仅表示此集合允许交出，不表示能够从中获得。'
        record={'id':pool['id'],'title':pool_label(pool),'frequency':frequency,'counts':counts,'version':version}
        pools.append(record)
        for name in dict.fromkeys(b.get('nodeName')for b in pool.get('nodeBindings',[])if b.get('nodeName')):
            nodes.append({**record,'title':name,'pool_name':pool['name']})
    return {'pools':pools,'nodes':nodes}

from PySide6.QtCore import Signal,Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QGridLayout,QLabel,QPushButton,QScrollArea

class SourceCards(QScrollArea):
    poolChosen=Signal(str)
    def __init__(self,parent=None):
        super().__init__(parent);self.setWidgetResizable(True);self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.host=QWidget();self.body=QVBoxLayout(self.host);self.body.setContentsMargins(0,0,6,0);self.setWidget(self.host);self.buttons=[]
        self.setStyleSheet('QScrollArea,QScrollArea QWidget{background:transparent;} QPushButton{background:#20302e;border:1px solid #47635b;border-left:2px solid #9bd6c1;border-radius:11px;color:#d9eee4;padding:9px;text-align:left;} QPushButton:checked{background:#36534a;}')
    def install(self,groups):
        self.buttons=[]
        while self.body.count():
            item=self.body.takeAt(0)
            if item.widget():item.widget().deleteLater()
        for key,title in (('pools','藏品池'),('nodes','可获取节点')):
            label=QLabel(title);label.setTextFormat(Qt.TextFormat.PlainText);self.body.addWidget(label)
            host=QWidget();grid=QGridLayout(host);grid.setContentsMargins(0,0,0,0);grid.setSpacing(7);self.body.addWidget(host)
            for i,row in enumerate(groups[key]):
                caption=row['title']+'\n'+(row.get('pool_name','')+'\n'if key=='nodes'else'')+row['frequency']
                button=QPushButton(caption);button.setCheckable(True);button.setMinimumHeight(62);button.setToolTip(row['counts']or'未核对完整次数与分母；不是本局概率。')
                button.setProperty('poolIdentity',row['id']);button.clicked.connect(lambda _,identity=row['id']:self.poolChosen.emit(identity));grid.addWidget(button,i//2,i%2);self.buttons.append(button)
            if not groups[key]:grid.addWidget(QLabel('该范围未列出；不表示没有取得途径。'),0,0,1,2)
        self.body.addStretch()
    def select(self,identity):
        for button in self.buttons:button.setChecked(button.property('poolIdentity')==identity)
