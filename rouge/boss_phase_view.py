"""Manual documentary reading of one exact boss reference, without calculations."""
from copy import deepcopy
import json

from PySide6.QtWidgets import QComboBox,QDialog,QHBoxLayout,QLabel,QPlainTextEdit,QTabWidget,QVBoxLayout

from . import boss_phase_reference as model
from .ui_state import replace_text
from .view_catalog import SubjectPicture


def target_identity(identity):
    return (type(identity)is tuple and len(identity)==3
        and type(identity[0])is str and type(identity[1])is str
        and type(identity[2])is int and identity==model.TARGET)


def _validated(result,identity):
    if (type(result)is not dict or result.get('source_valid')is not True
            or result.get('status')!='documented_reference'):
        return False
    reference=result.get('reference');source=result.get('source_identity')
    if type(reference)is not dict or type(source)is not dict:return False
    if (type(reference.get('stage_id'))is not str or type(reference.get('enemy_id'))is not str
            or type(reference.get('level'))is not int
            or(reference['stage_id'],reference['enemy_id'],reference['level'])!=identity):return False
    if type(reference.get('boss_name'))is not str or not reference['boss_name'].strip():return False
    for field in('manifest_sha256','data_sha256'):
        value=source.get(field)
        if type(value)is not str or len(value)!=64 or any(c not in'0123456789abcdefABCDEF'for c in value):return False
    phases=reference.get('phases')
    if type(phases)is not list or not phases:return False
    ids=set()
    for phase in phases:
        if (type(phase)is not dict or type(phase.get('id'))is not str or not phase['id'].strip()
                or type(phase.get('name'))is not str or not phase['name'].strip()or phase['id']in ids):return False
        ids.add(phase['id'])
    return True


class BossPhaseReferencePanel(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setModal(False);self.resize(960,760)
        self.identity=self.scope_key=self.result=None;self._view_key=None
        layout=QVBoxLayout(self)
        self.notice=QLabel();self.notice.setWordWrap(True);layout.addWidget(self.notice)
        header=QHBoxLayout();self.boss_picture=SubjectPicture();header.addWidget(self.boss_picture)
        selection=QVBoxLayout();selection.addWidget(QLabel('选择要阅读的形态或转换资料'))
        self.phase=QComboBox();self.phase.setAccessibleName('首领形态与转换资料；总览或手动选择文献条目')
        selection.addWidget(self.phase);selection.addStretch(1);header.addLayout(selection,1);layout.addLayout(header)
        self.tabs=QTabWidget();layout.addWidget(self.tabs,1)
        self.player=QPlainTextEdit();self.player.setReadOnly(True)
        self.technical=QPlainTextEdit();self.technical.setReadOnly(True)
        self.tabs.addTab(self.player,'形态、转换与注意事项')
        self.tabs.addTab(self.technical,'技术详情与完整来源')
        self.phase.currentIndexChanged.connect(self._phase_changed)
        self.clear_reference()

    def clear_reference(self,notice='请先选中对应首领，再手动打开形态与转换资料。'):
        self.identity=self.scope_key=self.result=self._view_key=None
        blocked=self.phase.blockSignals(True);self.phase.clear();self.phase.setEnabled(False);self.phase.blockSignals(blocked)
        self.boss_picture.set_subject(None,None,'')
        replace_text(self.player,'',preserve=False);replace_text(self.technical,'',preserve=False)
        self.tabs.setCurrentIndex(0);self.notice.setText(notice)
        self.setWindowTitle('首领形态与转换资料')

    def _query(self,identity):
        try:return model.phase_reference(*identity)
        except (OSError,ValueError,TypeError,KeyError):return None

    def _render(self,phase_id,*,preserve):
        self._view_key=(self.scope_key,phase_id)
        replace_text(self.player,model.reference_text(self.result,phase_id=phase_id),preserve=preserve)
        source={'result':deepcopy(self.result),'selected_phase_id':phase_id,
            'selection_is_documentary_not_actual_boss_phase':True}
        replace_text(self.technical,json.dumps(source,ensure_ascii=False,indent=2),preserve=preserve)

    def set_reference(self,identity,result=None):
        if not target_identity(identity):
            self.clear_reference('已更换敌人，旧首领形态与转换资料已清除。');return False
        if result is None:result=self._query(identity)
        if not _validated(result,identity):
            self.clear_reference('形态与转换资料暂时无法核对，旧内容与图片已清除。');return False
        scope=(identity,json.dumps(result['source_identity'],sort_keys=True,separators=(',',':')))
        keep=self.identity==identity and self.scope_key==scope
        selected=self.phase.currentData()if keep else None
        phases=result['reference']['phases']
        if selected is not None and not any(p['id']==selected for p in phases):
            self.clear_reference('所选条目与当前资料不一致，旧内容已清除；请重新打开。');return False
        if not keep:self.clear_reference()
        self.identity=identity;self.scope_key=scope;self.result=deepcopy(result)
        blocked=self.phase.blockSignals(True);self.phase.clear();self.phase.addItem('总览：形态与转换',None)
        for phase in phases:self.phase.addItem(phase['name'],phase['id'])
        self.phase.setCurrentIndex(self.phase.findData(selected));self.phase.setEnabled(True);self.phase.blockSignals(blocked)
        name=result['reference']['boss_name']
        self.notice.setText('只读文献与固定资料。所选条目不代表本局实际形态；不据此计算面板、伤害或转换时刻。')
        self.setWindowTitle(name+' · 形态与转换资料')
        self.boss_picture.set_subject('enemy',identity[1],name+'（固定敌人原图，不代表当前形态）')
        self._render(selected,preserve=keep)
        return True

    def _phase_changed(self,*_):
        identity=self.identity
        if identity is None:return False
        selected=self.phase.currentData();result=self._query(identity)
        if not _validated(result,identity):
            self.clear_reference('资料暂时无法核对，旧内容与图片已清除。');return False
        scope=(identity,json.dumps(result['source_identity'],sort_keys=True,separators=(',',':')))
        if scope!=self.scope_key:
            self.clear_reference('资料版本已变化，旧选择已清除；请重新手动打开。');return False
        if selected is not None and not any(p['id']==selected for p in result['reference']['phases']):
            self.clear_reference('无法核对所选形态条目，旧内容已清除。');return False
        keep=self._view_key==(scope,selected)
        self.result=deepcopy(result);self._render(selected,preserve=keep)
        if not keep:self.tabs.setCurrentWidget(self.player)
        return True

    def refresh_reference(self):
        # Source loss discards identity: recovery alone cannot refill the reader.
        if self.identity is None:return False
        result=self._query(self.identity)
        if not _validated(result,self.identity):
            self.clear_reference('形态与转换资料暂时无法核对，旧内容与图片已清除。');return False
        scope=(self.identity,json.dumps(result['source_identity'],sort_keys=True,separators=(',',':')))
        if scope!=self.scope_key:
            self.clear_reference('资料版本已变化，旧选择已清除；请重新手动打开。');return False
        return self.set_reference(self.identity,result)
