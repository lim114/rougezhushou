"""Read-only public node directory, including unknown and historical references."""
from copy import deepcopy
from functools import lru_cache
import json
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QLineEdit,
    QLabel,QListWidget,QListWidgetItem,QPlainTextEdit,QSplitter,QPushButton,QCheckBox)
from . import node_catalog as catalog
from .ui_state import replace_text

KINDS={'event':'事件','battle':'战斗资料','function':'功能节点','original':'未归类原文'}
ROLES={'display_option_reference':'选择参考','explanatory_text':'说明参考',
       'community_navigation_guide':'导航参考'}
CATEGORIES={'normal':'普通','emergency':'紧急','boss':'首领','pursuit':'追猎',
            'event':'事件内战斗','special':'特殊挑战','resident':'居民战斗'}


def floor_text(floors):
    return '、'.join(f'第{n}层' for n in floors) if floors else '层数资格未知'


def map_conditions(graph,run_config):
    from .run_config import config_data,difficulty_value
    zones=config_data()['zones'];zone=zones.get((graph or {}).get('zone_id'),{})
    icon=zone.get('zoneIconId');floor=next((n for n in range(1,7) if icon==f'zone_{n}'),None)
    special=bool(zone.get('isHiddenZone')) or not zone
    return {'floor':None if special else floor,'special_region':special,
            'difficulty':difficulty_value((run_config or {}).get('difficulty'))}


@lru_cache(maxsize=64)
def event_text(event_id):
    result=catalog.event_details(event_id);event=result['event']
    lines=[event['title'],f"类型：{'、'.join(event['node_types']) or '特殊传送来源'}",
           f"公开层数参考：{floor_text(event['floors'])}",
           '游戏内当前能否进入、按钮是否可选：未知。下列是固定资料中的流程，不能据此自动选择。']
    rewards={r['choice_id']:r for r in catalog.event_reward_options(event_id)['rows']}
    scenes=result['rows']; numbers={s['key']:n for n,s in enumerate(scenes,1)}
    for number,scene in enumerate(scenes,1):
        lines += ['',f'场景 {number}',scene['description']]
        lines.extend(scene.get('edesc_texts',[]))
        for choice in scene['choices']:
            role=ROLES.get(choice['presentation_role'],'展示参考（不是已证按钮）')
            lines += [f"  {role}：{choice['title']}",f"    {choice.get('description') or '结果说明未知'}"]
            if choice.get('conditional'):lines.append(f"    条件：{choice['conditional']}")
            targets=choice.get('destination_keys',[])
            lines.append('    后续：'+('、'.join(f'场景 {numbers[t]}' for t in targets if t in numbers)
                          if targets else '资料无导航目标，游戏后续未知'))
            for sub in choice.get('subchoices',[]):
                name=(sub.get('parts') or ['名称未知'])[0]
                target=sub.get('community_destination_scene_id')
                destination=f'场景 {numbers[target]}' if target in numbers else '后续未知'
                lines.append(f'    子选择参考：{name} → {destination}')
            reward=rewards.get(choice['key'],{})
            for reference in reward.get('rewards',[]):
                lines.append('    有证具名奖励：'+str(reference.get('reward',{}).get('name') or reference.get('description') or '见来源原文'))
            if reward.get('rewards'):lines.append('    完整奖励池、数量和领取资格尚未核验。')
    unlinked=result.get('unlinked_original_scenes',[])
    if unlinked:
        lines += ['','同名原始场景的来源链尚未归类（不能认定从入口可达）：']
        for scene in unlinked:lines.append(f"  {scene.get('description') or scene.get('title') or scene['id']}")
    lines += ['',result['notice'],'来源覆盖：固定社区目录；原始未归类场景另列，不声称当前服务器完整。']
    sources=result['sources'].values() if isinstance(result['sources'],dict) else result['sources']
    for source in sources:
        if isinstance(source,dict):lines.append(str(source.get('url') or source.get('source_url') or source))
    return '\n'.join(lines)


class NodeCatalogPanel(QWidget):
    stageSelected=Signal(str)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.dossier=None;self.node_context=None;self.entries=[];self.detail_key=None
        layout=QVBoxLayout(self)
        self.context_label=QLabel('公开目录：不要求打开游戏，也不提供生成概率。')
        self.context_label.setWordWrap(True);layout.addWidget(self.context_label)
        controls=QHBoxLayout()
        self.kind=QComboBox();self.kind.addItem('全部公开内容',None)
        for key,label in KINDS.items():self.kind.addItem(label,key)
        self.node_type=QComboBox();self.node_type.addItem('全部节点类型',None)
        types=sorted({t for e in catalog.all_events(include_indirect=True)['rows'] for t in e['node_types']}
                     | {'作战','紧急作战','险路恶敌','险路尽头','“居民”据点','羽瞰点','曲折密道','林间空地','诡意行商','秘境行商','应急助力'})
        for t in types:self.node_type.addItem(t,t)
        self.floor=QComboBox();self.floor.addItem('全部层数参考',None)
        for f in range(1,7):self.floor.addItem(f'第{f}层',f)
        self.search=QLineEdit();self.search.setPlaceholderText('搜索事件名、正文或选项')
        for w in (self.kind,self.node_type,self.floor,self.search):controls.addWidget(w)
        layout.addLayout(controls)
        actions=QHBoxLayout();self.bind_button=QPushButton('查看地图所选节点');self.bind_button.setEnabled(False)
        self.all_button=QPushButton('回到公开目录');actions.addWidget(self.bind_button);actions.addWidget(self.all_button)
        self.status=QLabel();self.status.setWordWrap(True);actions.addWidget(self.status,1);layout.addLayout(actions)
        split=QSplitter();self.list=QListWidget();self.list.setAccessibleName('节点所有可能内容分支')
        split.addWidget(self.list);right=QWidget();rl=QVBoxLayout(right)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);rl.addWidget(self.detail,1)
        self.battle_button=QPushButton('查看对应固定战斗地图');self.battle_button.setEnabled(False)
        rl.addWidget(self.battle_button);split.addWidget(right);split.setStretchFactor(1,3);layout.addWidget(split,1)
        for control in (self.kind,self.node_type,self.floor):control.currentIndexChanged.connect(self.refresh)
        self.search.textChanged.connect(self.refresh)
        self.list.currentItemChanged.connect(lambda *_:self.show_selected())
        self.bind_button.clicked.connect(self.bind_current_node);self.all_button.clicked.connect(self.show_directory)
        self.battle_button.clicked.connect(self.select_stage)
        self.refresh()

    def set_node(self,graph,node_id,floor=None,difficulty=None,special_region=False):
        """Receive a copy only; periodic sampling never switches the user's mode."""
        self.node_context=(deepcopy(graph),node_id,{'floor':floor,'difficulty':difficulty,'special_region':special_region}) if node_id else None
        self.bind_button.setEnabled(self.node_context is not None)
        if self.dossier is not None:
            if self.node_context:self.bind_current_node()
            else:self.show_directory()

    def bind_current_node(self):
        if not self.node_context:return
        graph,key,conditions=self.node_context
        try:self.dossier=catalog.node_dossier(graph,key,**conditions)
        except (ValueError,TypeError,KeyError) as error:
            self.status.setText(str(error));return
        p=self.dossier['position'];row=p.get('row');col=p.get('col')
        self.context_label.setText(f'地图所选节点：第{row+1}行、第{col+1}列' if type(row) is int and type(col) is int else '地图所选节点')
        self.refresh()

    def show_directory(self):
        self.dossier=None;self.context_label.setText('公开目录：不要求打开游戏，也不提供生成概率。');self.refresh()

    def _entries(self):
        nt=self.node_type.currentData();floor=self.floor.currentData();kind=self.kind.currentData()
        if self.dossier is not None:
            events=self.dossier['rows'];battles=self.dossier.get('battle_rows',[]);functions=self.dossier.get('function_rows',[])
            originals=[]
        else:
            events=catalog.all_events(node_type=nt,include_indirect=True)['rows']
            if floor is not None:events=[e for e in events if not e['floors'] or floor in e['floors']]
            battles=catalog.battle_candidates(node_type=nt,floor=floor,context='all')['rows'] if nt is None or nt in ('作战','紧急作战','险路恶敌','不期而遇','诡意行商','狭路相逢','“居民”据点') else []
            functions=catalog.function_nodes(node_type=nt)['rows']
            originals=[{'id':str(item.get('id') or index),
                        'title':f"未归类原文 · {item.get('title') or item.get('id') or index}",
                        'record':item} for index,item in enumerate(catalog.original_references()['rows'])]
        entries=[]
        for category,rows in (('event',events),('battle',battles),('function',functions),('original',originals)):
            if kind and kind!=category:continue
            for r in rows:
                title=r.get('title') or r.get('name') or r.get('node_type') or r.get('id')
                key=str(r.get('id') or r.get('stage_id') or r.get('node_type'))
                if category=='event':text=event_text(r['id']) if self.search.text().strip() else title
                else:text=json.dumps(r,ensure_ascii=False)
                if self.search.text().strip().casefold() not in text.casefold():continue
                entries.append({'kind':category,'key':category+':'+key,'title':title,'record':r})
        return entries

    def refresh(self,*_):
        current=self.list.currentItem();selected=current.data(Qt.ItemDataRole.UserRole) if current else None
        scroll=self.list.verticalScrollBar().value()
        try:entries=self._entries()
        except (ValueError,TypeError,KeyError) as error:self.status.setText(str(error));return
        self.entries=entries;self.list.blockSignals(True);self.list.clear()
        selected_index=None
        for index,e in enumerate(entries):
            item=QListWidgetItem(f"【{KINDS[e['kind']]}】{e['title']}");item.setData(Qt.ItemDataRole.UserRole,e['key']);self.list.addItem(item)
            if e['key']==selected:selected_index=index
        self.list.setCurrentRow(selected_index if selected_index is not None else 0 if entries else -1)
        self.list.verticalScrollBar().setValue(scroll if selected_index is not None else 0)
        self.list.blockSignals(False);self.status.setText(f'{len(entries)}条来源参考；实际资格未知。');self.show_selected()

    def show_selected(self):
        item=self.list.currentItem();key=item.data(Qt.ItemDataRole.UserRole) if item else None
        entry=next((e for e in self.entries if e['key']==key),None)
        self.battle_button.setEnabled(bool(entry and entry['kind']=='battle'))
        if not entry:text='没有符合筛选的资料。不能把资料缺失视为不可能出现。'
        elif entry['kind']=='event':text=event_text(entry['record']['id'])
        elif entry['kind']=='function':
            r=entry['record'];text=r['node_type']+'\n\n'+'\n\n'.join(x.get('description_text','')+'\n'+x.get('url','') for x in r.get('references',[]))
            for ref in r.get('extra_condition_references',[]):text+='\n\n'+str(ref.get('description_text') or ref.get('text') or ref)
            text+='\n\n功能资料不证明当前解锁/实际状态；林间空地没有当前事件，过去内容单独保留。'
        elif entry['kind']=='battle':
            r=entry['record'];text=f"{entry['title']}\n\n类别：{'、'.join(CATEGORIES.get(t,t) for t in r.get('categories',[]))}\n层数：{floor_text(r.get('floors'))}\n关卡版本：{r.get('id') or r.get('stage_id')}\n"
            text+='\n'.join(r.get('notes',[]))+'\n实际出现/分支/出怪全局时钟：未知。此项仅连接到对应固定地图资料。'
        else:text='未归类原始资料，尚不能连接为完整可达事件链。\n\n'+json.dumps(entry['record']['record'],ensure_ascii=False,indent=2)
        if self.dossier:
            text+='\n\n当前节点读取与过去记忆分别保留；事件候选不表示实际进入。'
            for name,label in (('current_content','当前读取'),('history_content','过去读取')):
                value=self.dossier.get(name)
                if value:text+=f'\n{label}：'+str(value.get('title') or value.get('identity_status') or '有资料但身份未知')
            hist=self.dossier.get('history_events',[])
            if hist:text+='\n过去类型的候选：'+'、'.join(e['title'] for e in hist)
        replace_text(self.detail,text,preserve=self.detail_key==key);self.detail_key=key

    def select_stage(self):
        item=self.list.currentItem()
        if not item:return
        entry=next((e for e in self.entries if e['key']==item.data(Qt.ItemDataRole.UserRole)),None)
        if entry and entry['kind']=='battle':self.stageSelected.emit(entry['record'].get('id') or entry['record']['stage_id'])
