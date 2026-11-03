"""Read-only movement-part wishlist and declared source-opportunity review."""
from copy import deepcopy
import json
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QPlainTextEdit, QPushButton, QSpinBox, QTreeWidget, QTreeWidgetItem, QVBoxLayout)
from . import movement_source_planning as planning
from .ui_state import replace_text


class MovementSourcePanel(QDialog):
    mapNodeSelected = Signal(str, object)
    catalogEventSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('加工品获取清单 · 来源机会与条件')
        self.setModal(False)
        self.resize(1140, 800)
        self.context = {}
        self.graph = None
        self.epoch = None
        self.result = None
        self.detail_key = None
        self._loading = False
        self._declaration_scopes = {}
        layout = QVBoxLayout(self)
        notice = QLabel('选择想补齐的加工品，逐一审查两商店、种子培育与离层/首领来源。来源标志来自PRTS原卡片；当前陈列、实际池和入口可达状态需另行确认。')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        body = QHBoxLayout()
        self.targets = QTreeWidget()
        self.targets.setHeaderLabel('获取目标（持有后仍保留）')
        self.targets.setAccessibleName('12项加工品获取目标清单')
        self.targets.setMaximumWidth(230)
        for key, row in planning.reference_data()['items'].items():
            item = QTreeWidgetItem([row['item']['name']])
            item.setData(0, Qt.ItemDataRole.UserRole, key)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Unchecked)
            self.targets.addTopLevelItem(item)
        body.addWidget(self.targets, 1)
        self.sources = QTreeWidget()
        self.sources.setHeaderLabel('每个目标的来源机会')
        self.sources.setAccessibleName('声明图来源机会与历史参考')
        body.addWidget(self.sources, 2)
        right = QVBoxLayout()
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        right.addWidget(self.detail, 1)
        form = QFormLayout()
        self.access = self.boolean_combo('入口可达')
        self.completion = self.boolean_combo('对应完成条件')
        self.stock = self.boolean_combo('此目标当前陈列')
        self.seed = self.boolean_combo('持有种子')
        self.unmodified = QCheckBox('明确声明采用无修正文档售价')
        self.price = self.number_input('此目标独立报价')
        self.gold = self.number_input('此入口金币声明（未知时沿用上下文）')
        form.addRow('入口可达声明', self.access)
        form.addRow('完成条件声明', self.completion)
        form.addRow('当前陈列声明', self.stock)
        form.addRow('种子持有声明', self.seed)
        form.addRow(self.unmodified)
        form.addRow('此目标独立报价', self.price)
        form.addRow('独立金币声明', self.gold)
        right.addLayout(form)
        label = QLabel('这些情形声明仅保存在本面板的当前声明图范围，不购买、不培育，也不写本局库存。未读到陈列不等于没有。')
        label.setWordWrap(True)
        right.addWidget(label)
        links = QHBoxLayout()
        self.map_button = QPushButton('查看声明图位置')
        self.catalogue = QComboBox()
        self.catalogue.setAccessibleName('分别保留的独立事件目录组')
        self.catalogue_button = QPushButton('查看独立事件目录')
        links.addWidget(self.map_button)
        links.addWidget(self.catalogue, 1)
        links.addWidget(self.catalogue_button)
        right.addLayout(links)
        self.technical = QCheckBox('显示原ID与来源字段')
        right.addWidget(self.technical)
        body.addLayout(right, 4)
        layout.addLayout(body, 1)
        self.targets.itemChanged.connect(self.refresh)
        self.sources.currentItemChanged.connect(self.render)
        self.technical.toggled.connect(self.render)
        for widget in (self.access, self.completion, self.stock, self.seed):
            widget.currentIndexChanged.connect(self.edit_declaration)
        for widget in (self.price, self.gold):
            widget.valueChanged.connect(self.edit_declaration)
        self.unmodified.toggled.connect(self.edit_declaration)
        self.map_button.clicked.connect(self.preview_position)
        self.catalogue_button.clicked.connect(self.open_catalogue)
        self.refresh()

    @staticmethod
    def boolean_combo(label):
        combo = QComboBox()
        combo.setAccessibleName(label + '三态声明')
        for text, value in [('未知 / 未声明', None), ('是（声明）', True), ('否（声明）', False)]:
            combo.addItem(text, value)
        return combo

    @staticmethod
    def number_input(label):
        box = QSpinBox()
        box.setRange(-1, 100000)
        box.setValue(-1)
        box.setSpecialValueText('未知')
        box.setAccessibleName(label)
        return box

    def target_ids(self):
        return [self.targets.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(self.targets.topLevelItemCount())
            if self.targets.topLevelItem(i).checkState(0) == Qt.CheckState.Checked]

    def _scope(self):
        nodes = tuple(sorted((node.get('id'), node.get('row'), node.get('col'), node.get('observed_type'),
            node.get('base_node_type'), node.get('node_type_raw')) for node in (self.graph or {}).get('nodes', [])))
        return (self.epoch, (self.graph or {}).get('zone_id'), (self.graph or {}).get('template_id'), self.graph is None, nodes)

    def _declarations(self):
        remembered = self._declaration_scopes.setdefault(self._scope(), {})
        allowed = {n['id'] for n in self.graph['nodes']} if self.graph is not None else {'directory:' + k for k in planning.reference_data()['channels']}
        return {key: deepcopy(value) for key, value in remembered.items() if key in allowed}

    def set_reference(self, target_item_ids=None, graph=None, context=None, *, epoch=None):
        if target_item_ids is not None:
            planning.source_review(target_item_ids, graph, context, epoch=epoch)
            self.targets.blockSignals(True)
            for i in range(self.targets.topLevelItemCount()):
                item = self.targets.topLevelItem(i)
                item.setCheckState(0, Qt.CheckState.Checked if item.data(0, Qt.ItemDataRole.UserRole) in target_item_ids else Qt.CheckState.Unchecked)
            self.targets.blockSignals(False)
        self.graph = deepcopy(graph)
        self.context = deepcopy(context or {})
        self.epoch = epoch
        self.refresh()

    def set_map_context(self, graph=None, context=None, *, epoch=None):
        self.graph = deepcopy(graph)
        if context is not None:
            self.context = deepcopy(context)
        self.epoch = epoch
        self.refresh()

    def set_context(self, context=None):
        self.context = deepcopy(context or {})
        self.refresh()

    def selected_key(self):
        item = self.sources.currentItem()
        return item.data(0, Qt.ItemDataRole.UserRole) if item else None

    def selected_row(self):
        key = self.selected_key()
        return next((r for r in (self.result or {}).get('rows', []) if json.dumps(r['review_key'], ensure_ascii=False) == key), None)

    def refresh(self, *_):
        if self._loading:
            return
        try:
            self.result = planning.source_review(self.target_ids(), self.graph, self.context,
                self._declarations(), epoch=self.epoch)
            targets = self.result['targets']
            count = {status: sum(t[status + '_source_rows'] for t in targets) for status in ('matched', 'unknown', 'excluded', 'historical')}
            self.summary.setText(f"固定12项 / 6类渠道；已选{len(targets)}项，条件相符{count['matched']}、待证{count['unknown']}、不符{count['excluded']}、历史参考{count['historical']}。来源不等于实际池，持有数量与获取目标分别保留。")
            self.populate()
        except (ValueError, TypeError, KeyError) as error:
            self.result = None
            self.sources.clear()
            self.summary.setText(str(error))
            replace_text(self.detail, str(error), preserve=False)
            self.load_controls(None)

    def populate(self):
        previous = self.selected_key()
        had_groups = self.sources.topLevelItemCount() > 0
        expanded = {self.sources.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(self.sources.topLevelItemCount()) if self.sources.topLevelItem(i).isExpanded()}
        self.sources.blockSignals(True)
        self.sources.clear()
        groups = {}
        selected = None
        for row in self.result['rows']:
            key = row['item_id']
            if key not in groups:
                target = next(t for t in self.result['targets'] if t['item_id'] == key)
                quantity = target['owned_quantity_declared']
                held = str(quantity) + '件（声明）' if quantity is not None else '持有（声明，件数未知）' if target['owned_presence_declared'] is True else '未持有（声明）' if target['owned_presence_declared'] is False else '持有未知'
                group = QTreeWidgetItem([row['name'] + ' · ' + held])
                group.setData(0, Qt.ItemDataRole.UserRole, key)
                self.sources.addTopLevelItem(group)
                groups[key] = group
            pos = row.get('position')
            location = f" · {pos['row']+1}行{pos['col']+1}列" if pos else ' · 独立目录'
            item = QTreeWidgetItem(groups[key], [row['channel']['label'] + location + ' · ' + planning.STATUS[row['status']]])
            review_key = json.dumps(row['review_key'], ensure_ascii=False)
            item.setData(0, Qt.ItemDataRole.UserRole, review_key)
            if review_key == previous:
                selected = item
        if selected is None and self.sources.topLevelItemCount():
            selected = self.sources.topLevelItem(0).child(0)
        self.sources.setCurrentItem(selected)
        for key, group in groups.items():
            group.setExpanded(key in expanded or not had_groups)
        self.sources.blockSignals(False)
        self.render()

    def load_controls(self, row):
        self._loading = True
        declaration = row['declaration'] if row else {}
        editable = bool(row and not row['historical_reference'])
        shop = bool(row and row['channel']['membership_rule'] == 'shop')
        completion = row['channel']['completion_field'] if row else None
        values = ((self.access, declaration.get('access_declared')), (self.completion, declaration.get(completion)),
            (self.stock, declaration.get('stock_presence', {}).get(row['item_id']) if row else None),
            (self.seed, declaration.get('seed_presence')))
        for widget, value in values:
            widget.setCurrentIndex(widget.findData(value))
        self.unmodified.setChecked(declaration.get('unmodified_price_scenario') is True)
        self.price.setValue(declaration.get('declared_prices', {}).get(row['item_id'], -1) if row else -1)
        self.gold.setValue(declaration.get('gold_declared') if declaration.get('gold_declared') is not None else -1)
        self.access.setEnabled(editable)
        self.completion.setEnabled(editable and completion is not None)
        self.completion.setAccessibleName(('培育完成' if completion == 'cultivation_completed' else '通关成功' if completion == 'victory_declared' else '离层完成') + '三态声明')
        for widget in (self.stock, self.price, self.gold, self.unmodified):
            widget.setEnabled(editable and shop)
        self.seed.setEnabled(editable and row['channel_id'] == 'seed')
        self._loading = False

    def render(self, *_):
        row = self.selected_row()
        key = tuple(row['review_key']) if row else None
        text = planning.source_text(row, self.technical.isChecked()) if row else '选择加工品目标及具体来源，查看条件与出处。'
        replace_text(self.detail, text, preserve=key == self.detail_key)
        self.detail_key = key
        self.load_controls(row)
        previous = self.catalogue.currentData()
        self.catalogue.clear()
        for i, reference in enumerate(row['channel']['catalogue_refs'] if row else []):
            self.catalogue.addItem(reference['title'] + f' · 独立目录{i+1}', reference['event_id'])
        index = self.catalogue.findData(previous)
        if index >= 0:
            self.catalogue.setCurrentIndex(index)
        self.catalogue_button.setEnabled(self.catalogue.count() > 0)
        self.map_button.setEnabled(bool(row and row['position']))

    def edit_declaration(self, *_):
        if self._loading:
            return
        row = self.selected_row()
        if not row or row['historical_reference']:
            return
        declaration = deepcopy(row['declaration'])
        declaration['access_declared'] = self.access.currentData()
        if row['channel']['completion_field']:
            declaration[row['channel']['completion_field']] = self.completion.currentData()
        if row['channel']['membership_rule'] == 'shop':
            declaration.setdefault('stock_presence', {})[row['item_id']] = self.stock.currentData()
            prices = declaration.setdefault('declared_prices', {})
            if self.price.value() >= 0:
                prices[row['item_id']] = self.price.value()
            else:
                prices.pop(row['item_id'], None)
            declaration['gold_declared'] = None if self.gold.value() < 0 else self.gold.value()
            declaration['unmodified_price_scenario'] = self.unmodified.isChecked()
        elif row['channel_id'] == 'seed':
            declaration['seed_presence'] = self.seed.currentData()
        try:
            planning.movement_source(row['item_id'], row['channel_id'], row['context'], declaration)
        except (ValueError, TypeError, KeyError) as error:
            self.summary.setText(str(error))
            replace_text(self.detail, str(error), preserve=False)
            return
        self._declaration_scopes.setdefault(self._scope(), {})[row['source_key']] = declaration
        self.refresh()

    def preview_position(self):
        row = self.selected_row()
        if row and row['position']:
            self.mapNodeSelected.emit(row['node_id'], deepcopy(row['position']))

    def open_catalogue(self):
        identity = self.catalogue.currentData()
        if identity is not None:
            self.catalogEventSelected.emit(identity)
