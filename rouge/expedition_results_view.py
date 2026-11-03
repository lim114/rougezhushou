"""Manual expedition-result reading; never dispatches, chooses or writes a run."""
from copy import deepcopy
import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QTabWidget, QPlainTextEdit)

from . import expedition_results as results
from .player_node_information import _plain
from .ui_state import replace_text

EVENT = 'community_group_024'
NOTICE = '这里只查阅派出与归来的资料，不会派出干员或选择游戏选项；本局是否可选、是否归来与实际领取仍未确认。'
RESOURCE_NAMES = {'hope': '希望', 'gold': '源石锭', 'hp': '目标生命值', 'shield': '护盾'}
IDENTITY_FIELDS = ('reference_id', 'event_id', 'scene_key', 'choice_key')


def _resources(rows):
    return '、'.join(str(row['quantity_reference']) + RESOURCE_NAMES.get(row['resource'], '未确认资源')
                    for row in rows if type(row.get('quantity_reference')) is int)


def choice_text(reference):
    lines = ['【正在查阅】' + _plain(reference['choice_title']), '', '【选择时】']
    immediate = _resources(reference['immediate_resource_references'])
    dispatch = reference['dispatch_reference']
    if dispatch is None:
        lines += ['获得' + immediate + '。', '', '【派出期间】',
                  '这项是休息，不派出干员。', '', '【归来时】',
                  '这项未列派出或归来结果，不把休息的收益推迟到归来。']
    else:
        lines += [f'派出{dispatch["operator_count_reference"]}名干员；资料未列立即获得的资源。',
                  '归来后的收益不能提前算到现在。', '', '【派出期间】',
                  '派出的干员暂时不能编入队伍。', '', '【归来时】',
                  '游戏写作“本区域探索结束后”或“进入新区域时”归来；社区资料记为“'
                  + _plain(dispatch['community_return_when']) + '”。']
        returned = _resources(reference['return_resource_references'])
        if returned:
            lines.append('归来获得' + returned + '。')
        else:
            lines.append('这条分支未明确归来资源数量，不能当作零收益。')
        item = reference['documented_return_item']
        if item is not None:
            lines += ['归来藏品：' + _plain(item['name']) + '（数量未确认）。',
                      '可手动点击“查看归来藏品说明”阅读图标与用途。']
        if reference['promotion_reference'] is False:
            lines.append('这条探索源头分支的资料标明不进阶。')
        if reference['beak_reference'] is not None:
            lines.append('条件资料：' + _plain(reference['beak_reference']['source_text']))
    unknowns = (['本局是否可选、实际选择或派出对象、是否已归来与领取、实际数量']
                if dispatch is not None else ['本局是否可选、是否已选择休息与实际领取数量'])
    if dispatch is not None:
        unknowns += ['特殊区域能否按同一归来时点处理，不能据此给出倒计时']
        if reference['promotion_reference'] is None:
            unknowns += ['普通派出的进阶、等级及技能变化']
        if reference['beak_reference'] is not None:
            unknowns += ['“喙”相关说明的当前适用与具体结果（原文见资料与依据，不能直接套用于探索源头）']
    lines += ['', '【尚未确认】', '；'.join(unknowns) + '。',
              '以上选项分开查阅，收益不能相加；这里只阅读资料，不会在游戏中执行。']
    return '\n'.join(lines)


def item_text(details):
    item = details['item']
    return '\n'.join([_plain(item['name']) + ' · 归来藏品资料', NOTICE, '',
        '【用途】', _plain(item.get('usage')) or '资料未写明。', '',
        '【物品说明】', _plain(item.get('description')) or '资料未写明。', '',
        '【物品条目的解锁说明】', _plain(item.get('unlockCondDesc')) or '资料未写明。',
        _plain(details['unlock_notice']), '',
        '这是探索源头的归来藏品说明，不是选择时立即领取的奖励。',
        '数量、实际归来与领取、是否持有或生效：尚未确认。'])


class ExpeditionResultsPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('未涉足之树 · 派出与归来结果')
        self.setModal(False)
        self.resize(900, 680)
        self.event_id = None
        self.scope_key = None
        self.packet = None
        self._view_key = None
        self._details_identity = None
        layout = QVBoxLayout(self)
        self.notice = QLabel(NOTICE)
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        row = QHBoxLayout()
        self.choice = QComboBox()
        self.choice.setAccessibleName('手动查阅的完整派出或休息选项')
        self.choice.setPlaceholderText('请选择要查阅的选项；不表示游戏中已选择')
        self.open_item_button = QPushButton('查看归来藏品说明')
        self.open_item_button.setEnabled(False)
        self.open_item_button.hide()
        row.addWidget(self.choice, 1)
        row.addWidget(self.open_item_button)
        layout.addLayout(row)
        self.icon = QLabel()
        self.icon.setAccessibleName('手动查阅的归来藏品固定图标')
        self.icon.hide()
        layout.addWidget(self.icon)
        self.reading_tabs = QTabWidget()
        self.result_text = QPlainTextEdit()
        self.item_text = QPlainTextEdit()
        self.source_text = QPlainTextEdit()
        for reader, title in ((self.result_text, '派出与归来结果'),
                              (self.item_text, '归来藏品说明'),
                              (self.source_text, '资料与依据')):
            reader.setReadOnly(True)
            reader.setAccessibleName('未涉足之树 · ' + title)
            self.reading_tabs.addTab(reader, title)
        layout.addWidget(self.reading_tabs, 1)
        self.choice.currentIndexChanged.connect(self.refresh_reference)
        self.open_item_button.clicked.connect(self.open_selected_item)
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

    def _clear_item(self, message='尚未手动打开归来藏品说明；探索源头一项可单独查看。'):
        self._details_identity = None
        self.icon.clear()
        self.icon.hide()
        replace_text(self.item_text, message, preserve=False)

    def _invalidate(self, message):
        self.packet = None
        self._view_key = None
        self._populate([], None)
        self._clear_item(message)
        self.open_item_button.setEnabled(False)
        self.open_item_button.hide()
        for reader in (self.result_text, self.source_text):
            replace_text(reader, message, preserve=False)

    def set_reference(self, event_id, *, scope_key=None):
        scope = (event_id, deepcopy(scope_key))
        if scope != (self.event_id, self.scope_key):
            self._invalidate('尚未选择要查阅的资料；请手动选择。')
            self.reading_tabs.setCurrentIndex(0)
        self.event_id, self.scope_key = scope
        self.refresh_reference()

    def _checked_choice(self, row):
        reference = results.choice_reference(self.event_id, row['scene_key'], row['choice_key'])
        if (not reference or reference.get('status') != 'documented_reference'
                or reference.get('source_valid') is not True):
            return None
        if any(type(reference.get(key)) is not str or reference[key] != row[key] for key in IDENTITY_FIELDS):
            return None
        return reference

    def _details(self, reference):
        details = results.item_details(self.event_id, reference['scene_key'], reference['choice_key'])
        item = reference['documented_return_item']
        if (not details or details.get('status') != 'documented_reference'
                or details.get('source_valid') is not True or item is None):
            return None
        expected = (self.event_id, reference['scene_key'], reference['choice_key'])
        if tuple(details.get(key) for key in ('event_id', 'scene_key', 'choice_key')) != expected:
            return None
        if any(type(details.get(key)) is not dict for key in ('reference', 'item', 'icon_reference')):
            return None
        if any(details.get('reference', {}).get(key) != reference[key] for key in IDENTITY_FIELDS):
            return None
        if (details.get('item', {}).get('id') != item['item_id']
                or details.get('icon_reference', {}).get('item_id') != item['item_id']):
            return None
        return details

    def _render_item(self, details, *, preserve):
        pixmap = QPixmap(str(results.ROOT / details['icon_reference']['file']))
        self.icon.clear()
        if pixmap.isNull():
            self.icon.setText('图标暂时无法显示；物品说明见下方。')
        else:
            self.icon.setPixmap(pixmap.scaledToWidth(104, Qt.TransformationMode.SmoothTransformation))
        self.icon.show()
        replace_text(self.item_text, item_text(details), preserve=preserve)
        replace_text(self.source_text, json.dumps(details, ensure_ascii=False, indent=2), preserve=preserve)

    def refresh_reference(self, *_):
        selected = self.choice.currentData()
        try:
            packet = results.event_reference(self.event_id)
        except (OSError, ValueError, KeyError, TypeError):
            packet = None
        if (not packet or packet.get('status') != 'documented_reference'
                or packet.get('source_valid') is not True):
            self._invalidate('派出与归来资料未能核对；旧选择、结果与图片已清除，请稍后重新选择。'
                if self.event_id == EVENT else '当前没有查阅未涉足之树；请选择相应事件后打开。')
            return
        self.packet = packet
        self._populate(packet['rows'], selected)
        row = next((row for row in packet['rows'] if row['reference_id'] == self.choice.currentData()), None)
        try:
            reference = self._checked_choice(row) if row else None
        except (OSError, ValueError, KeyError, TypeError):
            reference = None
        if row is not None and reference is None:
            self._invalidate('所选完整选项未能重新核对；旧选择、结果与图片已清除。')
            return
        key = (self.event_id, self.scope_key, reference['scene_key'], reference['choice_key'],
               reference['reference_id']) if reference else None
        same = key is not None and key == self._view_key
        has_item = bool(reference and reference['documented_return_item'] is not None)
        self.open_item_button.setVisible(has_item)
        self.open_item_button.setEnabled(has_item)
        replace_text(self.result_text, choice_text(reference) if reference else
                     '请手动选择要查阅的选项；这里只阅读资料，不会在游戏中作出选择。', preserve=same)
        if same and self._details_identity == key:
            try:
                details = self._details(reference)
            except (OSError, ValueError, KeyError, TypeError):
                details = None
            if details is None:
                self._invalidate('归来藏品详情未能重新核对；旧选择、结果与图片已清除。')
                return
            self._render_item(details, preserve=True)
        else:
            self._clear_item()
            replace_text(self.source_text, json.dumps({'source': packet['source'],
                'source_reference': packet['source_reference'], 'selected_reference': reference,
                'return_explanatory_reference': packet['return_explanatory_reference'],
                'unknowns': packet['unknowns'], 'notice': NOTICE}, ensure_ascii=False, indent=2), preserve=same)
        self._view_key = key

    def open_selected_item(self):
        selected = self.choice.currentData()
        row = next((row for row in (self.packet or {}).get('rows', []) if row['reference_id'] == selected), None)
        if type(selected) is not str or row is None:
            self._invalidate('所选藏品未能对应完整选项；旧结果与图片已清除，请重新选择。')
            return
        try:
            reference = self._checked_choice(row)
            if reference is None:
                self._invalidate('所选完整选项未能重新核对；旧选择、结果与图片已清除。')
                return
            if reference['documented_return_item'] is None:
                return
            details = self._details(reference)
        except (OSError, ValueError, KeyError, TypeError):
            details = None
        if details is None:
            self._invalidate('归来藏品资料未能重新核对；旧选择、结果与图片已清除。')
            return
        self.refresh_reference()
        if self.choice.currentData() != selected:
            return
        key = (self.event_id, self.scope_key, reference['scene_key'], reference['choice_key'], selected)
        self._render_item(details, preserve=self._details_identity == key)
        self._details_identity = key
        self.reading_tabs.setCurrentWidget(self.item_text)
