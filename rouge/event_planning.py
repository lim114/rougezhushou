"""Source-bound event requirements and choice-to-fixed-battle references.

Three-state checks concern documented rules in declared conditions. They never
promote a match into actual server eligibility or infer entry scripts from NEXT.
"""
from copy import deepcopy
from functools import lru_cache
import json,re
from pathlib import Path
from . import node_catalog as catalog


@lru_cache(maxsize=1)
def reference_data():
    return json.loads((Path(__file__).with_name('data')/'event-planning-reference.json').read_text(encoding='utf-8'))


def _reference():
    reference=reference_data();source=catalog._data()['sources']['cached_community_catalog']
    if reference['sources']['event_catalog_dom']['sha256']!=source['sha256']:
        raise ValueError('事件目录原件已变化；资格和关卡链接资料必须重新绑定，不能复用旧组编号。')
    return reference


def _and(*values):return False if False in values else None if None in values else True
def _or(*values):return True if True in values else None if None in values else False
def _not(value):return None if value is None else not value


def _context(context):
    if context is None:context={}
    if not isinstance(context,dict):raise ValueError('事件条件需要对象。')
    context=deepcopy(context)
    catalog._floor(context.get('floor'),context.get('special_region',False))
    catalog._difficulty(context.get('difficulty'))
    if context.get('node_type') is not None:catalog._text(context['node_type'],'节点类型')
    if context.get('entry_mode','unknown') not in ('unknown','natural','content','processed_item'):
        raise ValueError('入口上下文需要unknown、natural、content或processed_item。')
    if context.get('movement_item_id') is not None:catalog._text(context['movement_item_id'],'移动加工品')
    quantities=context.get('item_quantities',{})
    if not isinstance(quantities,dict) or any(not isinstance(k,str) or not k or type(v) is not int or v<0 for k,v in quantities.items()):
        raise ValueError('持有数量需要原物品ID到非负整数的对象。')
    if type(context.get('inventory_complete',False)) is not bool:raise ValueError('inventory_complete需要布尔值。')
    gold=context.get('gold')
    if gold is not None and (type(gold) is not int or gold<0):raise ValueError('源石锭需要非负整数或留空。')
    history=context.get('event_history',{})
    if not isinstance(history,dict):raise ValueError('事件历史需要按目录事件ID分组的对象。')
    valid={e['id'] for e in catalog._data()['events']}
    for key,row in history.items():
        if key not in valid or not isinstance(row,dict):raise ValueError('事件历史ID不存在或状态不是对象。')
        for field in ('encountered','visited','entered'):
            if row.get(field) is not None and type(row[field]) is not bool:raise ValueError('历史状态需要布尔值或留空。')
    return context


def _owned(context,item_id):
    quantities=context.get('item_quantities',{})
    if item_id in quantities:return quantities[item_id]>0
    return False if context.get('inventory_complete',False) else None


def _named_item(name):
    matches=_reference()['named_required_items'].get(name,[])
    return matches[0] if len(matches)==1 else None


def _event_id(title):
    matches=[e['id'] for e in catalog._data()['events'] if e['title']==title]
    return matches[0] if len(matches)==1 else None


def _history(context,title,field):
    key=_event_id(title)
    return None if key is None else context.get('event_history',{}).get(key,{}).get(field)


def _check(key,matches,text,*,kind='requirement',**details):
    return {'key':key,'matches':matches,'source_text':text,'kind':kind,**details}


def _status(checks):
    values=[row['matches'] for row in checks]
    return 'excluded' if False in values else 'unknown' if None in values or not values else 'matched'


def _result(**values):
    data=_reference()
    return {'sources':deepcopy(data['sources']),'scope':'documented_rules_in_declared_context',
            'actual_server_eligible':None,'game_entry_script_verified':False,'inventory_updated':False,
            'matched_meaning':'仅已列出的资料条件相符，不表示当前必然生成或选项必然可选。',
            'limits':deepcopy(data['limits']),**values}


def _event_checks(event,context):
    checks=[];node_type=context.get('node_type');floor=context.get('floor')
    checks.append(_check('documented_node_type',None if node_type is None else node_type in event['node_types'],
                         '目录节点类型：'+' / '.join(event['node_types']),kind='catalog_scope'))
    matches=None if floor is None or context.get('special_region',False) or not event['floors'] else floor in event['floors']
    checks.append(_check('documented_main_floor',matches,'目录主层范围：'+str(event['floors']),kind='catalog_scope',
                         special_region_not_filtered=context.get('special_region',False)))
    mode=context.get('entry_mode','unknown')
    if event['natural'] is False:
        move=context.get('movement_item_id')
        match=False if mode=='natural' else True if mode=='content' else (
            True if move=='rogue_6_scrap_M_07' else None) if mode=='processed_item' else None
        checks.append(_check('special_movement_entry',match,'不会自然出现；通过装载小八界可能传送至此。',
                             movement_item_id=move,required_item_id='rogue_6_scrap_M_07'))
    else:
        # The fixed catalog explicitly marks natural/server qualification as unrecovered.
        checks.append(_check('entry_context',True if mode=='content' else None,
                             event['natural_reason'],kind='unknown_server_generation'))
    for scene in event['scenes']:
        for note in scene['edesc_texts']:
            if note=='本事件仅在遭遇沉寂之屋事件后有概率出现。':
                checks.append(_check('encountered_prior_event',_history(context,'沉寂之屋','encountered'),note,
                                     required_event_id=_event_id('沉寂之屋'),history_field='encountered'))
    return checks


def event_eligibility(event_id,context=None):
    context=_context(context);event=catalog._event(event_id);checks=_event_checks(event,context)
    return _result(event=catalog._summary(event),status=_status(checks),checks=checks,
                   unmatched_source_requirements=[r['key'] for r in checks if r['matches'] is False],
                   unknown_source_requirements=[r['key'] for r in checks if r['matches'] is None],
                   context=deepcopy(context),all_server_conditions_known=False,
                   supplementary_notes=list(dict.fromkeys(t for s in event['scenes'] for t in s['edesc_texts'])))


def qualified_events(context=None,include_indirect=True):
    context=_context(context)
    if type(include_indirect) is not bool:raise ValueError('include_indirect需要布尔值。')
    groups={'matched':[],'unknown':[],'excluded':[]};rows=[]
    for event in catalog.all_events(include_indirect=include_indirect)['rows']:
        result=event_eligibility(event['id'],context)
        rows.append(result);groups[result['status']].append(result)
    return _result(rows=rows,**groups,context=context,
                   original_unclassified_records_have_no_entry_rules=True,
                   status_scope='fixed source constraints only; all_server_conditions_known=false')


def choice_eligibility(event_id,scene_key,context=None):
    context=_context(context);event=catalog._event(event_id);scene=catalog._scene(event_id,scene_key)
    base=_event_checks(event,context);rows=[];original=_reference()['original_choices']
    for choice in scene['choices']:
        text=choice['conditional'] or '';checks=deepcopy(base);parsed=[]
        owned=re.fullmatch(r'仅在持有(?:【([^】]+)】|(.+?))时出现',text)
        if owned and not text.startswith('仅在持有超过'):
            name=owned.group(1) or owned.group(2);item_id=_named_item(name)
            parsed.append(_check('required_owned_item',None if item_id is None else _owned(context,item_id),text,
                                 required_item_name=name,required_item_id=item_id))
        gold=re.fullmatch(r'仅在持有超过(\d+)源石锭时出现',text)
        if gold:
            minimum=int(gold.group(1));value=context.get('gold')
            parsed.append(_check('gold_strictly_greater',None if value is None else value>minimum,text,
                                 threshold=minimum,comparison='>',gold_declared=value))
        if text=='若同时持有【沙盘α】和【沙盘β】或访问过【窥视箱中】，则不会出现此选项':
            alpha,beta=_named_item('沙盘α'),_named_item('沙盘β')
            pair=_and(None if alpha is None else _owned(context,alpha),None if beta is None else _owned(context,beta))
            visited=_history(context,'窥视箱中','visited')
            parsed.append(_check('excluded_by_sandbox_pair_or_visited_box',_not(_or(pair,visited)),text,
                                 simultaneous_pair_matches=pair,visited_box_matches=visited,
                                 required_item_ids=[alpha,beta],excluded_event_id=_event_id('窥视箱中'),history_field='visited'))
        checks.extend(parsed)
        mapped=[deepcopy(original[cid]) for cid in choice['game_choice_ids'] if cid in original]
        if any(row['isHiddenChoice'] for row in mapped):
            checks.append(_check('hidden_option_unlock',None,'原件isHiddenChoice为true；解锁脚本条件未公开。'))
        rows.append({'choice_key':choice['key'],'choice_title':choice['title'],'presentation_role':choice['presentation_role'],
                     'status':_status(checks),'checks':checks,'parsed_special_requirements':parsed,
                     'conditional_text':choice['conditional'],'unparsed_condition_text':text if text and not parsed else None,
                     'game_choice_ids':deepcopy(choice['game_choice_ids']),'original_choice_records':mapped,
                     'actual_selectable':None,'full_server_conditions_known':False,
                     'source_origin_scene_binding_verified':False})
    return _result(event=catalog._summary(event),scene_key=scene_key,rows=rows,context=context)


def event_battle_links(event_id,scene_key=None,choice_key=None,context=None):
    """Keep every exact page-linked stage ID and group aliases by original level file."""
    context=_context(context);event=catalog._event(event_id)
    if scene_key is not None:catalog._scene(event_id,scene_key)
    choices={c['key']:(s,c) for s in event['scenes'] for c in s['choices']}
    if choice_key is not None and choice_key not in choices:raise ValueError('战斗选项引用不属于所选事件。')
    if choice_key is not None and scene_key is not None and choices[choice_key][0]['key']!=scene_key:
        raise ValueError('战斗选项引用不属于所选场景。')
    rows=[]
    for record in _reference()['battle_links']:
        if record['event_id']!=event_id or (scene_key is not None and record['scene_key']!=scene_key) or (choice_key is not None and record['choice_key']!=choice_key):continue
        choice=choices[record['choice_key']][1]
        if choice['title']!=record['choice_title']:raise ValueError('选项标题与固定链接原件不符，需要重新绑定。')
        eligibility=next(r for r in choice_eligibility(event_id,record['scene_key'],context)['rows'] if r['choice_key']==record['choice_key'])
        result=deepcopy(record);links=[]
        emergency=record['conditional_text']=='升级为紧急作战'
        for link in record['stage_page_links']:
            levels={};excluded=[]
            for stage in link['stage_records']:
                row=deepcopy(stage);row['source_difficulty_matches']=None if not emergency else row['difficulty']=='FOUR_STAR'
                row['actual_stage_instance']=None
                if row['source_difficulty_matches'] is False:excluded.append(row)
                else:levels.setdefault(row['level_id'],[]).append(row)
            links.append({**deepcopy(link),'fixed_level_groups':[{'level_id':key,'stage_records':values,
                            'same_level_aliases':len(values)>1,'actual_stage_id':None} for key,values in levels.items()],
                          'excluded_by_explicit_difficulty':excluded})
        result.update(stage_page_links=links,choice_eligibility=eligibility,
                      actual_stage_id=None,stage_identity_rule='exact wiki code+name; every matching original ID retained',
                      preview_stage_candidates=[deepcopy(stage) for link in links for group in link['fixed_level_groups']
                                                for stage in group['stage_records']],
                      excluded_stage_candidates=[deepcopy(stage) for link in links for stage in link['excluded_by_explicit_difficulty']],
                      generic_pool_requirement=None)
        if record['conditional_text']=='随机出现下一层的普通作战中的一个':
            floor=context.get('floor');special=context.get('special_region',False)
            pool=[]
            if type(floor) is int and floor<6 and not special:
                pool=catalog.battle_candidates('作战',floor=floor+1,context='natural')['rows']
            result['generic_pool_requirement']={'source_text':record['conditional_text'],
                'next_main_floor_reference':floor+1 if type(floor) is int and floor<6 and not special else None,
                'fixed_named_pool':pool,'server_pool_complete':False,'actual_choice':None,
                'special_region_next_main_floor_rule_verified':False}
        rows.append(result)
    return _result(event=catalog._summary(event),rows=rows,scene_key=scene_key,choice_key=choice_key,
                   context=context,all_actual_stage_instances_verified=False)


COMMANDS={'events':qualified_events,'event':event_eligibility,'choices':choice_eligibility,'battles':event_battle_links}
