"""Temporary account-snapshot planning; never changes persistent technology."""
from copy import deepcopy

from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton,
    QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout)

from .technology import technology_labels
from .p2_technology_upgrade import format_technology_upgrade, source_data, technology_upgrade_plan


def _amount(value=None):
    box = QSpinBox(); box.setRange(-1, 9999); box.setSpecialValueText('未知')
    box.setValue(-1 if value is None else value); return box


class TechnologyTargetDialog(QDialog):
    def __init__(self, existing=(), declaration=None, parent=None):
        super().__init__(parent); self.setWindowTitle('科技目标 · 独立接受与扣费情景'); self.resize(590, 340)
        declaration = declaration or {}; layout = QVBoxLayout(self)
        notice = QLabel('这里只声明一个局外目标及接受分支；扣除/返还各自声明，未知不是0。普通购买前置逻辑未闭合。')
        notice.setWordWrap(True); layout.addWidget(notice)
        form = QFormLayout(); layout.addLayout(form)
        self.node = QComboBox(); labels = technology_labels()
        for identity, node in source_data()['common_development_raw']['developments'].items():
            if node['nodeType'] == 'DIFFICULTY' or identity in existing: continue
            self.node.addItem(labels[identity] + f" · 新节点原费用{node['tokenCost']}", identity)
        if declaration.get('node_id'): self.node.setCurrentIndex(self.node.findData(declaration['node_id']))
        form.addRow('所选付费目标', self.node)
        self.acceptance = QComboBox()
        for label, value in [('接受未知', None), ('假设目标被接受', True), ('假设目标未被接受', False)]:
            self.acceptance.addItem(label, value)
        self.acceptance.setCurrentIndex(self.acceptance.findData(declaration.get('accepted'))); form.addRow('明确接受情景', self.acceptance)
        self.charge = _amount(declaration.get('charged_tokens')); self.refund = _amount(declaration.get('refunded_tokens'))
        form.addRow('声明扣除的演化算子', self.charge); form.addRow('声明返还的演化算子', self.refund)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept); self.buttons.rejected.connect(self.reject); layout.addWidget(self.buttons)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(self.node.count() > 0)

    def declaration(self):
        return {'node_id': self.node.currentData(), 'accepted': self.acceptance.currentData(),
                'charged_tokens': None if self.charge.value() < 0 else self.charge.value(),
                'refunded_tokens': None if self.refund.value() < 0 else self.refund.value()}


class TechnologyUpgradePlannerDialog(QDialog):
    def __init__(self, snapshot, parent=None):
        super().__init__(parent); self.snapshot = deepcopy(snapshot); self.steps = []; self.result = None
        self.setWindowTitle('长期科技 · 所选目标预算与生灵资格'); self.resize(1170, 810)
        layout = QVBoxLayout(self)
        notice = QLabel('账户声明快照：' + self.snapshot['profile_name'] + '。这里只规划：三个生灵自动门按任一前置、模式和难度核资格；'
                        '所选目标费用不含未知的普通前置成本。符合资格仍不证明实际激活；不会购买或改写档案。')
        notice.setWordWrap(True); layout.addWidget(notice)
        choices = QHBoxLayout(); choices.addWidget(QLabel('模式声明'))
        self.mode = QComboBox()
        for label, value in [('未知', None), ('常规行动', 'regular'), ('其它模式', 'other')]: self.mode.addItem(label, value)
        choices.addWidget(self.mode); choices.addWidget(QLabel('保密等级声明'))
        self.grade = _amount(); self.grade.setMaximum(15); choices.addWidget(self.grade)
        choices.addWidget(QLabel('演化算子预算声明')); self.budget = _amount(); choices.addWidget(self.budget)
        choices.addStretch(); layout.addLayout(choices)
        self.gates = QTableWidget(3, 8)
        self.gates.setHorizontalHeaderLabels(['自动门', '任一前置', '模式', '难度', '初始资格', '接受情景后资格', '原档案门标记', '实际激活'])
        self.gates.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.gates.setMaximumHeight(150)
        layout.addWidget(self.gates)
        actions = QHBoxLayout()
        self.add_button = QPushButton('添加付费目标情景'); self.add_button.clicked.connect(self.add_target); actions.addWidget(self.add_button)
        self.edit_button = QPushButton('编辑所选'); self.edit_button.clicked.connect(self.edit_target); actions.addWidget(self.edit_button)
        self.remove_button = QPushButton('移除所选'); self.remove_button.clicked.connect(self.remove_target); actions.addWidget(self.remove_button)
        self.calculate_button = QPushButton('核对所选预算与自动门资格'); self.calculate_button.clicked.connect(self.calculate); actions.addWidget(self.calculate_button)
        self.copy_button = QPushButton('复制条件、预算与资格'); self.copy_button.clicked.connect(self.copy_result); actions.addWidget(self.copy_button)
        layout.addLayout(actions)
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(['目标', '新节点原费用', '所选计划费用', '接受情景', '声明扣除', '声明返还', '声明预算余额', '普通购买合法性'])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); layout.addWidget(self.table)
        self.details = QPlainTextEdit(); self.details.setReadOnly(True); layout.addWidget(self.details)
        self.mode.currentIndexChanged.connect(self.invalidate); self.grade.valueChanged.connect(self.invalidate); self.budget.valueChanged.connect(self.invalidate)
        self.calculate()

    def preview(self):
        return {'mode': self.mode.currentData(), 'grade': None if self.grade.value() < 0 else self.grade.value(),
                'budget': None if self.budget.value() < 0 else self.budget.value(), 'steps': deepcopy(self.steps)}

    def invalidate(self, *_args):
        self.result = None; self.copy_button.setEnabled(False); labels = technology_labels()
        self.table.setRowCount(len(self.steps))
        for index, step in enumerate(self.steps):
            self.table.setItem(index, 0, QTableWidgetItem(labels[step['node_id']]))
            for column in range(1, 8): self.table.setItem(index, column, QTableWidgetItem('待核对'))
        for row in range(3):
            for column in range(8): self.gates.setItem(row, column, QTableWidgetItem('待核对'))
        self.details.setPlainText('条件已修改，请核对所选目标费用与自动门资格。')

    def add_target(self):
        editor = TechnologyTargetDialog([step['node_id'] for step in self.steps], parent=self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.steps.append(editor.declaration()); self.invalidate()

    def edit_target(self):
        index = self.table.currentRow()
        if not 0 <= index < len(self.steps): return
        editor = TechnologyTargetDialog([step['node_id'] for n, step in enumerate(self.steps) if n != index], self.steps[index], self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.steps[index] = editor.declaration(); self.invalidate()

    def remove_target(self):
        index = self.table.currentRow()
        if 0 <= index < len(self.steps): self.steps.pop(index); self.invalidate()

    def calculate(self):
        self.invalidate()
        try: result = technology_upgrade_plan(self.snapshot, self.preview())
        except (ValueError, KeyError, TypeError) as error: self.details.setPlainText(str(error)); return
        self.result = result; labels = technology_labels()
        def show(value): return '未知' if value is None else str(value)
        def qualify(value): return '未知' if value is None else '符合' if value else '不符合'
        states = {'unknown': '未知', 'locked': '未解锁（声明）', 'unlocked': '已解锁（声明）'}
        for index, (initial, gate) in enumerate(zip(result['initial_gates'], result['final_gates'])):
            values = [gate['name'], qualify(gate['front_any_qualified']), qualify(gate['mode_qualified']),
                      qualify(gate['grade_qualified']), qualify(initial['eligible_reference']), qualify(gate['eligible_reference']),
                      states[gate['manual_gate_mark']], '未知']
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip('资格使用任一前置声明；自动门手动标记不替代前置。')
                self.gates.setItem(index, column, item)
        for index, row in enumerate(result['rows']):
            values = [labels[row['id']], show(row['nominal_new_node_cost']), show(row['planned_cost_reference']),
                      '未知' if row['accepted_declared'] is None else '假设接受' if row['accepted_declared'] else '假设未接受',
                      show(row['charged_tokens_declared']), show(row['refunded_tokens_declared']),
                      show(row['declared_budget_after']), '未知']
            for column, value in enumerate(values): self.table.setItem(index, column, QTableWidgetItem(value))
        self.gates.resizeColumnsToContents(); self.table.resizeColumnsToContents()
        self.details.setPlainText(format_technology_upgrade(result)); self.copy_button.setEnabled(True)

    def copy_result(self):
        if self.result is not None: QApplication.clipboard().setText(format_technology_upgrade(self.result))
