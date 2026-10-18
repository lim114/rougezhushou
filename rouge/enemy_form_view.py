"""Manual, modeless reading of the eight documented disguise references."""
from copy import deepcopy
import json

from PySide6.QtWidgets import QDialog,QHBoxLayout,QLabel,QPlainTextEdit,QTabWidget,QVBoxLayout
from . import enemy_form_reference as model
from .ui_state import replace_text
from .view_catalog import SubjectPicture


def target_identity(identity):
    return (type(identity)is tuple and len(identity)==3
        and type(identity[0])is str and identity[0]in model.STAGES
        and type(identity[1])is str and identity[1]in model.ALIASES
        and type(identity[2])is int and identity[2]==0)


class EnemyFormReferencePanel(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setModal(False);self.resize(960,760)
        self.setWindowTitle('本性难移 · 伪装与现身资料')
        self.identity=self.scope_key=self.result=None
        layout=QVBoxLayout(self)
        self.notice=QLabel();self.notice.setWordWrap(True);layout.addWidget(self.notice)
        pictures=QHBoxLayout()
        self.body_picture=SubjectPicture();pictures.addWidget(self.body_picture)
        self.disguise_picture=SubjectPicture();pictures.addWidget(self.disguise_picture)
        layout.addLayout(pictures)
        self.tabs=QTabWidget();layout.addWidget(self.tabs,1)
        self.player=QPlainTextEdit();self.player.setReadOnly(True)
        self.technical=QPlainTextEdit();self.technical.setReadOnly(True)
        self.tabs.addTab(self.player,'伪装对象、现身与条件')
        self.tabs.addTab(self.technical,'技术详情与完整来源')
        self.clear_reference()

    def clear_reference(self,notice='请先在战斗资料中选中本性难移的对应空值体，再手动打开。'):
        self.identity=self.scope_key=self.result=None
        self.notice.setText(notice)
        self.body_picture.set_subject(None,None,'')
        self.disguise_picture.set_subject(None,None,'')
        replace_text(self.player,'',preserve=False)
        replace_text(self.technical,'',preserve=False)
        self.tabs.setCurrentIndex(0)
        self.setWindowTitle('本性难移 · 伪装与现身资料')

    def set_reference(self,identity,result=None):
        # An explicit tuple is required: a failed query never selects another enemy.
        if not target_identity(identity):
            self.clear_reference();return False
        if result is None:result=model.disguise_reference(*identity)
        if (not result or result.get('source_valid')is not True
                or result.get('status')!='documented_reference'):
            self.clear_reference((result or {}).get('notice','伪装与现身资料暂时无法核对，旧内容已清除。'))
            return False
        row=result.get('reference')or{}
        if (row.get('stage_id'),row.get('enemy_id'),row.get('level'))!=identity:
            self.clear_reference('当前敌人与资料不一致，旧内容已清除。');return False
        scope=(identity,json.dumps(result['source_identity'],sort_keys=True))
        keep=self.scope_key==scope
        if not keep:self.clear_reference()
        self.identity=identity;self.scope_key=scope;self.result=deepcopy(result)
        target=row['disguise_enemy_reference']
        self.notice.setText('本性难移 · '+('紧急作战'if row['difficulty']=='FOUR_STAR'else'普通作战')
            +'。只读文献和固定对应资料；不判断本局是否已经伪装或现身。')
        self.setWindowTitle(row['documented_variant_name']+' · 伪装与现身资料')
        self.body_picture.set_subject('enemy',row['enemy_id'],'本体原记录：'+row['fixed_name']+'（缺图时不借用伪装对象图片）')
        self.disguise_picture.set_subject('enemy',target['id'],'对应敌人的独立图鉴：'+target['name']+'（不代表本局形态）')
        replace_text(self.player,model.reference_text(result),preserve=keep)
        replace_text(self.technical,json.dumps(result,ensure_ascii=False,indent=2),preserve=keep)
        return True

    def refresh_reference(self):
        # After source loss identity is None; recovery requires an explicit reopen.
        if self.identity is None:return False
        return self.set_reference(self.identity)
