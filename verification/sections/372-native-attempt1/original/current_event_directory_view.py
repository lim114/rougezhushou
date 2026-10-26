"""A common current-event catalogue with exact, separately owned reader windows."""
import importlib, json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QListWidget, QListWidgetItem, QPlainTextEdit, QTabWidget, QPushButton
from . import current_event_directory as model
from .ui_state import replace_text


def make_event_dialog(target, parent=None):
    if type(target) is not dict or type(target.get('event')) is not dict: return None
    row = target['event']; reader = row['reader']; eid = row['event_id']
    fresh = model.reference(row.get('id'))
    if fresh is None or not model.same(row, fresh['selected']): return None
    key = target.get('entry_key'); entry = next((e for e in row['entries'] if e['key'] == key), None)
    if key is not None and entry is None: return None
    expected = {'event': row, 'entry_key': key,
                'scene_id': entry['scene_id'] if entry else row['event']['entry_scene_id'],
                'choice_id': entry['choice_id'] if entry else None, 'actual_eligible': None, 'run_updated': False}
    if not model.same(target, expected): return None
    args = {
        'resources': ('current_resource_events_view', 'CurrentResourceEventsDialog', (eid,)),
        'vine333': ('current_vine_events_view', 'CurrentVineEventsDialog', (eid,)),
        'encounters': ('current_encounters_view', 'CurrentEncountersDialog', (eid,)),
        'shadow346': ('current_shadow_view', 'CurrentShadowDialog', ()),
        'memory336': ('current_memory_tree_view', 'CurrentMemoryTreeDialog', ()),
        'lake': ('current_lake_view', 'CurrentLakeDialog', ()),
        'cave334': ('current_cave_view', 'CurrentCaveDialog', ()),
        'agency340': ('current_agency_view', 'CurrentAgencyDialog', ()),
        'peace343': ('current_peace_view', 'CurrentPeaceDialog', ()),
        'dog335': ('current_lone_dog_view', 'CurrentLoneDogDialog', ()),
        'sand': ('current_sand_view', 'CurrentSandDialog', (eid,)),
        'resting345': ('current_resting_view', 'CurrentRestingDialog', ()),
        'scout342': ('current_scout_view', 'CurrentScoutDialog', ()),
        'reconstruction344': ('current_reconstruction_view', 'CurrentReconstructionDialog', ()),
        'shop': ('current_unattended_shop_view', 'CurrentUnattendedShopDialog', ()),
        'portal341': ('current_portal_view', 'CurrentPortalDialog', ()),
        'box': ('box_event_view', 'BoxEventDialog', ()),
        'ritual': ('current_ritual_view', 'CurrentRitualDialog', (eid,)),
        'exit339': ('current_exit_view', 'CurrentExitDialog', ()),
        'rest': ('current_rest_travel_view', 'CurrentRestTravelDialog', (eid,)),
        'flows321': ('documented_event_flow_view', 'DocumentedEventFlowDialog', (eid,))}
    if reader not in args: return None
    module, cls, positional = args[reader]
    dialog = getattr(importlib.import_module('.' + module, __package__), cls)(*positional, parent=parent)
    panel = dialog.panel
    if panel.result is None or panel.result['event']['id'] != eid:
        dialog.close(); return None
    panel.scene.setCurrentIndex(panel.scene.findData(target['scene_id']))
    if panel.scene_id != target['scene_id']:
        dialog.close(); return None
    cid = target['choice_id']
    if cid is not None:
        matches = [i for i in range(panel.choices.count()) if panel.choices.item(i).data(Qt.ItemDataRole.UserRole) == cid]
        if len(matches) != 1: dialog.close(); return None
        panel.choices.setCurrentRow(matches[0])
        if panel.choice_id != cid: dialog.close(); return None
    return dialog


class CurrentEventDirectoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.result = None; self.event_dialog = None; self.event_id = None; self.entry_key = None
        layout = QVBoxLayout(self); notice = QLabel(model.NOTICE); notice.setWordWrap(True); layout.addWidget(notice)
        row = QHBoxLayout(); self.query = QLineEdit(); self.query.setPlaceholderText('搜索事件、选项或奖励原文'); self.query.setAccessibleName('当前事件目录搜索')
        self.node_type = QComboBox(); self.node_type.setAccessibleName('固定资料所列节点类别'); self.node_type.addItem('全部资料分类', None)
        self.topic = QComboBox(); self.topic.setAccessibleName('原文提到的条件或内容'); self.topic.addItem('全部文字内容', None)
        for key, label in model.TOPICS: self.topic.addItem(label, key)
        row.addWidget(self.query, 2); row.addWidget(self.node_type, 1); row.addWidget(self.topic, 1); layout.addLayout(row)
        self.refresh_button = QPushButton('重新核对事件目录'); layout.addWidget(self.refresh_button)
        self.count = QLabel(); self.count.setWordWrap(True); layout.addWidget(self.count)
        row = QHBoxLayout(); self.events = QListWidget(); self.events.setAccessibleName('当前已核对事件'); self.entries = QListWidget(); self.entries.setAccessibleName('准确对话中的选项或结果参考')
        self.events.setMaximumHeight(200); self.entries.setMaximumHeight(200); row.addWidget(self.events, 1); row.addWidget(self.entries, 2); layout.addLayout(row)
        self.open_button = QPushButton('打开这份事件资料'); layout.addWidget(self.open_button)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for reader, label in ((self.player, '事件与原文'), (self.technical, '来源与范围')):
            reader.setReadOnly(True); self.tabs.addTab(reader, label)
        layout.addWidget(self.tabs, 1)
        self.query.textChanged.connect(self._filters_changed); self.node_type.currentIndexChanged.connect(self._filters_changed)
        self.topic.currentIndexChanged.connect(self._filters_changed); self.refresh_button.clicked.connect(self.refresh_reference)
        self.events.currentItemChanged.connect(self._event_selected); self.entries.currentItemChanged.connect(self._entry_selected)
        self.open_button.clicked.connect(self.open_event); self.refresh_reference()

    def _close_event(self):
        if self.event_dialog is not None:
            panel = self.event_dialog.panel
            if hasattr(panel, 'clear_reference'): panel.clear_reference()
            self.event_dialog.close()
        self.event_dialog = None

    def clear_reference(self):
        self._close_event(); self.result = None; self.event_id = None; self.entry_key = None
        for w in (self.events, self.entries):
            blocked = w.blockSignals(True); w.clear(); w.blockSignals(blocked)
        self.open_button.setEnabled(False); self.count.setText('来源尚未核对；没有沿用旧目录。')
        replace_text(self.player, model.UNAVAILABLE, preserve=False); replace_text(self.technical, '', preserve=False); self.tabs.setCurrentIndex(0)

    def _filters(self): return {'query': self.query.text(), 'node_type': self.node_type.currentData(), 'topic': self.topic.currentData()}

    def refresh_reference(self, *_):
        fresh = model.reference(**self._filters())
        if fresh is None: self.clear_reference(); return False
        keep = self.result is not None and model.same(self.result['source_identity'], fresh['source_identity'])
        selected = self.event_id if keep else None; entry = self.entry_key if keep else None
        if not keep: self._close_event()
        self.result = fresh
        if self.node_type.count() == 1:
            blocked = self.node_type.blockSignals(True)
            for label in dict.fromkeys(t for r in fresh['data']['rows'] for t in r['node_types']): self.node_type.addItem(label, label)
            self.node_type.addItem('分类尚未明确', 'unclassified'); self.node_type.blockSignals(blocked)
        blocked = self.events.blockSignals(True); self.events.clear()
        for r in fresh['rows']:
            item = QListWidgetItem(r['title'] + ' · ' + ('、'.join(r['node_types']) or '分类未明')); item.setData(Qt.ItemDataRole.UserRole, r['id']); self.events.addItem(item)
            if r['id'] == selected: self.events.setCurrentItem(item)
        self.events.blockSignals(blocked)
        if selected is None: self.events.setCurrentRow(-1)
        self.count.setText('当前显示' + str(len(fresh['rows'])) + '份事件资料；固定总目录39份，完整游戏事件池未知。')
        self._event_selected(self.events.currentItem(), preserve=keep, requested_entry=entry)
        if keep and self.event_dialog is not None and self.event_dialog.isVisible():
            if not self.event_dialog.panel.refresh_reference(): self._close_event()
        return True

    def _filters_changed(self, *_):
        self._close_event(); self.event_id = None; self.entry_key = None; self.refresh_reference()

    def _event_selected(self, item, *_, preserve=False, requested_entry=None):
        if self.result is None: return
        identity = item.data(Qt.ItemDataRole.UserRole) if item else None
        keep = preserve and identity == self.event_id
        if not keep: self._close_event()
        self.event_id = identity; self.entry_key = requested_entry if keep else None
        self.result['selected'] = next((r for r in self.result['rows'] if r['id'] == identity), None)
        blocked = self.entries.blockSignals(True); self.entries.clear(); row = self.result['selected']
        for entry in row['entries'] if row else []:
            label = entry['scene_label'] + ' · ' + entry['title']
            if entry['presentation'] == 'outcome_reference' or entry['actual_game_button'] is False: label += '（结果参考）'
            item = QListWidgetItem(label); item.setData(Qt.ItemDataRole.UserRole, entry['key']); self.entries.addItem(item)
            if entry['key'] == self.entry_key: self.entries.setCurrentItem(item)
        self.entries.blockSignals(blocked)
        if self.entry_key is None: self.entries.setCurrentRow(-1)
        self._render(keep)

    def _entry_selected(self, item, *_):
        self._close_event(); self.entry_key = item.data(Qt.ItemDataRole.UserRole) if item else None; self._render(False)

    def _render(self, preserve):
        if self.result is None: return
        row = self.result['selected']; self.open_button.setEnabled(row is not None)
        self.open_button.setText('打开这一段准确对话与选项' if self.entry_key else '打开这份事件的起始资料')
        replace_text(self.player, model.player_text(self.result, self.entry_key), preserve=preserve)
        replace_text(self.technical, json.dumps(row or {'notice': model.NOTICE}, ensure_ascii=False, indent=2), preserve=preserve)
        if not preserve: self.tabs.setCurrentIndex(0)

    def open_event(self):
        target = model.resolve(self.result, self.entry_key)
        if target is None: self.clear_reference(); return False
        self._close_event(); self.event_dialog = make_event_dialog(target, self)
        if self.event_dialog is None: self.clear_reference(); return False
        self.event_dialog.show(); return True

    def closeEvent(self, event): self._close_event(); super().closeEvent(event)


class CurrentEventDirectoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle('节点事件目录 · 条件原文与准确流程'); self.resize(1220, 900)
        layout = QVBoxLayout(self); self.panel = CurrentEventDirectoryPanel(self); layout.addWidget(self.panel)
    def closeEvent(self, event): self.panel.clear_reference(); super().closeEvent(event)
