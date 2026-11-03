"""Observed map steps linked only to an exactly identified, pinned template."""
from copy import deepcopy
from .player_replay import observation_time

KINDS = {'map_position_updated': '位置读到', 'map_node_passed': '确认经过',
         'map_node_revealed': '类型读到', 'map_node_content_confirmed': '详情关联'}

def _apply_reading(node,event):
    kind=event.get('kind')
    if kind=='map_node_passed':
        original=event.get('original_type')
        if not isinstance(original,str)or original=='林间空地'or original.startswith(('未知','类型未确认')):
            original=node.get('remembered_type')or node.get('observed_type')
        node.update(observed_type='林间空地',visited=True)
        if isinstance(original,str)and original!='林间空地'and not original.startswith(('未知','类型未确认')):node['remembered_type']=original
    elif kind=='map_node_revealed'and isinstance(event.get('type'),str):
        node['observed_type']=event['type']
    elif kind=='map_node_content_confirmed':
        content=event.get('content')
        if isinstance(content,dict)and content.get('source')=='same_frame_selected_node':
            previous=node.get('remembered_content')
            if previous and previous!=content:node.setdefault('content_history',[]).append(previous)
            node['remembered_content']=deepcopy(content)


def node_steps(state):
    from .map_recognition import map_data
    from .player_floor_resources import snapshots
    templates = {row['id']: row for row in map_data()['templates']}
    layouts = {};observed={};positions={};resources={}
    resource_reads={row['index']:row for row in snapshots(state)}
    result = []
    for index, event in enumerate(state.get('history', [])):
        if not isinstance(event, dict):
            continue
        kind, zone = event.get('kind'), event.get('zone_id')
        if not isinstance(kind,str):continue
        if not isinstance(zone,str)or not zone:zone=None
        if index in resource_reads:resources[zone]=resource_reads[index]
        if zone is not None and kind in('map_confirmed','map_layout_changed'):
            identity=event.get('template_id')if kind=='map_confirmed'else event.get('current_template')
            if kind=='map_layout_changed'or layouts.get(zone)!=identity:
                observed[zone]={};positions[zone]=None
                if kind=='map_layout_changed':resources.pop(zone,None)
            layouts[zone]=identity if isinstance(identity,str)else None
        if kind not in KINDS:
            continue
        identity = event.get('current') if kind == 'map_position_updated' else event.get('node_id')
        template = templates.get(layouts.get(zone))
        if template and template['zone_id'] != zone:
            template = None
        node = next((row for row in template['nodes'] if row['id'] == identity), None) if template else None
        if node:
            if kind=='map_position_updated':positions[zone]=identity
            else:_apply_reading(observed.setdefault(zone,{}).setdefault(identity,{}),event)
        distance = node.get('distance') if node else None
        distance = distance if type(distance) is int and distance >= 0 else None
        result.append({'index': index, 'zone_id': zone, 'template': deepcopy(template) if node else None,
                       'node_id': identity, 'distance': distance, 'event': deepcopy(event),
                       'observed_nodes':deepcopy(observed.get(zone,{})),
                       'last_confirmed_current_node':positions.get(zone),
                       'resource_snapshot':deepcopy(resources.get(zone)),
                       'label': KINDS[kind], 'time': observation_time(event.get('at'))})
    return result

def template_graph(row):
    """Project only saved reads at or before this step onto its exact template."""
    template = row.get('template')
    if not template:
        return None
    from .map_recognition import map_data
    nodes=[{**deepcopy(node),'template_type':node.get('fixed_type')}for node in template['nodes']]
    if 'observed_nodes'in row:
        for node in nodes:node.update(deepcopy(row['observed_nodes'].get(node['id'],{})))
    else:
        chosen=next((node for node in nodes if node['id']==row.get('node_id')),None)
        if chosen is not None:_apply_reading(chosen,row.get('event',{}))
    return {'zone_id': template['zone_id'], 'template_id': template['id'],
            'nodes': nodes,
            'grid': {'rows': template['rows'], 'cols': template['cols']},
            'edges': deepcopy(template['edges']), 'source': deepcopy(map_data()['source']),
            'last_confirmed_current_node':row.get('last_confirmed_current_node')}

def zone_label(identity):
    from .run_config import config_data
    zone = config_data()['zones'].get(identity, {})
    icon = zone.get('zoneIconId')
    floor = next((i for i in range(1, 7) if icon == f'zone_{i}'), None)
    return (f'第{floor}层 · ' if floor else '特殊或未确认层数 · ') + (zone.get('name') or '区域未读到')

from PySide6.QtCore import Qt,QSignalBlocker
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QListWidgetItem, QSplitter,QTabBar,QHBoxLayout,QPushButton
from .player_map import PreviewMapView

class RecordedMapView(PreviewMapView):
    def paintEvent(self,event):
        if self.graph is not None:return super().paintEvent(event)
        from PySide6.QtGui import QPainter,QColor
        painter=QPainter(self);painter.fillRect(self.rect(),QColor('#0e1717'));painter.setPen(QColor('#eff4f4'));painter.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,'该条记录缺少可核对的历史地图模板\n不能从当前地图补回过去的位置')

class NodeReplayPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.key = None
        body = QVBoxLayout(self)
        self.notice = QLabel('按层查看已读位置；距起点的模板步数不是实际消耗的行动次数。')
        self.notice.setWordWrap(True)
        body.addWidget(self.notice)
        self.floors = QComboBox()
        self.floors.hide()
        self.floor_tabs=QTabBar();self.floor_tabs.setExpanding(False);self.floor_tabs.setDrawBase(False);self.floor_tabs.setUsesScrollButtons(True)
        self.floor_tabs.setAccessibleName('选择已保存记录的楼层或区域');floor_bar=QHBoxLayout();floor_bar.addWidget(self.floor_tabs,1)
        self.readings_toggle=QPushButton('逐条回看');self.readings_toggle.setCheckable(True);floor_bar.addWidget(self.readings_toggle);body.addLayout(floor_bar)
        self.floor_tabs.currentChanged.connect(self.floors.setCurrentIndex);self.floors.currentIndexChanged.connect(self.floor_tabs.setCurrentIndex)
        from .player_resource_strip import ResourceStrip
        self.resource_pills=ResourceStrip();self.resource_pills.set_rows([]);self.resource_pills.setAccessibleName('所选历史记录之前最近一次同区域资源；不使用当前局数量');body.addWidget(self.resource_pills)
        self.resources=QLabel();self.resources.setWordWrap(True);self.resources.setAccessibleName('所选历史记录之前最近一次同区域资源快照');body.addWidget(self.resources)
        split = QSplitter()
        body.addWidget(split, 1)
        self.entries = QListWidget()
        self.entries.hide();self.readings_toggle.toggled.connect(self.entries.setVisible)
        self.view = RecordedMapView()
        self.view.setContentsMargins(0,30,0,0)
        split.addWidget(self.entries)
        split.addWidget(self.view)
        self.floors.currentIndexChanged.connect(self.show_rows)
        self.entries.currentItemChanged.connect(self.selected)

    def refresh(self, state):
        kinds=(*KINDS,'map_confirmed','map_layout_changed','floor_resources_read')
        key=repr((state.get('id'),[(i,e)for i,e in enumerate(state.get('history',[]))if isinstance(e,dict)and e.get('kind')in kinds]))
        if key == self.key:
            return
        rows = node_steps(state)
        changed_run = getattr(self, 'run_id', None) != state.get('id')
        self.run_id = state.get('id')
        self.key, self.rows = key, rows
        if changed_run:
            self.entries.clear()
        old = self.floors.currentData()
        self.floors.blockSignals(True)
        self.floors.clear()
        self.floors.addItem('所有已读区域', None)
        for identity in dict.fromkeys(row['zone_id'] for row in rows):
            self.floors.addItem(zone_label(identity), identity)
        found = self.floors.findData(old)
        self.floors.setCurrentIndex(max(0, found))
        self.floors.blockSignals(False)
        with QSignalBlocker(self.floor_tabs):
            while self.floor_tabs.count():self.floor_tabs.removeTab(0)
            for index in range(self.floors.count()):
                label=self.floors.itemText(index);self.floor_tabs.addTab(label.split(' · ')[0]);self.floor_tabs.setTabData(index,self.floors.itemData(index));self.floor_tabs.setTabToolTip(index,label)
            self.floor_tabs.setCurrentIndex(self.floors.currentIndex())
        self.show_rows()

    def show_rows(self, *_):
        from .map_reporting import location
        item = self.entries.currentItem()
        old = item.data(Qt.ItemDataRole.UserRole) if item else None
        offset = self.entries.verticalScrollBar().value()
        self.entries.blockSignals(True)
        self.entries.clear()
        for row in self.rows:
            if self.floors.currentIndex() > 0 and row['zone_id'] != self.floors.currentData():
                continue
            distance = f'距起点{row["distance"]}步' if row['distance'] is not None else '模板位置未确认'
            template=row.get('template');node=next((n for n in template['nodes']if n['id']==row['node_id']),None)if template else None
            place=location(node,template['rows'])if node else'模板位置未确认'
            item = QListWidgetItem(row['label']+' · '+place)
            item.setToolTip(row['time']+'\n'+distance+'；距起点步数不是实际消耗行动次数。')
            item.setData(Qt.ItemDataRole.UserRole, row['index'])
            self.entries.addItem(item)
            if row['index'] == old:
                self.entries.setCurrentItem(item)
        self.entries.verticalScrollBar().setValue(offset)
        self.entries.blockSignals(False)
        if _ and self.floors.currentIndex()>0 and self.entries.currentItem()is None and self.entries.count():
            self.entries.setCurrentRow(self.entries.count()-1)
        self.selected()

    def selected(self, *_):
        from .player_floor_resources import snapshot_text,snapshot_entries
        item = self.entries.currentItem()
        row = next((row for row in self.rows if row['index'] == item.data(Qt.ItemDataRole.UserRole)), None) if item else None
        graph = template_graph(row) if row else None
        self.view.set_map(graph, historical=True)
        self.resources.setText(snapshot_text(row.get('resource_snapshot')if row else None))
        snapshot=row.get('resource_snapshot')if row else None
        self.resource_pills.set_rows([{**entry,'key':'history:'+entry['key'],'note':snapshot_text(snapshot)}for entry in snapshot_entries(snapshot)]if snapshot else[])
        self.resource_pills.setToolTip(snapshot_text(snapshot));self.resources.setVisible(snapshot is None)
        if graph:
            self.view.select_node(row['node_id'])
        self.notice.setText((zone_label(row['zone_id']) + '；' + row['label'] + '。' if row else '') +
                            '图中累积显示截至所选记录已读到的节点；白圈为所选节点，金圈为当时最近已读位置。不还原未读步骤，不把后来的节点状态填回过去。资源只列当时已读数量，未列项目不代表零。')
