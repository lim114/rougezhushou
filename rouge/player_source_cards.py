"""Readable source cards; observations remain per-pool, never merged by node name."""
from . import public_archive

def source_cards(index,version,identity):
    from .player_item_sources import pool_label
    from .player_source_map import PAIRS
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
        bindings={b['nodeName']:b.get('nodeType')for b in pool.get('nodeBindings',[])if b.get('nodeName')}
        for name,node_type in bindings.items():
            nodes.append({**record,'title':name,'pool_name':pool['name'],'map_kind':name if PAIRS.get(node_type)==name else None})
    return {'pools':pools,'nodes':nodes}

from PySide6.QtCore import Signal,Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,QScrollArea,QSizePolicy

class SourceCards(QScrollArea):
    poolChosen=Signal(str)
    nodeChosen=Signal(str,str)
    def __init__(self,parent=None):
        super().__init__(parent);self.setWidgetResizable(True);self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.host=QWidget();self.body=QVBoxLayout(self.host);self.body.setContentsMargins(0,0,6,0);self.setWidget(self.host);self.buttons=[]
        self.setStyleSheet('QScrollArea,QScrollArea QWidget{background:transparent;} QPushButton{background:#20302e;border:1px solid #47635b;border-left:2px solid #9bd6c1;border-radius:11px;color:#d9eee4;padding:9px;text-align:left;} QPushButton:checked{background:#36534a;}')
    def install(self,groups):
        self.buttons=[]
        while self.body.count():
            item=self.body.takeAt(0)
            if item.widget():item.widget().deleteLater()
        sections=[('pools','藏品池',groups['pools']),('nodes','对应地图节点',[r for r in groups['nodes']if r.get('map_kind')]),('origins','其它取得来源',[r for r in groups['nodes']if not r.get('map_kind')])]
        for key,title,rows in sections:
            if key=='origins'and not rows:continue
            label=QLabel(title);label.setTextFormat(Qt.TextFormat.PlainText);self.body.addWidget(label)
            host=QWidget();grid=QGridLayout(host);grid.setContentsMargins(0,0,0,0);grid.setSpacing(7);grid.setColumnStretch(0,1);grid.setColumnStretch(1,1);self.body.addWidget(host)
            for i,row in enumerate(rows):
                caption=row['title']+'\n'+(row.get('pool_name','')+'\n'if key!='pools'else'')+row['frequency']
                button=QPushButton();button.setAccessibleName(caption);button.setCheckable(True);button.setMinimumHeight(62);button.setMinimumWidth(0);button.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Minimum)
                label=QLabel(caption,button);label.setTextFormat(Qt.TextFormat.PlainText);label.setWordWrap(True);label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents);label.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
                box=QHBoxLayout(button);box.setContentsMargins(10,8,10,8)
                if key=='nodes':
                    from .player_map import node_sprite
                    picture=QLabel(button);picture.setFixedSize(36,36);picture.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                    picture.setPixmap(QPixmap.fromImage(node_sprite(row['map_kind'])).scaled(36,36,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation));box.addWidget(picture);button.picture=picture
                box.addWidget(label,1);button.caption=label
                button.setToolTip((row['counts']or'未核对完整次数与分母；不是本局概率。')+('\n点击在助手地图查看这类节点；不表示本局可达或会掉落。'if key=='nodes'else'\n来源未直接对应地图节点；点击查看所属池条件。'if key=='origins'else''))
                button.setProperty('poolIdentity',row['id']);button.setProperty('mapKind',row.get('map_kind'))
                if key=='nodes':button.clicked.connect(lambda _,identity=row['id'],kind=row['map_kind']:self.nodeChosen.emit(identity,kind))
                else:button.clicked.connect(lambda _,identity=row['id']:self.poolChosen.emit(identity))
                grid.addWidget(button,i//2,i%2);self.buttons.append(button)
            if not rows:grid.addWidget(QLabel('该范围未列出；不表示没有取得途径。'),0,0,1,2)
        self.body.addStretch()
    def select(self,identity):
        for button in self.buttons:button.setChecked(button.property('poolIdentity')==identity)
