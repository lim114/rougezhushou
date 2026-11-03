"""Manual reading of documented next-region effects; never changes a run."""
from copy import deepcopy
import json

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox,
                              QTabWidget, QPlainTextEdit)

from . import future_region_effects as results
from .player_node_information import _plain
from .ui_state import replace_text


EVENT = 'community_group_009'
NOTICE = ('手动查阅下一地区的资料，不执行游戏选项或改动本局。'
          '文献阶段不代表本局已经生成或生效。')
PHASE_NAMES = {'early': '早期', 'middle': '中期', 'late': '晚期'}
IDENTITY_FIELDS = ('reference_id', 'event_id', 'scene_key', 'choice_key')


def choice_text(reference, packet):
    """Keep direct resources, later node effects and victory rewards separate."""
    lines = ['【正在查阅】' + _plain(reference['choice_title']), '',
             '【选择条件资料】', _plain(reference['requirement_text']), '',
             '【选择时的直接变化】']
    for row in reference['direct_resources']:
        quantity = row['quantity_reference']
        if row['resource'] == 'gold' and row['action'] == 'gain':
            lines.append(f'资料记载：获得{quantity}源石锭。')
        elif row['resource'] == 'seed' and row['action'] == 'sow':
            lines.append(f'资料记载：种下{quantity}枚种子；不是领取种子。')
        else:
            lines.append('这项资源变化尚未整理，请保留上方选项原文。')
    lines += ['', '【下一地区的条件效果】']
    region = reference['future_region_reference']
    lines += ['下一区域：“' + _plain(region['name']) + '”（资料；一种影响部分节点的区域效果）。',
              _plain(region['affected_nodes']) + '；不是全队现在获得的加成。', '',
              '【当前难度的文献阶段】']
    phase = packet['documented_phase']
    context = packet['context']
    if phase in PHASE_NAMES:
        lines.append(f'按当前难度查表（资料）：常规行动 · 保密等级{context["difficulty"]} → {PHASE_NAMES[phase]}。')
    else:
        lines.append('当前没有可确定的文献阶段，下面三档资料均可查阅。')
        if context.get('mode') == 'NORMAL' and type(context.get('difficulty')) is int and context['difficulty'] in (0, 1):
            lines.append('保密等级0或1下，选项指定生成与所用阶段尚未核验。')
        else:
            lines.append('当前模式或难度尚无已核对的阶段对照，不默认早期。')
    lines += ['', '【三档属性资料】']
    for row in region['phases']:
        selected = row['phase'] == phase
        label = _plain(row['phase_name']) + ('（当前难度的文献阶段）' if selected else '')
        lines.append(('▶ ' if selected else '  ') + label + '：')
        lines.append(f'攻击力 +{row["attack_percent"]}%　生命值 +{row["max_hp_percent"]}%'
                     f'　（常规保密等级{row["normal_difficulty_min"]}–{row["normal_difficulty_max"]}）')
    reward = reference['conditional_victory_reward']
    lines += ['', '【战斗胜利后的奖励】',
              _plain(reward['condition']) + '，资料记载可获得随机零件。',
              '完整零件池、数量与本局实际领取：尚未确认；不能按进入节点或整层统一加算。', '',
              '【仍需确认的实际情况】',
              '本局是否可选、是否已经选择，以及实际扣除或领取：尚未确认。',
              '是否生成、具体受影响节点、实际阶段及属性变化：尚未确认。',
              '两个选项分开查阅，不能把两条分支的资源或奖励相加。']
    return '\n'.join(lines)


class FutureRegionEffectsPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('呼吸的红苔 · 下一地区影响')
        self.setModal(False)
        self.resize(900, 680)
        self.event_id = None
        self.scope_key = None
        self.mode = None
        self.difficulty = None
        self.packet = None
        self._view_key = None
        self._reading_key = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(NOTICE)
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        self.choice = QComboBox()
        self.choice.setAccessibleName('手动查阅下一地区影响的完整选项')
        self.choice.setPlaceholderText('请选择要查阅的选项；不表示游戏中已经选择')
        layout.addWidget(self.choice)
        self.reading_tabs = QTabWidget()
        self.player_text = QPlainTextEdit()
        self.source_text = QPlainTextEdit()
        for reader, title in ((self.player_text, '玩家说明'), (self.source_text, '资料与依据')):
            reader.setReadOnly(True)
            reader.setAccessibleName('红苔下一地区影响 · ' + title)
            self.reading_tabs.addTab(reader, title)
        layout.addWidget(self.reading_tabs, 1)
        self.choice.currentIndexChanged.connect(self.refresh_reference)
        self.refresh_reference()

    def _populate(self, rows, selected):
        self.choice.blockSignals(True)
        try:
            self.choice.clear()
            for row in rows:
                self.choice.addItem(_plain(row['choice_title']), row['reference_id'])
            self.choice.setCurrentIndex(self.choice.findData(selected) if type(selected) is str else -1)
        finally:
            self.choice.blockSignals(False)

    def _invalidate(self, message):
        self.packet = None
        self._view_key = None
        self._reading_key = None
        self._populate([], None)
        for reader in (self.player_text, self.source_text):
            replace_text(reader, message, preserve=False)
        self.reading_tabs.setCurrentIndex(0)

    def set_reference(self, event_id, *, mode=None, difficulty=None, scope_key=None):
        scope = (event_id, deepcopy(scope_key))
        if scope != (self.event_id, self.scope_key):
            self._invalidate('尚未选择要查阅的资料；旧选择与内容已清除，请手动选择。')
        self.event_id, self.scope_key = scope
        self.mode, self.difficulty = deepcopy(mode), deepcopy(difficulty)
        self.refresh_reference()

    def _rows(self, packet):
        rows = packet['choices']
        if type(rows) is not list or packet.get('event_id') != self.event_id:
            raise ValueError('Invalid future-region reading scope.')
        seen = set()
        for row in rows:
            if type(row) is not dict or any(type(row.get(key)) is not str for key in IDENTITY_FIELDS):
                raise ValueError('Incomplete future-region choice identity.')
            if row['event_id'] != self.event_id or row['reference_id'] in seen:
                raise ValueError('Inconsistent future-region choice identity.')
            seen.add(row['reference_id'])
        return rows

    def refresh_reference(self, *_):
        selected = self.choice.currentData()
        try:
            packet = results.event_reference(self.event_id, mode=self.mode, difficulty=self.difficulty)
            if (type(packet) is not dict or packet.get('status') != 'documented_reference'
                    or packet.get('source_valid') is not True):
                raise ValueError('Future-region sources unavailable.')
            rows = self._rows(packet)
            self._populate(rows, selected)
            row = next((row for row in rows if row['reference_id'] == self.choice.currentData()), None)
            key = (self.event_id, self.scope_key, packet['scope_key'],
                   row['scene_key'] if row else None, row['choice_key'] if row else None,
                   row['reference_id'] if row else None)
            same = key == self._reading_key
            player = choice_text(row, packet) if row else (
                '请手动选择要查阅的选项；这里只阅读下一地区的资料，不会在游戏中作出选择。')
            source = json.dumps({'packet': packet,
                'selected_reference': {key: row[key] for key in IDENTITY_FIELDS} if row else None,
                'notice': NOTICE},
                ensure_ascii=False, indent=2, allow_nan=False)
        except (OSError, ValueError, KeyError, TypeError):
            self._invalidate('下一地区资料未能重新核对；旧选择与内容已清除，请稍后手动重新选择。'
                if self.event_id == EVENT else '当前不是呼吸的红苔；旧选择与内容已清除，请打开对应事件。')
            return
        self.packet = packet
        replace_text(self.player_text, player, preserve=same)
        replace_text(self.source_text, source, preserve=same)
        self._view_key = key if row else None
        self._reading_key = key
