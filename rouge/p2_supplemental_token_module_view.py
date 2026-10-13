"""Independent source-endpoint comparisons for Ling and Magallan tokens."""
from copy import deepcopy

from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDialog,
    QGroupBox, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout)

from .p2_supplemental_token_modules import (FIELDS, LABELS,
    compare_supplemental_token_modules, format_supplemental_token_modules, supported_operators)


class SupplementalTokenModuleDialog(QDialog):
    def __init__(self, operator, training, parent=None):
        super().__init__(parent)
        if operator not in supported_operators():
            raise ValueError('当前补充召唤物模组范围仅含令与麦哲伦。')
        self.operator = operator; self.training = deepcopy(training); self.result = None
        self.fusion_result = None; self.level_result = None
        self.setWindowTitle(supported_operators()[operator] + ' · 分技能召唤物培养端点与模组对照')
        self.resize(1190, 780); layout = QVBoxLayout(self)
        self.scope_label = QLabel('显式选择独立实体的原始资料阶段和1级/满级端点。宿主培养只核技能及模组门，'
                                 '不会替您选择实体阶段、插值或继承本体信赖/潜能。当前完整面板与实际在场未知。')
        self.scope_label.setWordWrap(True); layout.addWidget(self.scope_label)
        choices = QHBoxLayout()
        self.cultivation_mode = QComboBox()
        self.cultivation_mode.addItem('独立资料端点', 'endpoints')
        self.cultivation_mode.addItem('按宿主声明培养等级（原生分支参考）', 'host_level')
        choices.addWidget(self.cultivation_mode)
        self.phase_label = QLabel('独立实体资料阶段'); choices.addWidget(self.phase_label)
        self.phase = QComboBox(); self.phase.addItem('请选择资料阶段', None)
        for elite in range(3): self.phase.addItem('精英' + str(elite) + '资料', elite)
        choices.addWidget(self.phase); self.endpoint_label = QLabel('资料端点'); choices.addWidget(self.endpoint_label)
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
        if operator == 'char_2023_ling':
            from .ling_fusion_reference import FORM_FIELDS, FORM_LABELS
            self.ling_panel = QGroupBox('令三技能 · 弦惊形态与技能状态（文档算式参考）')
            form_layout = QVBoxLayout(self.ling_panel)
            rank_row = QHBoxLayout(); rank_row.addWidget(QLabel('宁作吾等级'))
            self.ling_rank = QComboBox(); self.ling_rank.addItem('请选择技能等级', None)
            for rank in range(1, 11):
                self.ling_rank.addItem(f'等级{rank}' if rank <= 7 else f'专精{rank - 7}', rank)
            rank_row.addWidget(self.ling_rank); rank_row.addStretch(); form_layout.addLayout(rank_row)
            self.ling_forms = QTableWidget(0, 4 + len(FORM_FIELDS))
            self.ling_forms.setHorizontalHeaderLabels(['模组阶段', '形态', '技能状态声明', '参考资格',
                                                      *[FORM_LABELS[k] for k in FORM_FIELDS]])
            self.ling_forms.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            form_layout.addWidget(self.ling_forms); layout.addWidget(self.ling_panel)
            self.ling_rank.currentIndexChanged.connect(self.invalidate)
        self.details = QPlainTextEdit(); self.details.setReadOnly(True); layout.addWidget(self.details)
        self.phase.currentIndexChanged.connect(self.invalidate)
        self.endpoint.currentIndexChanged.connect(self.invalidate)
        self.cultivation_mode.currentIndexChanged.connect(self.mode_changed); self.mode_changed()

    def mode_changed(self, *_args):
        endpoints = self.cultivation_mode.currentData() == 'endpoints'
        for widget in (self.phase_label, self.phase, self.endpoint_label, self.endpoint):
            widget.setVisible(endpoints)
        self.scope_label.setText(
            '显式选择独立实体资料阶段与1级/满级端点；宿主培养只核资格门，不自动确定实际实体培养。'
            if endpoints else
            '使用打开窗口时捕获的宿主声明精英和等级，按文档对应实体培养。逐属性插值/保留下界标志未观察，'
            '保留独立混合条件，不默认实际分支；完整当前面板与实际在场未知。')
        self.invalidate()

    def invalidate(self, *_args):
        self.result = None; self.copy_button.setEnabled(False); self.table.setRowCount(0)
        self.fusion_result = None
        self.level_result = None
        if hasattr(self, 'ling_forms'): self.ling_forms.setRowCount(0)
        self.details.setPlainText(
            '请显式选择独立实体资料阶段和端点后比较。所选端点为局外反事实，不确认当前实体培养。'
            if self.cultivation_mode.currentData() == 'endpoints' else
            '点击比较以使用捕获的宿主声明培养。缺少精英或等级时保留未知，不默认满级。')

    def calculate(self):
        self.invalidate()
        if self.cultivation_mode.currentData() == 'host_level':
            self.calculate_host_level(); return
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
        if hasattr(self, 'ling_rank'):
            if self.ling_rank.currentData() is None:
                self.details.appendPlainText('令三技能形态对照：请明确选择宁作吾等级后重新比较。')
                return
            from .ling_fusion_reference import ling_fusion_reference, format_ling_fusion_reference, FORM_FIELDS
            self.fusion_result = ling_fusion_reference(self.training,
                {'token_elite': self.phase.currentData(), 'endpoint': self.endpoint.currentData()},
                self.ling_rank.currentData())
            self.populate_ling_forms(self.fusion_result['rows'])
            self.details.appendPlainText(format_ling_fusion_reference(self.fusion_result))

    def populate_ling_forms(self, rows):
        from .ling_fusion_reference import FORM_FIELDS
        for row in rows:
            index = self.ling_forms.rowCount(); self.ling_forms.insertRow(index)
            texts = [str(row['module_level']), '基础形态' if row['form'] == 'basic' else '高级形态',
                     '技能开启' if row['skill_active_declared'] else '技能未开启',
                     ('文档算式分项' if row['state'] == 'documented_formula_reference' else '宿主门未符合')
                     + ('；数值插值分支' if row.get('cultivation_branch') == 'numeric_lerp' else
                        '；保留下界分支' if row.get('cultivation_branch') == 'keep_lower_frame' else
                        '；逐属性混合条件' if row.get('cultivation_branch') == 'mixed_field_reference' else '')]
            for key in FORM_FIELDS:
                v = row['values'][key]
                texts.append('未知' if v is None else v if isinstance(v, str) else f'{v:g}')
            for column, value in enumerate(texts):
                item = QTableWidgetItem(value)
                item.setToolTip('固定资料端点与明确模式的文档算式，不证明实际合成/施放或当前完整面板。')
                self.ling_forms.setItem(index, column, item)
        self.ling_forms.resizeColumnsToContents()

    def calculate_host_level(self):
        from .token_level_reference import token_modules_by_host_level, format_token_level_reference
        rank = self.ling_rank.currentData() if hasattr(self, 'ling_rank') else None
        try:
            result = token_modules_by_host_level(self.operator, self.training, rank)
        except (ValueError, TypeError, KeyError) as error:
            self.details.setPlainText(str(error)); return
        self.level_result = result
        training = result['host_training']
        self.qualification.setText(f"宿主声明培养：精英{training['elite']}、等级{training['level']}。"
            '实体培养按文档对应；实际插值标志/实例未知，逐属性分支组合保留。')
        for variant in result['variants']:
            for branch in variant['branches']:
                label = {'numeric_lerp': '数值插值条件', 'keep_lower_frame': '保留下界条件',
                         'mixed_field_reference': '逐属性混合条件'}[branch['branch']]
                for stage in branch['stages']:
                    index = self.table.rowCount(); self.table.insertRow(index)
                    texts = [f"S{variant['skill']}", variant['token_name'], str(variant['token_level_reference']),
                             str(stage['module_level']), label + ('；宿主门未符合' if stage['state'] == 'host_gate_unmet' else ''),
                             *['未知' if stage['values'][key] is None else f"{stage['values'][key]:g}" for key in FIELDS]]
                    for column, value in enumerate(texts):
                        item = QTableWidgetItem(value)
                        item.setToolTip('实际KeepLowerValue未观察；仅本行条件分项，完整当前面板未知。')
                        self.table.setItem(index, column, item)
        self.table.resizeColumnsToContents(); self.copy_button.setEnabled(True)
        self.details.setPlainText(format_token_level_reference(result))
        if hasattr(self, 'ling_forms'):
            self.populate_ling_forms(result['ling_forms'])
            if rank is None: self.details.appendPlainText('需要明确宁作吾等级后才列基础/高级形态技能状态参考。')

    def copy_result(self):
        if self.level_result is not None:
            from .token_level_reference import format_token_level_reference
            QApplication.clipboard().setText(format_token_level_reference(self.level_result)); return
        if self.result is not None:
            text = format_supplemental_token_modules(self.result)
            if self.fusion_result is not None:
                from .ling_fusion_reference import format_ling_fusion_reference
                text += '\n\n' + format_ling_fusion_reference(self.fusion_result)
            QApplication.clipboard().setText(text)
