"""Read-only named reward browser for declared left/middle/right opponents."""
from copy import deepcopy
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QCheckBox, QTreeWidget, QTreeWidgetItem, QVBoxLayout)
from . import duel_reward_planning as planning
from .ui_state import replace_text


class DuelRewardPanel(QDialog):
    stageSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('狭路相逢 · 档次奖励与具名候选')
        self.setModal(False)
        self.resize(940, 740)
        self.context = {}
        self.result = None
        self.detail_key = None
        layout = QVBoxLayout(self)
        notice = QLabel('对照左、中、右对手的条件奖励和固定目录；实际随机池、选择与领取未知。')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        row = QHBoxLayout()
        self.stage = QComboBox()
        self.stage.setAccessibleName('狭路相逢固定关卡资料')
        self.stage.addItem('两份固定关卡参考', None)
        for key, stage in planning.reference_data()['stages'].items():
            self.stage.addItem(stage['original']['name'], key)
        row.addWidget(self.stage)
        self.tier = QComboBox()
        self.tier.setAccessibleName('文档左中右奖励档次')
        for key, tier in planning.reference_data()['tiers'].items():
            self.tier.addItem(tier['label'], key)
        row.addWidget(self.tier)
        self.success = QComboBox()
        self.success.setAccessibleName('限定时间内获胜的声明情形')
        for label, value in [('限时获胜未声明', None), ('声明限时内获胜', True), ('声明未限时获胜', False)]:
            self.success.addItem(label, value)
        row.addWidget(self.success)
        layout.addLayout(row)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.search = QLineEdit()
        self.search.setPlaceholderText('检索具名物品或用途；保留完整来源覆盖计数')
        layout.addWidget(self.search)
        body = QHBoxLayout()
        self.items = QTreeWidget()
        self.items.setHeaderHidden(True)
        self.items.setAccessibleName('条件相符、特殊来源待证与档次不符的具名目录')
        body.addWidget(self.items, 1)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        body.addWidget(self.detail, 2)
        layout.addLayout(body, 1)
        self.technical = QCheckBox('显示来源ID与字段')
        layout.addWidget(self.technical)
        self.battle_button = QPushButton('查看所选固定战斗地图')
        layout.addWidget(self.battle_button)
        for widget in (self.stage, self.tier, self.success):
            widget.currentIndexChanged.connect(self.refresh)
        self.search.textChanged.connect(self.populate)
        self.items.currentItemChanged.connect(self.render)
        self.technical.toggled.connect(self.render)
        self.battle_button.clicked.connect(self.select_stage)
        self.refresh()

    def set_reference(self, stage_id=None, context=None):
        # Validate before updating controls, so an unrelated stage is not silently
        # substituted by the combo's two-stage default.
        planning.duel_rewards(stage_id, self.tier.currentData(), context,
            self.success.currentData())
        self.context = deepcopy(context or {})
        self.stage.blockSignals(True)
        self.stage.setCurrentIndex(self.stage.findData(stage_id))
        self.stage.blockSignals(False)
        self.refresh()

    def set_context(self, context=None):
        self.context = deepcopy(context or {})
        self.refresh()

    def selected_id(self):
        selected = self.items.currentItem()
        return selected.data(0, Qt.ItemDataRole.UserRole) if selected else None

    def refresh(self, *_):
        try:
            self.result = planning.duel_rewards(self.stage.currentData(), self.tier.currentData(),
                self.context, self.success.currentData())
            rule = self.result['tier_rule']
            self.summary.setText(rule['source_text'] + '；已列条件：' +
                planning.QUALIFICATIONS[self.result['documented_condition_status']] +
                '。实际池成员与领取未知。')
            self.populate()
        except (ValueError, TypeError, KeyError) as error:
            self.result = None
            self.items.clear()
            self.summary.setText(str(error))
            replace_text(self.detail, str(error), preserve=False)
        self.battle_button.setEnabled(bool(self.result and self.stage.currentData()))

    def populate(self, *_):
        previous = self.selected_id()
        had_groups = self.items.topLevelItemCount() > 0
        expanded = {self.items.topLevelItem(i).text(0) for i in range(self.items.topLevelItemCount())
            if self.items.topLevelItem(i).isExpanded()}
        self.items.blockSignals(True)
        self.items.clear()
        groups = {}
        selected = None
        needle = self.search.text().strip().casefold()
        for row in (self.result or {}).get('rows', []):
            searchable = row['name'] + ' ' + (row['item'].get('usage') or '')
            if needle and needle not in searchable.casefold():
                continue
            label = planning.MEMBERSHIP_NAMES[row['membership_status']]
            if label not in groups:
                groups[label] = QTreeWidgetItem([label])
                self.items.addTopLevelItem(groups[label])
                groups[label].setExpanded(label in expanded or not had_groups)
            name = row['name'] + ' · ' + row['kind_name']
            if row['documented_grade'] is not None:
                name += ' · ' + planning.GRADE_NAMES[row['documented_grade']]
            item = QTreeWidgetItem(groups[label], [name])
            item.setData(0, Qt.ItemDataRole.UserRole, row['item_id'])
            if row['item_id'] == previous:
                selected = item
        if selected is None and self.items.topLevelItemCount():
            selected = self.items.topLevelItem(0).child(0)
        self.items.setCurrentItem(selected)
        # Qt may expand a selected descendant's parent while restoring it.
        # Reinstate the user's collapsed groups after selection restoration.
        for label, group in groups.items():
            group.setExpanded(label in expanded or not had_groups)
        self.items.blockSignals(False)
        self.render()

    def render(self, *_):
        identity = self.selected_id()
        key = (self.stage.currentData(), self.tier.currentData(), identity)
        if self.result:
            text = planning.reward_text(self.result, identity, self.technical.isChecked())
            replace_text(self.detail, text, preserve=self.detail_key == key)
        self.detail_key = key

    def select_stage(self):
        identity = self.stage.currentData()
        if self.result and identity in planning.reference_data()['stages']:
            self.stageSelected.emit(identity)
