"""Same-frame zone/resource observations, never inferred floor transitions."""
from copy import deepcopy
from .player_resource_history import numeric_read,resource_name
from .player_replay import observation_time

def record_snapshot(state,observed,at):
    from .run_config import config_data
    zone=(observed.get('config')or{}).get('zone')or{};graph=observed.get('map')or{};zid=None;template=None
    saved=state.get('maps',{}).get(graph.get('zone_id'))or{}
    if graph.get('status')=='matched'and saved.get('captured_at')==at and saved.get('template_id')==graph.get('template_id'):
        zid=graph.get('zone_id');template=graph.get('template_id')
    elif not zone.get('reused_from_run')and(state.get('config',{}).get('zone')or{}).get('captured_at')==at:zid=zone.get('id')
    if zid not in config_data()['zones']:return False
    values={}
    raw=observed.get('resources');raw=raw if isinstance(raw,dict)else{}
    for key,record in raw.items():
        accepted=state.get('resources',{}).get(key)or{}
        if isinstance(record,dict)and numeric_read(record.get('value'))and accepted.get('value')==record['value']and accepted.get('captured_at')==at:values[key]=record['value']
    if not values:return False
    prior=next((r for r in reversed(state.get('history',[]))if r.get('kind')=='floor_resources_read'),None)
    identity={'zone_id':zid,'template_id':template,'values':values}
    if prior and all(prior.get(k)==v for k,v in identity.items()):return False
    state['history'].append({'kind':'floor_resources_read','at':at,**identity,'source':'same_frame_zone_and_resources'});return True

def snapshots(state):
    from .run_config import config_data
    result=[]
    for index,event in enumerate(state.get('history',[])):
        if not isinstance(event,dict)or event.get('kind')!='floor_resources_read'or event.get('source')!='same_frame_zone_and_resources':continue
        if event.get('zone_id')not in config_data()['zones']or not isinstance(event.get('values'),dict):continue
        values={k:v for k,v in event['values'].items()if isinstance(k,str)and numeric_read(v)}
        if values:result.append({**deepcopy(event),'values':values,'index':index})
    return result

def snapshot_text(row):
    if row is None:return '该层当时资源尚未记录；不使用当前资源补写。'
    return '该区域读取时（'+observation_time(row.get('at'))+'）：'+'　'.join(resource_name(k)+' '+f'{v:g}'for k,v in row['values'].items())+'。未列字段未读；不是入层、出层或结算。'

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QListWidget,QListWidgetItem
class FloorResourcesPage(QWidget):
    def __init__(self):
        super().__init__();self.rows=[];body=QVBoxLayout(self);body.addWidget(QLabel('只展示同一画面已确认区域与资源的记录；旧数据不会追填。'));self.entries=QListWidget();body.addWidget(self.entries,1);self.detail=QLabel();self.detail.setWordWrap(True);body.addWidget(self.detail);self.entries.currentRowChanged.connect(self.selected)
    def refresh(self,state):
        from .player_map import zone_info
        rows=snapshots(state);identity=(state.get('id'),rows)
        if getattr(self,'identity',None)==identity:return
        old=self.entries.currentItem();keep=old.data(Qt.ItemDataRole.UserRole)if old and self.identity[0]==state.get('id')else None;self.identity=deepcopy(identity);self.rows=rows;self.entries.blockSignals(True);self.entries.clear()
        for row in rows:
            label=zone_info({'zone_id':row['zone_id']})[0];item=QListWidgetItem(label+' · '+observation_time(row.get('at')));item.setData(Qt.ItemDataRole.UserRole,row['index']);self.entries.addItem(item)
            if row['index']==keep:self.entries.setCurrentItem(item)
        self.entries.blockSignals(False);self.selected(self.entries.currentRow())
    def selected(self,index):self.detail.setText(snapshot_text(self.rows[index]if 0<=index<len(self.rows)else None))
