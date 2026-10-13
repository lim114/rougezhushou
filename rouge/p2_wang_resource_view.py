"""Temporary, human-readable receipt editor for Wang's independent pools."""
from copy import deepcopy
import json

from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
    QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout)

from .p2_wang_resource_ledger import (LIMITS, POOLS, POOL_LABELS,
    format_wang_resource_ledger, format_wang_training, wang_resource_ledger, wang_resource_reference)


KINDS = {'manual_receipt': '手动创建结果声明', 'skill_receipt': '技能取得结果声明',
         'loss_receipt': '消失与明确返还声明', 'snapshot': '新的独立快照'}
FIELDS = {
    'manual_receipt': [('manual_created', '成功手动棋子数（单次0–1）', 1),
                       ('extra_created', '成功跟子数（单次0–1）', 1),
                       ('stock_spent', '声明卡片库存消耗', 9999),
                       ('currency_spent', '声明费用支出', 9999),
                       ('sp_spent', '声明技力支出', 9999)],
    'skill_receipt': [('accepted_stock', '声明实际入库（名义取得2）', 2),
                      ('sp_spent', '声明技力支出', 9999)],
    'loss_receipt': [('manual_lost', '声明手动棋子减少', 9999),
                     ('extra_lost', '声明活跃跟子减少', 9999),
                     ('stock_returned', '声明实际库存返还', 9999),
                     ('currency_returned', '声明实际费用返还', 9999),
                     ('sp_returned', '声明实际技力返还', 9999)],
    'snapshot': [(key, POOL_LABELS[key], LIMITS[key]) for key in POOLS]}


def _control(maximum, value=None):
    control = QSpinBox(); control.setRange(-1, maximum)
    control.setSpecialValueText('未知'); control.setValue(-1 if value is None else value)
    return control


class WangReceiptDialog(QDialog):
    def __init__(self, kind, identity, snapshot_id, declaration=None, parent=None):
        super().__init__(parent)
        self.kind = kind; self.identity = identity
        self.setWindowTitle(KINDS[kind]); self.resize(520, 410)
        layout = QVBoxLayout(self)
        label = QLabel('只填写已明确声明的数量；0表示明确没有改变，未知不是0。创建、消失或返还之间不自动推导。')
        label.setWordWrap(True); layout.addWidget(label)
        form = QFormLayout(); layout.addLayout(form)
        declaration = declaration or {}
        values = declaration.get('state', {}) if kind == 'snapshot' else declaration
        self.snapshot_name = None
        if kind == 'snapshot':
            self.snapshot_name = QLineEdit(values.get('snapshot_id', snapshot_id))
            form.addRow('独立快照名称', self.snapshot_name)
            label.setText('这是新的独立声明快照，会开始新的账本段；不会被视作上一段余额已核验或已恢复。')
        self.controls = {}
        for key, caption, maximum in FIELDS[kind]:
            control = _control(maximum, values.get(key))
            self.controls[key] = control; form.addRow(caption, control)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def declaration(self):
        values = {key: None if control.value() < 0 else control.value()
                  for key, control in self.controls.items()}
        if self.kind == 'snapshot':
            return {'id': self.identity, 'kind': self.kind,
                    'state': {'snapshot_id': self.snapshot_name.text(), **values}}
        return {'id': self.identity, 'kind': self.kind, **values}


class WangResourceLedgerDialog(QDialog):
    def __init__(self, training, parent=None, *, skill=1, rank=1):
        super().__init__(parent)
        self.training = deepcopy(training); self.steps = []; self.result = None; self.serial = 0
        self.setWindowTitle('望 · 卡片棋子与跟子弹道分池账本'); self.resize(1120, 760)
        layout = QVBoxLayout(self)
        notice = QLabel('局外声明序列：卡片库存、手动棋子与跟子弹道各自记账。没有实际摆位、技能时钟或游戏操作。'
                        '打开时的培养条件固定；当前本局数量保持未知。')
        notice.setWordWrap(True); layout.addWidget(notice)
        choices = QHBoxLayout(); choices.addWidget(QLabel('技能来源'))
        self.skill = QComboBox(); self.skill.addItem('S1 取势', 1)
        if self.training.get('elite', 2) >= 1:
            self.skill.addItem('S2 连星', 2)
        self.skill.setCurrentIndex(max(0, self.skill.findData(skill))); choices.addWidget(self.skill)
        choices.addWidget(QLabel('等级'))
        self.rank = QSpinBox(); self.rank.setRange(1, 10 if self.training.get('elite', 2) == 2 else 7)
        self.rank.setValue(rank); choices.addWidget(self.rank); choices.addStretch(); layout.addLayout(choices)
        self.source_label = QLabel(); self.source_label.setWordWrap(True); layout.addWidget(self.source_label)
        initial = QHBoxLayout(); initial.addWidget(QLabel('初始快照'))
        self.initial_name = QLineEdit('初始声明'); self.initial_name.setMaximumWidth(140)
        initial.addWidget(self.initial_name); self.initial_controls = {}
        for key in POOLS:
            initial.addWidget(QLabel(POOL_LABELS[key]))
            control = _control(LIMITS[key]); self.initial_controls[key] = control; initial.addWidget(control)
            control.valueChanged.connect(self.invalidate)
        layout.addLayout(initial)
        actions = QHBoxLayout(); self.add_buttons = {}
        for kind, label in KINDS.items():
            button = QPushButton('添加' + label); button.clicked.connect(lambda _checked=False, k=kind: self.add_step(k))
            self.add_buttons[kind] = button; actions.addWidget(button)
        self.edit_button = QPushButton('编辑所选'); self.edit_button.clicked.connect(self.edit_step); actions.addWidget(self.edit_button)
        self.remove_button = QPushButton('移除所选'); self.remove_button.clicked.connect(self.remove_step); actions.addWidget(self.remove_button)
        layout.addLayout(actions)
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(['步骤', '声明类型', '卡片库存', '手动棋子', '活跃跟子弹道', '费用', '技力', '账本状态'])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        calculation = QHBoxLayout()
        self.calculate_button = QPushButton('核对声明资源链'); self.calculate_button.clicked.connect(self.calculate)
        calculation.addWidget(self.calculate_button)
        self.copy_button = QPushButton('复制资源链与声明'); self.copy_button.clicked.connect(self.copy_result)
        calculation.addWidget(self.copy_button); layout.addLayout(calculation)
        self.details = QPlainTextEdit(); self.details.setReadOnly(True); layout.addWidget(self.details)
        self.initial_name.textChanged.connect(self.invalidate)
        self.skill.currentIndexChanged.connect(self.change_reference); self.rank.valueChanged.connect(self.change_reference)
        self.change_reference(); self.calculate()

    def preview(self):
        return {'initial': {'snapshot_id': self.initial_name.text(),
                            **{key: None if control.value() < 0 else control.value()
                               for key, control in self.initial_controls.items()}},
                'steps': deepcopy(self.steps)}

    def change_reference(self, *_args):
        try:
            reference = wang_resource_reference(self.training, self.skill.currentData(), self.rank.value())
            extra = '未知（所选模组额外池未闭合）' if reference['extra_limit_reference'] is None else str(reference['extra_limit_reference'])
            self.source_label.setText(f"固定培养：{format_wang_training(reference)}；库存参考上限{reference['stock_limit_reference']}；"
                                      f"手动棋子上限{reference['manual_limit_reference']}；跟子基础参数{reference['base_extra_limit_parameter']}，"
                                      f"完整上限参考{extra}；技能名义取得2枚、技力消耗{reference['sp_cost_parameter']}。")
            self.source_label.setToolTip(reference['talent_source']['selector'] + '\n' + reference['skill_source']['selector'])
        except (ValueError, KeyError, TypeError) as error:
            self.source_label.setText(str(error))
        self.invalidate()

    def invalidate(self, *_args):
        self.result = None; self.copy_button.setEnabled(False)
        self.table.setRowCount(len(self.steps))
        for index, step in enumerate(self.steps):
            for column, value in enumerate([step['id'], KINDS[step['kind']], *(['待核对'] * 6)]):
                item = QTableWidgetItem(value)
                item.setToolTip(json.dumps(step, ensure_ascii=False)); self.table.setItem(index, column, item)
        self.details.setPlainText('声明已修改，请核对资源链。')

    def add_step(self, kind):
        if len(self.steps) >= 60:
            self.details.setPlainText('声明序列最多60项。'); return
        self.serial += 1
        dialog = WangReceiptDialog(kind, f'声明-{self.serial}', f'独立快照-{self.serial}', parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.steps.append(dialog.declaration()); self.invalidate()

    def edit_step(self):
        index = self.table.currentRow()
        if not 0 <= index < len(self.steps): return
        step = self.steps[index]
        dialog = WangReceiptDialog(step['kind'], step['id'], '', step, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.steps[index] = dialog.declaration(); self.invalidate()

    def remove_step(self):
        index = self.table.currentRow()
        if 0 <= index < len(self.steps):
            self.steps.pop(index); self.invalidate()

    def calculate(self):
        self.invalidate()
        try:
            result = wang_resource_ledger(self.training, self.preview(),
                                          skill=self.skill.currentData(), rank=self.rank.value())
        except (ValueError, TypeError, KeyError) as error:
            self.details.setPlainText(str(error)); return
        self.result = result
        for index, row in enumerate(result['rows']):
            for column, key in enumerate(POOLS, 2):
                value = row['after'][key]
                self.table.setItem(index, column, QTableWidgetItem('未知' if value is None else str(value)))
            status = {'independent_snapshot': '新的独立快照', 'declared_balance': '声明余额',
                      'partial_unknown': '部分未知', 'contradicted_declaration': '负余额矛盾，阻断',
                      'blocked_after_contradiction': '前链已阻断'}[row['status']]
            outside = [POOL_LABELS[key] for key, value in row['within_reference'].items() if value is False]
            if outside: status += '；超过参考：' + '、'.join(outside)
            self.table.setItem(index, 7, QTableWidgetItem(status))
        self.table.resizeColumnsToContents(); self.copy_button.setEnabled(True)
        self.details.setPlainText(format_wang_resource_ledger(result))

    def copy_result(self):
        if self.result is not None:
            QApplication.clipboard().setText(format_wang_resource_ledger(self.result) + '\n\n独立声明：\n' +
                                             json.dumps(self.result['preview'], ensure_ascii=False, indent=2))
