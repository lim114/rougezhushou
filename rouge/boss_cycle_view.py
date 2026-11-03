"""Manual documentary reading of two exact boss entries, without calculations."""
from copy import deepcopy
import json

from PySide6.QtWidgets import QComboBox,QDialog,QHBoxLayout,QLabel,QPlainTextEdit,QTabWidget,QVBoxLayout

from . import boss_cycle_reference as model
from .ui_state import replace_text
from .view_catalog import SubjectPicture


def target_identity(identity):
    return (type(identity)is tuple and len(identity)==3
        and type(identity[0])is str and type(identity[1])is str
        and type(identity[2])is int and identity in model.TARGETS)


def _validated(result,identity):
    if (type(result)is not dict or result.get('source_valid')is not True
            or result.get('status')!='documented_reference'):
        return False
    reference=result.get('reference');source=result.get('source_identity')
    if type(reference)is not dict or type(source)is not dict:return False
    if (type(reference.get('stage_id'))is not str or type(reference.get('enemy_id'))is not str
            or type(reference.get('level'))is not int
            or(reference['stage_id'],reference['enemy_id'],reference['level'])!=identity):return False
    if type(reference.get('entry_name'))is not str or not reference['entry_name'].strip():return False
    for field in('manifest_sha256','data_sha256'):
        value=source.get(field)
        if type(value)is not str or len(value)!=64 or any(c not in'0123456789abcdefABCDEF'for c in value):return False
    topics=reference.get('topics')
    if type(topics)is not list or not topics:return False
    ids=set()
    for topic in topics:
        if (type(topic)is not dict or type(topic.get('id'))is not str or not topic['id'].strip()
                or type(topic.get('name'))is not str or not topic['name'].strip()or topic['id']in ids):return False
        ids.add(topic['id'])
    return True


class BossCycleReferencePanel(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setModal(False);self.resize(960,760)
        self.identity=self.scope_key=self.result=None;self._view_key=None
        layout=QVBoxLayout(self)
        self.notice=QLabel();self.notice.setWordWrap(True);layout.addWidget(self.notice)
        header=QHBoxLayout();self.lorentz_picture=SubjectPicture();self.cube_picture=SubjectPicture()
        header.addWidget(self.lorentz_picture);header.addWidget(self.cube_picture)
        selection=QVBoxLayout();selection.addWidget(QLabel('选择要阅读的交替流程或具体主体的资料'))
        self.topic=QComboBox();self.topic.setAccessibleName('交替激活与模块条件资料；总览或手动选择文献条目')
        selection.addWidget(self.topic);selection.addStretch(1);header.addLayout(selection,1);layout.addLayout(header)
        self.tabs=QTabWidget();layout.addWidget(self.tabs,1)
        self.player=QPlainTextEdit();self.player.setReadOnly(True)
        self.technical=QPlainTextEdit();self.technical.setReadOnly(True)
        self.tabs.addTab(self.player,'交替流程、主体与模块条件')
        self.tabs.addTab(self.technical,'技术详情与完整来源')
        self.topic.currentIndexChanged.connect(self._topic_changed)
        self.clear_reference()

    def clear_reference(self,notice='请先选中对应首领，再手动打开交替激活与模块条件资料。'):
        self.identity=self.scope_key=self.result=self._view_key=None
        blocked=self.topic.blockSignals(True);self.topic.clear();self.topic.setEnabled(False);self.topic.blockSignals(blocked)
        self.lorentz_picture.set_subject(None,None,'');self.cube_picture.set_subject(None,None,'')
        replace_text(self.player,'',preserve=False);replace_text(self.technical,'',preserve=False)
        self.tabs.setCurrentIndex(0);self.notice.setText(notice)
        self.setWindowTitle('交替激活与模块条件资料')

    def _query(self,identity):
        try:return model.cycle_reference(*identity)
        except (OSError,ValueError,TypeError,KeyError):return None

    def _render(self,topic_id,*,preserve):
        self._view_key=(self.scope_key,topic_id)
        replace_text(self.player,model.reference_text(self.result,topic_id=topic_id),preserve=preserve)
        source={'result':deepcopy(self.result),'selected_topic_id':topic_id,
            'selection_is_documentary_not_actual_cycle_state':True}
        replace_text(self.technical,json.dumps(source,ensure_ascii=False,indent=2),preserve=preserve)

    def set_reference(self,identity,result=None):
        if not target_identity(identity):
            self.clear_reference('已更换敌人，旧交替激活与模块条件资料已清除。');return False
        if result is None:result=self._query(identity)
        if not _validated(result,identity):
            self.clear_reference('交替激活与模块条件资料暂时无法核对，旧内容与图片已清除。');return False
        scope=(identity,json.dumps(result['source_identity'],sort_keys=True,separators=(',',':')))
        keep=self.identity==identity and self.scope_key==scope
        selected=self.topic.currentData()if keep else None
        topics=result['reference']['topics']
        if selected is not None and not any(p['id']==selected for p in topics):
            self.clear_reference('所选条目与当前资料不一致，旧内容已清除；请重新打开。');return False
        if not keep:self.clear_reference()
        self.identity=identity;self.scope_key=scope;self.result=deepcopy(result)
        blocked=self.topic.blockSignals(True);self.topic.clear();self.topic.addItem('总览：交替激活与模块条件',None)
        for topic in topics:self.topic.addItem(topic['name'],topic['id'])
        self.topic.setCurrentIndex(self.topic.findData(selected));self.topic.setEnabled(True);self.topic.blockSignals(blocked)
        name=result['reference']['entry_name']
        self.notice.setText('上方是两名首领的固定原图，不表示当前激活状态，也不是模块图片。两个主体的完整关联流程均可阅读；不据此计算本局伤害、倒计时或模块效果。')
        self.setWindowTitle(name+' · 交替激活与模块条件资料')
        self.lorentz_picture.set_subject('enemy','enemy_2147_shophm','洛伦茨，扰动之谬（固定原图，不代表当前激活状态）')
        self.cube_picture.set_subject('enemy','enemy_2148_shorbb','源阶方（固定原图，不代表当前激活状态）')
        self._render(selected,preserve=keep)
        return True

    def _topic_changed(self,*_):
        identity=self.identity
        if identity is None:return False
        selected=self.topic.currentData();result=self._query(identity)
        if not _validated(result,identity):
            self.clear_reference('资料暂时无法核对，旧内容与图片已清除。');return False
        scope=(identity,json.dumps(result['source_identity'],sort_keys=True,separators=(',',':')))
        if scope!=self.scope_key:
            self.clear_reference('资料版本已变化，旧选择已清除；请重新手动打开。');return False
        if selected is not None and not any(p['id']==selected for p in result['reference']['topics']):
            self.clear_reference('无法核对所选主题条目，旧内容已清除。');return False
        keep=self._view_key==(scope,selected)
        self.result=deepcopy(result);self._render(selected,preserve=keep)
        if not keep:self.tabs.setCurrentWidget(self.player)
        return True

    def refresh_reference(self):
        # Source loss discards identity: recovery alone cannot refill the reader.
        if self.identity is None:return False
        result=self._query(self.identity)
        if not _validated(result,self.identity):
            self.clear_reference('交替激活与模块条件资料暂时无法核对，旧内容与图片已清除。');return False
        scope=(self.identity,json.dumps(result['source_identity'],sort_keys=True,separators=(',',':')))
        if scope!=self.scope_key:
            self.clear_reference('资料版本已变化，旧选择已清除；请重新手动打开。');return False
        return self.set_reference(self.identity,result)
