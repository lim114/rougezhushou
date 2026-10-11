"""Keep editable preview selection while explicitly refreshing raw run facts."""
from copy import deepcopy
from PySide6.QtWidgets import QPushButton
from .reference_dialog import ReferenceDialog
from .supplemental_skills import supplemental_profiles
from .supplemental_run import run_skill_reference,format_run_reference


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

    def refresh_environment(self):
        self.environment=deepcopy(self.environment_provider())
        self.calculate()
