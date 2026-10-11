"""Keep editable preview selection while explicitly refreshing raw run facts."""
from copy import deepcopy
from PySide6.QtWidgets import QPushButton
from .reference_dialog import ReferenceDialog
from .supplemental_skills import supplemental_profiles
from .supplemental_run import run_skill_reference,format_run_reference
from .supplemental_comparison import compare_ranks,format_comparison
from .supplemental_cultivation import compare_cultivation,cultivation_defaults,format_cultivation_comparison


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
             ('delta','差值'),('unit','单位'),('declared_total','声明次数合计')],parent)
        self.refresh_button=QPushButton('更新本局条件')
        self.layout().insertWidget(2,self.refresh_button)
        self.refresh_button.clicked.connect(self.refresh_environment)
        self.children_dialogs=[]
        self.rank_button=QPushButton('本局技能等级收益对照')
        self.layout().insertWidget(3,self.rank_button)
        self.rank_button.clicked.connect(self.show_ranks)
        self.cultivation_button=QPushButton('本局培养与招募来源对照')
        self.layout().insertWidget(4,self.cultivation_button)
        self.cultivation_button.clicked.connect(self.show_cultivation)

    def show_cultivation(self):
        if self.result is None:
            self.notice.setPlainText('请先计算当前干员条件，再打开对照工具。');return
        result=deepcopy(self.result)
        dialog=ReferenceDialog('补充干员 · 本局培养与招募来源对照',
            '方案仅用于局外比较；来源null为未知，non_emergency为非应急，emergency_hire为应急助力。',
            cultivation_defaults(result['preview'],result['environment']),
            lambda p:compare_cultivation(result['preview'],result['environment'],p),format_cultivation_comparison,
            [('proposal','培养方案'),('name','分项'),('value','预计结果'),
             ('base_value','当前培养基准'),('delta','差值'),('unit','单位')],self)
        self.children_dialogs.append(dialog);dialog.show()

    def show_ranks(self):
        if self.result is None:
            self.notice.setPlainText('请先计算当前干员条件，再打开对照工具。');return
        result=deepcopy(self.result)
        dialog=ReferenceDialog('补充干员 · 本局技能等级收益对照',
            '冻结打开时的干员与本局条件；各分项独立显示，差值相对当前技能等级。',
            {'ranks':list(range(1,8))},
            lambda p:compare_ranks(result['preview'],result['environment'],p),format_comparison,
            [('rank','技能等级'),('name','分项'),('value','预计结果'),
             ('base_value','当前等级基准'),('delta','差值'),('unit','单位')],self)
        self.children_dialogs.append(dialog);dialog.show()

    def refresh_environment(self):
        self.environment=deepcopy(self.environment_provider())
        self.calculate()
