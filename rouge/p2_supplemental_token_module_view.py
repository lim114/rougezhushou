"""Independent source-endpoint comparisons for Ling and Magallan tokens."""
from copy import deepcopy

from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDialog,
    QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout)

from .p2_supplemental_token_modules import (FIELDS, LABELS,
    compare_supplemental_token_modules, format_supplemental_token_modules, supported_operators)


class SupplementalTokenModuleDialog(QDialog):
    def __init__(self, operator, training, parent=None):
        super().__init__(parent)
        if operator not in supported_operators():
            raise ValueError('当前补充召唤物模组范围仅含令与麦哲伦。')
        self.operator = operator; self.training = deepcopy(training); self.result = None
        self.setWindowTitle(supported_operators()[operator] + ' · 分技能召唤物培养端点与模组对照')
        self.resize(1190, 780); layout = QVBoxLayout(self)
        self.scope_label = QLabel('显式选择独立实体的原始资料阶段和1级/满级端点。宿主培养只核技能及模组门，'
                                 '不会替您选择实体阶段、插值或继承本体信赖/潜能。当前完整面板与实际在场未知。')
        self.scope_label.setWordWrap(True); layout.addWidget(self.scope_label)
        choices = QHBoxLayout(); choices.addWidget(QLabel('独立实体资料阶段'))
        self.phase = QComboBox(); self.phase.addItem('请选择资料阶段', None)
        for elite in range(3): self.phase.addItem('精英' + str(elite) + '资料', elite)
        choices.addWidget(self.phase); choices.addWidget(QLabel('资料端点'))
        self.endpoint = QComboBox(); self.endpoint.addItem('请选择端点', None)
        self.endpoint.addItem('该阶段1级', 'first'); self.endpoint.addItem('该阶段满级', 'last')
        choices.addWidget(self.endpoint); choices.addStretch()
        self.calculate_button = QPushButton('比较全部技能变体与模组阶段'); self.calculate_button.clicked.connect(self.calculate)
        choices.addWidget(self.calculate_button)
        self.copy_button = QPushButton('复制端点、条件与对照'); self.copy_button.clicked.connect(self.copy_result)
        choices.addWidget(self.copy_button); layout.addLayout(choices)
        self.qualification = QLabel('打开时宿主培养固定。请先明确选择独立资料端点；不会自动采用宿主等级。')
        self.qualification.setWordWrap(True); layout.addWidget(self.qualification)
        self.table = QTableWidget(0, 13)
        self.table.setHorizontalHeaderLabels(['技能', '独立实体', '资料等级', '模组阶段', '资格与分项状态',
                                             *[LABELS[key] for key in FIELDS]])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        self.details = QPlainTextEdit(); self.details.setReadOnly(True); layout.addWidget(self.details)
        self.phase.currentIndexChanged.connect(self.invalidate)
        self.endpoint.currentIndexChanged.connect(self.invalidate); self.invalidate()

    def invalidate(self, *_args):
        self.result = None; self.copy_button.setEnabled(False); self.table.setRowCount(0)
        self.details.setPlainText('请显式选择独立实体资料阶段和端点后比较。所选端点为局外反事实，不确认当前实体培养。')

    def calculate(self):
        self.invalidate()
        try:
            result = compare_supplemental_token_modules(self.operator, self.training,
                        {'token_elite': self.phase.currentData(), 'endpoint': self.endpoint.currentData()})
        except (ValueError, TypeError, KeyError) as error:
            self.details.setPlainText(str(error)); return
        self.result = result
        training = result['host_training']
        self.qualification.setText(f"宿主资格参考：精英{training['elite']}、等级{training['level']}；"
            f"对照模组：{result['module_name']}，精英{result['module_unlock_elite']}等级{result['module_unlock_level']}门"
            + ('已符合。' if result['module_qualified'] else '未符合。')
            + '库存、在场上限与完整当前实体面板未知；本表只合成独立端点和直接装备加值。')
        states = {'base_endpoint': '原始端点', 'direct_addition_reference': '直接装备分项',
                  'host_gate_unmet': '宿主技能/模组门未符合'}
        for variant in result['variants']:
            for stage in variant['stages']:
                index = self.table.rowCount(); self.table.insertRow(index)
                status = states[stage['state']]
                if not variant['skill_qualified'] and stage['module_level'] == 0:
                    status += '；宿主技能门未符合'
                row = [f"S{variant['skill']}", variant['token_name'], str(variant['token_level_endpoint']),
                       str(stage['module_level']), status,
                       *['未知' if stage['values'][key] is None else f"{stage['values'][key]:g}" for key in FIELDS]]
                for column, value in enumerate(row):
                    item = QTableWidgetItem(value)
                    item.setToolTip('独立培养与直接装备参考；完整当前面板未知。\n' + stage['source_selector'])
                    self.table.setItem(index, column, item)
        self.table.resizeColumnsToContents(); self.copy_button.setEnabled(True)
        self.details.setPlainText(format_supplemental_token_modules(result))

    def copy_result(self):
        if self.result is not None:
            QApplication.clipboard().setText(format_supplemental_token_modules(self.result))
