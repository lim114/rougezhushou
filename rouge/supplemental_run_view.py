"""Keep editable preview selection while explicitly refreshing raw run facts."""
from copy import deepcopy
from PySide6.QtWidgets import QPushButton,QGridLayout
from .reference_dialog import ReferenceDialog
from .supplemental_skills import supplemental_profiles, MissingHpExceedsMaximum
from .supplemental_run import run_skill_reference,format_run_reference
from .supplemental_comparison import _compare_ranks, format_comparison
from .skill_upgrade_comparison import RankListError
from .supplemental_cultivation import _compare_cultivation,ProposalInputError,cultivation_defaults,format_cultivation_comparison
from .supplemental_enemies import _compare_fixed_enemies, enemy_defaults, format_fixed_enemies, EnemySelectionError
from .enemy_environment import EnemyReferenceError
from .supplemental_budget import (NoBudgetSource, _budget_reference, _budget_defaults, _declared_healing_budget,
    _declared_damage_budget,format_supplemental_damage_budget,
    format_supplemental_healing_budget)
from .damage_budget import DamageBudgetInputError, damage_sources
from .healing_budget import HealingBudgetInputError, healing_sources


from .charge_timeline import DeclaredTimeError


class SupplementalRunDialog(ReferenceDialog):
    def __init__(self,preview,environment_provider,parent=None):
        self.environment_provider=environment_provider
        self.environment=deepcopy(environment_provider())
        profiles=supplemental_profiles()['operators']
        super().__init__('补充干员 · 本局属性与单次技能对照',
            '本局条件为打开时快照；“更新本局条件”保留当前干员及编辑内容。次数为手动声明，不推算原生时钟。可选operator：'+
            '；'.join(k+'（'+v['name']+'）' for k,v in profiles.items()),preview,
            lambda p:run_skill_reference(p,self.environment),format_run_reference,
            [('name','分项'),('base_value','不含本局修正'),('value','计入本局属性'),
             ('delta','差值'),('unit','单位'),('declared_total','声明次数合计')],parent,defer_initial_calculation=True)
        self.refresh_button=QPushButton('更新本局条件')
        self.tools_layout=QGridLayout();self.layout().insertLayout(2,self.tools_layout)
        self.tools_layout.addWidget(self.refresh_button,0,0)
        self.refresh_button.clicked.connect(self.refresh_environment)
        self.children_dialogs=[]
        self.rank_button=QPushButton('本局技能等级收益对照')
        self.tools_layout.addWidget(self.rank_button,0,1)
        self.rank_button.clicked.connect(self.show_ranks)
        self.cultivation_button=QPushButton('本局培养与招募来源对照')
        self.tools_layout.addWidget(self.cultivation_button,1,0)
        self.cultivation_button.clicked.connect(self.show_cultivation)
        self.enemy_button=QPushButton('固定关卡敌人与保密等级对照')
        self.tools_layout.addWidget(self.enemy_button,1,1)
        self.enemy_button.clicked.connect(self.show_enemies)
        self.damage_button=QPushButton('逐目标声明伤害预算')
        self.healing_button=QPushButton('逐友方声明治疗预算')
        self.tools_layout.addWidget(self.damage_button,2,0);self.tools_layout.addWidget(self.healing_button,2,1)
        self.damage_button.clicked.connect(self.show_damage_budget)
        self.healing_button.clicked.connect(self.show_healing_budget)
        self.calculate()

    def invalidate(self):
        super().invalidate()
        self.damage_button.hide();self.healing_button.hide()

    def calculate(self):
        super().calculate()
        self.update_budget_entries()

    def update_budget_entries(self):
        if self.result is None:return
        reference = _budget_reference(self.result)
        self.damage_button.setVisible(bool(damage_sources(reference)))
        self.healing_button.setVisible(bool(healing_sources(reference)))
        kind=supplemental_profiles()['operators'][self.result['preview']['operator']]['kind']
        self.healing_button.setText('自身声明治疗预算' if kind=='self_heal' else '逐友方声明治疗预算')

    def show_damage_budget(self):
        self.show_budget(False)

    def show_healing_budget(self):
        self.show_budget(True)

    def show_budget(self,healing):
        if self.result is None:
            self.notice.setPlainText('请先计算当前干员条件，再打开预算工具。');return
        result=deepcopy(self.result);p=result['preview'];environment=result['environment']
        reference = _budget_reference(result)
        sources = healing_sources(reference) if healing else damage_sources(reference)
        try:
            initial = _budget_defaults(p, reference, sources, healing=healing)
        except NoBudgetSource as error:
            self.notice.setPlainText(str(error))
            return
        columns=([('at_seconds','声明秒数'),('recipient','接收者'),('kind','事件'),
                  ('amount_reference','单次参考'),('effective_healing','有效治疗'),('overhealing','过量'),('hp_after','剩余预算生命')]
                 if healing else [('at_seconds','声明秒数'),('target','目标'),('source','来源'),
                  ('per_hit','单次参考'),('effective_damage','有效伤害'),('overkill','溢出'),('hp_after','剩余预算生命')])
        labels='；'.join(s['id']+'：'+s['name'] for s in sources)
        dialog=ReferenceDialog('补充干员 · '+('声明治疗预算' if healing else '逐目标声明伤害预算'),
            '时刻与对象由用户声明，不能视为原生时钟。可用来源：'+labels,initial,
            lambda q:_declared_healing_budget(p,environment,q,reference,sources) if healing else _declared_damage_budget(p,environment,q,opened_reference=reference),
            format_supplemental_healing_budget if healing else format_supplemental_damage_budget,columns,self,
            input_errors=(HealingBudgetInputError, DamageBudgetInputError, DeclaredTimeError, MissingHpExceedsMaximum))
        self.children_dialogs.append(dialog);dialog.show()

    def show_enemies(self):
        if self.result is None:
            self.notice.setPlainText('请先计算当前干员条件，再打开对照工具。');return
        operator_preview = deepcopy(self.result['preview'])
        environment = deepcopy(self.result['environment'])
        dialog=ReferenceDialog('补充干员 · 固定关卡敌人与保密等级对照',
            '每名敌人以所选第一个保密等级为基准。未提供等级时，4级只是局外默认方案；grades为空表示原记录待确认，请填写0–15。',
            enemy_defaults(environment),
            lambda p:_compare_fixed_enemies(operator_preview, environment, p, opened_result=True),format_fixed_enemies,
            [('enemy_name','候选敌人'),('grade','保密等级'),('name','分项'),('value','预计参考'),
             ('base_value','首选难度基准'),('delta','差值'),('unit','单位')],self,input_errors=(EnemySelectionError, EnemyReferenceError, MissingHpExceedsMaximum))
        self.children_dialogs.append(dialog);dialog.show()

    def show_cultivation(self):
        if self.result is None:
            self.notice.setPlainText('请先计算当前干员条件，再打开对照工具。');return
        result=deepcopy(self.result)
        dialog=ReferenceDialog('补充干员 · 本局培养与招募来源对照',
            '方案仅用于局外比较；来源null为未知，non_emergency为非应急，emergency_hire为应急助力。',
            cultivation_defaults(result['preview'],result['environment']),
            lambda p:_compare_cultivation(result['preview'],result['environment'],p,baseline=result),format_cultivation_comparison,
            [('proposal','培养方案'),('name','分项'),('value','预计结果'),
             ('base_value','当前培养基准'),('delta','差值'),('unit','单位')],self,input_errors=(ProposalInputError,))
        self.children_dialogs.append(dialog);dialog.show()

    def show_ranks(self):
        if self.result is None:
            self.notice.setPlainText('请先计算当前干员条件，再打开对照工具。');return
        result=deepcopy(self.result)
        dialog=ReferenceDialog('补充干员 · 本局技能等级收益对照',
            '冻结打开时的干员与本局条件；各分项独立显示，差值相对当前技能等级。',
            {'ranks':list(range(1,8))},
            lambda p:_compare_ranks(result['preview'],result['environment'],p,baseline=result),format_comparison,
            [('rank','技能等级'),('name','分项'),('value','预计结果'),
             ('base_value','当前等级基准'),('delta','差值'),('unit','单位')],self,input_errors=(RankListError, MissingHpExceedsMaximum))
        self.children_dialogs.append(dialog);dialog.show()

    def refresh_environment(self):
        self.environment=deepcopy(self.environment_provider())
        self.calculate()
