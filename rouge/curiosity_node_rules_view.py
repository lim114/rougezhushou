"""Manual, source-bound fate-node reading; no game/run or route actions."""
from copy import deepcopy
import json

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox,
                              QPushButton, QTabWidget, QPlainTextEdit)

from . import curiosity_node_rules as rules
from .player_node_information import _plain
from .ui_state import replace_text

NOTICE = '只查阅命运所指的固定资料；不会标记地图、选择游戏选项或改变本局。'
IDENTITY_FIELDS = ('event_id', 'scene_key', 'choice_key', 'reference_id')


def choice_label(row):
    scene = int(row['scene_key'].rsplit(':', 1)[1]) + 1
    choice = int(row['choice_key'].rsplit(':', 1)[1]) + 1
    return f'场景{scene} · 选项{choice}：' + _plain(row['choice_title'])


def reference_text(row, packet):
    context = packet['node_context_reference']
    lines = ['【适用范围】', _plain(context['title'])]
    lines += [_plain(t) for t in context['texts']]
    lines += ['这是固定资料对第五层流程的描述，不据此确定本局节点数量、位置或事件身份。']
    if row is None:
        lines += ['', '【查看具体选择】',
                  '请在上方选择一项，分别查看标记、收藏品、节点转换、暂离或决战的说明。',
                  '未选择时不会打开作战，也不会把某一项的结果套到其它选项。']
        return '\n'.join(lines)
    lines += ['', '【正在查阅】', choice_label(row), '', '【选择文字】',
              _plain(row['choice_description']) or '资料未另列结果。']
    if row.get('condition_text'):
        lines += ['', '【这项选择的条件或说明】', _plain(row['condition_text'])]
    for rule in row['documented_rules']:
        lines += ['', '【' + _plain(rule['title']) + '】', _plain(rule['text'])]
    if row.get('related_stage_reference'):
        lines += ['', '【对应作战资料】',
                  '混沌源阶理论：可用下方按钮单独查看固定地图、敌人与出怪资料。',
                  '这里的按钮只打开助手资料，不代表本局已转换节点、已经进入或已经开战。']
    lines += ['', '【本局尚未确认】',
              '实际事件身份、节点位置、标记、是否选择、是否支付或领取、转换与再访状态均未确认。',
              '这里只解释资料，不更新地图历史、库存、藏品效果或战斗计算。']
    return '\n'.join(lines)


def _same(left, right):
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


class CuriosityNodeRulesPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('命运所指 · 标记、转换与再访')
        self.setModal(False)
        self.resize(940, 730)
        self.event_id = self.scope_key = self.packet = None
        self._reading_key = self._source_scope = None
        self.battle_window = self.battle_preview = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(NOTICE)
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        self.choice = QComboBox()
        self.choice.setAccessibleName('命运所指的具体资料选项')
        self.choice.setPlaceholderText('请选择要查阅的选项；不代表游戏中已经选择')
        layout.addWidget(self.choice)
        self.reading_tabs = QTabWidget()
        self.player_text, self.source_text = QPlainTextEdit(), QPlainTextEdit()
        for reader, title in ((self.player_text, '玩家说明'), (self.source_text, '资料与依据')):
            reader.setReadOnly(True)
            reader.setAccessibleName('命运所指 · ' + title)
            self.reading_tabs.addTab(reader, title)
        layout.addWidget(self.reading_tabs, 1)
        self.open_stage_button = QPushButton('查看对应作战：混沌源阶理论')
        self.open_stage_button.setToolTip('只打开固定资料，不转换节点或进入游戏战斗。')
        self.open_stage_button.setEnabled(False)
        layout.addWidget(self.open_stage_button)
        self.choice.currentIndexChanged.connect(self.refresh_reference)
        self.open_stage_button.clicked.connect(self.open_related_stage)
        self.refresh_reference()

    def _populate(self, rows, selected):
        self.choice.blockSignals(True)
        try:
            self.choice.clear()
            for row in rows:
                self.choice.addItem(choice_label(row), row['reference_id'])
            self.choice.setCurrentIndex(self.choice.findData(selected) if type(selected) is str else -1)
        finally:
            self.choice.blockSignals(False)

    def _clear_battle(self):
        if self.battle_preview is not None:
            try:
                self.battle_preview.set_stage(None)
            except (OSError, ValueError, KeyError, TypeError, RuntimeError):
                pass
        if self.battle_window is not None:
            try:
                self.battle_window.close()
                self.battle_window.deleteLater()
            except RuntimeError:
                pass
        self.battle_window = self.battle_preview = None

    def _invalidate(self, message):
        self.packet = None
        self._reading_key = self._source_scope = None
        self._populate([], None)
        self._clear_battle()
        self.open_stage_button.setEnabled(False)
        self.reading_tabs.setCurrentIndex(0)
        for reader in (self.player_text, self.source_text):
            replace_text(reader, message, preserve=False)

    def set_reference(self, event_id, *, scope_key=None):
        if (self.event_id, self.scope_key) != (event_id, scope_key):
            self._invalidate('正在切换资料范围，请重新选择具体选项。')
        self.event_id, self.scope_key = event_id, deepcopy(scope_key)
        self.refresh_reference()

    def _rows(self, packet):
        rows = packet['choices']
        if type(rows) is not list or len(rows) != (2 if self.event_id == 'community_group_030' else 3):
            raise ValueError('Incomplete fate-node choices.')
        seen = set()
        for row in rows:
            if type(row) is not dict or any(type(row.get(k)) is not str for k in IDENTITY_FIELDS):
                raise ValueError('Fate choice identity incomplete.')
            if (row['event_id'] != self.event_id or row['reference_id'] != row['choice_key']
                    or row['reference_id'] in seen
                    or not row['scene_key'].startswith(self.event_id + ':scene:')
                    or not row['choice_key'].startswith(row['scene_key'] + ':choice:')):
                raise ValueError('Fate choice identity inconsistent.')
            seen.add(row['reference_id'])
        return rows

    @staticmethod
    def _stage_ok(stage):
        return stage is None or (type(stage) is dict and stage.get('stage_id') == 'ro6_b_5'
            and stage.get('title') == '混沌源阶理论' and stage.get('reference_only') is True
            and 'immediate_transition' in stage and stage['immediate_transition'] is None)

    def _details(self, row):
        detail = rules.choice_reference(self.event_id, row['scene_key'], row['choice_key'])
        if (type(detail) is not dict or detail.get('status') != 'documented_reference'
                or detail.get('source_valid') is not True or detail.get('event_id') != self.event_id
                or not _same(detail.get('reference'), row)
                or not self._stage_ok(detail.get('related_stage_reference'))
                or not _same(detail.get('related_stage_reference'), row.get('related_stage_reference'))):
            raise ValueError('Fate choice source changed.')
        return detail

    def refresh_reference(self, *_):
        selected = self.choice.currentData()
        try:
            packet = rules.event_reference(self.event_id)
            if (type(packet) is not dict or packet.get('target') is not True
                    or packet.get('status') != 'documented_reference' or packet.get('source_valid') is not True):
                raise ValueError('Fate sources unavailable.')
            rows = self._rows(packet)
            if self._source_scope is not None and self._source_scope != packet['scope_key']:
                selected = None
                self._reading_key = None
                self._clear_battle()
                self.reading_tabs.setCurrentIndex(0)
            self._populate(rows, selected)
            row = next((r for r in rows if r['reference_id'] == self.choice.currentData()), None)
            detail = self._details(row) if row else None
            key = (self.event_id, self.scope_key, packet['scope_key'], row['reference_id'] if row else None)
            same = key == self._reading_key
            if not same:
                self._clear_battle()
            player = reference_text(row, packet)
            source = json.dumps({'event_reference': packet, 'selected_choice': detail, 'notice': NOTICE},
                                ensure_ascii=False, indent=2, allow_nan=False)
        except (OSError, ValueError, KeyError, TypeError):
            self._invalidate('命运所指资料暂时未能重新核对；旧选择、说明与作战预览已清除。恢复后请手动重新选择。')
            return
        self.packet = packet
        self._source_scope, self._reading_key = packet['scope_key'], key
        self.open_stage_button.setEnabled(bool(detail and detail.get('related_stage_reference')))
        replace_text(self.player_text, player, preserve=same)
        replace_text(self.source_text, source, preserve=same)

    def open_related_stage(self):
        selected = self.choice.currentData()
        row = next((r for r in (self.packet or {}).get('choices', []) if r['reference_id'] == selected), None)
        if type(selected) is not str or row is None:
            return False
        try:
            details = self._details(row)
            if not details.get('related_stage_reference'):
                return False
        except (OSError, ValueError, KeyError, TypeError):
            self._invalidate('所选说明与作战资料未能重新核对；旧说明和预览已清除。')
            return False
        self.refresh_reference()
        if self.choice.currentData() != selected or self.packet is None:
            return False
        try:
            if self.battle_window is None:
                from .battle_view import BattlePreviewPanel
                self.battle_window = QDialog(self)
                self.battle_window.setWindowTitle('固定作战资料 · 混沌源阶理论')
                self.battle_window.setModal(False)
                self.battle_window.resize(1180, 850)
                layout = QVBoxLayout(self.battle_window)
                note = QLabel('固定资料预览；不转换节点，不应用节点或概念体效果，不代表本局已经开战。')
                note.setWordWrap(True)
                layout.addWidget(note)
                self.battle_preview = BattlePreviewPanel(self.battle_window)
                layout.addWidget(self.battle_preview, 1)
            self.battle_preview.set_stage('ro6_b_5')
            self.battle_window.show()
            self.battle_window.raise_()
            self.battle_window.activateWindow()
        except (OSError, ValueError, KeyError, TypeError, RuntimeError):
            self._invalidate('对应固定作战资料暂时无法打开；请稍后重新选择。')
            return False
        return True
