"""Local pictures and evidence-backed groups; never changes calculation inputs."""
import json
from functools import lru_cache
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

DATA=Path(__file__).with_name('data')
PROFESSIONS={'pioneer':'先锋','warrior':'近卫','tank':'重装','sniper':'狙击',
             'caster':'术师','medic':'医疗','support':'辅助','special':'特种'}
ENEMY_TIERS={'NORMAL':'普通','ELITE':'精英','BOSS':'领袖'}
STAGE_GROUPS=('floor_1','floor_2','floor_3','floor_4','floor_5','hidden','unconfirmed')


@lru_cache(maxsize=1)
def view_catalog():
    return json.loads((DATA/'view-catalog.json').read_text(encoding='utf-8'))


def portrait_record(kind,identity):
    if kind=='profession':return profession_catalog()['professions'].get(identity)
    if kind=='skill':
        data=skill_catalog();entry=data['skills'].get(identity) or {}
        return data['images'].get(entry.get('image'))
    group={'operator':'operators','enemy':'enemies'}.get(kind)
    if group is None:return None
    entry=view_catalog()[group].get(identity) or {}
    return view_catalog()['images'].get(entry.get('portrait'))


@lru_cache(maxsize=256)
def _picture(filename,edge):
    pixmap=QPixmap(str(DATA/filename))
    return pixmap.scaled(edge,edge,Qt.AspectRatioMode.KeepAspectRatio,
                         Qt.TransformationMode.SmoothTransformation) if not pixmap.isNull() else pixmap


def portrait_icon(kind,identity):
    record=portrait_record(kind,identity)
    return QIcon(_picture(record['file'],32)) if record else QIcon()


@lru_cache(maxsize=1)
def skill_catalog():
    return json.loads((DATA/'skill-icons.json').read_text(encoding='utf-8'))


def skill_icon(identity):
    return portrait_icon('skill',identity)


@lru_cache(maxsize=1)
def profession_catalog():
    return json.loads((DATA/'profession-icons.json').read_text(encoding='utf-8'))


def profession_icon(identity):
    return portrait_icon('profession',identity)


def profession_branch_icons():
    return {label:profession_icon(key) for key,label in PROFESSIONS.items()}


def add_groups(combo,groups,placeholder=None):
    """Headings are not selectable and cannot masquerade as a data entry."""
    combo.clear()
    if placeholder is not None:combo.addItem(placeholder,None)
    first=None
    for heading,items in groups:
        if not items:continue
        combo.addItem('── '+heading+' ──',None)
        item=combo.model().item(combo.count()-1)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled & ~Qt.ItemFlag.ItemIsSelectable)
        item.setData(True,Qt.ItemDataRole.UserRole+1)
        for title,data,icon in items:
            combo.addItem(icon,title,data)
            if first is None:first=combo.count()-1
    combo.setCurrentIndex(0 if placeholder is not None else first if first is not None else -1)
    combo.setIconSize(QSize(28,28));combo.setMaxVisibleItems(24)


def operator_groups(profiles,implemented):
    counts={p['name']:sum(v['name']==p['name'] for v in profiles.values()) for p in profiles.values()}
    groups=[]
    for profession,label in PROFESSIONS.items():
        entries=sorted(((key,p) for key,p in profiles.items() if p['profession']==profession),
                       key=lambda v:(v[0] not in implemented,v[1]['name'],v[0]))
        items=[]
        for key,p in entries:
            title=p['name']+(' · '+p['subprofession'] if counts[p['name']]>1 else '')
            title+='（培养档案）' if key not in implemented else ''
            items.append((title,key,portrait_icon('operator',key)))
        groups.append((label,items))
    return groups


def stage_groups(stages):
    metadata=view_catalog()['stages'];groups=[]
    for group in STAGE_GROUPS:
        entries=[(sid,s) for sid,s in stages.items() if metadata[sid]['group']==group]
        totals={}
        for _,s in entries:
            key=(s['name'],s['difficulty']);totals[key]=totals.get(key,0)+1
        seen={};items=[]
        for sid,s in entries:
            key=(s['name'],s['difficulty']);seen[key]=seen.get(key,0)+1
            title=s['name']+' · '+('紧急' if s['difficulty']=='FOUR_STAR' else '普通')
            if totals[key]>1:title+=' · 同名资料'+str(seen[key])
            items.append((title,sid,QIcon()))
        if entries:groups.append((metadata[entries[0][0]]['label'],items))
    return groups


def enemy_groups(enemies,data_for):
    groups=[]
    for tier in (*ENEMY_TIERS,None):
        entries=[e for e in enemies if (e['level_type'] if e['level_type'] in ENEMY_TIERS else None)==tier]
        items=[(e['name']+' · 引用等级'+str(e['level']),data_for(e),portrait_icon('enemy',e['id'])) for e in entries]
        groups.append((ENEMY_TIERS.get(tier,'类别未确认'),items))
    return groups


class SubjectPicture(QWidget):
    """A small reference portrait, with an explicit missing-picture state."""
    def __init__(self,parent=None,*,edge=76):
        super().__init__(parent)
        self.key=None
        layout=QHBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        self.edge=edge;self.image=QLabel();self.image.setFixedSize(edge,edge)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profession=QLabel();self.profession.setFixedSize(26,26);self.profession.hide()
        self.caption=QLabel();self.caption.setWordWrap(True)
        layout.addWidget(self.image);layout.addWidget(self.profession);layout.addWidget(self.caption,1)
        self.set_subject(None,None,'')

    def set_subject(self,kind,identity,title):
        key=(kind,identity,title)
        if key==self.key:return
        self.key=key;record=portrait_record(kind,identity) if kind and identity else None
        self.image.clear();self.caption.setText(title)
        self.profession.clear();self.profession.hide()
        if kind=='operator' and identity:
            profession=view_catalog()['operators'].get(identity,{}).get('profession')
            job=portrait_record('profession',profession) if profession else None
            if job:
                self.profession.setPixmap(_picture(job['file'],26));self.profession.show()
                self.profession.setAccessibleName(PROFESSIONS[profession]+'职业图标')
                self.profession.setToolTip(PROFESSIONS[profession]+'职业图标\n'+job['url'])
        self.setAccessibleName(title)
        if record:
            pixmap=_picture(record['file'],self.edge)
            if not pixmap.isNull():
                self.image.setPixmap(pixmap)
                self.setToolTip(('技能图标；按技能ID及原始iconId对应。\n' if kind=='skill' else
                                '资料头像；不代表当前装扮、精英形态或实战状态。\n')+record['url']+
                                '\n游戏图片版权归鹰角网络。')
                return
        self.image.setText('图片未取得' if identity else '')
        self.setToolTip('此引用未取得对应图片；不借用其他单位的图片。' if identity else '')
