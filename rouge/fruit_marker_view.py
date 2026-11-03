"""Independent real Qt marker declaration workflow, with no run-state access."""
from copy import deepcopy
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout)
from . import fruit_marker_planning as planning
from .ui_state import replace_text


class FruitMarkerPanel(QDialog):
    nodePreviewRequested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('藏果地 · 声明标记、密道触发与保留')
        self.setModal(False); self.resize(1000, 780)
        self.events = []; self.result = None
        layout = QVBoxLayout(self)
        notice = QLabel('这里只比较明确声明的标记和探索步骤。路线进入、另一端关系、覆盖与完成均须独立声明；不操作游戏、不记录本局、不把移动当作实收奖励。')
        notice.setWordWrap(True); layout.addWidget(notice)
        row = QHBoxLayout()
        self.map_id = QLineEdit('声明地图'); self.node_id = QLineEdit('声明标记节点')
        self.node_type = QComboBox()
        for value in planning.NODE_TYPES: self.node_type.addItem(value, value)
        self.initial_marker = QComboBox()
        for value in ('unknown', 'none', 'fruit', 'civilization'):
            self.initial_marker.addItem(planning.MARKERS[value], value)
        for label, widget in [('地图身份', self.map_id), ('标记节点身份', self.node_id),
                              ('节点类型', self.node_type), ('初始标记', self.initial_marker)]:
            row.addWidget(QLabel(label)); row.addWidget(widget)
        layout.addLayout(row)
        row = QHBoxLayout()
        self.paired_id = QLineEdit(); self.paired_id.setPlaceholderText('独立声明的另一端节点身份')
        self.pair_label = QLabel('密道另一端')
        row.addWidget(self.pair_label); row.addWidget(self.paired_id)
        self.owned = self.tri('迷藏持有'); self.new_region = self.tri('进入新区域')
        row.addWidget(self.owned); row.addWidget(self.new_region); layout.addLayout(row)
        row = QHBoxLayout()
        self.performed = self.tri('本步骤完成')
        self.covered = self.tri('覆盖文明之烬')
        self.place_button = QPushButton('添加独立放置声明')
        row.addWidget(self.performed); row.addWidget(self.covered); row.addWidget(self.place_button)
        layout.addLayout(row)
        row = QHBoxLayout()
        self.mode = QComboBox()
        self.mode.addItem('普通节点探索', 'explore'); self.mode.addItem('曲折密道钻出条件', 'corridor')
        self.entry_id = QLineEdit(); self.entry_id.setPlaceholderText('入口节点身份（另一端）')
        self.exit_id = QLineEdit(); self.exit_id.setPlaceholderText('钻出节点身份（标记端）')
        self.from_other = self.tri('从另一端进入')
        row.addWidget(self.mode); row.addWidget(self.entry_id); row.addWidget(self.exit_id); row.addWidget(self.from_other)
        layout.addLayout(row)
        row = QHBoxLayout()
        self.after_marker = QComboBox()
        self.after_marker.addItem('步骤后标记未另行声明', None)
        for value in ('unknown', 'fruit', 'civilization', 'none'):
            self.after_marker.addItem('步骤后独立声明：' + planning.MARKERS[value], value)
        self.visit_button = QPushButton('添加探索/钻出声明')
        self.clear_button = QPushButton('清空这份局外流程')
        self.node_button = QPushButton('查看此声明节点的地图预览')
        row.addWidget(self.after_marker); row.addWidget(self.visit_button); row.addWidget(self.clear_button)
        row.addWidget(self.node_button); layout.addLayout(row)
        self.summary = QLabel(); self.summary.setWordWrap(True); layout.addWidget(self.summary)
        self.steps = QTreeWidget(); self.steps.setHeaderLabels(['声明步骤', '来源条件', '后续条件状态'])
        self.steps.setAccessibleName('藏果地独立声明步骤和条件结果'); layout.addWidget(self.steps, 1)
        self.detail = QPlainTextEdit(); self.detail.setReadOnly(True); layout.addWidget(self.detail, 3)
        self.technical = QCheckBox('显示原ID、声明输入和完整来源字段'); layout.addWidget(self.technical)
        for combo in (self.node_type, self.initial_marker, self.owned, self.new_region):
            combo.currentIndexChanged.connect(self.refresh)
        for field in (self.node_id, self.map_id, self.paired_id): field.editingFinished.connect(self.refresh)
        self.mode.currentIndexChanged.connect(self.mode_changed)
        self.place_button.clicked.connect(self.add_placement)
        self.visit_button.clicked.connect(self.add_visit)
        self.clear_button.clicked.connect(self.clear_events)
        self.node_button.clicked.connect(self.preview_node)
        self.technical.toggled.connect(self.render)
        self.mode_changed(); self.refresh()

    @staticmethod
    def tri(label):
        combo = QComboBox(); combo.setAccessibleName(label + '独立声明')
        for text, value in [(label + '：未知', None), (label + '：是（声明）', True), (label + '：否（声明）', False)]:
            combo.addItem(text, value)
        return combo

    def node_declaration(self):
        return {'map_id': self.map_id.text(), 'node_id': self.node_id.text(),
                'node_type': self.node_type.currentData(), 'marker': self.initial_marker.currentData(),
                'paired_node_id': self.paired_id.text() or None if self.node_type.currentData() == '曲折密道' else None}

    def set_reference(self, node):
        # Rebinding does not erase or silently retarget a caller's prior steps.
        planning.declared_marker_flow(node)
        for widget, value in ((self.map_id, node['map_id']), (self.node_id, node['node_id']),
                              (self.paired_id, node['paired_node_id'] or '')):
            widget.setText(value)
        for widget, value in ((self.node_type, node['node_type']), (self.initial_marker, node['marker'])):
            widget.blockSignals(True); widget.setCurrentIndex(widget.findData(value)); widget.blockSignals(False)
        self.refresh()

    def set_events(self, events):
        planning.declared_marker_flow(self.node_declaration(), events,
            relic_owned=self.owned.currentData(), new_region_entered=self.new_region.currentData())
        self.events = deepcopy(events); self.refresh()

    def set_corridor_route(self, *, entry_node_id=None, exit_node_id=None, from_other_end=None):
        if from_other_end is not None and type(from_other_end) is not bool:
            raise ValueError('另一端声明需要布尔或null。')
        self.mode.setCurrentIndex(self.mode.findData('corridor'))
        self.entry_id.setText(entry_node_id or ''); self.exit_id.setText(exit_node_id or '')
        self.from_other.setCurrentIndex(self.from_other.findData(from_other_end))

    def mode_changed(self, *_):
        corridor = self.mode.currentData() == 'corridor'
        for widget in (self.entry_id, self.exit_id, self.from_other): widget.setVisible(corridor)

    def append_event(self, event):
        proposed = [*self.events, event]
        try:
            planning.declared_marker_flow(self.node_declaration(), proposed,
                relic_owned=self.owned.currentData(), new_region_entered=self.new_region.currentData())
        except ValueError as error:
            self.summary.setText('此步骤未加入：' + str(error)); return
        self.events = proposed; self.refresh()

    def add_placement(self):
        self.append_event({'kind': 'place', 'node_id': self.node_id.text(),
            'performed': self.performed.currentData(), 'covers_civilization': self.covered.currentData()})

    def add_visit(self):
        corridor = self.mode.currentData() == 'corridor'
        self.append_event({'kind': 'visit', 'node_id': self.node_id.text(), 'mode': self.mode.currentData(),
            'performed': self.performed.currentData(), 'entry_node_id': self.entry_id.text() or None if corridor else None,
            'exit_node_id': self.exit_id.text() or None if corridor else None,
            'from_other_end': self.from_other.currentData() if corridor else None,
            'marker_after': self.after_marker.currentData()})

    def clear_events(self):
        self.events = []; self.refresh()

    def refresh(self, *_):
        pair = self.node_type.currentData() == '曲折密道'
        self.pair_label.setVisible(pair); self.paired_id.setVisible(pair)
        selected = self.steps.currentItem()
        prior = selected.data(0, Qt.ItemDataRole.UserRole) if selected else None
        try:
            self.result = planning.declared_marker_flow(self.node_declaration(), self.events,
                relic_owned=self.owned.currentData(), new_region_entered=self.new_region.currentData())
        except ValueError as error:
            self.result = None; self.steps.clear(); self.summary.setText(str(error))
            replace_text(self.detail, str(error), preserve=False); self.node_button.setEnabled(False); return
        self.steps.clear()
        for row in self.result['rows']:
            item = QTreeWidgetItem([str(row['index']) + (' · 放置' if row['kind'] == 'place' else ' · 探索/钻出'),
                planning.STATUSES[row['condition_status']], planning.MARKERS[row['admitted_marker_after']]])
            item.setData(0, Qt.ItemDataRole.UserRole, row['index']); self.steps.addTopLevelItem(item)
            if row['index'] == prior: self.steps.setCurrentItem(item)
        self.steps.resizeColumnToContents(0); self.steps.resizeColumnToContents(1)
        self.summary.setText(f"{len(self.events)}个局外声明步骤；三件具名文档候选；生成条件：" +
            planning.STATUSES[self.result['generation_condition_status']] + '。实收、重复上限与最终实际标记均未知。')
        self.node_button.setEnabled(True); self.render()

    def render(self, *_):
        if self.result is not None:
            replace_text(self.detail, planning.format_marker_flow(self.result, technical=self.technical.isChecked()))

    def preview_node(self):
        if self.result is not None:
            self.nodePreviewRequested.emit({'map_id': self.result['node']['map_id'], 'node_id': self.result['node']['node_id'],
                'source': 'explicit_offline_marker_declaration', 'actual_map_binding_verified': False})
