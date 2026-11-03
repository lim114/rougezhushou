"""Manual fixed main-queue group/package reader; never chooses game results."""
from copy import deepcopy
import json,re
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QPushButton,QPlainTextEdit,QTabWidget)
from . import spawn_candidates as candidates
from .player_node_information import _plain
from .ui_state import replace_text
from .view_catalog import SubjectPicture

NOTICE=('这里只查阅固定主出场队列的候选资料。候选组与关联包分开阅读；'
        '不代表本局选中了哪项、出现次数或概率，也不能据关联包断定成员同时出现。')
KINDS={'group':'候选组','package':'关联包'}


def _name(value,fallback):
    text=_plain(value)if type(value)is str else''
    if not text or re.search(r'https?://|(?:enemy|trap|act|action|route|wave|fragment)_[A-Za-z0-9_]+',text):return fallback
    return text


def _relation_label(row):
    return _name(row.get('display_label'),'尚未取得名称的'+KINDS[row['kind']])


def _member_label(number,row):
    label=_name(row.get('type_label'),'记录类型未确认')
    name=_name(row.get('display_name'),'具体名称未取得')
    return f'条目{number} · {label} · {name}'


def candidate_text(packet,relation=None,member=None):
    lines=[_name(packet.get('stage_name'),'固定战斗资料'),NOTICE,'']
    lines.append('【查阅范围】')
    lines.append('当前主队列条目涉及的候选资料。'if packet['origin_action_id']is not None else'本关固定主队列的资料目录。')
    if relation is None:
        return'\n'.join(lines+['请选择候选组或关联包，再手动选择一条记录。',
            '尚未选择具体记录；没有改变战斗预览的筛选、地图选点或敌人。'])
    lines+=['','【'+KINDS[relation['kind']]+'】',_relation_label(relation),
        f"这份关系资料列出{len(relation['members'])}条源记录；这是记录数，不是实际敌人数。"]
    if relation['kind']=='group':
        lines.append('这些是这组资料中的候选记录；本局选中哪项、选择次数和概率：尚未确认。')
    else:
        lines.append('关联包只是原资料的关系标记；不能据此断定成员同时出现、全部采用或实际生成数量。')
    if member is None:return'\n'.join(lines+['','请在上方手动选择一条记录，查看它的类型与具体来源。'])
    lines+=['','【所选记录】',_name(member.get('type_label'),'记录类型未确认')+'：'+_name(member.get('display_name'),'名称未取得')]
    count=member.get('declared_count')
    if type(count)is int and count>=0:
        lines.append(f'本条计划记录的数量：{count}；这是单条源参数，不等于本局实际数量，也不与其它候选相加。')
    else:lines.append('本条计划记录的数量尚未确认；不能推算实际生成数量。')
    if member['action_type']=='SPAWN':
        enemies=member['enemy_references']
        names=list(dict.fromkeys(_name(row.get('name'),'敌人名称未取得')for row in enemies))
        lines+=['','【敌人资料】','、'.join(names)if names else'此条尚未与本关固定敌人参数对应。']
        if len(enemies)>1:lines.append('本关有多份同名敌人配置，当前条目尚不能唯一对应；原引用编号保留在资料与依据，不能当作敌人的精英档次。')
        if member['spawn_reference']is not None:
            lines.append('已找到这条源记录对应的固定路线与唯一敌人参数；可手动在战斗预览中查看。')
        else:lines.append('敌人参数或固定路线未能唯一对应，暂不提供战斗预览跳转。')
    elif member['action_type']=='ACTIVATE_PREDEFINED':
        ref=member['predefined_reference'];status=(ref or{}).get('status')
        lines+=['','【预置目标资料】']
        if status=='empty_key':lines.append('原记录没有指定激活目标；这与“空动作”不同，不能任选一个物件代替。')
        elif status=='ambiguous_alias':lines.append('同一别名对应多项预置资料，尚不能唯一确认要激活哪一项。')
        elif status=='unresolved_alias':lines.append('原别名尚未与本关预置对象对应，目标与位置仍未知。')
        elif status=='exact_alias':
            objects=ref['objects']
            lines.append('原别名与本关预置对象已对应；这是固定资料，尚未确认本局激活或实际位置。')
            for obj in objects:
                lines.append('预置对象：'+_name(obj.get('name'),'未取得中文名称的场景对象')+'。')
                cell=obj.get('display_cell')
                if type(cell)is dict and type(cell.get('row'))is int and type(cell.get('col'))is int:
                    lines.append(f"资料格点：第{cell['row']+1}行、第{cell['col']+1}列；不表示本局物件当前就在这里。")
            lines.append('不会借用敌人头像，也不把预置对象当作普通敌人出怪条目跳转。')
        else:lines.append('预置目标资料尚未确认；不借用其它条目的头像或坐标。')
    elif member['action_type']=='EMPTY':
        lines+=['','这是空动作记录，不生成敌人；仍保留其在候选组或关联包中的原始位置。']
    else:lines+=['','此动作类型仅保留固定原文，不从相邻记录推断目标、位置或效果。']
    lines+=['','【仍未确认】','本局是否选中、实际出现或激活、生成数量、绝对时间与当前服务器行为：均未知。',
        '权重、原键、完整动作和来源身份放在“资料与依据”，不会由此生成概率或路线建议。']
    return'\n'.join(lines)


class SpawnCandidatesPanel(QDialog):
    spawnReferenceSelected=Signal(object)
    sourceInvalidated=Signal()
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle('固定候选组与关联包资料');self.setModal(False);self.resize(900,680)
        self.stage_id=None;self.origin_action_id=None;self.scope_key=None;self.packet=None
        self._view_key=None;self._manual_identity=None;self._picture_identity=None
        layout=QVBoxLayout(self);self.notice=QLabel(NOTICE);self.notice.setWordWrap(True);layout.addWidget(self.notice)
        row=QHBoxLayout();self.relation_kind=QComboBox();self.relation_kind.setAccessibleName('候选组与关联包分支')
        for key,name in KINDS.items():self.relation_kind.addItem(name,key)
        self.relation=QComboBox();self.relation.setAccessibleName('完整主队列关系资料');self.relation.setPlaceholderText('请选择候选组或关联包')
        row.addWidget(self.relation_kind);row.addWidget(self.relation,1);layout.addLayout(row)
        self.member=QComboBox();self.member.setAccessibleName('关系中的完整源条目');self.member.setPlaceholderText('请选择具体记录');layout.addWidget(self.member)
        for control in(self.relation,self.member):
            control.setMinimumContentsLength(12);control.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.picture=SubjectPicture(edge=88);layout.addWidget(self.picture);self.picture.hide()
        self.reading_tabs=QTabWidget();self.player_text=QPlainTextEdit();self.source_text=QPlainTextEdit()
        for reader,label in((self.player_text,'候选资料说明'),(self.source_text,'资料与依据')):
            reader.setReadOnly(True);reader.setAccessibleName('出怪候选 · '+label);self.reading_tabs.addTab(reader,label)
        layout.addWidget(self.reading_tabs,1)
        self.open_spawn_button=QPushButton('在战斗预览中查看这条资料');self.open_spawn_button.setEnabled(False);layout.addWidget(self.open_spawn_button)
        self.relation_kind.currentIndexChanged.connect(self._kind_changed)
        self.relation.currentIndexChanged.connect(self._relation_changed)
        self.member.currentIndexChanged.connect(self.refresh_reference)
        self.open_spawn_button.clicked.connect(self.open_selected_spawn)
        self.refresh_reference()

    @staticmethod
    def _populate(control,rows,selected):
        control.blockSignals(True)
        try:
            control.clear()
            for label,key in rows:control.addItem(label,key)
            control.setCurrentIndex(control.findData(selected)if type(selected)is str else-1)
        finally:control.blockSignals(False)

    def _clear_picture(self):
        self.picture.set_subject(None,None,'');self.picture.hide();self._picture_identity=None

    def _invalidate(self,message,*,notify=False):
        self.packet=None;self._view_key=None;self._manual_identity=None
        self._populate(self.relation,[],None);self._populate(self.member,[],None)
        self._clear_picture();self.open_spawn_button.setEnabled(False)
        for reader in(self.player_text,self.source_text):replace_text(reader,message,preserve=False)
        if notify:self.sourceInvalidated.emit()

    def set_reference(self,stage_id,origin_action_id=None,*,scope_key=None):
        context=(stage_id,origin_action_id,scope_key)
        if context!=(self.stage_id,self.origin_action_id,self.scope_key):
            self._invalidate('尚未选择要查阅的关系与具体记录。',notify=True);self.reading_tabs.setCurrentIndex(0)
        self.stage_id=stage_id;self.origin_action_id=origin_action_id;self.scope_key=deepcopy(scope_key)
        self.refresh_reference()

    def _query(self):
        if self.stage_id is None:return None
        return(candidates.stage_reference(self.stage_id)if self.origin_action_id is None
            else candidates.action_reference(self.stage_id,self.origin_action_id))

    @staticmethod
    def _source_key(packet):
        return(packet['stage_id'],packet['origin_action_id'],packet['scope_key'],deepcopy(packet['source_identity']))

    def _kind_changed(self,*_):
        self._populate(self.relation,[],None);self._populate(self.member,[],None);self._view_key=None
        self.refresh_reference()

    def _relation_changed(self,*_):
        self._populate(self.member,[],None);self._view_key=None;self.refresh_reference()

    def _selected(self):
        if not self.packet:return None,None
        kind=self.relation_kind.currentData();rows=self.packet['groups']if kind=='group'else self.packet['packages']if kind=='package'else[]
        relation=next((row for row in rows if row['reference_id']==self.relation.currentData()),None)
        member=next((row for row in relation['members']if row['reference_id']==self.member.currentData()),None)if relation else None
        return relation,member

    def _show_picture(self,member):
        refs=(member or{}).get('enemy_references',[])
        ids={r['id']for r in refs if r.get('source_role')=='fixed_stage_enemy_reference'}
        valid=bool(member and member['action_type']=='SPAWN'and refs and len(ids)==1
            and all(r.get('source_role')=='fixed_stage_enemy_reference'and r['id']in ids for r in refs))
        if not valid:self._clear_picture();return
        identity=next(iter(ids));name=_name(refs[0].get('name'),'已核对的敌人资料')
        self.picture.set_subject('enemy',identity,name+' · 固定资料头像');self.picture.show();self._picture_identity=identity

    def refresh_reference(self,*_):
        selected_relation=self.relation.currentData();selected_member=self.member.currentData()
        old_source=self._source_key(self.packet)if self.packet else None
        try:packet=self._query()
        except(OSError,ValueError,TypeError,KeyError,IndexError):packet=None
        if(not packet or packet.get('status')!='documented_reference'or packet.get('source_valid')is not True
            or packet.get('stage_id')!=self.stage_id or packet.get('origin_action_id')!=self.origin_action_id):
            self._invalidate('候选资料暂时无法核对；旧关系、条目、头像与跳转已清除。请稍后手动重新选择。',
                notify=self.stage_id is not None or self.packet is not None or self._view_key is not None);return
        source=self._source_key(packet)
        if old_source is not None and old_source!=source:
            self._invalidate('资料身份已变化；旧选择已清除，请重新选择。',notify=True);selected_relation=selected_member=None;self.reading_tabs.setCurrentIndex(0)
        self.packet=packet;kind=self.relation_kind.currentData()
        relations=packet['groups']if kind=='group'else packet['packages']if kind=='package'else[]
        self._populate(self.relation,[(_relation_label(row),row['reference_id'])for row in relations],selected_relation)
        relation=next((row for row in relations if row['reference_id']==self.relation.currentData()),None)
        members=relation['members']if relation else[]
        self._populate(self.member,[(_member_label(i,row),row['reference_id'])for i,row in enumerate(members,1)],selected_member)
        relation,member=self._selected()
        key=(deepcopy(source),deepcopy(self.scope_key),kind,relation['reference_id']if relation else None,member['reference_id']if member else None)
        same=self._view_key==key
        self._manual_identity=deepcopy(key)if member else None;self._show_picture(member)
        self.open_spawn_button.setEnabled(bool(member and member['action_type']=='SPAWN'and member['spawn_reference']is not None and type(member['token'])is dict))
        replace_text(self.player_text,candidate_text(packet,relation,member),preserve=same)
        technical={'stage_id':self.stage_id,'origin_action_id':self.origin_action_id,'scope_key':packet['scope_key'],
            'source_identity':packet['source_identity'],'selected_relation':relation,'selected_member':member,
            'source':packet['source'],'source_file':packet['source_file'],
            'all_main_queue_groups':packet['groups'],'all_main_queue_packages':packet['packages'],
            'selected_action':packet['selected_action'],'notice':packet['notice'],'actual_selection':None,'probabilities':None}
        replace_text(self.source_text,json.dumps(technical,ensure_ascii=False,indent=2),preserve=same);self._view_key=deepcopy(key)

    def open_selected_spawn(self):
        relation,member=self._selected()
        if not relation or not member or member['action_type']!='SPAWN'or member['spawn_reference']is None:return False
        token=deepcopy(member['token']);selected=(relation['reference_id'],member['reference_id'])
        try:resolved=candidates.resolve_reference(token)
        except(OSError,ValueError,TypeError,KeyError,IndexError):resolved=None
        if(not resolved or resolved['stage_id']!=self.stage_id or resolved['origin_action_id']!=self.origin_action_id
            or resolved['scope_key']!=self.packet['scope_key']or resolved['source_identity']!=self.packet['source_identity']
            or resolved['token']!=token or resolved['relation']['reference_id']!=selected[0]
            or resolved['member']['reference_id']!=selected[1]or resolved['member']['spawn_reference']is None):
            self._invalidate('所选资料未能重新核对；旧条目、头像和跳转已清除，请重新选择。',notify=True);return False
        self.refresh_reference();relation,member=self._selected()
        if(not relation or not member or(relation['reference_id'],member['reference_id'])!=selected
            or member['token']!=resolved['token']):return False
        self.spawnReferenceSelected.emit(deepcopy(resolved['token']));return True
