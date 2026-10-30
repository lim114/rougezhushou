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
    'floor_resources_read': '读到区域资源快照',
    'shop_items_read': '读到商店商品名称',
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
    if kind=='shop_items_read':
        from .player_shop_memory import qualified
        items=qualified(event)
        lines+=['','当时确认读到的商品：'+('、'.join(r['name']for r in items)if items else'原记录暂时无法核对'),
            '这是部分商品名称，不代表已经买下、仍在出售或完整商店库存。']
    lines += ['', '这是助手当时读到的记录，不是完整游戏日志。',
              '没有记录的步骤、奖励、胜负和结算不会补写；相邻记录不代表因果关系。']
    return '\n'.join(lines)

from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QListWidgetItem, QPlainTextEdit, QTabWidget

class ReplayPanel(QWidget):
    noteRequested=Signal(object)
    def __init__(self, run, parent=None,source_panel=None):
        super().__init__(parent)
        self.run = run
        self.snapshot = None
        self.rows = {}
        self.key = None
        self.scene_popup=None;self.scene_binding=None
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
        from PySide6.QtWidgets import QPushButton
        self.shop_button=QPushButton('查看这次读到的商店清单');layout.addWidget(self.shop_button);self.shop_button.hide();self.shop_button.clicked.connect(self.open_selected_shop)
        self.scene_button=QPushButton('查看这条记录的事件或关卡资料');layout.addWidget(self.scene_button);self.scene_button.hide();self.scene_button.clicked.connect(self.open_selected_scene)
        self.tabs.addTab(page, '读取记录')
        from .player_replay_nodes import NodeReplayPage
        self.nodes=NodeReplayPage();self.tabs.addTab(self.nodes,'逐层节点')
        from .player_resource_history import ResourceHistoryPage
        self.resources=ResourceHistoryPage();self.tabs.addTab(self.resources,'资源变化')
        from .player_floor_resources import FloorResourcesPage
        self.floor_resources=FloorResourcesPage();self.tabs.addTab(self.floor_resources,'各层资源记录')
        from .player_evidence_history import EvidenceHistoryPage
        self.evidence=EvidenceHistoryPage();self.tabs.addTab(self.evidence,'藏品与队伍变化')
        from .player_shop_replay import ShopReplayPage
        self.shop=ShopReplayPage(source_panel);self.tabs.addTab(self.shop,'商店货物')
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
            self.shop.refresh(state)
            if self.scene_popup is not None and self.scene_popup.isVisible():self.scene_popup.panel.refresh()
            return
        self.key = key
        self.nodes.refresh(state)
        self.resources.refresh(state)
        self.floor_resources.refresh(state)
        self.evidence.refresh(state)
        self.shop.refresh(state)
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
        if self.scene_popup is not None and self.scene_popup.isVisible():self.scene_popup.panel.refresh()
        from .player_replay_archive import snapshot_notice
        self.notice.setText(snapshot_notice(self,len(self.rows),state))

    def selected(self, *_):
        item = self.entries.currentItem()
        row = self.rows.get(item.data(Qt.ItemDataRole.UserRole)) if item else None
        from .player_shop_memory import recorded_shops
        self.shop_button.setVisible(bool(row and any(index==row['index']for index,_ in recorded_shops(self.snapshot or{}))))
        from .player_recorded_scene import recorded_context
        context=recorded_context(self.snapshot or{},row['index'])if row else None
        self.scene_button.setVisible(context is not None)
        binding=(self.sessions.currentData(),row['index'],repr(context))if context and row else None
        if binding!=self.scene_binding:self.close_scene()
        text = event_text(row) if row else '选择一条记录查看；读取时间不等于游戏动作发生时间。'
        if self.detail.toPlainText() != text:
            self.detail.setPlainText(text)

    def open_selected_shop(self):
        self.refresh();item=self.entries.currentItem();index=item.data(Qt.ItemDataRole.UserRole)if item else None
        if self.shop.select_observation(index):self.tabs.setCurrentWidget(self.shop);return True
        return False

    def close_scene(self):
        if self.scene_popup is not None:self.scene_popup.close();self.scene_popup=None
        self.scene_binding=None

    def open_selected_scene(self):
        self.refresh();item=self.entries.currentItem();index=item.data(Qt.ItemDataRole.UserRole)if item else None
        from .player_recorded_scene import recorded_context
        context=recorded_context(self.snapshot or{},index)
        if context is None:self.close_scene();return False
        self.close_scene()
        from types import SimpleNamespace
        from .player_recent_scene import RecentScenePanel
        from .player_compact import ToolPopover
        reading=SimpleNamespace(state={'id':self.snapshot.get('id'),'last_node_content':deepcopy(context)})
        panel=RecentScenePanel(reading,historical=True);panel.noteRequested.connect(self.noteRequested)
        self.scene_popup=ToolPopover('这条历史记录的节点资料',panel,self);self.scene_popup.panel=panel;self.scene_popup.resize(760,600)
        self.scene_binding=(self.sessions.currentData(),index,repr(context));self.scene_popup.show();return True

    def hideEvent(self,event):
        self.close_scene();super().hideEvent(event)

    def closeEvent(self,event):
        self.close_scene();super().closeEvent(event)
