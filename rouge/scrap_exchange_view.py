"""Read-only exchange scenarios with complete finite candidates and capability gates."""
from copy import deepcopy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QSpinBox, QTreeWidget, QTreeWidgetItem, QVBoxLayout)
from . import scrap_exchange_planning as planning, duel_reward_planning as parts
from .ui_state import replace_text


class ScrapExchangePanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('失与得 · 零件兑换候选与资格')
        self.setModal(False)
        self.resize(970, 760)
        self.context = {}
        self.result = None
        self.detail_key = None
        layout = QVBoxLayout(self)
        notice = QLabel('声明准备提供的零件，对照完整文档候选及声带、手掌条件；实际随机池与库存变化未知。')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        row = QHBoxLayout()
        self.offered = QComboBox()
        self.offered.setAccessibleName('准备提供的固定零件')
        self.offered.addItem('选择准备提供的零件', None)
        for key, item in parts.reference_data()['items'].items():
            self.offered.addItem(item['item']['name'] + ' · ' + item['kind_name'] +
                ' · ' + parts.GRADE_NAMES[item['documented_grade']], key)
        row.addWidget(self.offered, 1)
        row.addWidget(QLabel('声明件数'))
        self.quantity = QSpinBox()
        self.quantity.setRange(-1, 100000)
        self.quantity.setValue(-1)
        self.quantity.setSpecialValueText('未知')
        row.addWidget(self.quantity)
        layout.addLayout(row)
        row = QHBoxLayout()
        self.vocal_cords = self.declaration('声带')
        self.palm = self.declaration('手掌')
        row.addWidget(self.vocal_cords)
        row.addWidget(self.palm)
        self.exchange_index = QComboBox()
        self.exchange_index.addItem('第1次交换', 1)
        self.exchange_index.addItem('第2次交换', 2)
        row.addWidget(self.exchange_index)
        self.first_type = QComboBox()
        self.first_type.setAccessibleName('首次交换收藏品或零件类型')
        for label, value in [('首次类型未知', None), ('首次交换零件', 'SCRAP'), ('首次交换收藏品', 'RELIC')]:
            self.first_type.addItem(label, value)
        row.addWidget(self.first_type)
        layout.addLayout(row)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.search = QLineEdit()
        self.search.setPlaceholderText('检索可得零件或文档排除项；完整覆盖计数保留')
        layout.addWidget(self.search)
        body = QHBoxLayout()
        self.items = QTreeWidget()
        self.items.setHeaderHidden(True)
        body.addWidget(self.items, 1)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        body.addWidget(self.detail, 2)
        layout.addLayout(body, 1)
        self.technical = QCheckBox('显示原ID与来源字段')
        layout.addWidget(self.technical)
        for widget in (self.offered, self.vocal_cords, self.palm, self.exchange_index, self.first_type):
            widget.currentIndexChanged.connect(self.refresh)
        self.quantity.valueChanged.connect(self.refresh)
        self.search.textChanged.connect(self.populate)
        self.items.currentItemChanged.connect(self.render)
        self.technical.toggled.connect(self.render)
        self.refresh()

    @staticmethod
    def declaration(label):
        combo = QComboBox()
        combo.setAccessibleName(label + '账户能力解锁声明')
        for text, value in [(label + '未声明', None), (label + '已解锁（声明）', True), (label + '未解锁（声明）', False)]:
            combo.addItem(text, value)
        return combo

    def set_reference(self, offered_item_id=None, context=None):
        if offered_item_id is not None:
            planning.exchange_candidates(offered_item_id, context)
        self.context = deepcopy(context or {})
        self.offered.blockSignals(True)
        self.offered.setCurrentIndex(self.offered.findData(offered_item_id))
        self.offered.blockSignals(False)
        self.refresh()

    def set_context(self, context=None):
        self.context = deepcopy(context or {})
        self.refresh()

    def selected_id(self):
        selected = self.items.currentItem()
        return selected.data(0, Qt.ItemDataRole.UserRole) if selected else None

    def refresh(self, *_):
        second = self.exchange_index.currentData() == 2
        self.palm.setEnabled(second)
        self.first_type.setEnabled(second)
        identity = self.offered.currentData()
        try:
            self.result = planning.exchange_candidates(identity, self.context,
                exchange_index=self.exchange_index.currentData(), vocal_cords_unlocked=self.vocal_cords.currentData(),
                palm_unlocked=self.palm.currentData(), first_exchange_item_type=self.first_type.currentData(),
                owned_quantity=None if self.quantity.value() < 0 else self.quantity.value()) if identity else None
            text = ('固定30项文档候选比较；候选' + str(len(self.result['documented_candidates'])) +
                '项。已列条件：' + parts.QUALIFICATIONS[self.result['documented_condition_status']] +
                '；实际消耗、陈列与领取未知。') if self.result else '选择准备提供的零件后，查看文档候选与能力门。'
            self.summary.setText(text)
            self.populate()
            if not self.result:
                replace_text(self.detail, text, preserve=False)
        except (ValueError, TypeError, KeyError) as error:
            self.result = None
            self.items.clear()
            self.summary.setText(str(error))
            replace_text(self.detail, str(error), preserve=False)

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
        rows = (self.result or {}).get('rows', [])
        rows = sorted(rows, key=lambda r: (not r['documented_pool_membership'], r['documented_grade']))
        for row in rows:
            if needle and needle not in (row['name'] + ' ' + (row['item'].get('usage') or '')).casefold():
                continue
            label = planning.MEMBERSHIP[row['membership_status']]
            if label not in groups:
                groups[label] = QTreeWidgetItem([label])
                self.items.addTopLevelItem(groups[label])
            text = row['name'] + ' · ' + parts.GRADE_NAMES[row['documented_grade']]
            if row['same_as_offered_item']:
                text += ' · 与提供物相同'
            item = QTreeWidgetItem(groups[label], [text])
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
        key = (self.offered.currentData(), self.selected_id())
        if self.result:
            text = planning.exchange_text(self.result, self.selected_id(), self.technical.isChecked())
            replace_text(self.detail, text, preserve=self.detail_key == key)
        self.detail_key = key
