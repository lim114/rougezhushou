"""Read exact event-choice reward illustrations without changing a run."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox,
                              QTabWidget, QPlainTextEdit)

from . import named_reward_items as results
from .player_node_information import _plain
from .ui_state import replace_text


NOTICE = '手动查阅选项对应的奖励资料；不会领取物品、改动本局或勾选计算藏品。'
IDENTITY_FIELDS = ('reference_id', 'event_id', 'scene_key', 'choice_key', 'item_id')
KIND_NAMES = {'RELIC': '收藏品', 'SCRAP': '零件'}


def choice_label(row):
    """Display ordinal labels only; they are not progress or entry evidence."""
    scene = int(row['scene_key'].rsplit(':', 1)[1]) + 1
    choice = int(row['choice_key'].rsplit(':', 1)[1]) + 1
    return (f'流程{scene} · 选项{choice}：' + _plain(row['choice_title'])
            + ' → ' + _plain(row['name']))


def item_text(details):
    row, item = details['reference'], details['item']
    condition = _plain(row['condition_text']) if row['condition_text'] else None
    lines = [_plain(row['name']) + ' · ' + KIND_NAMES[row['item_kind']], '',
             '【对应选项】', choice_label(row),
             _plain(row['choice_description']) or '资料未另列结果说明。', '',
             '【这个选项的条件资料】', condition or
             '原资料未列出额外选择条件；不等于本局一定可以选择。', '',
             '【物品用途】', _plain(item.get('usage')) or '资料未写明。', '',
             '【完整物品说明】', _plain(item.get('description')) or '资料未写明。', '',
             '【图鉴解锁说明】', _plain(item.get('unlockCondDesc')) or '资料未另列图鉴解锁文字。',
             '这里是物品图鉴的解锁说明，不能直接当作当前选项的出现或可选条件。', '',
             '【数量与本局情况】',
             '原资料明确了物品名称，未明确本次奖励数量；不默认1件。',
             '本局能否选择、是否领取或持有、是否已生效：尚未确认。',
             '同一物品的不同选项分别查阅，不能把各分支的奖励相加。']
    return '\n'.join(lines)


class NamedRewardItemsPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('选项奖励 · 物品图文')
        self.setModal(False)
        self.resize(900, 680)
        self.event_id = None
        self.scope_key = None
        self.packet = None
        self._view_key = None
        self._reading_key = None
        self._source_scope = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(NOTICE)
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        self.choice = QComboBox()
        self.choice.setAccessibleName('手动查阅奖励图文的完整选项')
        self.choice.setPlaceholderText('请选择要查阅的选项；不表示游戏中已经选择')
        layout.addWidget(self.choice)
        self.icon = QLabel()
        self.icon.setAccessibleName('所选奖励的固定资料图标')
        self.icon.hide()
        layout.addWidget(self.icon)
        self.reading_tabs = QTabWidget()
        self.player_text = QPlainTextEdit()
        self.source_text = QPlainTextEdit()
        for reader, title in ((self.player_text, '玩家说明'), (self.source_text, '资料与依据')):
            reader.setReadOnly(True)
            reader.setAccessibleName('选项奖励图文 · ' + title)
            self.reading_tabs.addTab(reader, title)
        layout.addWidget(self.reading_tabs, 1)
        self.choice.currentIndexChanged.connect(self.refresh_reference)
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

    def _invalidate(self, message):
        self.packet = None
        self._view_key = self._reading_key = self._source_scope = None
        self._populate([], None)
        self.icon.clear()
        self.icon.hide()
        self.icon.setAccessibleName('所选奖励的固定资料图标')
        for reader in (self.player_text, self.source_text):
            replace_text(reader, message, preserve=False)
        self.reading_tabs.setCurrentIndex(0)

    def set_reference(self, event_id, *, scope_key=None):
        scope = (event_id, deepcopy(scope_key))
        if scope != (self.event_id, self.scope_key):
            self._invalidate('旧选择与图文已清除；请手动选择要查阅的资料。')
        self.event_id, self.scope_key = scope
        self.refresh_reference()

    def _rows(self, packet):
        if packet.get('event_id') != self.event_id or type(packet.get('scope_key')) is not str:
            raise ValueError('Reward event scope changed.')
        rows = packet['choices']
        if type(rows) is not list:
            raise ValueError('Reward choices unavailable.')
        seen = set()
        for row in rows:
            if type(row) is not dict or any(type(row.get(key)) is not str for key in IDENTITY_FIELDS):
                raise ValueError('Incomplete reward choice identity.')
            if (row['event_id'] != self.event_id or row['reference_id'] != row['choice_key']
                    or row['reference_id'] in seen or row.get('item_kind') not in KIND_NAMES
                    or not row['scene_key'].startswith(self.event_id + ':scene:')
                    or not row['choice_key'].startswith(row['scene_key'] + ':choice:')
                    or not row['scene_key'].rsplit(':', 1)[1].isdigit()
                    or not row['choice_key'].rsplit(':', 1)[1].isdigit()):
                raise ValueError('Inconsistent reward choice identity.')
            seen.add(row['reference_id'])
        return rows

    def _details(self, row):
        details = results.item_details(self.event_id, row['scene_key'], row['choice_key'])
        if (type(details) is not dict or details.get('status') != 'documented_reference'
                or details.get('source_valid') is not True or details.get('event_id') != self.event_id
                or any(type(details.get(key)) is not dict for key in ('reference', 'item', 'icon_reference'))):
            raise ValueError('Reward details unavailable.')
        # Whole-row comparison preserves distinct conditions for the same item.
        if (json.dumps(details['reference'], sort_keys=True, allow_nan=False)
                != json.dumps(row, sort_keys=True, allow_nan=False)):
            raise ValueError('Reward details no longer match the exact choice.')
        item, icon = details['item'], details['icon_reference']
        if (item.get('id') != row['item_id'] or item.get('type') != row['item_kind']
                or icon.get('item_id') != row['item_id'] or icon.get('icon_id') != item.get('iconId')):
            raise ValueError('Reward image or item identity changed.')
        relative = Path(icon['file'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Reward image path is outside the public source root.')
        raw = (results.ROOT / relative).read_bytes()
        if (type(icon.get('bytes')) is not int or len(raw) != icon['bytes']
                or sha256(raw).hexdigest() != icon['sha256']):
            raise ValueError('Reward image bytes changed.')
        pixmap = QPixmap()
        if not pixmap.loadFromData(raw):
            raise ValueError('Reward image cannot be decoded.')
        return details, pixmap

    def refresh_reference(self, *_):
        selected = self.choice.currentData()
        try:
            packet = results.event_reference(self.event_id)
            if (type(packet) is not dict or packet.get('target') is not True
                    or packet.get('status') != 'documented_reference'
                    or packet.get('source_valid') is not True):
                raise ValueError('Reward sources unavailable.')
            rows = self._rows(packet)
            if self._source_scope is not None and packet['scope_key'] != self._source_scope:
                selected = None
                self._reading_key = self._view_key = None
                self.reading_tabs.setCurrentIndex(0)
            self._populate(rows, selected)
            row = next((row for row in rows if row['reference_id'] == self.choice.currentData()), None)
            details, pixmap = self._details(row) if row else (None, None)
            key = (self.event_id, self.scope_key, packet['scope_key'],
                   row['scene_key'] if row else None, row['choice_key'] if row else None,
                   row['reference_id'] if row else None)
            same = key == self._reading_key
            player = item_text(details) if details else (
                '请手动选择一条完整选项，查看对应收藏品或零件的图标、用途与说明。'
                '这里只查阅资料，不会在游戏中作出选择。')
            source = json.dumps({'packet': packet, 'selected_item_details': details, 'notice': NOTICE},
                                ensure_ascii=False, indent=2, allow_nan=False)
        except (OSError, ValueError, KeyError, TypeError):
            self._invalidate('奖励图文资料未能重新核对；旧选择、图标与说明已清除，请稍后手动重新选择。')
            return
        self.packet = packet
        self._source_scope = packet['scope_key']
        if pixmap is None:
            self.icon.clear()
            self.icon.hide()
            self.icon.setAccessibleName('所选奖励的固定资料图标')
        else:
            self.icon.setPixmap(pixmap.scaledToWidth(96, Qt.TransformationMode.SmoothTransformation))
            self.icon.setAccessibleName('固定资料图标：' + _plain(row['name']))
            self.icon.show()
        replace_text(self.player_text, player, preserve=same)
        replace_text(self.source_text, source, preserve=same)
        self._view_key = key if row else None
        self._reading_key = key
