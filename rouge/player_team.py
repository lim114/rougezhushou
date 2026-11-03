"""Read-only recruited roster; account facts and unresolved flags never fill gaps."""
from .catalog import operator_profiles,catalog
from .record_flags import active_record,projected_run_metadata
from .view_catalog import PROFESSIONS,portrait_icon,profession_icon,skill_icon
import math

def qualified_fields(record, profile):
    fields={k:v for k,v in record.get('fields',{}).items()if k not in record.get('invalid_fields',[])}
    phases=profile.get('phases',[])
    elite=fields.get('elite')
    if type(elite)is not int or not 0<=elite<len(phases):fields.pop('elite',None)
    cap=phases[elite]['max_level']if 'elite'in fields else max((p['max_level']for p in phases),default=0)
    for key,low,high in [('level',1,cap),('potential',1,6),('selected_skill',1,len(profile.get('skills',[]))),('module_level',0,3)]:
        value=fields.get(key)
        if type(value)is not int or not low<=value<=high:fields.pop(key,None)
    trust=fields.get('trust')
    if type(trust)not in(int,float)or not 0<=trust<=100:fields.pop('trust',None)
    if fields.get('module_id')is not None and not any(m['id']==fields['module_id']for m in profile.get('modules',[])):
        fields.pop('module_id',None);fields.pop('module_level',None)
    if fields.get('module_id')is None and fields.get('module_level',0)>0:
        fields.pop('module_id',None);fields.pop('module_level',None)
    return fields

def crew_rows(state):
    profiles=operator_profiles();rows=[]
    for identity,raw in state.get('operators',{}).items():
        if not isinstance(raw,dict)or raw.get('scope')=='account'or not active_record(raw,'present'):continue
        record=projected_run_metadata(raw);profile=profiles.get(identity,{})
        fields=qualified_fields(record,profile)
        rows.append({'id':identity,'name':profile.get('name')or record.get('name')or'姓名待核对','profession':profile.get('profession'),'profile':profile,'record':record,'fields':fields,'calculable':identity in catalog()['operators']})
    return rows

def crew_text(row):
    f=row['fields'];r=row['record'];p=row['profile']
    def value(key,suffix=''):
        x=f.get(key);return str(x)+suffix if type(x)in(int,float)else'未读到'
    labels=[row['name']+' · '+PROFESSIONS.get(row['profession'],'职业未确认'),'本局培养（只读）','精英阶段：'+value('elite'),'等级：'+value('level'),'潜能：'+value('potential'),'信赖加成进度：'+value('trust','%')]
    advanced=r.get('advanced');labels+=['本局进阶：'+('已进阶'if advanced is True else'未进阶'if advanced is False else'未确认')]
    labels+=['招募来源：'+{'emergency_hire':'应急雇佣（已读标记）','non_emergency':'非应急雇佣（已读标记）'}.get(r.get('recruitment_kind'),'未确认')]
    module=f.get('module_id');entry=next((m for m in p.get('modules',[])if m['id']==module),None)
    labels+=['模组：'+(entry['name']if entry else'未装备'if module is None and 'module_id'in f else'名称未核对'if module else'未读到')+'；阶段：'+value('module_level')]
    selected=f.get('selected_skill');labels+=['所选技能：'+((p['skills'][selected-1]['levels'][0].get('name')or'名称未核对')if selected is not None else'未读到'),'','已读技能等级']
    for i,skill in enumerate(p.get('skills',[]),1):
        rank=r.get('skill_ranks',{}).get(str(i));rank=None if str(i)in r.get('invalid_skill_ranks',[])else rank
        text='专精'+{8:'一',9:'二',10:'三'}[rank]if type(rank)is int and rank in(8,9,10)else'等级'+str(rank)if type(rank)is int and 1<=rank<=7 else'未读到'
        name=(skill.get('levels')or[{}])[0].get('name')or f'第{i}技能';labels.append(name+'：'+text)
    labels+=['','信赖按属性加成进度显示，100%封顶；不把它冒充游戏信赖总进度。','未读信息不会用账号详情补齐；这是最近培养记录，不代表所有藏品加成已核对或本局实际面板。']
    return '\n'.join(labels)

from PySide6.QtCore import Qt,QSize,Signal
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QTabWidget,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton
class TeamPanel(QWidget):
    openOperator=Signal(str)
    def __init__(self,run,parent=None):
        super().__init__(parent);self.run=run;self.rows={};self.key=None;body=QVBoxLayout(self)
        self.notice=QLabel();self.notice.setWordWrap(True);body.addWidget(self.notice);self.tabs=QTabWidget();body.addWidget(self.tabs,1);self.lists={}
        for key,label in[(None,'总览（已招募）'),*PROFESSIONS.items(),('unknown','职业待确认')]:
            widget=QListWidget();widget.setIconSize(QSize(48,48));self.tabs.addTab(widget,profession_icon(key)if key in PROFESSIONS else portrait_icon('operator',''),label);self.lists[key]=widget;widget.currentItemChanged.connect(self.selected)
        self.tabs.currentChanged.connect(self.selected);self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1);self.skills=QListWidget();self.skills.setIconSize(QSize(30,30));self.skills.setMaximumHeight(125);body.addWidget(self.skills);self.calculate=QPushButton('查看这名干员的本局计算');self.calculate.clicked.connect(self.open_selected);body.addWidget(self.calculate);self.refresh()
    def refresh(self):
        rows=crew_rows(self.run.state);key=repr(rows)
        if key==self.key:return
        self.key=key;old={k:w.currentItem().data(Qt.ItemDataRole.UserRole)if w.currentItem()else None for k,w in self.lists.items()};positions={k:w.verticalScrollBar().value()for k,w in self.lists.items()};self.rows={r['id']:r for r in rows}
        for k,w in self.lists.items():
            w.blockSignals(True);w.clear()
            for row in rows:
                if k is not None and(k=='unknown'and row['profession']in PROFESSIONS or k!='unknown'and row['profession']!=k):continue
                picture=portrait_icon('operator',row['id']);item=QListWidgetItem(picture,row['name']+' · '+PROFESSIONS.get(row['profession'],'职业未确认')+(' · 图片待补'if picture.isNull()else''));item.setData(Qt.ItemDataRole.UserRole,row['id']);w.addItem(item)
                if row['id']==old[k]:w.setCurrentItem(item)
            w.verticalScrollBar().setValue(positions[k]);w.blockSignals(False)
        count=self.run.state.get('crew_count');self.notice.setText(f'已确认在队{len(rows)}名。'+(f'已读队伍总数{count}名；缺少的成员仍待读取。'if type(count)is int and count>len(rows)else'名单是否完整仍需队伍页面证据。')+'仅本局记录，未知和已离队不混入总览；头像和职业来自固定资料。')
        self.selected()
    def selected(self,*_):
        item=self.tabs.currentWidget().currentItem();row=self.rows.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        text=crew_text(row)if row else'选择已招募干员查看本局培养；不展示白值或代填未读信息。'
        if self.detail.toPlainText()!=text:
            self.detail.setPlainText(text);self.skills.clear()
            for index,skill in enumerate(row['profile'].get('skills',[])if row else[],1):
                name=skill['levels'][0]['name'];self.skills.addItem(QListWidgetItem(skill_icon(skill['id']),name+(' · 当前所选'if row['fields'].get('selected_skill')==index else'')))
        self.calculate.setVisible(bool(row and row['calculable']))
    def open_selected(self):
        item=self.tabs.currentWidget().currentItem();row=self.rows.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        if row and row['calculable']:self.openOperator.emit(row['id'])
