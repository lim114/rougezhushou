"""Source-bound event requirements and choice-to-fixed-battle references.

Three-state checks concern documented rules in declared conditions. They never
promote a match into actual server eligibility or infer entry scripts from NEXT.
"""
from copy import deepcopy
from functools import lru_cache
import json,re
from pathlib import Path
from . import node_catalog as catalog
from . import choice_held_requirements
from . import choice_recruitment_results
from . import peace_guardian_results


@lru_cache(maxsize=1)
def reference_data():
    return json.loads((Path(__file__).with_name('data')/'event-planning-reference.json').read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def current_observation():
    return json.loads((Path(__file__).with_name('data')/'event-current-observation.json').read_text(encoding='utf-8'))


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
    presence=context.get('item_presence',{})
    if not isinstance(presence,dict) or any(not isinstance(k,str) or not k or
            v is not None and type(v) is not bool for k,v in presence.items()):
        raise ValueError('持有状态需要原物品ID到布尔值或未知的对象。')
    if any(presence[k] is not None and presence[k] is not (v>0)
            for k,v in quantities.items() if k in presence):
        raise ValueError('持有状态与数量声明矛盾，不能任选其一覆盖。')
    if type(context.get('inventory_complete',False)) is not bool:raise ValueError('inventory_complete需要布尔值。')
    complete_ids=context.get('inventory_complete_item_ids')
    if ('inventory_complete_item_ids' in context and (not isinstance(complete_ids,list) or
            any(not isinstance(key,str) or not key for key in complete_ids) or len(complete_ids)!=len(set(complete_ids)))):
        raise ValueError('库存完整度范围需要不重复的原物品ID列表；省略仅用于手动完整库存声明。')
    prior=context.get('pre_entry_item_quantities',{})
    if not isinstance(prior,dict) or any(not isinstance(k,str) or not k or type(v) is not int or v<0 for k,v in prior.items()):
        raise ValueError('进入前持有需要原物品ID到非负整数的对象。')
    for key in ('pre_entry_inventory_complete','pre_entry_item_origins_complete'):
        if type(context.get(key,False)) is not bool:raise ValueError(key+'需要布尔值。')
    origins=context.get('pre_entry_item_origins',{})
    if not isinstance(origins,dict) or any(not isinstance(k,str) or not k or not isinstance(v,list) or
        any(not isinstance(source,str) or not source for source in v) for k,v in origins.items()):
        raise ValueError('进入前物品来源需要原物品ID到来源ID列表的对象。')
    gold=context.get('gold')
    if gold is not None and (type(gold) is not int or gold<0):raise ValueError('源石锭需要非负整数或留空。')
    resources=context.get('resources',{})
    valid_resources=('hp','max_hp','gold','hope','shield','ap')
    if not isinstance(resources,dict) or any(k not in valid_resources or type(v) is not int or v<0 for k,v in resources.items()):
        raise ValueError('resources只接受hp/max_hp/gold/hope/shield/ap非负整数。')
    if gold is not None and 'gold' in resources and gold!=resources['gold']:
        raise ValueError('gold与resources.gold声明不一致，不能选择其中一个覆盖。')
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
    if item_id in context.get('item_presence',{}):return context['item_presence'][item_id]
    return False if _inventory_complete_for(context,[item_id]) else None


def _inventory_complete_for(context,item_ids):
    if not context.get('inventory_complete',False):return False
    if 'inventory_complete_item_ids' not in context:return True  # Explicit offline global declaration.
    return set(item_ids)<=set(context['inventory_complete_item_ids'])


def _quantity_inventory_complete_for(context,item_ids):
    if not _inventory_complete_for(context,item_ids):return False
    quantities=context.get('item_quantities',{});presence=context.get('item_presence',{})
    return not any(key not in quantities and key in presence and presence[key] is not False for key in item_ids)


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
    historical=context.get('reference_context_scope')=='historical_title_reference_only'
    reference=catalog.natural_event_requirements(event,floor=floor,entry_mode=mode,
        special_region=False,historical=False) if mode=='natural' and floor is not None and not (
            context.get('special_region',False) or historical) else None
    if reference and reference['context_applicable']:
        checks.append(deepcopy(reference['check']) if reference['source_valid'] else
            _check('documented_node_natural_main_floor',None,
                '自然主层限制资料暂时无法核对；不能据此排除。',kind='source_node_floor_requirement',source_valid=False))
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
        owned_reference=choice_held_requirements.choice_reference(event_id,choice)
        if owned_reference:
            item_id=owned_reference['required_item_id']
            existing=next((row for row in parsed if row['key']=='required_owned_item' and row['required_item_id']==item_id),None)
            if existing is None:
                existing=_check('required_owned_item',_owned(context,item_id),owned_reference['source_text'],
                    required_item_name=owned_reference['required_item_name'],required_item_id=item_id,
                    source_field='top_level_result_description')
                parsed.append(existing)
            existing.update(description_condition_reference=owned_reference,
                holding_is_consumption=False,actual_consumed=None)
        checks.extend(parsed)
        mapped=[deepcopy(original[cid]) for cid in choice['game_choice_ids'] if cid in original]
        if any(row['isHiddenChoice'] for row in mapped):
            checks.append(_check('hidden_option_unlock',None,'原件isHiddenChoice为true；解锁脚本条件未公开。'))
        edition_warnings=[]
        if event['title']=='被歌颂的影子' and '若在进入本事件前已拥有【犬植浆】' in scene['description']:
            edition_warnings.append({'kind':'newer_document_rule_differs','old_revision':'427904',
                                     'observed_revision':current_observation()['source']['revision'],
                                     'source':deepcopy(current_observation()['source']),
                                     'reason':current_observation()['delta'],
                                     'query':'scene-outcomes','actual_server_rule_verified':False})
        recruitment=choice_recruitment_results.choice_reference(event_id,choice,scene_key=scene_key)
        movement=peace_guardian_results.choice_result_reference(event,scene,choice)
        result_annotation=bool((recruitment and recruitment['status']=='documented_reference'
                               and recruitment['annotation_role']=='selection_result')
            or (movement and movement['status']=='documented_reference'
                and movement['annotation_role']=='selection_result'))
        rows.append({'choice_key':choice['key'],'choice_title':choice['title'],'presentation_role':choice['presentation_role'],
                     'status':_status(checks),'checks':checks,'parsed_special_requirements':parsed,
                     'conditional_text':choice['conditional'],'unparsed_condition_text':text if text and not parsed and not result_annotation else None,
                     'game_choice_ids':deepcopy(choice['game_choice_ids']),'original_choice_records':mapped,
                     'actual_selectable':None,'full_server_conditions_known':False,
                     'source_origin_scene_binding_verified':False,'edition_warnings':edition_warnings,
                     **({'recruitment_result_reference':recruitment} if recruitment is not None else {}),
                     **({'movement_result_reference':movement} if movement is not None else {})})
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


def _pre_owned(context,item_id):
    values=context.get('pre_entry_item_quantities',{})
    if item_id in values:return values[item_id]>0
    return False if context.get('pre_entry_inventory_complete',False) else None


def scene_outcomes(event_id,scene_key,context=None):
    """Current documented terminal-reward conditions, preserving snapshot and origin gaps."""
    context=_context(context);event=catalog._event(event_id);scene=catalog._scene(event_id,scene_key)
    observation=current_observation()
    applicable=event['title']==observation['event_title'] and '若在进入本事件前已拥有【犬植浆】' in scene['description']
    if not applicable:
        return _result(event=catalog._summary(event),scene_key=scene_key,rows=[],current_rule_applicable=False,
                       full_current_scene_rules_known=False)
    plant,dog=_named_item('植浆'),_named_item('犬植浆')
    plant_owned=None if plant is None else _pre_owned(context,plant)
    dog_owned=None if dog is None else _pre_owned(context,dog)
    origins=context.get('pre_entry_item_origins',{}).get(dog,[])
    from_event=False if dog_owned is False else True if dog_owned is True and event_id in origins else (
        False if dog_owned is True and context.get('pre_entry_item_origins_complete',False) else None)
    dog_condition=_and(_not(plant_owned),_not(from_event));ap_condition=_not(dog_condition)
    rows=[{'outcome':'named_relic','item_id':dog,'item_name':'犬植浆','quantity':1,
           'document_condition_matches':dog_condition,'status':'unknown' if dog_condition is None else 'matched' if dog_condition else 'excluded',
           'source_condition':'进入前无植浆，且不持有来自本事件的犬植浆','actual_granted':None,'probability':None},
          {'outcome':'action_points','resource':'ap','quantity':1,'document_condition_matches':ap_condition,
           'status':'unknown' if ap_condition is None else 'matched' if ap_condition else 'excluded',
           'source_condition':'前一条件的补集：拥有植浆或持有来自本事件的犬植浆','actual_granted':None,'probability':None}]
    return _result(event=catalog._summary(event),scene_key=scene_key,rows=rows,current_rule_applicable=True,
                   current_document_source=deepcopy(observation['source']),fixed_old_catalog_revision='427904',
                   version_difference=observation['delta'],pre_entry_snapshot_required=True,
                   pre_entry_plant_owned=plant_owned,pre_entry_dog_owned=dog_owned,
                   pre_entry_dog_from_this_event=from_event,actual_final_reward=None,
                   full_current_scene_rules_known=False,current_document_rule_is_deterministic=True,
                   additional_limits=deepcopy(observation['limits'])+[
                       '当前持有不能替代进入前快照；犬植浆的来源未知时保留两个候选。',
                       '只实现直接读到的当前文档条件；没有把整份旧目录换成新版本，也未证明客户端脚本。'])


RESOURCE_NAMES={'目标生命值上限':'max_hp','目标生命值':'hp','源石锭':'gold','希望':'hope','护盾':'shield','行动力':'ap'}


def _outside_parentheses(text):
    depth=0;result=[]
    for char in text:
        if char in '(（':depth+=1
        elif char in ')）':depth=max(0,depth-1)
        elif not depth:result.append(char)
    return ''.join(result)


def _resource_value(context,resource):
    if resource=='gold' and context.get('gold') is not None:return context['gold']
    return context.get('resources',{}).get(resource)


def _item_name_candidates(name):
    return [key for key,row in _reference()['source_item_names'].items() if row['name']==name]


def final_ap_conversion(remaining_ap=None):
    """FINAL has original equal-amount wording; no borrowed rule for boss exits."""
    if remaining_ap is not None and (type(remaining_ap) is not int or remaining_ap<0):raise ValueError('剩余AP需要非负整数。')
    records=[deepcopy(row) for key,row in _reference()['original_choices'].items()
             if key in ('choice_ro6_final1_1','choice_ro6_final1_5','choice_ro6_final1_3') and '等量希望' in row['description']]
    if not records:raise ValueError('原件没有等量希望描述，不能使用1:1参考。')
    return _result(exit_node_type='FINAL',remaining_ap_declared=remaining_ap,conversion_ratio_reference=1,
                   hope_gain_reference=remaining_ap,original_choice_records=records,
                   actual_hope_gain=None,actual_transition_succeeded=None,boss_exit_rule_verified=False)


def choice_resources(event_id,scene_key,context=None):
    """Documented top-level resource amounts and independent nominal budgets."""
    context=_context(context);event=catalog._event(event_id);scene=catalog._scene(event_id,scene_key);rows=[]
    eligibility_by_key=None
    for choice in scene['choices']:
        description=choice['description'] or '';top=_outside_parentheses(description);actions=[]
        pattern=r'(消耗|获得|回复|损失|失去)(\d+)(?:点)?(目标生命值上限|目标生命值|源石锭|希望|护盾|行动力)'
        for match in re.finditer(pattern,top):
            verb,amount,name=match.groups();quantity=int(amount);resource=RESOURCE_NAMES[name]
            value=_resource_value(context,resource);cost=verb in ('消耗','损失','失去')
            guard=1 if cost and resource=='hp' and '至少保留1目标生命值' in description else None
            actions.append({'kind':'nominal_cost' if cost else 'nominal_gain_or_recovery','resource':resource,
                'source_item_id':_reference()['resource_item_ids'].get(resource),'quantity_reference':quantity,
                'source_match':match.group(0),'resource_value_declared':value,
                'nominal_budget_covers':None if not cost or value is None or guard is not None else value>=quantity,
                'minimum_retained_hp_reference':guard,'special_payment_rule_verified':False if guard else None,
                'actual_changed':None})
        for match in re.finditer(r'消耗一半(?:的)?(目标生命值|源石锭)',top):
            resource=RESOURCE_NAMES[match.group(1)];value=_resource_value(context,resource)
            actions.append({'kind':'fraction_cost','resource':resource,'fraction_reference':0.5,
                'source_match':match.group(0),'resource_value_declared':value,
                'fraction_arithmetic_reference':None if value is None else value*0.5,
                'actual_integer_cost':None,'integer_rounding_verified':False,'nominal_budget_covers':None,'actual_changed':None})
        for match in re.finditer(r'(消耗|获得)(?:随机|零件箱里的)?(\d+)件(加工品|自然物|概念体|零件)',top):
            verb,amount,name=match.groups();category={'加工品':'MOVE','自然物':'GOODS','概念体':'PASSIVE','零件':None}[name]
            ids=[key for key,item in _reference()['source_item_names'].items()
                 if item['type']=='SCRAP' and (category is None or item['scrap_category']==category)]
            quantities=context.get('item_quantities',{});known=sum(quantities.get(key,0) for key in ids)
            amount=int(amount);cost=verb=='消耗';complete=_quantity_inventory_complete_for(context,ids)
            coverage=None if not cost else True if known>=amount else False if complete else None
            actions.append({'kind':'category_item_cost' if cost else 'random_category_item_gain',
                'scrap_category':category,'quantity_reference':amount,'candidate_item_ids':ids,
                'known_owned_subtotal':known,'inventory_complete_declared':complete,'nominal_budget_covers':coverage,
                'source_match':match.group(0),'actual_items_selected':None,'actual_pool_complete':False,'probability':None})
        for verb,name,quantity in (('消耗','源私钥',1),('交出','源私钥',1),('种下','种子',1)):
            if (verb+name in top) or (verb=='种下' and '种下1枚种子' in top):
                ids=_item_name_candidates(name);owned=None if len(ids)!=1 else _owned(context,ids[0])
                actions.append({'kind':'named_item_cost','item_name':name,'candidate_item_ids':ids,
                    'quantity_reference':quantity,'nominal_budget_covers':owned,'actual_consumed':None,
                    'source_match':verb+name})
        conversion=None
        if '等量希望' in top and event['title']=='险路尽头':
            conversion=final_ap_conversion(_resource_value(context,'ap'))
        if eligibility_by_key is None:
            # One scene result per external query; defer until first needed.
            eligibility_by_key={}
            for reference in choice_eligibility(event_id,scene_key,context)['rows']:
                eligibility_by_key.setdefault(reference['choice_key'],reference)
        if choice['key'] not in eligibility_by_key:raise StopIteration
        eligibility=eligibility_by_key[choice['key']]
        rows.append({'choice_key':choice['key'],'choice_title':choice['title'],'presentation_role':choice['presentation_role'],
                     'description':description,'resource_references':actions,'ap_conversion_reference':conversion,
                     'choice_eligibility':eligibility,'complete_resource_effects_known':False,
                     'unparsed_description_retained':description,'nested_relic_effects_auto_applied':False,
                     'actual_new_resources':None,'budget_failure_is_server_exclusion':False})
    return _result(event=catalog._summary(event),scene_key=scene_key,rows=rows,context=context,
                   complete_node_resource_effects_known=False,
                   additional_limits=['数量只来自顶层原文；括号内藏品效果不混入直接节点增减。',
                       '预算覆盖不足与服务器不可选/不出现是不同状态，资格三态仍独立。',
                       '半数取整、最低保留HP的特殊扣除、随机物品选择及未解析效果仍未知。'])


COMMANDS={'events':qualified_events,'event':event_eligibility,'choices':choice_eligibility,'battles':event_battle_links,
          'scene-outcomes':scene_outcomes,'resources':choice_resources,'final-conversion':final_ap_conversion}


def _original_context(context):
    """Separate startup declarations; current held items never imply inheritance."""
    context=_context(context)
    for key,values in (('phase',('run_start','map_node')),('exploration_mode',('NORMAL','MONTH_TEAM'))):
        if context.get(key) is not None and context[key] not in values:raise ValueError(key+'声明不在支持范围中。')
    previous=context.get('previous_regions_completed')
    if previous is not None and (type(previous) is not int or previous<0):raise ValueError('上一局通过区域数需要非负整数或留空。')
    data=catalog._original_entries();known=set(data['startup']['known_legacy_ids'])
    inherited=context.get('inherited_legacy_ids',[]);presence=context.get('inherited_legacy_presence',{})
    if (not isinstance(inherited,list) or any(not isinstance(key,str) or key not in known for key in inherited)
        or len(set(inherited))!=len(inherited)):raise ValueError('继承LEGACY需要原件唯一ID列表；同名不能代替原ID。')
    if (not isinstance(presence,dict) or any(key not in known or (value is not None and type(value) is not bool)
        for key,value in presence.items())):raise ValueError('继承LEGACY状态需要原ID到布尔或未知的对象。')
    if any(presence.get(key) is False for key in inherited):raise ValueError('同一继承LEGACY的正/负声明冲突。')
    if type(context.get('inherited_legacy_complete',False)) is not bool:raise ValueError('inherited_legacy_complete需要布尔值。')
    if context.get('fog_color') is not None and context['fog_color'] not in ('red','blue','green','gold','orange','purple'):
        raise ValueError('雾色需要red/blue/green/gold/orange/purple或留空。')
    if context.get('original_scene_id') is not None:
        catalog._text(context['original_scene_id'],'原场景声明')
        if context['original_scene_id'] not in catalog._original()['scenes']:raise ValueError('原场景声明不在固定原件中。')
    return context


def _inherited_legacy(context,legacy_id):
    if legacy_id in context.get('inherited_legacy_ids',[]):return True
    if legacy_id in context.get('inherited_legacy_presence',{}):return context['inherited_legacy_presence'][legacy_id]
    return False if context.get('inherited_legacy_complete',False) else None


def original_entry_qualification(record_id,context=None):
    """Source entry identity and independent choice gates, never natural spawning."""
    context=_original_context(context);raw=catalog.original_references(record_id=record_id)['rows'][0]
    data=catalog._original_entries();reference=data['records'].get(record_id);checks=[];extra={}
    if reference is None:
        checks=[_check('original_source_scene_unrecovered',None,
                       '原来源场景/展示条件未恢复；nextSceneId只能证明目的地。')]
        owned_reference=choice_held_requirements.original_reference(record_id)
        if owned_reference:
            checks.append(_check('required_owned_item',_owned(context,owned_reference['required_item_id']),
                owned_reference['source_text'],required_item_name=owned_reference['required_item_name'],
                required_item_id=owned_reference['required_item_id'],source_field='original_result_description',
                description_condition_reference=owned_reference,holding_is_consumption=False,actual_consumed=None))
            extra.update(documented_choice_requirements=deepcopy(checks[1:]),
                documented_choice_requirements_status=_status(checks[1:]))
    elif reference['kind']=='portal_entry_variant':
        event=catalog._event(reference['source_event_id']);checks=_event_checks(event,context)
        fog=context.get('fog_color');identity=context.get('original_scene_id')
        matches=None if fog is None and identity is None else _and(
            True if fog is None else fog==reference['fog_color'],True if identity is None else identity==record_id)
        checks.append(_check('explicit_portal_entry_identity',matches,
            reference['label']+'完整差分句与原description逐字相等；不从ID后缀推断实例。',
            fog_color_reference=reference['fog_color'],original_scene_id_reference=record_id))
        extra.update(documented_identity_matches=matches,actual_original_scene_selected=None,
                     original_id_suffix_used_as_evidence=False)
    else:
        phase=context.get('phase');previous=context.get('previous_regions_completed')
        checks=[_check('startup_phase',None if phase is None else phase=='run_start','行动奖励属于开始探索时的支援阶段，未加入普通地图自然候选。'),
            _check('previous_completed_regions',None if previous is None else previous>=2,
                '上一局至少通过两个区域；抵达的最高层号和当前持有不能替代。',minimum_completed_regions=2)]
        scene=context.get('original_scene_id')
        if scene is not None:checks.append(_check('startup_scene_identity',scene==data['startup']['scene']['id'],'明确原场景ID须对应行动奖励。'))
        if reference['kind']=='startup_legacy_extra':
            mode=context.get('exploration_mode');legacy=reference['legacy_id']
            checks += [_check('legacy_normal_mode_scope',None if mode is None else mode=='NORMAL','襁褓培育/继承仅常规探索生效；模式未知不默认常规。'),
                _check('inherited_original_legacy',_inherited_legacy(context,legacy),
                       '对应继承LEGACY原ID的force_add_choice直接指向本隐藏选项与行动奖励场景。',legacy_id=legacy)]
            extra.update(legacy_id=legacy,documented_extra_blue_display_count=1,actual_selectable=None)
        else:
            # The regular action section documents NORMAL. It does not prove absence in every other mode.
            mode=context.get('exploration_mode')
            checks.append(_check('regular_mode_documented_scope',True if mode=='NORMAL' else None,'常规行动的初始支援公开规则；其它模式未在此入口依据中闭合。'))
        extra.update(documented_regular_candidate_count=6,documented_regular_display_count=3,
            actual_displayed_choice_ids=None,all_twelve_choices_displayed=False)
    return _result(record=raw,reference=deepcopy(reference),checks=checks,status=_status(checks),context=context,
        source_scene_link_verified=bool(reference and reference['source_scene_link_verified']),
        special_entry_sources=deepcopy(data['sources']),actual_server_eligible=None,
        full_server_conditions_known=False,natural_node_generation_verified=False,
        reachable_from_entry=None,generation_probability=None,
        limits=deepcopy(data['limits']),**extra)


def original_entry_variants(event_id,context=None):
    context=_original_context(context);catalog._event(event_id)
    records=[(key,row) for key,row in catalog._original_entries()['records'].items() if row.get('source_event_id')==event_id]
    rows=[original_entry_qualification(key,context) for key,_ in records]
    return _result(event_id=event_id,rows=rows,context=context,actual_original_scene_selected=None,
        source_scene_link_verified=bool(records),source_scene_script_recovered=False,
        original_id_suffix_used_as_evidence=False,special_entry_sources=deepcopy(catalog._original_entries()['sources']))


COMMANDS.update({'original-entry':original_entry_qualification,'original-variants':original_entry_variants})
