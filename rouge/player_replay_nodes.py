"""Observed map steps linked only to an exactly identified, pinned template."""
from copy import deepcopy
from .player_replay import observation_time

KINDS = {'map_position_updated': '位置读到', 'map_node_passed': '确认经过',
         'map_node_revealed': '类型读到', 'map_node_content_confirmed': '详情关联'}

def node_steps(state):
    from .map_recognition import map_data
    templates = {row['id']: row for row in map_data()['templates']}
    layouts = {}
    result = []
    for index, event in enumerate(state.get('history', [])):
        if not isinstance(event, dict):
            continue
        kind, zone = event.get('kind'), event.get('zone_id')
        if not isinstance(kind,str):continue
        if not isinstance(zone,str)or not zone:zone=None
        if zone is not None and kind in('map_confirmed','map_layout_changed'):
            identity=event.get('template_id')if kind=='map_confirmed'else event.get('current_template')
            layouts[zone]=identity if isinstance(identity,str)else None
        if kind not in KINDS:
            continue
        identity = event.get('current') if kind == 'map_position_updated' else event.get('node_id')
        template = templates.get(layouts.get(zone))
        if template and template['zone_id'] != zone:
            template = None
        node = next((row for row in template['nodes'] if row['id'] == identity), None) if template else None
        distance = node.get('distance') if node else None
        distance = distance if type(distance) is int and distance >= 0 else None
        result.append({'index': index, 'zone_id': zone, 'template': deepcopy(template) if node else None,
                       'node_id': identity, 'distance': distance, 'event': deepcopy(event),
                       'label': KINDS[kind], 'time': observation_time(event.get('at'))})
    return result

def template_graph(row):
    """Show a template reference, never copy later revealed nodes into the past."""
    template = row.get('template')
    if not template:
        return None
    from .map_recognition import map_data
    nodes=[{**deepcopy(node),'template_type':node.get('fixed_type')}for node in template['nodes']]
    chosen=next((node for node in nodes if node['id']==row.get('node_id')),None)
    event=row.get('event',{})
    if chosen is not None:
        if event.get('kind')=='map_node_passed':
            chosen['observed_type']='林间空地'
            original=event.get('original_type')
            if isinstance(original,str)and original!='林间空地'and not original.startswith(('未知','类型未确认')):chosen['remembered_type']=original
        elif event.get('kind')=='map_node_revealed'and isinstance(event.get('type'),str):chosen['observed_type']=event['type']
    return {'zone_id': template['zone_id'], 'template_id': template['id'],
            'nodes': nodes,
            'grid': {'rows': template['rows'], 'cols': template['cols']},
            'edges': deepcopy(template['edges']), 'source': deepcopy(map_data()['source'])}

def zone_label(identity):
    from .run_config import config_data
    zone = config_data()['zones'].get(identity, {})
    icon = zone.get('zoneIconId')
    floor = next((i for i in range(1, 7) if icon == f'zone_{i}'), None)
    return (f'第{floor}层 · ' if floor else '特殊或未确认层数 · ') + (zone.get('name') or '区域未读到')

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QListWidgetItem, QSplitter
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
        body.addWidget(self.floors)
        split = QSplitter()
        body.addWidget(split, 1)
        self.entries = QListWidget()
        self.view = RecordedMapView()
        split.addWidget(self.entries)
        split.addWidget(self.view)
        self.floors.currentIndexChanged.connect(self.show_rows)
        self.entries.currentItemChanged.connect(self.selected)

    def refresh(self, state):
        rows = node_steps(state)
        key = repr((state.get('id'), rows))
        if key == self.key:
            return
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
        self.show_rows()

    def show_rows(self, *_):
        item = self.entries.currentItem()
        old = item.data(Qt.ItemDataRole.UserRole) if item else None
        offset = self.entries.verticalScrollBar().value()
        self.entries.blockSignals(True)
        self.entries.clear()
        for row in self.rows:
            if self.floors.currentIndex() > 0 and row['zone_id'] != self.floors.currentData():
                continue
            distance = f'距起点{row["distance"]}步' if row['distance'] is not None else '模板位置未确认'
            item = QListWidgetItem(row['time'] + ' · ' + row['label'] + ' · ' + distance)
            item.setData(Qt.ItemDataRole.UserRole, row['index'])
            self.entries.addItem(item)
            if row['index'] == old:
                self.entries.setCurrentItem(item)
        self.entries.verticalScrollBar().setValue(offset)
        self.entries.blockSignals(False)
        self.selected()

    def selected(self, *_):
        item = self.entries.currentItem()
        row = next((row for row in self.rows if row['index'] == item.data(Qt.ItemDataRole.UserRole)), None) if item else None
        graph = template_graph(row) if row else None
        self.view.set_map(graph, historical=True)
        if graph:
            self.view.select_node(row['node_id'])
        self.notice.setText((zone_label(row['zone_id']) + '；' + row['label'] + '。' if row else '') +
                            '图中只显示对应模板和所选记录的位置；不还原未读步骤，不把后来的节点状态填回过去。')
