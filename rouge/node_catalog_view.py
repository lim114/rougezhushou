"""Read-only public node directory, including unknown and historical references."""
from copy import deepcopy
from functools import lru_cache
import json
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QLineEdit,
    QLabel,QTreeWidget,QTreeWidgetItem,QPlainTextEdit,QSplitter,QPushButton,QCheckBox)
from . import node_catalog as catalog
from . import event_planning
from .battle_reward_planning import stage_reward_sources,reward_source_text
from .ui_state import replace_text
from .stage_context import stage_context_text

KINDS={'event':'事件','battle':'战斗资料','function':'功能节点','original':'未归类原文','map':'本图节点'}
QUALIFICATIONS={'matched':'已列条件相符','unknown':'资格未确认','excluded':'已列条件不符'}
ROLES={'display_option_reference':'选择参考','explanatory_text':'说明参考',
       'community_navigation_guide':'导航参考'}
CATEGORIES={'normal':'普通','emergency':'紧急','boss':'首领','pursuit':'追猎',
            'event':'事件内战斗','special':'特殊挑战','resident':'居民战斗'}
RESOURCE_NAMES={'hp':'目标生命值','max_hp':'目标生命值上限','gold':'源石锭',
                'hope':'希望','shield':'护盾','ap':'行动力'}
BUDGETS={True:'覆盖已列费用',False:'不足已列费用',None:'预算未知'}
SCRAP_CATEGORIES={'MOVE':'加工品','GOODS':'自然物','PASSIVE':'概念体',None:'零件'}


def resource_reference_lines(reference):
    """Format declared amounts without claiming payment or changing eligibility."""
    kind=reference['kind'];amount=reference.get('quantity_reference')
    source=reference.get('source_match') or '见原文'
    lines=[]
    if kind in ('nominal_cost','nominal_gain_or_recovery'):
        name=RESOURCE_NAMES[reference['resource']]
        label='费用参考' if kind=='nominal_cost' else '增量或回复参考'
        lines.append(f'{label}：{source}；明确数量 {amount}{name}。')
        if kind=='nominal_cost':
            value=reference.get('resource_value_declared')
            held=f'声明资源 {value}{name}' if value is not None else '资源数量未声明'
            lines.append(f"名义预算：{BUDGETS[reference['nominal_budget_covers']]}；{held}。")
            if reference.get('minimum_retained_hp_reference'):
                lines.append(f"最低保留参考：{reference['minimum_retained_hp_reference']}目标生命值；特殊扣除规则未证，实际费用未知。")
    elif kind=='fraction_cost':
        value=reference.get('fraction_arithmetic_reference')
        arithmetic=str(value) if value is not None else '未知（资源数量未声明）'
        lines += [f'费用参考：{source}；比例 1/2；算术参考 {arithmetic}。',
                  '名义预算：预算未知；实际整数费用和取整规则未证。']
    elif kind in ('category_item_cost','random_category_item_gain'):
        category=SCRAP_CATEGORIES[reference['scrap_category']]
        if kind=='category_item_cost':
            coverage=BUDGETS[reference['nominal_budget_covers']]
            complete='有关零件数量声明完整' if reference['inventory_complete_declared'] else '有关零件数量不完整'
            lines += [f'物品费用参考：{source}；{amount}件{category}。',
                      f"名义预算：{coverage}；已声明数量小计 {reference['known_owned_subtotal']}件，{complete}。"]
        else:lines.append(f'随机物品增量参考：{source}；{amount}件{category}；实际物品与完整奖励池未知。')
    elif kind=='named_item_cost':
        lines += [f"物品费用参考：{reference['item_name']} × {amount}；{source}。",
                  f"名义预算：{BUDGETS[reference['nominal_budget_covers']]}；实际消耗未知。"]
    return lines


def scene_outcome_lines(result):
    if not result.get('current_rule_applicable'):return []
    observation=event_planning.current_observation()
    source=result['current_document_source'];lines=[
        '版本警示：本场景的旧版流程与较新文档条件不同。',
        f"固定旧版 {result['fixed_old_catalog_revision']}：{observation['old_rule']}",
        f"较新文档 {source['revision']}：{observation['current_rule']}",
        '进入前条件：需要独立的进入前持有快照及犬植浆来源；当前持有不能替代。']
    for row in result['rows']:
        reward=f"{row['item_name']} × {row['quantity']}" if row['outcome']=='named_relic' else f"{row['quantity']}行动力"
        lines.append(f"当前文档分支参考：{reward}；{QUALIFICATIONS[row['status']]}；{row['source_condition']}。")
    lines += ['实际领取：未知；未证当前服务器脚本。仅此场景有较新文档观察，整份目录仍保留固定旧版范围。',
              '当前条件来源：'+source['url']]
    return lines


def choice_requirement_lines(check):
    state='相符' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
    lines=['条件核对：'+state+'；'+check['source_text']]
    reference=check.get('description_condition_reference')
    if reference:
        source=reference['sources']['current_event_document']
        lines += [f"持有门原ID：{reference['required_item_id']}；仅判断持有，不认定消耗或实际可选。",
            f"文字条件来源：固定427904与较新{source['revision']}已对照；"+source['url']]
        ids=reference.get('original_content_reference_ids') or [reference['record_id']]
        lines.append('同值原选项文字：'+'、'.join(ids)+'；该文字佐证不补来源入口链。')
    return lines

def known_node_type(value):
    return value if isinstance(value,str) and value and not value.startswith(('未知','类型未确认')) else None


def original_scene_reference(content):
    """Use an exact declaration or the existing same-frame unique read contract."""
    if not isinstance(content,dict) or content.get('kind')!='event':return None
    declarations=[content[k] for k in ('original_scene_id','scene_id') if content.get(k) is not None]
    if any(not isinstance(key,str) for key in declarations) or len(set(declarations))>1:return None
    declared=declarations[0] if declarations else None
    if declared and declared not in catalog._original()['scenes']:return None
    candidates=content.get('scene_candidates')
    observed=None
    if (content.get('source')=='same_frame_selected_node' and content.get('identity_status')=='visible_scene'
            and isinstance(candidates,list) and len(candidates)==1 and isinstance(candidates[0],str)
            and catalog._original()['scenes'].get(candidates[0],{}).get('title')==content.get('title')):
        observed=candidates[0]
    if observed and declared and observed!=declared:return None
    if observed:return observed,'同帧唯一原场景候选（实际实例仍待核验）'
    if declared:return declared,'声明原场景ID对应（身份仍须核验）'
    return None


class CatalogTree(QTreeWidget):
    """Grouped visible tree, with stable flat-entry selection for existing callers."""
    def __init__(self):
        super().__init__();self.setHeaderHidden(True);self.flat=[];self.groups={}

    def clear(self):
        super().clear();self.flat=[];self.groups={}

    def add_entry(self,text,key,group):
        parent=self.groups.get(group)
        if parent is None:
            parent=QTreeWidgetItem([group]);self.addTopLevelItem(parent);self.groups[group]=parent
        item=QTreeWidgetItem(parent,[text]);item.setData(0,Qt.ItemDataRole.UserRole,key)
        self.flat.append(item);return item

    def setCurrentRow(self,index,expand=True):
        item=self.flat[index] if 0<=index<len(self.flat) else None
        self.setCurrentItem(item)
        if item and expand:item.parent().setExpanded(True)

    def selected_key(self):
        item=self.currentItem();return item.data(0,Qt.ItemDataRole.UserRole) if item else None

    def expanded_groups(self):return {name for name,item in self.groups.items() if item.isExpanded()}


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
    return _event_flow_text(event_id)


def event_details_text(event_id,context=None):
    """Read-only scene/choice planning using declarations supplied by the caller."""
    return _event_flow_text(event_id,context=context,planning=True)


def _event_flow_text(event_id,context=None,planning=False):
    result=catalog.event_details(event_id);event=result['event']
    lines=[event['title'],f"类型：{'、'.join(event['node_types']) or '特殊传送来源'}",
           f"公开层数参考：{floor_text(event['floors'])}",
           '游戏内当前能否进入、按钮是否可选：未知。下列是固定资料中的流程，不能据此自动选择。']
    if planning:
        lines += ['资源参考：顶层原文明示数量单独列出；预算与资格分别判断，实际变化未知。',
                  '流程来源：固定旧版427904；较新末舞条件在对应场景标明，不声称当前完整覆盖。']
    rewards={r['choice_id']:r for r in catalog.event_reward_options(event_id)['rows']}
    scenes=result['rows']; numbers={s['key']:n for n,s in enumerate(scenes,1)}
    for number,scene in enumerate(scenes,1):
        lines += ['',f'场景 {number}',scene['description']]
        lines.extend(scene.get('edesc_texts',[]))
        resources={r['choice_key']:r for r in event_planning.choice_resources(event_id,scene['key'],context)['rows']} if planning else {}
        if planning:lines.extend(scene_outcome_lines(event_planning.scene_outcomes(event_id,scene['key'],context)))
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
            if planning:
                row=resources[choice['key']];qualification=row['choice_eligibility']
                lines.append('    已列选项条件：'+QUALIFICATIONS[qualification['status']]+'；服务器是否可选仍未知。')
                for check in qualification['parsed_special_requirements']:
                    lines.extend('    '+line for line in choice_requirement_lines(check))
                references=row['resource_references']
                if not references:lines.append('    资源数量：未识别顶层明确数量；不能视为零费用或零收益。')
                for reference in references:
                    lines.extend('    '+line for line in resource_reference_lines(reference))
                conversion=row.get('ap_conversion_reference')
                if conversion:
                    gain=conversion['hope_gain_reference']
                    lines.append('    FINAL转换参考：每1行动力对应1希望；'+
                        (f'声明余AP得到{gain}希望参考' if gain is not None else '余AP未声明，转换量未知')+'；实际领取未知。')
                if qualification.get('edition_warnings'):
                    lines.append('    旧版导航参考：本场景有版本差异，请对照上方较新条件；当前按钮与后续尚未核验。')
                if qualification.get('unparsed_condition_text'):
                    lines.append('    未解析条件：'+qualification['unparsed_condition_text'])
                lines += ['    未解析边界：完整效果未证；上方结果原文保留，括号内藏品效果不自动计即时增减。',
                          '    预算不足只表示已列费用覆盖不足，不改变事件资格，不认定服务器隐藏或禁用选项。']
    unlinked=result.get('unlinked_original_scenes',[])
    if unlinked:
        lines += ['','同名原始场景的来源链尚未归类（不能认定从入口可达）：']
        for scene in unlinked:lines.append(f"  {scene.get('description') or scene.get('title') or scene['id']}")
    lines += ['',result['notice'],'来源覆盖：固定社区目录；原始未归类场景另列，不声称当前服务器完整。']
    sources=result['sources'].values() if isinstance(result['sources'],dict) else result['sources']
    for source in sources:
        if isinstance(source,dict):lines.append(str(source.get('url') or source.get('source_url') or source))
    return '\n'.join(lines)


def special_original_text(record_id,context=None):
    result=event_planning.original_entry_qualification(record_id,context);reference=result['reference']
    if reference is None:
        raw=result['record'];destination=raw.get('nextSceneId')
        lines=['来源入口仍未知；nextSceneId只证明目的地，不反推来源场景。']
        if destination:lines.append('原件目的地：'+destination)
        if result.get('documented_choice_requirements'):
            lines.append('原选项已列持有条件：'+QUALIFICATIONS[result['documented_choice_requirements_status']])
            for check in result['documented_choice_requirements']:lines.extend(choice_requirement_lines(check))
            lines.append('该条件结果不证明本原选项属于当前事件入口；未加入普通节点自然候选。')
        lines.append('当前服务器资格与完整可达链：未知。')
        return '\n'.join(lines)
    kind=reference['kind'];lines=['特殊入口资料：'+QUALIFICATIONS[result['status']],
        '来源绑定：'+('直接指针或完整差分原文已证' if result['source_scene_link_verified'] else '公开候选库身份相符；原sourceScene指针仍未证'),
        '实际当前展示/进入/服务器资格：未知；未加入普通地图自然候选。']
    if kind=='portal_entry_variant':
        lines += ['固定目录入口：'+reference['source_community_scene'],
            '原场景：'+reference['source_scene_id']+' · '+reference['label'],
            '直接文字依据：共同入口前缀与下列明确差分句组合后，和原description逐字相等：',
            reference['explicit_clause'],'同色多个原ID仍分别保留；没有按ID数字或后缀挑选当前实例。',
            '加工品稀有度对应初始秘境AP、自然出现脚本与13个拒绝差分的源场景仍未知。']
    else:
        lines += ['来源阶段：开始探索时的行动奖励；上一局通过区域数不是当前层数或最高抵达层号。',
            '常规初始候选库：6项中随机展示3项；候选库不是本次展示全集。',
            '襁褓羽蛇的额外蓝色支援：1项，实际选中/显示哪项未知。']
        if kind=='startup_legacy_extra':
            lines += ['继承LEGACY原ID：'+reference['legacy_id']+'；同名羽蛇的六种原ID不能合并。',
                '原force_add_choice参数：choice_id='+record_id+'；scene_ids='+reference['source_scene_id'],
                '原件路径：'+reference['source_path'],
                '当前持有的襁褓生灵不能替代上一局继承来源；缺独立继承记录时继续未知。']
        elif kind=='startup_regular_pool':lines.append('仅按公开候选标题唯一对应原choice；没有原件sourceScene指针，不能冒称该指针已证。')
    for check in result['checks']:
        state='相符' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
        lines.append('条件核对：'+state+'；'+check['source_text'])
    sources=result['special_entry_sources']
    lines += ['固定社区目录427904与本次独立在线433770/434599规则观察分开；不是当前完整目录替换。',
        '原件来源：'+sources['original']['url'],'固定差分来源：'+sources['fixed_community']['url']]
    if kind!='portal_entry_variant':
        lines.extend('独立规则来源：'+row['url'] for row in sources['online_independent_rules'])
    return '\n'.join(lines)


class NodeCatalogPanel(QWidget):
    stageSelected=Signal(str)
    mapNodeSelected=Signal(str,object)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.dossier=None;self.node_context=None;self.entries=[];self.detail_key=None
        self.map_context=None;self.runtime_context={};self._first_tree=True
        layout=QVBoxLayout(self)
        self.context_label=QLabel('公开目录以自然入口核对已列条件；特殊事件原文仍保留，不代表当前可进入，不提供生成概率。')
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
        self.map_button=QPushButton('浏览本图节点');self.map_button.setEnabled(False);actions.addWidget(self.map_button)
        self.expand_button=QPushButton('展开');self.collapse_button=QPushButton('收起')
        actions.addWidget(self.expand_button);actions.addWidget(self.collapse_button)
        self.status=QLabel();self.status.setWordWrap(True);actions.addWidget(self.status,1);layout.addLayout(actions)
        split=QSplitter();self.list=CatalogTree();self.list.setAccessibleName('节点类型与资格分支')
        split.addWidget(self.list);right=QWidget();rl=QVBoxLayout(right)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);rl.addWidget(self.detail,1)
        self.battle_button=QPushButton('查看对应固定战斗地图');self.battle_button.setEnabled(False)
        self.event_stage=QComboBox();self.event_stage.setAccessibleName('事件选项对应作战资料');rl.addWidget(self.event_stage)
        self.map_location=QComboBox();self.map_location.setAccessibleName('该内容对应地图节点');rl.addWidget(self.map_location)
        self.map_jump=QPushButton('在地图预览定位节点');self.map_jump.setEnabled(False);rl.addWidget(self.map_jump)
        self.map_contents=QPushButton('查看此节点事件与作战');self.map_contents.setEnabled(False);rl.addWidget(self.map_contents)
        rl.addWidget(self.battle_button);split.addWidget(right);split.setStretchFactor(1,3);layout.addWidget(split,1)
        for control in (self.kind,self.node_type,self.floor):control.currentIndexChanged.connect(self.refresh)
        self.search.textChanged.connect(self.refresh)
        self.list.currentItemChanged.connect(lambda *_:self.show_selected())
        self.bind_button.clicked.connect(self.bind_current_node);self.all_button.clicked.connect(self.show_directory)
        self.battle_button.clicked.connect(self.select_stage)
        self.expand_button.clicked.connect(self.list.expandAll);self.collapse_button.clicked.connect(self.list.collapseAll)
        self.map_button.clicked.connect(self.show_map_nodes);self.map_jump.clicked.connect(self.select_map_node)
        self.map_contents.clicked.connect(self.show_map_entry_contents)
        self.refresh()

    def set_map_context(self,graph,conditions=None,epoch=None,historical=True,runtime_context=None):
        incoming=(deepcopy(graph),deepcopy(conditions or {}),epoch,bool(historical)) if graph else None
        changed=incoming!=self.map_context or (runtime_context or {})!=self.runtime_context
        self.map_context=incoming;self.runtime_context=deepcopy(runtime_context or {})
        self.map_button.setEnabled(bool(incoming))
        if changed:self.refresh()

    def show_map_nodes(self):
        self.dossier=None;self.kind.setCurrentIndex(self.kind.findData('map'))
        self.context_label.setText('本图节点按类型分类；当前读取与历史分开，定位只改变助手预览。');self.refresh()

    def _event_context(self,event=None):
        context=deepcopy(self.runtime_context)
        context.update(node_type=self.node_type.currentData(),floor=self.floor.currentData(),entry_mode='natural')
        if self.dossier and self.node_context:
            graph,key,conditions=self.node_context;context.update(conditions)
            node=next((n for n in graph.get('nodes',[]) if n['id']==key),{})
            if event and event.get('historical_read_reference'):
                # Today's inventory/gold and a passed clearing cannot establish
                # what was owned, paid, or selectable at this historical reading.
                context=deepcopy(conditions)
                previous=known_node_type(node.get('remembered_type'))
                context.update(node_type=previous if previous in event['node_types'] else None,
                    entry_mode='content',reference_context_scope='historical_title_reference_only')
                return context
            context['node_type']=known_node_type(node.get('observed_type'))
            content=self.dossier.get('current_content') or {}
            if event and content.get('kind')=='event' and content.get('title')==event['title']:
                context['entry_mode']='content'
        return context

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
        if self.kind.currentData()=='map':
            self.kind.blockSignals(True);self.kind.setCurrentIndex(0);self.kind.blockSignals(False)
        p=self.dossier['position'];row=p.get('row');col=p.get('col')
        position=f'第{row+1}行、第{col+1}列' if type(row) is int and type(col) is int else '位置未确认'
        self.context_label.setText('地图所选节点：'+position+'；使用节点类型及所属层数，目录类型/层数筛选已停用。')
        self.refresh()

    def show_directory(self):
        self.dossier=None
        if self.kind.currentData()=='map':
            self.kind.blockSignals(True);self.kind.setCurrentIndex(0);self.kind.blockSignals(False)
        self.context_label.setText('公开目录以自然入口核对已列条件；特殊事件原文仍保留，不代表当前可进入，不提供生成概率。');self.refresh()

    def _entries(self):
        nt=self.node_type.currentData();floor=self.floor.currentData();kind=self.kind.currentData()
        if kind=='map':
            if not self.map_context:return []
            graph,conditions,epoch,historical=self.map_context;rows=[]
            for node in graph.get('nodes',[]):
                label=node.get('observed_type') or '类型未确认'
                if nt and label!=nt:continue
                content=node.get('content') or {};title=f"第{node['row']+1}行、第{node['col']+1}列 · {label}"
                if content.get('title'):title+=' · '+content['title']
                if self.search.text().strip().casefold() not in json.dumps(node,ensure_ascii=False).casefold():continue
                rows.append({'kind':'map','key':f"map:{epoch}:{graph.get('zone_id')}:{graph.get('template_id')}:{node['id']}",
                    'title':title,'record':deepcopy(node),'group':label,'map_binding':{
                        'epoch':epoch,'zone_id':graph.get('zone_id'),'template_id':graph.get('template_id'),
                        'row':node['row'],'col':node['col'],'node_id':node['id']}})
            return rows
        if self.dossier is not None:
            events=[*self.dossier['rows'],*self.dossier.get('history_observed_event_rows',[])]
            battles=[*self.dossier.get('battle_rows',[]),*self.dossier.get('history_observed_battle_rows',[])]
            functions=[*self.dossier.get('function_rows',[]),*self.dossier.get('history_observed_function_rows',[])]
            originals=[]
        else:
            events=catalog.all_events(node_type=nt,include_indirect=True)['rows']
            if floor is not None:events=[e for e in events if not e['floors'] or floor in e['floors']]
            battle_result=catalog.battle_candidates(node_type=nt,floor=floor,context='all',entry_mode='natural') if nt is None or nt in ('作战','紧急作战','险路恶敌','不期而遇','诡意行商','狭路相逢','“居民”据点') else {'rows':[],'excluded':[]}
            battles=[*battle_result['rows'],*({**r,'entry_condition_excluded_reference':True} for r in battle_result['excluded'])]
            functions=catalog.function_nodes(node_type=nt)['rows']
            originals=[{'id':str(item.get('id') or index),
                        'title':f"原文 · {item.get('title') or item.get('id') or index} · {item['record_id']}",
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
                entry={'kind':category,'key':category+':'+key,'title':title,'record':r}
                if r.get('historical_read_reference'):
                    entry['key']+=':historical_read';entry['history_read']=True
                if category=='event':
                    entry['qualification']=event_planning.event_eligibility(r['id'],self._event_context(r))
                    entry['group']=' / '.join(r['node_types']) or '特殊入口'
                    entry['group']=('历史已读内容 · '+entry['group'] if entry.get('history_read') else entry['group']+' · '+QUALIFICATIONS[entry['qualification']['status']])
                elif category=='function':entry['group']=('历史已读类型 · ' if entry.get('history_read') else '')+r['node_type']
                elif category=='battle':
                    reference=r.get('entry_context_reference')
                    label=reference['label'] if reference else ' / '.join(CATEGORIES.get(t,t) for t in r.get('categories',[]))
                    prefix='历史已读内容 · ' if entry.get('history_read') else '已列条件排除 · ' if r.get('entry_condition_excluded_reference') else ''
                    entry['group']=prefix+label+' · 战斗资料'
                else:
                    reference=r['record'].get('special_entry_reference')
                    entry['group']=('特殊入口原文 · 来源身份已证' if reference['source_scene_link_verified'] else '初始候选原文 · 源场景未证') if reference else '未归类原文 · 入口未知'
                entries.append(entry)
        return entries

    def refresh(self,*_):
        bound=self.dossier is not None
        self.node_type.setEnabled(not bound)
        self.floor.setEnabled(not bound and self.kind.currentData()!='map')
        self.node_type.setToolTip('绑定节点时使用它的类型；返回公开目录后可筛选。' if bound else '')
        self.floor.setToolTip('本图或绑定节点使用记录的所属层数；返回公开目录后可筛选。' if not self.floor.isEnabled() else '')
        selected=self.list.selected_key();expanded=self.list.expanded_groups()
        scroll=self.list.verticalScrollBar().value()
        try:entries=self._entries()
        except (ValueError,TypeError,KeyError) as error:self.status.setText(str(error));return
        self.entries=entries;self.list.blockSignals(True);self.list.clear()
        selected_index=None
        for index,e in enumerate(entries):
            self.list.add_entry(f"【{KINDS[e['kind']]}】{e['title']}",e['key'],e['group'])
            if e['key']==selected:selected_index=index
        self.list.setCurrentRow(selected_index if selected_index is not None else 0 if entries else -1,expand=False)
        # Qt may reveal the selected child by expanding its parent. Restore the
        # reader's branches after selection, including while the widget is shown.
        for name,item in self.list.groups.items():item.setExpanded(self._first_tree or name in expanded)
        self._first_tree=False
        self.list.verticalScrollBar().setValue(scroll if selected_index is not None else 0)
        self.list.blockSignals(False);self.status.setText(f'{len(entries)}条来源参考；同类型全集不是当前可发生全集，实际资格未知。');self.show_selected()

    def show_selected(self):
        key=self.list.selected_key()
        entry=next((e for e in self.entries if e['key']==key),None)
        previous=self.event_stage.itemData(self.event_stage.currentIndex(),Qt.ItemDataRole.UserRole+1)
        previous_location=self.map_location.currentData();self.event_stage.clear()
        self.map_location.clear();self.map_jump.setEnabled(False)
        self.map_contents.setEnabled(bool(entry and entry['kind']=='map'))
        if entry and entry['kind']=='event':
            result=event_planning.event_battle_links(entry['record']['id'],context=self._event_context(entry['record']))
            for row in result['rows']:
                status=QUALIFICATIONS[row['choice_eligibility']['status']]
                for number,stage in enumerate(row['preview_stage_candidates'],1):
                    difficulty={'NORMAL':'普通','FOUR_STAR':'紧急'}.get(stage['difficulty'],'难度未确认')
                    self.event_stage.addItem(f"{row['choice_title']} → {stage['name']} · {difficulty} · {status} · 资料候选{number}",stage['stage_id'])
                    self.event_stage.setItemData(self.event_stage.count()-1,
                        [row['scene_key'],row['choice_key'],stage['stage_id']],Qt.ItemDataRole.UserRole+1)
                pool=row.get('generic_pool_requirement') or {}
                for number,stage in enumerate(pool.get('fixed_named_pool',[]),1):
                    difficulty={'NORMAL':'普通','FOUR_STAR':'紧急'}.get(stage['difficulty'],'难度未确认')
                    self.event_stage.addItem(f"{row['choice_title']} → {stage['title']} · {difficulty} · {status} · 下一主层固定资料候选{number}",stage['id'])
                    self.event_stage.setItemData(self.event_stage.count()-1,
                        [row['scene_key'],row['choice_key'],stage['id'],'generic_next_floor'],Qt.ItemDataRole.UserRole+1)
            if previous:
                self.event_stage.setCurrentIndex(next((i for i in range(self.event_stage.count())
                    if self.event_stage.itemData(i,Qt.ItemDataRole.UserRole+1)==previous),0))
        self.event_stage.setVisible(bool(entry and entry['kind']=='event'))
        self.battle_button.setEnabled(bool(entry and (entry['kind']=='battle' or self.event_stage.count())))
        if not entry:text='没有符合筛选的资料。不能把资料缺失视为不可能出现。'
        elif entry['kind']=='event':
            q=entry['qualification'];text=event_details_text(entry['record']['id'],self._event_context(entry['record']))
            if entry.get('history_read'):
                text=('历史已读取内容；不证明当时已进入或选择了某个选项。\n'
                    '当前持有与资源不用于推定当时资格/费用；下方为固定选项及作战预览。\n\n'+text)
            text+='\n\n资料出现条件：'+QUALIFICATIONS[q['status']]+'；当前服务器资格仍未知。'
            text+='\n'+'\n'.join(('相符' if c['matches'] is True else '不符' if c['matches'] is False else '未知')+'：'+c['source_text'] for c in q['checks'])
            context=self._event_context(entry['record'])
            for scene in catalog.event_details(entry['record']['id'])['rows']:
                for choice in event_planning.choice_eligibility(entry['record']['id'],scene['key'],context)['rows']:
                    if choice['conditional_text']:
                        text+='\n选项 '+choice['choice_title']+'：'+QUALIFICATIONS[choice['status']]+'；'+choice['conditional_text']
            if self.event_stage.count():text+='\n作战入口见下方选择：仅固定资料预览，不代表实际触发或确定选中该变体。'
            for row in result['rows']:
                pool=row.get('generic_pool_requirement')
                if pool:
                    floor=pool['next_main_floor_reference']
                    text+='\n下一主层作战：'+(f'第{floor}层固定来源候选可预览' if pool['fixed_named_pool'] else '下一主层或固定池未确认，无可绑定关卡')+'；完整服务器池与实际选择未知。'
        elif entry['kind']=='map':
            graph,conditions,epoch,historical=self.map_context;r=entry['record']
            dossier=catalog.node_dossier(graph,r['id'],**conditions)
            text=entry['title']+'\n'+('历史地图记录' if historical else '当前匹配地图记录')+'；显示的是观测与资料，不操作游戏。'
            for name,label in (('observed_type','当前类型'),('remembered_type','过去类型'),('template_type','模板类型')):
                text+='\n'+label+'：'+str(r.get(name) or '未确认')
            for name,label in (('content','当前内容'),('remembered_content','过去内容')):
                if r.get(name):text+='\n'+label+'：'+str(r[name].get('title') or '身份尚未唯一确认')
            for content in r.get('content_history') or []:text+='\n历史读取：'+str(content.get('title') or '未确认')
            text+='\n\n固定事件资料（按已列条件分区）：'
            context=deepcopy(self.runtime_context);context.update(conditions,node_type=known_node_type(r.get('observed_type')),entry_mode='natural')
            for event in dossier['rows']:
                event_context=deepcopy(context)
                if (r.get('content') or {}).get('kind')=='event' and (r.get('content') or {}).get('title')==event['title']:
                    event_context['entry_mode']='content'
                qualification=event_planning.event_eligibility(event['id'],event_context)
                text+='\n  '+event['title']+'：'+QUALIFICATIONS[qualification['status']]
            text+='\n\n固定战斗资料：'+'、'.join(s['title'] for s in dossier['battle_rows'])
            for function in dossier['function_rows']:
                text+='\n\n功能 '+function['node_type']+'：'
                text+='\n'.join(ref.get('description_text','') for ref in function.get('references',[]))
            if dossier['history_events']:text+='\n\n过去类型/内容的事件资料：'+'、'.join(e['title'] for e in dossier['history_events'])
            text+='\n已读取的历史内容有独立分支入口；过去类型候选不能当作已发生事件。'
            text+='\n同类型资料不是当前可发生全集；出现资格须按前置、持有及服务器条件另外核验。'
            self.map_location.addItem(entry['title'],entry['map_binding']);self.map_jump.setEnabled(True)
        elif entry['kind']=='function':
            r=entry['record'];text=r['node_type']+'\n\n'+'\n\n'.join(x.get('description_text','')+'\n'+x.get('url','') for x in r.get('references',[]))
            for ref in r.get('extra_condition_references',[]):text+='\n\n'+str(ref.get('description_text') or ref.get('text') or ref)
            text+='\n\n功能资料不证明当前解锁/实际状态；林间空地没有当前事件，过去内容单独保留。'
        elif entry['kind']=='battle':
            r=entry['record'];text=f"{entry['title']}\n\n类别：{'、'.join(CATEGORIES.get(t,t) for t in r.get('categories',[]))}\n层数：{floor_text(r.get('floors'))}\n关卡版本：{r.get('id') or r.get('stage_id')}\n"
            text+='\n'.join(r.get('notes',[]))+'\n实际出现/分支/出怪全局时钟：未知。此项仅连接到对应固定地图资料。'
            text+='\n\n'+stage_context_text(r.get('entry_context_reference'))
            if r.get('entry_condition_excluded_reference'):
                text+='\n此条为已列条件排除的资料参考；仍可预览原图，不作为当前候选。'
            text+='\n\n'+reward_source_text(stage_reward_sources(r.get('id') or r.get('stage_id')))
        else:
            raw=entry['record']['record']
            text=special_original_text(raw['record_id'],self.runtime_context)+'\n\n完整原文与字段：\n'+json.dumps(raw,ensure_ascii=False,indent=2)
        if entry and entry.get('history_read') and entry['kind']!='event':
            text='历史已读取内容或类型；以下仅原件参考，不代表当前节点仍有此功能或作战。\n\n'+text
        if entry and entry['kind']!='map' and self.map_context:
            graph,_,epoch,_=self.map_context
            for node in graph.get('nodes',[]):
                if self.dossier and self.node_context:
                    bound_graph,bound_id,_=self.node_context
                    if (node['id']!=bound_id or any(graph.get(k)!=bound_graph.get(k)
                            for k in ('zone_id','template_id'))):continue
                records=[node.get('content'),node.get('remembered_content'),*(node.get('content_history') or [])]
                match=any(isinstance(r,dict) and r.get('title')==entry['title'] and r.get('kind')==entry['kind'] for r in records)
                if entry['kind']=='original':
                    raw=entry['record']['record'];reference=raw.get('special_entry_reference')
                    original_match=next((identity for r in records if (identity:=original_scene_reference(r))
                        and identity[0]==raw['record_id']),None)
                    match=bool(reference and reference['kind']=='portal_entry_variant' and original_match)
                if entry['kind']=='function':match=entry['title'] in (node.get('observed_type'),node.get('remembered_type'))
                if match:
                    binding={'node_id':node['id'],'row':node['row'],'col':node['col'],'epoch':epoch,
                        'zone_id':graph.get('zone_id'),'template_id':graph.get('template_id')}
                    source_label='当前/过去已读取类型对应' if entry['kind']=='function' else '当前/历史标题对应（同名身份仍须核验）'
                    if entry['kind']=='original':source_label=original_match[1]
                    self.map_location.addItem(f"第{node['row']+1}行、第{node['col']+1}列 · {source_label}",binding)
            self.map_jump.setEnabled(bool(self.map_location.count()))
        if previous_location:
            self.map_location.setCurrentIndex(next((i for i in range(self.map_location.count())
                if self.map_location.itemData(i)==previous_location),0 if self.map_location.count() else -1))
        if self.dossier:
            text+='\n\n当前节点读取与过去记忆分别保留；事件候选不表示实际进入。'
            for name,label in (('current_content','当前读取'),('history_content','过去读取')):
                value=self.dossier.get(name)
                if value:text+=f'\n{label}：'+str(value.get('title') or value.get('identity_status') or '有资料但身份未知')
            hist=self.dossier.get('history_events',[])
            if hist:text+='\n过去类型的候选：'+'、'.join(e['title'] for e in hist)
        replace_text(self.detail,text,preserve=self.detail_key==key);self.detail_key=key

    def select_stage(self):
        key=self.list.selected_key()
        entry=next((e for e in self.entries if e['key']==key),None)
        if entry and entry['kind']=='battle':self.stageSelected.emit(entry['record'].get('id') or entry['record']['stage_id'])
        elif entry and entry['kind']=='event' and self.event_stage.currentData():self.stageSelected.emit(self.event_stage.currentData())

    def select_map_node(self):
        binding=self.map_location.currentData()
        if binding:self.mapNodeSelected.emit(binding['node_id'],deepcopy(binding))

    def show_map_entry_contents(self):
        key=self.list.selected_key();entry=next((e for e in self.entries if e['key']==key),None)
        if not entry or entry['kind']!='map' or not self.map_context:return
        graph,conditions,_,_=self.map_context
        self.set_node(graph,entry['record']['id'],**conditions);self.bind_current_node()
