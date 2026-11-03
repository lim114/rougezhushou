"""Conditional base experience/gold over declared battles, never run resources."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from . import node_catalog

ENTRY_CONTEXTS=('unknown','map_battle','event_battle','pursuit')

@lru_cache(maxsize=1)
def reference_data():
    return json.loads((Path(__file__).with_name('data')/'base-settlement-reference.json').read_text(encoding='utf8'))

def _data():
    data=reference_data()
    if data['original_source']['sha256']!=node_catalog._original()['source']['game_data']['sha256']:
        raise ValueError('基础结算原件版本已变化，需要重新绑定关卡身份与来源范围。')
    return data

def _status(values):return 'excluded' if False in values else 'unknown' if None in values else 'matched'

def _settings(battle_floor,entry_context,special_region):
    if battle_floor is not None and (type(battle_floor) is not int or battle_floor not in range(1,7)):
        raise ValueError('战斗所属主层需要1–6整数或留空，秘境编号不能替代。')
    if entry_context not in ENTRY_CONTEXTS:raise ValueError('结算入口需要unknown/map_battle/event_battle/pursuit。')
    if special_region is not None and type(special_region) is not bool:raise ValueError('special_region需要布尔值或未知。')

def _candidate(rule,kind,contexts,*,battle_floor,entry_context,source_floor=None):
    entry=None if entry_context=='unknown' else entry_context in contexts
    floor=True if source_floor is None else None if battle_floor is None else source_floor==battle_floor
    return {'rule_kind':kind,'source_label':rule.get('source_label') or rule.get('source_column_kind'),
        'source_row_index':rule.get('source_row_index'),'entry_contexts_reference':list(contexts),
        'entry_context_matches':entry,'source_battle_floor':source_floor,'battle_floor_matches':floor,
        'status':_status([entry,floor]),'base_experience_reference':deepcopy(rule['experience']['base']),
        'base_gold_reference':deepcopy(rule['gold']['base']),
        'full_technology_experience_reference':rule['experience'].get('full_technology_reference'),
        'actual_experience_received':None,'actual_gold_received':None,'full_technology_auto_applied':False,
        'native_settlement_script_verified':False}

def _regional_rows(data,kind,contexts,*,floor,battle_floor,entry_context,special_region):
    main=_candidate(data['main_floor_table'][str(floor)][kind],'main_floor_'+kind,contexts,
        battle_floor=battle_floor,entry_context=entry_context,source_floor=floor)
    portal_rule=data['portal_rule'];inherited=kind in portal_rule['inherited_column_kinds']
    rule=data['main_floor_table'][str(floor)][kind] if inherited else {
        'source_label':'秘境首领/首领追猎原表空列：基础数值未知',
        'source_row_index':portal_rule['source_row_index'],
        'experience':{'base':None,'full_technology_reference':None},'gold':{'base':None}}
    portal=_candidate(rule,'portal_'+kind,contexts,battle_floor=battle_floor,
        entry_context=entry_context,source_floor=floor)
    portal['portal_numeric_source_documented']=inherited
    portal['blank_source_does_not_exclude_entry']=not inherited
    for row,scope in ((main,'main'),(portal,'portal')):
        row['region_scope']=scope
        region=None if special_region is None else (scope=='portal') is special_region
        row['special_region_matches']=region
        row['status']=_status([row['entry_context_matches'],row['battle_floor_matches'],region])
    return [main,portal]

def stage_base_rewards(stage_id,battle_floor=None,entry_context='unknown',special_region=None):
    if not isinstance(stage_id,str) or not stage_id:raise ValueError('固定原关卡ID需要非空文本。')
    _settings(battle_floor,entry_context,special_region);data=_data();stage=data['stages'].get(stage_id)
    if stage is None:raise ValueError('固定原关卡ID不存在；不从名称猜结算入口。')
    rows=[];refs=stage['source_pool_references'];raw=stage['original']
    for index in stage['special_rule_indices']:
        rule=data['special_battle_table'][index]
        contexts=['event_battle'] if rule['source_label'].startswith('不期而遇') else ['map_battle','event_battle']
        rows.append(_candidate(rule,'named_special_battle',contexts,battle_floor=battle_floor,entry_context=entry_context))
    natural=any(ref.get('source_membership') in ('normal_emergency_named_pool','boss_named_pool')
        and not ref.get('pursuit_marker') for ref in refs)
    pursuit=any(ref.get('pursuit_marker') for ref in refs) or 'pursuit' in stage['documented_categories']
    if natural and not stage['special_rule_indices']:
        kind='boss' if raw['isBoss'] else 'emergency' if raw['difficulty']=='FOUR_STAR' else 'normal'
        for floor in stage['settlement_source_floors'] or []:
            rows.extend(_regional_rows(data,kind,['map_battle'],floor=floor,battle_floor=battle_floor,
                entry_context=entry_context,special_region=special_region))
    if pursuit:
        if raw['isBoss']:
            for floor in stage['settlement_source_floors'] or []:
                rows.extend(_regional_rows(data,'boss_pursuit',['pursuit'],floor=floor,battle_floor=battle_floor,
                    entry_context=entry_context,special_region=special_region))
        else:
            source=data['ordinary_pursuit_rule']
            rule={'source_label':source['source_text'],'experience':{'base':source['experience']},'gold':{'base':source['gold']}}
            rows.append(_candidate(rule,'ordinary_pursuit',['pursuit'],battle_floor=battle_floor,entry_context=entry_context))
    return {'scope':'documented_base_settlement_in_declared_context','stage_id':stage_id,'stage_name':raw['name'],
        'difficulty':raw['difficulty'],'original_metadata':deepcopy(raw),'source':deepcopy(data['source']),
        'battle_floor_declared':battle_floor,'entry_context_declared':entry_context,'special_region_declared':special_region,
        'documented_origin_floors':deepcopy(stage['documented_floors']),'rows':rows,
        'settlement_origin_floors':deepcopy(stage['settlement_source_floors']),
        'floor_zero_binding':deepcopy(stage['floor_zero_binding']),
        'unresolved_scope':not rows,'actual_reward_total':None,'complete_settlement_pool_known':False,
        'inventory_updated':False,'actual_victory_verified':False,'source_limits':deepcopy(data['limits'])}

def _graph_nodes(graph):
    if graph is None:return {}
    if not isinstance(graph,dict) or not isinstance(graph.get('nodes'),list):raise ValueError('声明图需要节点列表。')
    nodes={};positions=set()
    for node in graph['nodes']:
        if not isinstance(node,dict) or not isinstance(node.get('id'),str) or not node['id']:raise ValueError('节点需要非空原ID。')
        if any(type(node.get(k)) is not int or node[k]<0 for k in ('row','col')):raise ValueError('节点行列需要非负整数。')
        if node.get('content') is not None and not isinstance(node['content'],dict):raise ValueError('当前内容需要对象或未知。')
        if node.get('observed_type') is not None and not isinstance(node['observed_type'],str):raise ValueError('当前类型需要文字或未知。')
        position=node['row'],node['col']
        if node['id'] in nodes or position in positions:raise ValueError('声明图节点ID或行列重复。')
        nodes[node['id']]=node;positions.add(position)
    return nodes

def _stages(step,node):
    supplied=[key for key in ('stage_id','stage_ids') if key in step]
    if len(supplied)>1:raise ValueError('stage_id与stage_ids不能同时声明。')
    if supplied:
        ids=[step['stage_id']] if supplied[0]=='stage_id' else step['stage_ids']
        if not isinstance(ids,list) or not ids or any(not isinstance(key,str) or not key for key in ids) or len(ids)!=len(set(ids)):
            raise ValueError('关卡候选需要不重复的非空原ID列表。')
        if any(key not in _data()['stages'] for key in ids):raise ValueError('声明关卡ID不在固定目录中。')
        return ids,[],'caller_declared_original_stage_ids'
    content=(node or {}).get('content') or {}
    if not isinstance(content,dict) or content.get('kind')!='battle':return [],[],'no_current_battle_identity'
    variant=content.get('variant_id');variants=content.get('variants')
    if variant is not None and (not isinstance(variant,str) or not variant):
        raise ValueError('当前战斗variant_id需要非空原ID或未知。')
    if variants is not None and (not isinstance(variants,list) or any(
            not isinstance(row,dict) or not isinstance(row.get('id'),str) or not row['id'] for row in variants)):
        raise ValueError('当前战斗variants需要完整原ID对象列表；不静默丢弃未知候选。')
    ids=[variant] if variant else [row['id'] for row in variants or []]
    ids=list(dict.fromkeys(ids))
    accepted=[key for key in ids if key in _data()['stages'] and _data()['stages'][key]['original']['name']==content.get('title')]
    return accepted,[key for key in ids if key not in accepted],'current_content_exact_id_and_title_reference'

def settlements(steps=None,graph=None):
    """Evaluate each battle declaration; unknown components never become zero."""
    nodes=_graph_nodes(graph)
    automatic=steps is None
    if automatic:
        steps=[{'target':key} for key,node in nodes.items() if (node.get('content') or {}).get('kind')=='battle'
            or node.get('observed_type') in ('作战','紧急作战','险路恶敌')]
    if not isinstance(steps,list) or len(steps)>100:raise ValueError('结算步骤需要至多100项对象列表。')
    rows=[];known_xp=known_gold_min=known_gold_max=0;unknown=[]
    if automatic and not steps:unknown.append({'step':None,'reasons':['no_current_battle_identity_in_declared_graph']})
    for ordinal,step in enumerate(steps,1):
        if not isinstance(step,dict):raise ValueError('结算步骤需要对象。')
        if set(step)-{'target','stage_id','stage_ids','battle_floor','entry_context','special_region','victory_declared'}:
            raise ValueError('结算步骤包含未支持的字段；不静默应用或忽略额外修正。')
        key=step.get('target');node=nodes.get(key) if key is not None else None
        if key is not None and (not isinstance(key,str) or node is None):raise ValueError('目标必须在所声明图中。')
        victory=step.get('victory_declared')
        if victory is not None and type(victory) is not bool:raise ValueError('胜利条件需要布尔值或留空。')
        zone_id=(graph or {}).get('zone_id')
        region_reference=None if zone_id not in _data()['zones'] else zone_id in _data()['portal_zone_ids']
        floor=step.get('battle_floor');entry=step.get('entry_context','unknown');special=step.get('special_region',region_reference)
        _settings(floor,entry,special)
        ids,unresolved,basis=_stages(step,node)
        candidates=[stage_base_rewards(identity,floor,entry,special) for identity in ids]
        applicable=[ref for candidate in candidates for ref in candidate['rows'] if ref['status']!='excluded']
        matched=[ref for ref in applicable if ref['status']=='matched']
        xp_values={ref['base_experience_reference'] for ref in matched}
        gold_values={(ref['base_gold_reference']['minimum'],ref['base_gold_reference']['maximum'])
            if ref['base_gold_reference'] is not None else None for ref in matched}
        unique=(len(xp_values)==len(gold_values)==1 and not unresolved and all(ref['status']=='matched' for ref in applicable))
        xp=next(iter(xp_values)) if unique else None;gold=next(iter(gold_values)) if unique else None
        reasons=[]
        if not ids:reasons.append('no_exact_current_or_declared_stage_identity')
        if unresolved:reasons.append('unresolved_current_stage_identity')
        if not unique:reasons.append('entry_or_origin_floor_or_variant_unresolved')
        if victory is None:reasons.append('victory_not_declared')
        if unique and xp is None:reasons.append('base_experience_not_documented')
        if unique and gold is None:reasons.append('base_gold_not_documented')
        admitted=victory is True and unique
        if admitted and xp is not None:known_xp+=xp
        if admitted and gold is not None:known_gold_min+=gold[0];known_gold_max+=gold[1]
        if reasons:unknown.append({'step':ordinal,'reasons':reasons})
        rows.append({'step':ordinal,'node_id':key,'position':{'row':node['row'],'col':node['col']} if node else None,
            'stage_candidates':ids,'unresolved_stage_ids':unresolved,'identity_basis':basis,'battle_references':candidates,
            'victory_declared':victory,'conditional_base_experience':xp,'conditional_base_gold':
                {'minimum':gold[0],'maximum':gold[1]} if gold is not None else None,
            'admitted_to_known_base_subtotal':admitted,'unknown_components':reasons,
            'actual_victory_verified':False,'actual_received':None})
    return {'scope':'offline_declared_battle_base_components','rows':rows,'source':deepcopy(_data()['source']),
        'automatic_graph_reference_only':automatic,'declared_steps':deepcopy(steps),
        'known_base_subtotal':{'experience':known_xp,'gold':{'minimum':known_gold_min,'maximum':known_gold_max}},
        'complete_conditional_base_reference':not unknown,
        'conditional_base_total':{'experience':known_xp,'gold':{'minimum':known_gold_min,'maximum':known_gold_max}} if not unknown else None,
        'unknown_components':unknown,'actual_reward_total':None,'actual_victory_verified':False,
        'complete_settlement_pool_known':False,'inventory_updated':False,'route_feasibility_evaluated':False,
        'probability':None,'limits':deepcopy(_data()['limits'])}

def gold_reference_text(value):
    if value is None:return '未知'
    return str(value['minimum']) if value['minimum']==value['maximum'] else f"{value['minimum']}–{value['maximum']}"

def stage_reward_text(result):
    lines=['基础战斗结算分项：'+result['stage_name'],
        '以下为胜利后、无经验/源石锭加成的基础参考；不包含装置奖励和完整掉落池。']
    if result.get('floor_zero_binding'):
        lines.append('层数来源补充：旧目录层数未归类；公开“0 源流交汇处 (VI)”与原区域名称/icon复核对应第6主层。地图模板与连线仍未知。')
    for row in result['rows']:
        if row['status']=='excluded':continue
        floor=f"战斗所属第{row['source_battle_floor']}主层；" if row['source_battle_floor'] is not None else ''
        context='追猎入口' if row['rule_kind'].endswith('pursuit') else '秘境战斗入口' if row.get('region_scope')=='portal' else '公开具名特殊入口' if row['rule_kind']=='named_special_battle' else '主层战斗入口'
        xp=row['base_experience_reference'];full=row['full_technology_experience_reference']
        lines.append(f"条件参考：{context}；{floor}基础指挥经验 {xp if xp is not None else '未知'}；源石锭 {gold_reference_text(row['base_gold_reference'])}。")
        if row.get('blank_source_does_not_exclude_entry'):
            lines.append('秘境原表对应首领/首领追猎列未列数值；不套主层数值，也不据此断言无法进入。')
        if full is not None:lines.append(f'满级生命游戏独立文档列：{full}指挥经验；未推定账户解锁或生效，未混入基础分项。')
    if not result['rows']:lines.append('此精确原ID的基础来源范围尚未绑定。')
    lines += ['实际胜利、领取、额外加成和完整奖励总量：未知。',
        f"基础表来源：PRTS {result['source']['revision']}；"+result['source']['url']]
    return '\n'.join(lines)
