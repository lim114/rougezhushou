"""Modeless source-reference browser; its only outgoing action selects a preview."""
from copy import deepcopy
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QPlainTextEdit,QComboBox,QPushButton,QCheckBox
from . import original_destinations as navigation
from .ui_state import replace_text


class OriginalDestinationPanel(QDialog):
    stageSelected=Signal(str)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('事件目的地原文与固定作战资料')
        self.setModal(False);self.resize(860,660)
        self.choice_id=None;self.context={};self.result=None;self.detail_key=None
        layout=QVBoxLayout(self)
        self.notice=QLabel('只读资料导航；原目的地不证明来源、实际触发或进入。')
        self.notice.setWordWrap(True);layout.addWidget(self.notice)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);layout.addWidget(self.detail,1)
        self.technical=QCheckBox('显示来源ID与技术字段');layout.addWidget(self.technical)
        self.stage=QComboBox();self.stage.setAccessibleName('目的地目录场景的独立作战链接');layout.addWidget(self.stage)
        self.battle_button=QPushButton('查看对应固定战斗地图');layout.addWidget(self.battle_button)
        self.technical.toggled.connect(self.refresh)
        self.battle_button.clicked.connect(self.select_stage)
        self.refresh()

    def set_reference(self,choice_id,context=None):
        self.choice_id=choice_id;self.context=deepcopy(context or {});self.refresh()

    def set_context(self,context=None):
        self.context=deepcopy(context or {});self.refresh()

    def refresh(self,*_):
        previous=self.stage.currentData(Qt.ItemDataRole.UserRole+1)
        self.stage.clear();self.result=None
        key=self.choice_id
        try:
            result=navigation.destination_reference(key,self.context) if key else None
            text=navigation.destination_text(result,self.technical.isChecked()) if result else '尚未选择原选项。'
            self.result=result
            for reference in (result or {}).get('catalog_references',[]):
                for link in reference['battle_links']['rows']:
                    status=navigation.STATUS[link['choice_eligibility']['status']]
                    for index,stage in enumerate(link['preview_stage_candidates'],1):
                        difficulty={'NORMAL':'普通','FOUR_STAR':'紧急'}.get(stage['difficulty'],'难度未确认')
                        identity=[reference['event_id'],reference['scene_key'],link['choice_key'],stage['stage_id']]
                        self.stage.addItem(f"{link['choice_title']} → {stage['name']} · {difficulty} · {status} · 资料候选{index}",stage['stage_id'])
                        self.stage.setItemData(self.stage.count()-1,identity,Qt.ItemDataRole.UserRole+1)
                    pool=link.get('generic_pool_requirement') or {}
                    for index,stage in enumerate(pool.get('fixed_named_pool',[]),1):
                        identity=[reference['event_id'],reference['scene_key'],link['choice_key'],stage['id'],'generic_next_floor']
                        self.stage.addItem(f"{link['choice_title']} → {stage['title']} · 下一主层固定资料候选{index} · {status}",stage['id'])
                        self.stage.setItemData(self.stage.count()-1,identity,Qt.ItemDataRole.UserRole+1)
            if previous:
                self.stage.setCurrentIndex(next((i for i in range(self.stage.count())
                    if self.stage.itemData(i,Qt.ItemDataRole.UserRole+1)==previous),0 if self.stage.count() else -1))
        except (ValueError,TypeError,KeyError) as error:text=str(error)
        self.stage.setVisible(bool(self.stage.count()));self.battle_button.setVisible(bool(self.stage.count()))
        replace_text(self.detail,text,preserve=self.detail_key==key);self.detail_key=key

    def select_stage(self):
        if self.result and self.stage.currentData():self.stageSelected.emit(self.stage.currentData())
