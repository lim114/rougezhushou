"""Possession and roster observations; no invented acquisition or drop attribution."""
from copy import deepcopy
from .player_replay import observation_time

KINDS = {
    'relic_confirmed': ('relic', '确认持有'),
    'relic_no_longer_held': ('relic', '确认不再持有'),
    'relic_variant_corrected': ('relic', '变体重新核对'),
    'tool_confirmed': ('tool', '确认持有'),
    'tool_no_longer_held': ('tool', '确认不再持有'),
    'operator_updated': ('operator', '培养信息读到'),
    'operator_no_longer_present': ('operator', '确认离队'),
    'recruitment_changed': ('operator', '招募来源读到'),
    'classification_corrected': ('operator', '旧标记纠正'),
    'char_buffs_updated': ('operator', '定向强化读到'),
}

def evidence_rows(state):
    from .catalog import catalog, tactical_tools, operator_profiles
    data = {'relic': catalog()['relics'], 'tool': tactical_tools(), 'operator': operator_profiles()}
    result = []
    history = state.get('history', [])
    contexts_by_time={}
    for event in history:
        if not isinstance(event,dict)or event.get('kind')!='node_content_seen' or not isinstance(event.get('title'),str):continue
        at=event.get('at')
        if observation_time(at)!='读取时间未确认':contexts_by_time.setdefault(at,[]).append(event['title'])
    for index, event in enumerate(history):
        if not isinstance(event, dict) or not isinstance(event.get('kind'),str)or event['kind'] not in KINDS:
            continue
        kind, label = KINDS[event['kind']]
        identity = event.get('current_id') if event['kind'] == 'relic_variant_corrected' else event.get('id')
        if not isinstance(identity,str):identity=None
        known = data[kind].get(identity, {}) if isinstance(identity, str) else {}
        at = event.get('at')
        contexts=contexts_by_time.get(at,[])if observation_time(at)!='读取时间未确认'else[]
        result.append({'index': index, 'kind': kind, 'label': label,
                       'id': identity, 'name': known.get('name') or '固定资料名称未核对',
                       'event': deepcopy(event), 'time': observation_time(at),
                       'icon': known.get('iconId'),
                       'same_time_contexts': list(dict.fromkeys(contexts))})
    return result

def evidence_text(row):
    lines = [row['name'] + ' · ' + row['label'], row['time']]
    event = row['event']
    if row['kind'] == 'operator':
        fields = event.get('fields')
        if isinstance(fields, dict):
            from .player_team import qualified_fields
            from .catalog import operator_profiles
            fields=qualified_fields({'fields':fields},operator_profiles().get(row['id'],{}))
            for key, label in [('elite', '精英阶段'), ('level', '等级'), ('potential', '潜能')]:
                value = fields.get(key)
                if type(value) is int:
                    lines.append('当条读到' + label + '：' + str(value))
        if event.get('reason'):
            lines.append('核对说明：' + str(event['reason']))
    if row['same_time_contexts']:
        lines += ['', '同一读取时间还记录到：' + '、'.join(row['same_time_contexts']),
                  '只说明读取时间相同，不能证明该节点发放了本条物品或干员。']
    lines += ['', '确认持有不是本次获得；暂时未读到也不会改写成丢失。',
              '没有明确的发放记录时，具体掉落来源、数量和结算保持未知。']
    return '\n'.join(lines)

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QListWidget, QListWidgetItem, QPlainTextEdit
from .view_catalog import portrait_icon,relic_icon,relic_icon_note
from pathlib import Path
from PySide6.QtGui import QIcon

def evidence_icon(row,items=None):
    if row['kind'] == 'operator':
        return portrait_icon('operator', row['id'] or '')
    if items is None:
        from .expansion_reference import packet
        data=packet();items=data['current']['details']['items']if data else{}
    item=items.get(row['id'],{})
    identity = item.get('iconId')
    if not isinstance(identity, str) or Path(identity).name != identity or '/' in identity or '\\' in identity:
        return QIcon()
    return relic_icon(identity)

class EvidenceHistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.key = None
        self.input_key = None
        body = QVBoxLayout(self)
        self.notice = QLabel('藏品、道具与队伍变化分别阅读；只有明确读取的事实，不猜奖励来源。')
        self.notice.setWordWrap(True)
        body.addWidget(self.notice)
        self.tabs = QTabWidget()
        body.addWidget(self.tabs, 1)
        self.lists = {}
        for key, name in [('relic', '收藏品'), ('tool', '战术道具'), ('operator', '队伍')]:
            widget = QListWidget()
            widget.setIconSize(QSize(40, 40))
            self.lists[key] = widget
            self.tabs.addTab(widget, name)
            widget.currentItemChanged.connect(self.selected)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        body.addWidget(self.detail, 1)
        self.tabs.currentChanged.connect(self.selected)

    def refresh(self, state):
        from .expansion_reference import packet,_plain
        data=packet();items=data['current']['details']['items']if data else{}
        input_key=repr((state.get('id'),state.get('history'),data['source_identity']if data else None))
        if input_key==self.input_key:return
        self.input_key=input_key
        rows = evidence_rows(state)
        for row in rows:
            item=items.get(row['id'])or{}
            if row['kind']!='operator'and row['name']=='固定资料名称未核对'and _plain(item.get('name')):
                row['name']=_plain(item['name']);row['name_note']='名称引用当前固定国服资料；不表示当时版本或领取来源已核验。'
        key = repr((state.get('id'), rows, data['source_identity']if data else None))
        if key == self.key:
            return
        changed_run = getattr(self, 'run_id', None) != state.get('id')
        self.run_id = state.get('id')
        self.key, self.rows = key, rows
        for kind, widget in self.lists.items():
            item = widget.currentItem()
            old = item.data(Qt.ItemDataRole.UserRole) if item and not changed_run else None
            offset = widget.verticalScrollBar().value() if not changed_run else 0
            widget.blockSignals(True)
            widget.clear()
            for row in rows:
                if row['kind'] != kind:
                    continue
                item = QListWidgetItem(evidence_icon(row,items),
                                       row['name'] + ' · ' + row['label'])
                item.setData(Qt.ItemDataRole.UserRole, row['index'])
                item.setToolTip('\n'.join(note for note in (row.get('name_note',''),relic_icon_note((items.get(row['id'])or{}).get('iconId')or''))if note))
                widget.addItem(item)
                if row['index'] == old:
                    widget.setCurrentItem(item)
            widget.verticalScrollBar().setValue(offset)
            widget.blockSignals(False)
        self.selected()

    def selected(self, *_):
        item = self.tabs.currentWidget().currentItem()
        row = next((row for row in self.rows if row['index'] == item.data(Qt.ItemDataRole.UserRole)), None) if item else None
        text = evidence_text(row) if row else '选择一条已读变化；未读取的发放和消耗不补写。'
        if item and item.toolTip():text+='\n\n资料说明\n'+item.toolTip()
        if self.detail.toPlainText() != text:
            self.detail.setPlainText(text)
