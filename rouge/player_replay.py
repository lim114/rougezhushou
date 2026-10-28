"""Player-readable, read-only views of actual local observations."""
from copy import deepcopy
from datetime import datetime
import math

EVENT_LABELS = {
    'config_updated': '对局信息更新',
    'node_content_seen': '读到节点详情',
    'resource_updated': '读到资源数量',
    'inventory_changed': '收藏品清单变化',
    'relic_confirmed': '确认持有收藏品',
    'tool_confirmed': '确认持有战术道具',
    'relic_no_longer_held': '确认不再持有收藏品',
    'tool_no_longer_held': '确认不再持有战术道具',
    'classification_corrected': '干员标记核对',
    'recruitment_changed': '干员招募来源更新',
    'char_buffs_updated': '干员定向强化更新',
    'operator_updated': '干员培养信息更新',
    'operator_no_longer_present': '确认干员离队',
    'map_layout_changed': '地图布局变化',
    'map_confirmed': '读到地图模板',
    'map_position_updated': '读到地图位置',
    'map_node_passed': '确认经过节点',
    'map_node_revealed': '读到节点类型',
    'map_node_content_confirmed': '确认节点详情关联',
    'relic_variant_corrected': '收藏品变体核对',
    'state_flag_reconfirmed': '持有或在队标记核对',
}

def observation_time(value):
    if type(value) not in (int, float):
        return '读取时间未确认'
    try:
        if not math.isfinite(value):
            return '读取时间未确认'
        return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
    except (OSError, ValueError, OverflowError):
        return '读取时间未确认'

def history_rows(state):
    """Keep stable saved order, even when timestamps tie or are unavailable."""
    raw = state.get('history', [])
    if not isinstance(raw, list):
        return []
    return [{'index': i, 'event': deepcopy(event),
             'label': EVENT_LABELS.get(event.get('kind'), '其他读取记录')if isinstance(event.get('kind'),str)else'其他读取记录',
             'time': observation_time(event.get('at'))}
            for i, event in enumerate(raw) if isinstance(event, dict)]

def event_text(row):
    from .catalog import catalog, operator_profiles, tactical_tools
    event = row['event']
    kind=event.get('kind')if isinstance(event.get('kind'),str)else''
    lines = [row['label'], row['time']]
    if isinstance(event.get('title'), str):
        lines.append('读到的名称：' + event['title'])
    identity = event.get('id')
    if isinstance(identity, str):
        source = (operator_profiles() if kind.startswith(('operator_', 'recruitment_', 'char_buffs_', 'classification_'))
                  else tactical_tools() if kind.startswith('tool_')
                  else catalog()['relics'])
        name = source.get(identity, {}).get('name')
        lines.append('对应条目：' + (name or '固定资料未找到对应名称'))
    if event.get('kind') == 'config_updated':
        field_key=event.get('field') if isinstance(event.get('field'),str) else None
        field = {'difficulty': '保密等级', 'squad': '分队', 'zone': '所在区域'}.get(field_key, '对局信息')
        current = event.get('current')
        if isinstance(current, dict):
            if field_key=='difficulty':
                from .run_config import difficulty_value
                value=difficulty_value(current)
            else:value=current.get('name')if isinstance(current.get('name'),str)else None
            lines.append(field + '：' + (str(value) if value is not None else '尚未核验'))
            if field_key=='difficulty' and value is None and type(current.get('value'))is int:
                lines.append(f'这条记录写有{current["value"]}；超出固定资料或模式尚未核对，不按已核验等级使用。')
    lines += ['', '这是助手当时读到的记录，不是完整游戏日志。',
              '没有记录的步骤、奖励、胜负和结算不会补写；相邻记录不代表因果关系。']
    return '\n'.join(lines)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QListWidgetItem, QPlainTextEdit, QTabWidget

class ReplayPanel(QWidget):
    def __init__(self, run, parent=None):
        super().__init__(parent)
        self.run = run
        self.snapshot = None
        self.rows = {}
        self.key = None
        body = QVBoxLayout(self)
        self.notice = QLabel('仅查看本机已读记录，不改变本局，不上传。')
        self.notice.setWordWrap(True)
        body.addWidget(self.notice)
        self.sessions = QComboBox()
        self.sessions.addItem('当前对局 · 最近读取', 'current')
        body.addWidget(self.sessions)
        self.tabs = QTabWidget()
        body.addWidget(self.tabs, 1)
        page = QWidget()
        layout = QVBoxLayout(page)
        self.entries = QListWidget()
        layout.addWidget(self.entries, 1)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        layout.addWidget(self.detail, 1)
        self.tabs.addTab(page, '读取记录')
        from .player_replay_nodes import NodeReplayPage
        self.nodes=NodeReplayPage();self.tabs.addTab(self.nodes,'逐层节点')
        self.entries.currentItemChanged.connect(self.selected)
        from .player_replay_archive import attach_history
        attach_history(self,body)
        self.refresh()

    def refresh(self):
        from .player_replay_archive import selected_state
        state = selected_state(self)
        key = repr((state.get('id'),state.get('started_at'),state.get('history')))
        if key == self.key:
            self.snapshot=state
            return
        self.key = key
        self.nodes.refresh(state)
        changed_run = self.snapshot is not None and self.snapshot.get('id') != state.get('id')
        self.snapshot = state
        old = self.entries.currentItem()
        identity = old.data(Qt.ItemDataRole.UserRole) if old and not changed_run else None
        offset = self.entries.verticalScrollBar().value() if not changed_run else 0
        self.rows = {row['index']: row for row in history_rows(state)}
        self.entries.blockSignals(True)
        self.entries.clear()
        for row in self.rows.values():
            item = QListWidgetItem(row['time'] + ' · ' + row['label'])
            item.setData(Qt.ItemDataRole.UserRole, row['index'])
            self.entries.addItem(item)
            if row['index'] == identity:
                self.entries.setCurrentItem(item)
        self.entries.verticalScrollBar().setValue(offset)
        self.entries.blockSignals(False)
        self.selected()
        from .player_replay_archive import snapshot_notice
        self.notice.setText(snapshot_notice(self,len(self.rows),state))

    def selected(self, *_):
        item = self.entries.currentItem()
        row = self.rows.get(item.data(Qt.ItemDataRole.UserRole)) if item else None
        text = event_text(row) if row else '选择一条记录查看；读取时间不等于游戏动作发生时间。'
        if self.detail.toPlainText() != text:
            self.detail.setPlainText(text)
