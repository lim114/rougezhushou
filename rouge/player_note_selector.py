"""Manual note browsing by pinned classifications, never live eligibility."""
import json
from . import expansion_reference as model,current_stage_directory as stages,current_event_directory as events

def catalogue_snapshot():
    ref=model.packet()
    if ref is None:return {'rows':[],'unavailable':['固定资料']}
    stage=stages.packet();event=events.packet();unavailable=[];categories=[]
    if stage is not None:categories.append('stages')
    else:unavailable.append('关卡分类')
    if event is not None and event['version_source_identity']==ref['source_identity']:categories.append('scenes')
    else:unavailable.append('事件分类')
    result=[];groups={}
    for row in event['data']['rows']if 'scenes'in categories else[]:
        for sid in row['event']['scene_ids']:groups.setdefault(sid,[]).extend(row['catalogue_groups'])
    for category in categories:
        for row in model.rows(category,changes_only=False,reference=ref):
            identity=row['id'];kind='reference-stage'if category=='stages'else'reference-scene'
            context={'kind':kind,'title':row['name'],'event_id':identity,'variant_id':json.dumps([ref['source_identity'],identity],ensure_ascii=True,sort_keys=True,separators=(',',':'))}
            if category=='stages':
                info=stage['data']['rows'][identity];floors=[info['floor']];nodes=[dict(stages.KINDS)[info['play_kind']]]
            else:
                matched=groups.get(identity,[]);floors=list(dict.fromkeys(('unknown'if n=='unknown'else'floor'+str(n))for g in matched for n in(g.get('floors')or['unknown'])))or['unknown'];nodes=list(dict.fromkeys(t for g in matched for t in g['node_types']))or['节点类别未确认']
            result.append({'context':context,'label':row['label'],'floors':floors,'nodes':nodes})
    return {'rows':result,'unavailable':unavailable}


def catalogue():return catalogue_snapshot()['rows']

def matching(rows,floor=None,node=None):
    return [r for r in rows if(floor is None or floor in r['floors'])and(node is None or node in r['nodes'])]

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget,QGridLayout,QLabel,QComboBox
class SceneNoteSelector(QWidget):
    chosen=Signal(object)
    def __init__(self,parent=None):
        super().__init__(parent);self.rows=[];bar=QGridLayout(self);bar.setContentsMargins(0,0,0,0)
        self.floor=QComboBox();self.node=QComboBox();self.scene=QComboBox()
        self.floor.setAccessibleName('笔记层数');self.node.setAccessibleName('笔记节点类别');self.scene.setAccessibleName('笔记准确场景')
        for value,label in stages.FLOORS:self.floor.addItem(label,value)
        for col,(label,widget)in enumerate(zip(('主题','层数','节点','详情'),(QLabel('黑流树海'),self.floor,self.node,self.scene))):
            bar.addWidget(QLabel(label),0,col);bar.addWidget(widget,1,col);bar.setColumnStretch(col,2 if col==3 else 1)
        for combo in(self.floor,self.node,self.scene):combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon);combo.setMinimumContentsLength(6)
        self.notice=QLabel();self.notice.setWordWrap(True);bar.addWidget(self.notice,2,0,1,4)
        self.floor.currentIndexChanged.connect(self.filter);self.node.currentIndexChanged.connect(self.filter);self.scene.activated.connect(self.select)
        self.reload()
    def reload(self):
        snapshot=catalogue_snapshot();self.rows=snapshot['rows'];missing=snapshot['unavailable'];self.notice.setText('暂不可核对：'+'、'.join(missing)+'；只列仍可核对的资料，不借用其它分类。'if missing else'');self.notice.setVisible(bool(missing))
        old=self.node.currentData();self.node.blockSignals(True);self.node.clear();self.node.addItem('全部节点类别',None)
        for node in dict.fromkeys(n for r in self.rows for n in r['nodes']):self.node.addItem(node,node)
        index=self.node.findData(old);self.node.setCurrentIndex(max(0,index));self.node.blockSignals(False);self.filter()
    def filter(self,*_):
        old=self.scene.currentData();self.scene.blockSignals(True);self.scene.clear()
        for row in matching(self.rows,self.floor.currentData(),self.node.currentData()):self.scene.addItem(row['label'],row['context'])
        self.scene.setCurrentIndex(self.scene.findData(old)if old is not None else-1);self.scene.setPlaceholderText('选择具体场景');self.scene.blockSignals(False)
    def select(self,*_):
        value=self.scene.currentData()
        if value is not None:self.chosen.emit(dict(value))
