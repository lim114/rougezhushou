"""Read-only seed source, cross-exploration gifts and exact original-variant browser."""
from copy import deepcopy
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QPushButton, QSpinBox, QTreeWidget, QTreeWidgetItem, QVBoxLayout)
from . import seed_cultivation_planning as planning, duel_reward_planning as parts
from .ui_state import replace_text


class SeedCultivationPanel(QDialog):
    originalChoiceSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('秘境行商 · 种子培育与下次探索奖励')
        self.setModal(False)
        self.resize(990, 790)
        self.context = {}
        self.result = None
        self.detail_key = None
        self.pending_item_id = None
        layout = QVBoxLayout(self)
        notice = QLabel('零件属于本局资料，黄色襁褓留待下次常规探索；同名原变体和蓝色支援分别保留，实际领取未知。')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        row = QHBoxLayout()
        row.addWidget(QLabel('种子件数声明'))
        self.seed_quantity = QSpinBox()
        self.seed_quantity.setRange(-1, 100000)
        self.seed_quantity.setSpecialValueText('未知')
        self.seed_quantity.setValue(-1)
        row.addWidget(self.seed_quantity)
        self.completed = self.declaration('培育完成', '声明培育完成', '声明未完成')
        row.addWidget(self.completed)
        self.current_normal = self.declaration('本局模式', '本局常规探索（声明）', '本局其它探索（声明）')
        row.addWidget(self.current_normal)
        layout.addLayout(row)
        row = QHBoxLayout()
        self.next_normal = self.declaration('下次模式', '下次常规探索（声明）', '下次其它探索（声明）')
        row.addWidget(self.next_normal)
        row.addWidget(QLabel('本局通过区域数（非最高层）'))
        self.regions = QSpinBox()
        self.regions.setRange(-1, 100000)
        self.regions.setSpecialValueText('未知')
        self.regions.setValue(-1)
        row.addWidget(self.regions)
        layout.addLayout(row)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.search = QLineEdit()
        self.search.setPlaceholderText('检索零件、黄色襁褓或后续支援名；同名原ID保持各自引用')
        layout.addWidget(self.search)
        body = QHBoxLayout()
        self.items = QTreeWidget()
        self.items.setHeaderHidden(True)
        self.items.setAccessibleName('本局零件与下次黄色襁褓的独立来源候选')
        body.addWidget(self.items, 1)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        body.addWidget(self.detail, 2)
        layout.addLayout(body, 1)
        self.technical = QCheckBox('显示原ID与明确字段来源')
        layout.addWidget(self.technical)
        self.blue_button = QPushButton('查看该原变体的后续支援原文')
        layout.addWidget(self.blue_button)
        for widget in (self.completed, self.current_normal, self.next_normal):
            widget.currentIndexChanged.connect(self.refresh)
        self.seed_quantity.valueChanged.connect(self.refresh)
        self.regions.valueChanged.connect(self.refresh)
        self.search.textChanged.connect(self.populate)
        self.items.currentItemChanged.connect(self.render)
        self.technical.toggled.connect(self.render)
        self.blue_button.clicked.connect(self.select_blue_reference)
        self.refresh()

    @staticmethod
    def declaration(label, yes, no):
        combo = QComboBox()
        combo.setAccessibleName(label + '声明')
        for text, value in [(label + '未知', None), (yes, True), (no, False)]:
            combo.addItem(text, value)
        return combo

    def set_reference(self, item_id=None, context=None):
        result = planning.seed_cultivation_reference(context)
        if item_id is not None and item_id not in {r['item_id'] for r in result['rows']}:
            raise ValueError('原引用不属于种子资料；不能把蓝色收藏品当立即奖励。')
        self.context = deepcopy(context or {})
        self.pending_item_id = item_id
        self.refresh()

    def set_context(self, context=None):
        self.context = deepcopy(context or {})
        self.refresh()

    def selected_id(self):
        selected = self.items.currentItem()
        return selected.data(0, Qt.ItemDataRole.UserRole) if selected else None

    def refresh(self, *_):
        try:
            self.result = planning.seed_cultivation_reference(self.context,
                seed_quantity=None if self.seed_quantity.value() < 0 else self.seed_quantity.value(),
                cultivation_completed=self.completed.currentData(),
                current_normal_exploration=self.current_normal.currentData(),
                next_normal_exploration=self.next_normal.currentData(),
                completed_regions=None if self.regions.value() < 0 else self.regions.value())
            self.summary.setText('完整43原引用；文档候选24项、原变体/特殊来源待证11项、类别不符8项。'
                '入口/完成：' + parts.QUALIFICATIONS[self.result['documented_condition_status']] +
                '；黄色襁褓模式：' + parts.QUALIFICATIONS[self.result['yellow_cultivation_condition_status']] + '。实际领取未知。')
            self.populate()
        except (ValueError, TypeError, KeyError) as error:
            self.result = None
            self.items.clear()
            self.summary.setText(str(error))
            replace_text(self.detail, str(error), preserve=False)
            self.blue_button.hide()

    def populate(self, *_):
        previous = self.pending_item_id or self.selected_id()
        self.pending_item_id = None
        had_groups = self.items.topLevelItemCount() > 0
        expanded = {self.items.topLevelItem(i).text(0) for i in range(self.items.topLevelItemCount())
            if self.items.topLevelItem(i).isExpanded()}
        self.items.blockSignals(True)
        self.items.clear()
        groups = {}
        aliases = {}
        selected = None
        needle = self.search.text().strip().casefold()
        rows = sorted((self.result or {}).get('rows', []), key=lambda r: (
            r['membership_status'] in ('documented_class_mismatch', 'original_yellow_group_variant', 'special_acquisition_unbound'),
            r['kind'] != 'current_scrap'))
        for row in rows:
            pointer = row.get('direct_blue_support_reference')
            name = row['name']
            if pointer:
                name += ' · 后续原支援参考：' + pointer['choice']['title']
            elif row['membership_status'] == 'original_yellow_group_variant':
                group = row['legacy_group_id']
                aliases[group] = aliases.get(group, 0) + 1
                name += ' · 原组变体参考' + str(aliases[group])
            if needle and needle not in (name + ' ' + (row['item'].get('usage') or '')).casefold():
                continue
            prefix = '本局零件 · ' if row['kind'] == 'current_scrap' else '下次黄色襁褓 · '
            label = prefix + planning.MEMBERSHIP[row['membership_status']]
            if label not in groups:
                groups[label] = QTreeWidgetItem([label])
                self.items.addTopLevelItem(groups[label])
            item = QTreeWidgetItem(groups[label], [name])
            item.setData(0, Qt.ItemDataRole.UserRole, row['item_id'])
            if row['item_id'] == previous:
                selected = item
        if selected is None and self.items.topLevelItemCount():
            selected = self.items.topLevelItem(0).child(0)
        self.items.setCurrentItem(selected)
        for label, group in groups.items():
            group.setExpanded(label in expanded or not had_groups)
        self.items.blockSignals(False)
        self.render()

    def render(self, *_):
        identity = self.selected_id()
        if self.result:
            text = planning.cultivation_text(self.result, identity, self.technical.isChecked())
            replace_text(self.detail, text, preserve=self.detail_key == identity)
        self.detail_key = identity
        selected = next((r for r in (self.result or {}).get('rows', []) if r['item_id'] == identity), None)
        self.blue_button.setVisible(bool(selected and selected.get('direct_blue_support_reference')))

    def select_blue_reference(self):
        identity = self.selected_id()
        selected = next((r for r in (self.result or {}).get('rows', []) if r['item_id'] == identity), None)
        pointer = (selected or {}).get('direct_blue_support_reference')
        if pointer:
            self.originalChoiceSelected.emit(pointer['choice']['id'])
