"""Manual ritual-effect reading and a separate, unchanged fixed-battle preview."""
from copy import deepcopy
import json

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                              QComboBox, QPushButton, QTabWidget, QPlainTextEdit)

from . import ritual_weakening as results
from .player_node_information import _plain
from .ui_state import replace_text


NOTICE = '只查阅调谐仪式的选项与弱化资料；不交付物品、不改变本局，也不应用弱化计算。'
IDENTITY_FIELDS = ('event_id', 'scene_key', 'choice_key', 'reference_id', 'weakening_id')


def choice_label(row):
    scene = int(row['scene_key'].rsplit(':', 1)[1]) + 1
    choice = int(row['choice_key'].rsplit(':', 1)[1]) + 1
    return f'流程{scene} · 选项{choice}：' + _plain(row['choice_title'])


def reference_text(row, packet):
    other = [r for r in packet['choices']
             if r['weakening_id'] == row['weakening_id'] and r['reference_id'] != row['reference_id']]
    lines = ['【正在查阅】', choice_label(row), '', '【交付方式与条件资料】',
             _plain(row.get('condition_text')) or '资料未另列选择条件；不能据此认定本局可选。',
             '提交数量与本局实际消耗仍未确认，不默认1件。', '',
             '【选项叙述原文】',
             _plain(row['choice_description']) or _plain(row['choice_title']),
             '原文中的叙述不单独作为效果结论；具体作用看下方已核对的效果说明。', '',
             '【同一效果的另一种方式】']
    if other:
        for alternative in other:
            lines.append(choice_label(alternative))
            if alternative.get('condition_text'):
                lines.append(_plain(alternative['condition_text']))
        lines.append('源私钥在这条选择中可替代对应的一项需求，不表示一次替代全部三个步骤。')
        lines.append('以上是分别列出的选择，不表示两种物品必须同时交付，也不能把效果重复相加。')
    else:
        lines.append('没有核对到另一种方式，不从同名选项推断。')
    lines += ['', '【资料所述弱化效果】', _plain(row['effect_text'])]
    if row['weakening_id'] == 'rogue_6_chimera_weaken_2':
        lines.append('“无法再吞噬生命”是选项叙述；已核对的效果为伤害降低，不能当作无伤或不再扣血。')
    lines += ['',
              '【相关作战资料】', '畸症：可用下方按钮单独查看固定地图、敌人与出怪资料。',
              '这是相关作战资料，不表示提交这项物品后立即进入该战斗。', '',
              '【本局尚未确认】',
              '当前是否满足条件、是否已选择或消耗物品、弱化是否已附着或生效：尚未确认。',
              '实际属性、伤害和技能结果仍未确认；这里不会把资料说明套入计算。']
    return '\n'.join(lines)


def _same_json(left, right):
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


class RitualWeakeningPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('调谐仪式 · 首领弱化资料')
        self.setModal(False)
        self.resize(900, 680)
        self.event_id = None
        self.scope_key = None
        self.packet = None
        self._view_key = self._reading_key = self._source_scope = None
        self.battle_window = None
        self.battle_preview = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(NOTICE)
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        self.choice = QComboBox()
        self.choice.setAccessibleName('调谐仪式的完整交付选项')
        self.choice.setPlaceholderText('请选择要查阅的选项；不代表游戏中已经选择')
        layout.addWidget(self.choice)
        self.reading_tabs = QTabWidget()
        self.player_text = QPlainTextEdit()
        self.source_text = QPlainTextEdit()
        for reader, title in ((self.player_text, '玩家说明'), (self.source_text, '资料与依据')):
            reader.setReadOnly(True)
            reader.setAccessibleName('调谐仪式 · ' + title)
            self.reading_tabs.addTab(reader, title)
        layout.addWidget(self.reading_tabs, 1)
        self.open_stage_button = QPushButton('查看相关作战：畸症')
        self.open_stage_button.setToolTip('只打开助手中的固定战斗资料；不会提交物品或进入游戏战斗。')
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
            self.battle_preview.set_stage(None)
        if self.battle_window is not None:
            self.battle_window.close()
            self.battle_window.deleteLater()
        self.battle_window = self.battle_preview = None

    def _invalidate(self, message):
        self.packet = None
        self._view_key = self._reading_key = self._source_scope = None
        self._populate([], None)
        self.open_stage_button.setEnabled(False)
        self._clear_battle()
        for reader in (self.player_text, self.source_text):
            replace_text(reader, message, preserve=False)
        self.reading_tabs.setCurrentIndex(0)

    def set_reference(self, event_id, *, scope_key=None):
        scope = (event_id, deepcopy(scope_key))
        if scope != (self.event_id, self.scope_key):
            self._invalidate('旧选择、效果与关联预览已清除；请手动选择要查阅的资料。')
        self.event_id, self.scope_key = scope
        self.refresh_reference()

    def _rows(self, packet):
        if packet.get('event_id') != self.event_id or type(packet.get('scope_key')) is not str:
            raise ValueError('Ritual event scope changed.')
        rows = packet['choices']
        if type(rows) is not list:
            raise ValueError('Ritual choices unavailable.')
        seen = set()
        for row in rows:
            if type(row) is not dict or any(type(row.get(k)) is not str for k in IDENTITY_FIELDS):
                raise ValueError('Ritual choice identity incomplete.')
            if (row['event_id'] != self.event_id or row['reference_id'] != row['choice_key']
                    or row['reference_id'] in seen
                    or not row['scene_key'].startswith(self.event_id + ':scene:')
                    or not row['choice_key'].startswith(row['scene_key'] + ':choice:')
                    or not row['scene_key'].rsplit(':', 1)[1].isdigit()
                    or not row['choice_key'].rsplit(':', 1)[1].isdigit()):
                raise ValueError('Ritual choice identity inconsistent.')
            seen.add(row['reference_id'])
        return rows

    @staticmethod
    def _stage_reference(reference):
        return (type(reference) is dict and reference.get('stage_id') == 'ro6_b_6'
                and reference.get('title') == '畸症' and reference.get('reference_only') is True
                and 'immediate_transition' in reference and reference['immediate_transition'] is None)

    def _details(self, row):
        details = results.weakening_details(self.event_id, row['scene_key'], row['choice_key'])
        if (type(details) is not dict or details.get('source_valid') is not True
                or details.get('status') != 'documented_reference'
                or details.get('event_id') != self.event_id
                or not _same_json(details.get('reference'), row)
                or not self._stage_reference(details.get('related_stage_reference'))
                or not _same_json(details['related_stage_reference'], row['related_stage_reference'])):
            raise ValueError('Ritual details no longer match the complete selected choice.')
        return details

    def refresh_reference(self, *_):
        selected = self.choice.currentData()
        try:
            packet = results.event_reference(self.event_id)
            if (type(packet) is not dict or packet.get('target') is not True
                    or packet.get('status') != 'documented_reference' or packet.get('source_valid') is not True):
                raise ValueError('Ritual sources unavailable.')
            rows = self._rows(packet)
            if self._source_scope is not None and self._source_scope != packet['scope_key']:
                selected = None
                self._view_key = self._reading_key = None
                self._clear_battle()
                self.reading_tabs.setCurrentIndex(0)
            self._populate(rows, selected)
            row = next((r for r in rows if r['reference_id'] == self.choice.currentData()), None)
            details = self._details(row) if row else None
            key = (self.event_id, self.scope_key, packet['scope_key'],
                   row['scene_key'] if row else None, row['choice_key'] if row else None,
                   row['reference_id'] if row else None)
            same = key == self._reading_key
            player = reference_text(row, packet) if row else (
                '请手动选择要查阅的交付选项，查看条件、另一种交付方式与资料所述弱化。'
                '选择这里只展示说明，不会提交物品或打开战斗。')
            source = json.dumps({'packet': packet, 'selected_weakening_details': details, 'notice': NOTICE},
                                ensure_ascii=False, indent=2, allow_nan=False)
        except (OSError, ValueError, KeyError, TypeError):
            self._invalidate('调谐仪式资料未能重新核对；旧选择、效果与关联预览已清除，请稍后手动重新选择。')
            return
        self.packet = packet
        self._source_scope = packet['scope_key']
        self.open_stage_button.setEnabled(details is not None)
        replace_text(self.player_text, player, preserve=same)
        replace_text(self.source_text, source, preserve=same)
        self._view_key = key if row else None
        self._reading_key = key
        # The separate battle reader is deliberately untouched on a valid refresh.

    def open_related_stage(self):
        selected = self.choice.currentData()
        row = next((r for r in (self.packet or {}).get('choices', []) if r['reference_id'] == selected), None)
        if type(selected) is not str or row is None:
            return False
        try:
            details = self._details(row)
        except (OSError, ValueError, KeyError, TypeError):
            self._invalidate('所选弱化与关联作战未能重新核对；旧选择、效果与关联预览已清除。')
            return False
        self.refresh_reference()
        if self.choice.currentData() != selected or self.packet is None:
            return False
        if self.battle_window is None:
            from .battle_view import BattlePreviewPanel
            self.battle_window = QDialog(self)
            self.battle_window.setWindowTitle('相关固定作战资料 · 畸症')
            self.battle_window.setModal(False)
            self.battle_window.resize(1180, 850)
            layout = QVBoxLayout(self.battle_window)
            note = QLabel('固定作战资料预览；不应用所查阅的弱化，也不表示本局已进入或即将进入战斗。')
            note.setWordWrap(True)
            layout.addWidget(note)
            self.battle_preview = BattlePreviewPanel(self.battle_window)
            layout.addWidget(self.battle_preview, 1)
        self.battle_preview.set_stage(details['related_stage_reference']['stage_id'])
        self.battle_window.show()
        self.battle_window.raise_()
        self.battle_window.activateWindow()
        return True
