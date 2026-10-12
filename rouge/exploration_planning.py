"""Offline exploration references over explicit graph and inventory declarations.

These functions never read or mutate run state. Range membership, declared
resources and source-backed subtotals are separate from actual game eligibility.
"""
from copy import deepcopy
from collections import deque
from functools import lru_cache
import json
from pathlib import Path
from .base_settlement_planning import settlements
from .node_arrival import arrival_reference,validate_arrival_state


@lru_cache(maxsize=1)
def reference_data():
    return json.loads((Path(__file__).with_name('data')/'exploration-reference.json').read_text(encoding='utf-8'))


def _integer(value,label,optional=False,minimum=0):
    if value is None and optional: return
    if type(value) is not int or value<minimum: raise ValueError(label+'需要非负整数。')


def _item(item_id,kind=None):
    if not isinstance(item_id,str) or item_id not in reference_data()['items']:
        raise ValueError('零件需要固定目录中的唯一标识。')
    item=reference_data()['items'][item_id]
    if kind and item['kind']!=kind: raise ValueError('所选零件不是'+kind+'类型。')
    return item


def _result(**values):
    return {'scope':'offline_declared_conditions','source':deepcopy(reference_data()['source']),
            'actual_gameplay_verified':False,'inventory_updated':False,
            'limits':deepcopy(reference_data()['limits']),**values}


def item_catalog(kind=None):
    if kind is not None and kind not in ('MOVE','GOODS','PASSIVE'):
        raise ValueError('类型需要MOVE、GOODS、PASSIVE或留空。')
    return _result(items=[deepcopy(item) for item in reference_data()['items'].values()
                         if kind is None or item['kind']==kind])


def _graph(graph,start=None):
    if not isinstance(graph,dict) or not isinstance(graph.get('nodes'),list) or not graph['nodes']:
        raise ValueError('地图需要非空节点列表。')
    nodes={};positions=set()
    for node in graph['nodes']:
        if not isinstance(node,dict) or not isinstance(node.get('id'),str) or not node['id']:
            raise ValueError('节点需要非空文字标识。')
        _integer(node.get('row'),'节点行');_integer(node.get('col'),'节点列')
        key=(node['row'],node['col'])
        if node['id'] in nodes or key in positions: raise ValueError('节点标识或位置重复。')
        for field in ('base_node_type','node_type_raw'):
            if node.get(field) is not None and node[field] not in reference_data()['node_types']:
                raise ValueError(field+'必须是原表节点类型。')
        if node.get('scrap_category') is not None and node['scrap_category'] not in ('EVENTS','BATTLES','EMPTY'):
            raise ValueError('scrap_category需要EVENTS、BATTLES或EMPTY。')
        for field in ('completed_declared','occupied_declared','other_blocked_declared','repeatable_declared'):
            if node.get(field) is not None and type(node[field]) is not bool:
                raise ValueError(field+'需要布尔值或留空。')
        validate_arrival_state(node)
        nodes[node['id']]=node;positions.add(key)
    if start is None: start=graph.get('current_node')
    if not isinstance(start,str) or start not in nodes:
        raise ValueError('起点需要地图中的明确节点；历史位置不自动作为起点。')
    return nodes,start


def _type_candidates(node):
    explicit=node.get('base_node_type') or node.get('node_type_raw')
    if explicit: return [explicit],'declared_original_node_type'
    # A displayed title may have multiple original types (STORY/STORY_HIDDEN).
    # Template and history types are deliberately not promoted to current type.
    label=node.get('observed_type')
    return [key for key,row in reference_data()['node_types'].items() if row['name']==label], 'declared_display_type'


def _membership(node,allowed):
    if 'ALL' in allowed: return True,'all_nodes_parameter'
    # Group membership is not serialized in this public original table. Preserve
    # every grouped candidate unless the caller explicitly declares the group.
    # Exact enum restrictions (shops, WISH, SACRIFICE) are directly testable.
    if any(key in allowed for key in ('EVENTS','BATTLES')):
        group=node.get('scrap_category')
        if group is None: return None,'original_group_membership_unknown'
        if group not in ('EVENTS','BATTLES','EMPTY'): raise ValueError('scrap_category需要EVENTS、BATTLES或EMPTY。')
        return group in allowed,'declared_scrap_category'
    types,basis=_type_candidates(node)
    if not types: return None,'node_type_unknown'
    values=[key in allowed for key in types]
    return values[0] if all(v==values[0] for v in values) else None,basis


def movement_targets(graph,item_id,start=None,remaining_uses=None):
    """All geometry/type candidates for one item; no random winner or probability."""
    item=_item(item_id,'MOVE');raw=item['raw'];nodes,start=_graph(graph,start)
    _integer(remaining_uses,'剩余次数',optional=True)
    if remaining_uses is not None and remaining_uses>raw['count']:
        raise ValueError('剩余次数超过固定原件初始次数；额外来源次数尚未核验。')
    if raw['rangeType']=='RANGE':
        offsets={(p['row'],p['col']) for p in reference_data()['ranges'][raw['range']]['grids']}
    else: offsets=None
    origin=nodes[start];rows=[];excluded=[];same=[]
    for key,node in nodes.items():
        if key==start:
            same.append({'node_id':key,'status':'same_position_reentry_unknown'});continue
        delta=(node['row']-origin['row'],node['col']-origin['col'])
        geometry=offsets is None or delta in offsets
        membership,basis=_membership(node,raw['node'])
        row={'node_id':key,'position':{'row':node['row'],'col':node['col']},
             'delta':{'row':delta[0],'col':delta[1]},'geometry_matches':geometry,
             'node_type_matches':membership,'type_basis':basis,
             'remaining_uses_declared':remaining_uses,'uses_available':None if remaining_uses is None else remaining_uses>0,
             'base_ap_cost':raw['step'],'actual_entry_eligible':None,
             'is_random_destination':raw['isRandomMove'],'probability':None}
        if not geometry or membership is False or remaining_uses==0:
            row['excluded_reasons']=[label for condition,label in ((not geometry,'outside_fixed_range'),
                (membership is False,'declared_node_type_mismatch'),(remaining_uses==0,'declared_uses_exhausted')) if condition]
            excluded.append(row)
        else: rows.append(row)
    return _result(item=deepcopy(item),start=start,targets=rows,excluded=excluded,
                   same_position=same,range_reference=deepcopy(reference_data()['ranges'].get(raw['range'])),
                   random_selection_verified=False,inventory_initial_uses=raw['count'])


def _and(*values):
    return False if False in values else None if None in values else True


MOVEMENT_GAINS={'rogue_6_scrap_M_09':[{'resource':'hope','amount':2}],
                'rogue_6_scrap_M_10':[{'resource':'gold','amount':4}],
                'rogue_6_scrap_M_12':[{'resource':'ap','amount':3}]}
PASSIVE_EFFECTS={
    'rogue_6_scrap_P_01':[{'resource':'battle_attack_speed_reference','amount':50},
                        {'resource':'random_relic','amount':1,'timing':'after_battle'}],
    'rogue_6_scrap_P_02':[{'resource':'random_relic','amount':1}],
    'rogue_6_scrap_P_03':[{'resource':'shield','amount':3}],
    'rogue_6_scrap_P_04':[{'resource':'battle_attack_speed_reference','amount':35}],
    'rogue_6_scrap_P_05':[{'resource':'random_relic','amount':1}],
    'rogue_6_scrap_P_06':[{'resource':'random_relic','amount':2}],
}


def movement_effects(graph,item_id,target,start=None,remaining_uses=None,passive_items=None):
    """Source-stated movement grants and each passive condition, kept separate."""
    result=movement_targets(graph,item_id,start,remaining_uses);nodes,_=_graph(graph,start)
    if not isinstance(target,str) or target not in nodes: raise ValueError('目的地必须在声明地图中。')
    destination=next((row for row in result['targets']+result['excluded'] if row['node_id']==target),None)
    if destination is None: raise ValueError('同格再进入适用性未知，不能作为加工品移动收益计算。')
    eligible=_and(destination['geometry_matches'],destination['node_type_matches'],destination['uses_available'])
    selection_condition=None if result['item']['raw']['isRandomMove'] else True
    grants=[{**deepcopy(grant),'condition_matches':_and(eligible,selection_condition),
             'actual_granted':None,'source_selector':result['item']['source_selector']}
            for grant in MOVEMENT_GAINS.get(item_id,[])]
    if passive_items is None:passive_items=[]
    if not isinstance(passive_items,list): raise ValueError('概念体持有声明需要对象列表。')
    passives=[];seen=set()
    for declaration in passive_items:
        if not isinstance(declaration,dict): raise ValueError('概念体声明需要对象。')
        item=_item(declaration.get('item_id'),'PASSIVE');key=item['id']
        if key in seen: raise ValueError('同一概念体重复持有叠加未核验，请分别保留来源，不合并计算。')
        seen.add(key);remaining=declaration.get('remaining_activations')
        _integer(remaining,'概念体剩余激活次数',optional=True)
        limited=key in ('rogue_6_scrap_P_01','rogue_6_scrap_P_02','rogue_6_scrap_P_03')
        if limited and remaining is not None and remaining>1:
            raise ValueError('一次性概念体声明激活次数超过固定描述。')
        availability=None if remaining is None else remaining>0
        match,basis=_membership(nodes[target],[item['raw']['node']])
        condition=_and(eligible,selection_condition,match,availability)
        passives.append({'item_id':key,'name':item['name'],'node_type_matches':match,'type_basis':basis,
                         'activation_available_declared':availability,'remaining_activations_declared':remaining,
                         'source_stated_single_activation':limited,'condition_matches':condition,
                         'effects':deepcopy(PASSIVE_EFFECTS[key]),'source_selector':item['source_selector'],
                         'random_reward_pool_known':False,'actual_activation':None})
    return _result(item=result['item'],start=result['start'],target=target,destination=destination,
                   declared_move_condition_matches=eligible,random_target_selection_condition=selection_condition,
                   movement_grants=grants,passives=passives,actual_new_resources=None,
                   combat_modifiers_applied=False,passive_stacking_verified=False,
                   additional_limits=['住民临时占领不自动改写原节点类型；特殊转换的原始节点归属须明确。',
                                      '攻速仅列触发资料，未接入战斗计算；随机收藏品仅有描述数量，不生成具名池。'])


def _zone(row):
    key=row['raw']['id'];mission=row['mission']['bannerText'];hint=row['exhaustion']['hintText']
    outcome='pursuit' if '追猎' in hint else 'return_original_zone' if '返回' in hint else None
    goal='BATTLE_BOSS' if '险路恶敌' in mission else 'FINAL' if '险路尽头' in mission else None
    return {'zone_id':key,'name':row['raw']['name'],'mission_text':mission,'exhaustion_text':hint,
            'goal_node_type':goal,'goal_requires_battle_victory':goal=='BATTLE_BOSS',
            'source_stated_exhaustion_outcome':outcome,
            'original_return_zone_identity':None,'source_selector':row['source_selector'],
            'layout_edges_verified':False}


def zone_catalog():
    """Keep all original zone IDs, including portals sharing one display name."""
    return _result(zones=[_zone(row) for row in reference_data()['zones'].values()])


def zone_budget(zone_id,action_points=None,walking_steps=None,item_id=None,goal_completed=None):
    """Payment subtotal and zone-specific exhaustion conditions, without ordering guesses."""
    if not isinstance(zone_id,str) or zone_id not in reference_data()['zones']:
        raise ValueError('区域需要固定原件中的唯一标识。')
    _integer(action_points,'行动力',optional=True);_integer(walking_steps,'徒步格点数',optional=True)
    if goal_completed is not None and type(goal_completed) is not bool:
        raise ValueError('目标完成状态需要布尔值或留空。')
    if walking_steps is not None and item_id is not None:
        raise ValueError('徒步与加工品分别是一种移动方案，不能同时填入。')
    item=_item(item_id,'MOVE') if item_id is not None else None
    cost=item['raw']['step'] if item else walking_steps
    grant=sum(row['amount'] for row in MOVEMENT_GAINS.get(item_id,[]) if row['resource']=='ap') if item else 0
    affordability=None if cost is None or action_points is None else action_points>=cost
    after_payment=action_points-cost if affordability is True else None
    after_grant=after_payment+grant if after_payment is not None else None
    zone=_zone(reference_data()['zones'][zone_id]);source_outcome=zone['source_stated_exhaustion_outcome']
    outcomes=[]
    if source_outcome=='pursuit':
        outcomes=[{'outcome':'pursuit','condition':'行动力耗尽且区域目标未完成',
                   'goal_condition_matches':None if goal_completed is None else not goal_completed},
                  {'outcome':'goal_resolved','condition':'区域目标完成；离层/结局实际流程另外核验',
                   'goal_condition_matches':goal_completed}]
    elif source_outcome=='return_original_zone':
        outcomes=[{'outcome':'return_original_zone','condition':'特殊区域行动力耗尽',
                   'goal_condition_matches':True,'return_zone_id':None}]
    boundary=after_payment==0 if after_payment is not None else None
    return _result(zone=zone,action_points_declared=action_points,walking_steps_declared=walking_steps,
                   movement_item=deepcopy(item),base_ap_cost=cost,source_stated_movement_ap_grant=grant,
                   base_cost_affordable=affordability,nominal_ap_after_payment=after_payment,
                   nominal_ap_after_stated_grant=after_grant,goal_completed_declared=goal_completed,
                   payment_zero_boundary=boundary,conditional_outcomes=outcomes,
                   actual_exhaustion_trigger=None,actual_final_ap=None,
                   limits=deepcopy(reference_data()['limits'])+[
                       '徒步格点数是声明成本；完成标志、住民、迷雾及其他来源费用未自动取得。',
                       '付款、移动奖励、羽瞰点返还及出口处理的执行顺序未核验；到零后再返还不能据此保证免追猎。',
                       '首领节点抵达不等于击败；特殊区返回原区域不冒充进入下一主层。'])


GOODS_EVENTS=('battle_completed','node_revealed','operator_recruited','movement_completed',
              'parts_obtained','item_obtained')
GOODS_DELTAS={
    ('rogue_6_scrap_G_02','battle_completed'):2,
    ('rogue_6_scrap_G_03','node_revealed'):1,
    ('rogue_6_scrap_G_04','operator_recruited'):3,
    ('rogue_6_scrap_G_07','parts_obtained'):1,
    ('rogue_6_scrap_G_09','parts_obtained'):4,
    ('rogue_6_scrap_G_10','movement_completed'):-2,
}


def goods_valuation(item_id,events=None,initial_estimate=None):
    """Source-backed estimate deltas over a declared event ledger; never a sale quote."""
    item=_item(item_id,'GOODS');_integer(initial_estimate,'初始估价',optional=True)
    if events is None:events=[]
    if not isinstance(events,list) or len(events)>1000: raise ValueError('估价事件需要至多1000项对象列表。')
    initial=item['raw']['sellPrice'] if initial_estimate is None else initial_estimate
    known_delta=0;unknown=[];rows=[];destroyed=False;destroyed_unknown=False;grants=[]
    for ordinal,event in enumerate(events,1):
        if not isinstance(event,dict) or event.get('kind') not in GOODS_EVENTS:
            raise ValueError('估价事件类别不在支持目录中。')
        count=event.get('count',1);_integer(count,'独立触发次数')
        perfect=event.get('perfect')
        if perfect is not None and type(perfect) is not bool: raise ValueError('完美作战需要布尔值或留空。')
        kind=event['kind'];delta=0;reasons=[];effects=[];status='no_source_stated_effect'
        if destroyed:
            status='after_declared_destruction'
        elif count:
            if (item_id,kind) in GOODS_DELTAS:
                delta=GOODS_DELTAS[(item_id,kind)]*count;status='known_description_delta'
            if item_id=='rogue_6_scrap_G_05' and kind=='movement_completed':
                reasons.append('每次移动后的随机估价变化缺范围和数值原件');status='random_change_unknown'
            if item_id=='rogue_6_scrap_G_06' and kind=='battle_completed':
                if perfect is True:
                    delta=4*count;status='known_description_delta'
                elif perfect is False:
                    destroyed=True;status='source_stated_destruction'
                else:
                    destroyed_unknown=True;reasons.append('作战完美状态未知：+4或损坏两个分支均保留')
                    effects=[{'condition':'perfect','estimate_delta':4*count},
                             {'condition':'nonperfect','destroyed':True}];status='condition_unknown'
            if item_id=='rogue_6_scrap_G_07' and kind=='item_obtained':
                grant={'item_id':'rogue_6_scrap_G_08','name':reference_data()['items']['rogue_6_scrap_G_08']['name'],
                       'quantity':3*count,'condition':'声明获得多生苔藓','source_selector':item['source_selector']}
                grants.append(grant);effects.append(deepcopy(grant));status='named_grant_reference'
                reasons.append('自身获得及派生3零件是否触发估价链的顺序/计数未核验；不自动追加parts_obtained')
        if destroyed_unknown and not destroyed:
            reasons.append('前序可能损坏，后续触发是否仍有效未知')
        known_delta+=delta
        for reason in reasons:unknown.append({'event_ordinal':ordinal,'reason':reason})
        rows.append({'event_ordinal':ordinal,'kind':kind,'count_declared':count,'perfect_declared':perfect,
                     'known_description_delta':delta,'status':status,'conditional_effects':effects,
                     'subtotal_before_unknown_effects':initial+known_delta,'source_selector':item['source_selector']})
    arithmetic=initial+known_delta
    return _result(item=deepcopy(item),initial_estimate_reference=initial,
                   initial_estimate_basis='fixed_sellPrice_parameter' if initial_estimate is None else 'caller_declaration',
                   events=rows,known_description_delta=known_delta,arithmetic_subtotal=arithmetic,
                   nominal_estimate=None if unknown or destroyed or destroyed_unknown else arithmetic,
                   destroyed_in_declared_ledger=destroyed,destruction_condition_unknown=destroyed_unknown,
                   unknown_effects=unknown,named_grant_references=grants,actual_sell_value=None,
                   valuation_floor_and_cap_verified=False,
                   limits=deepcopy(reference_data()['limits'])+[
                       'count表示声明的独立触发次数，不把一次批量获得自动拆成若干触发。',
                       '估价上下限、售卖修正、派生连锁与真实当前估价未自动取得；算术小计不是售价。',
                       '种子培育奖励、笼控器事件作用与随机价格范围没有完整池，保持原文参考。'])


ROUTE_RULES_SOURCE={'url':'https://prts.wiki/w/沉沦者的黑流树海',
                    'sha256':'b7a0e04867c45642914e9dd8ae2e3dbc51efd0c86b76d8e9f1bd42ac5eade381',
                    'checked_at':'2026-10-04','receipt':'.cache/research/routes-049/evidence.json',
                    'scope':'cached_complete_page; not a new current-server verification'}


def _passability(node):
    if node.get('occupied_declared') is True or node.get('other_blocked_declared') is True:return False
    types,_=_type_candidates(node)
    exception=bool(types) and all(key in ('EMPTY','DOOR') for key in types)
    completion=True if exception else node.get('completed_declared')
    return _and(completion,None if node.get('occupied_declared') is None else not node['occupied_declared'],
                None if node.get('other_blocked_declared') is None else not node['other_blocked_declared'])


def _adjacency(graph,nodes):
    edges=graph.get('edges')
    if not isinstance(edges,list):raise ValueError('步行方案需要声明连线列表。')
    adjacency={key:set() for key in nodes}
    for edge in edges:
        if (not isinstance(edge,(list,tuple)) or len(edge)!=2 or
            any(not isinstance(key,str) or key not in nodes for key in edge) or edge[0]==edge[1]):
            raise ValueError('连线必须是两个已知不同节点标识。')
        a,b=edge;adjacency[a].add(b);adjacency[b].add(a)
    return adjacency


def _walking_paths(graph,nodes,start,target):
    adjacency=_adjacency(graph,nodes);results={}
    for mode in ('topology','no_known_blocker','declared_clear'):
        previous={start:None};queue=deque([start])
        while queue and target not in previous:
            key=queue.popleft()
            for other in sorted(adjacency[key],key=lambda k:(nodes[k]['row'],nodes[k]['col'],k)):
                if other in previous:continue
                if other!=target and mode!='topology':
                    status=_passability(nodes[other])
                    if status is False or (mode=='declared_clear' and status is not True):continue
                previous[other]=key;queue.append(other)
        if target not in previous:results[mode]=None;continue
        path=[target]
        while path[-1]!=start:path.append(previous[path[-1]])
        path.reverse()
        results[mode]={'path':path,'steps':len(path)-1,
                       'intermediate_conditions':[{'node_id':key,'passability':_passability(nodes[key])}
                                                  for key in path[1:-1]]}
    return results


def movement_options(graph,target,inventory=None,action_points=None,start=None,passive_items=None,include_walking=True,
                     difficulty=None,split_unlocked=None):
    """Compare all declared item destinations and walking constraints by base cost."""
    nodes,start=_graph(graph,start);_integer(action_points,'行动力',optional=True)
    if not isinstance(target,str) or target not in nodes:raise ValueError('目标需要地图中的明确节点。')
    if type(include_walking) is not bool:raise ValueError('include_walking需要布尔值。')
    if inventory is None:inventory=[]
    if not isinstance(inventory,list) or len(inventory)>100:raise ValueError('加工品库存需要至多100项对象列表。')
    options=[];paths=None;seen=set()
    if include_walking:
        paths=_walking_paths(graph,nodes,start,target)
        candidate=paths['no_known_blocker']
        if candidate:
            reentry=start==target;cost=1 if reentry else candidate['steps']
            condition=_and(*(row['passability'] for row in candidate['intermediate_conditions']))
            options.append({'id':'walking','mode':'same_position_reentry_reference' if reentry else 'walking',
                'path':candidate['path'],'steps':candidate['steps'],'base_ap_cost':cost,
                'known_conditions_match':None if reentry else condition,
                'base_cost_affordable':None if action_points is None else action_points>=cost,
                'remaining_uses_declared':None,'actual_entry_eligible':None,
                'movement_grants':[],'passives':[],'source':deepcopy(ROUTE_RULES_SOURCE)})
    for ordinal,declaration in enumerate(inventory,1):
        if not isinstance(declaration,dict):raise ValueError('每个加工品库存条目需要对象。')
        item_id=declaration.get('item_id');item=_item(item_id,'MOVE');instance=declaration.get('instance_id',f'inventory:{ordinal}')
        if not isinstance(instance,str) or not instance or instance in seen:raise ValueError('库存实例标识需要唯一非空文字。')
        seen.add(instance)
        if target==start:continue
        effects=movement_effects(graph,item_id,target,start,declaration.get('remaining_uses'),passive_items)
        row=effects['destination'];condition=_and(effects['declared_move_condition_matches'],
                                                effects['random_target_selection_condition'])
        options.append({'id':instance,'mode':'processed_item','item_id':item_id,'name':item['name'],
            'is_random_destination':item['raw']['isRandomMove'],'probability':None,
            'base_ap_cost':row['base_ap_cost'],'remaining_uses_declared':declaration.get('remaining_uses'),
            'known_conditions_match':condition,'excluded_reasons':deepcopy(row.get('excluded_reasons',[])),
            'base_cost_affordable':None if action_points is None else action_points>=row['base_ap_cost'],
            'actual_entry_eligible':None,'movement_grants':effects['movement_grants'],'passives':effects['passives'],
            'source_selector':item['source_selector']})
    types,_=_type_candidates(nodes[target])
    arrival=arrival_reference(nodes[target],types,difficulty=difficulty,split_unlocked=split_unlocked)
    for row in options:
        item_grants=[g for g in row['movement_grants'] if g['resource']=='ap']
        item_ap=None if any(g['condition_matches'] is None for g in item_grants) else sum(g['amount'] for g in item_grants if g['condition_matches'] is True)
        payment=None if action_points is None or row['base_cost_affordable'] is False else action_points-row['base_ap_cost']
        node_ap=arrival['node_arrival_ap_reference']
        row.update(node_arrival_reference=deepcopy(arrival),item_ap_grant_reference=item_ap,
                   nominal_ap_after_payment_reference=payment,
                   nominal_ap_after_combined_grants_reference=None if payment is None or item_ap is None or node_ap is None else payment+item_ap+node_ap,
                   payment_zero_boundary_reference=None if payment is None else payment==0,
                   actual_ap_after_arrival=None)
    candidates=[row for row in options if row['known_conditions_match'] is not False and row['base_cost_affordable'] is not False]
    minimum=min((row['base_ap_cost'] for row in candidates),default=None)
    return _result(start=start,target=target,action_points_declared=action_points,walking_paths=paths,
                   options=options,node_arrival_reference=arrival,minimum_base_ap_cost_reference=minimum,
                   minimum_base_cost_candidates=[row['id'] for row in candidates if row['base_ap_cost']==minimum],
                   actual_best_route=None,limits=deepcopy(reference_data()['limits'])+[
                       '完成、住民和其他阻碍仅用明确声明；未知保留，已占领中途节点阻断步行。',
                       '加工品直达不受未完成中途节点阻断，但真实资格仍未知；每个库存实例独立保留。',
                       '最低基础成本只是候选比较，不是最优收益、确定可用方案或游戏操作。',
                       '羽瞰点只在明确首次且未领取声明下计入+1；历史类型或visited不补领取状态。',
                       '付款资格先核对基础成本，不能用到达后返还透支；付款到0的触发顺序未知。',
                       'AP小计只含移动、加工品和受约束的羽瞰点组件；其他节点结算及完整实际AP未知。'])


def itinerary(graph,steps,inventory=None,action_points=None,start=None,passive_items=None,
              difficulty=None,split_unlocked=None):
    """A scratch reference ledger for a declared multi-move plan, never run memory."""
    nodes,start=_graph(graph,start);_integer(action_points,'行动力',optional=True)
    if not isinstance(steps,list) or not 1<=len(steps)<=100:raise ValueError('移动计划需要1–100项步骤对象。')
    if inventory is None:inventory=[]
    if not isinstance(inventory,list):raise ValueError('库存需要对象列表。')
    stock=deepcopy(inventory);passives=deepcopy(passive_items or []);seen=set()
    for ordinal,entry in enumerate(stock,1):
        if not isinstance(entry,dict):raise ValueError('库存条目需要对象。')
        _item(entry.get('item_id'),'MOVE')
        instance=entry.setdefault('instance_id',f'inventory:{ordinal}')
        if not isinstance(instance,str) or not instance or instance in seen:raise ValueError('库存实例标识必须唯一。')
        seen.add(instance);_integer(entry.get('remaining_uses'),'加工品剩余次数',optional=True)
    cursor=start;ap=action_points;rows=[];stopped=None;known_cost=0;known_ap_grant=0;known_node_ap=0;conditions_known=True
    plan_graph=deepcopy(graph)
    for ordinal,step in enumerate(steps,1):
        if not isinstance(step,dict) or not isinstance(step.get('mode'),str):raise ValueError('每步需要移动mode和target。')
        target=step.get('target')
        if not isinstance(target,str) or target not in nodes:raise ValueError('每步目的地必须属于声明图。')
        if stopped:
            assumed_start=steps[ordinal-2]['target']
            scratch=deepcopy(plan_graph);scratch['current_node']=assumed_start
            unknown_stock=deepcopy(stock);unknown_passives=deepcopy(passives)
            for item in unknown_stock:item['remaining_uses']=None
            for passive in unknown_passives:passive['remaining_activations']=None
            independent=movement_options(scratch,target,unknown_stock,None,assumed_start,unknown_passives,
                                         difficulty=difficulty,split_unlocked=split_unlocked)
            selected=next((r for r in independent['options'] if r['id']==step['mode']),None)
            rows.append({'step':ordinal,'target':target,'status':'not_evaluated_after_stop','reason':stopped,
                         'declared_step':deepcopy(step),'assumed_start_from_declared_plan':assumed_start,
                         'independent_declared_option_reference':selected,'actual_continuation':None});continue
        scratch=deepcopy(plan_graph);scratch['current_node']=cursor
        options=movement_options(scratch,target,stock,ap,cursor,passives,
                                 difficulty=difficulty,split_unlocked=split_unlocked)
        selected=next((row for row in options['options'] if row['id']==step['mode']),None)
        if selected is None:raise ValueError('所选mode没有对应步行候选或库存实例。')
        if selected['known_conditions_match'] is False or selected['base_cost_affordable'] is False:
            stopped='known_condition_or_ap_failed';conditions_known=False
            rows.append({'step':ordinal,'target':target,'status':'blocked','option':selected,'reason':stopped});continue
        if selected['known_conditions_match'] is None:
            stopped='eligibility_or_inventory_condition_unknown';conditions_known=False
            rows.append({'step':ordinal,'target':target,'status':'unresolved','option':selected,'reason':stopped});continue
        cost=selected['base_ap_cost'];grant=sum(g['amount'] for g in selected['movement_grants']
                                               if g['resource']=='ap' and g['condition_matches'] is True)
        after_payment=None if ap is None else ap-cost
        arrival=selected['node_arrival_reference'];node_ap=arrival['node_arrival_ap_reference']
        # Unknown arrival AP is absent from the known subtotal. The combined
        # reference stays None and cannot fund the dependent next step.
        after_known=None if after_payment is None else after_payment+grant+(node_ap or 0)
        after_grant=None if after_payment is None or node_ap is None else after_payment+grant+node_ap
        known_cost+=cost;known_ap_grant+=grant;known_node_ap+=node_ap or 0
        if selected['mode']=='processed_item':
            entry=next(e for e in stock if e['instance_id']==step['mode'])
            entry['remaining_uses']-=1;entry['nominal_destroyed']=entry['remaining_uses']==0
        passive_rows=[]
        for row in selected['passives']:
            declaration=next(e for e in passives if e['item_id']==row['item_id'])
            if row['condition_matches'] is True and row['source_stated_single_activation']:
                declaration['remaining_activations']-=1
            passive_rows.append({'item_id':row['item_id'],'condition_matches':row['condition_matches'],
                'remaining_activations_reference':declaration.get('remaining_activations'),
                'effects':deepcopy(row['effects']),'actual_activation':None})
        boundary=after_payment==0 if after_payment is not None else None
        if boundary or ap is None:conditions_known=False
        rows.append({'step':ordinal,'start':cursor,'target':target,'status':'conditional_reference_step',
                     'option':selected,'base_ap_cost':cost,'stated_ap_grant':grant,
                     'nominal_ap_after_payment':after_payment,'nominal_ap_after_stated_grant':after_grant,
                     'stated_node_arrival_ap_grant':node_ap,'node_arrival_reference':arrival,
                     'nominal_ap_after_known_grants_subtotal':after_known,
                     'unknown_ap_components':['node_arrival'] if node_ap is None else [],
                     'payment_zero_boundary':boundary,'passive_reference_states':passive_rows,
                     'actual_move_succeeded':None})
        if arrival['first_component_condition_matches'] is True:
            next(n for n in plan_graph['nodes'] if n['id']==target)['light_arrival_declaration']={'first_entry':False,'reward_received':True}
        ap=after_grant;cursor=target
        if boundary:
            stopped='zero_ap_callback_order_unverified';conditions_known=False
        elif node_ap is None:
            stopped='node_arrival_ap_condition_unknown';conditions_known=False
    return _result(start=start,steps=rows,known_base_ap_cost_sum=known_cost,known_stated_ap_grant_sum=known_ap_grant,
                   known_node_arrival_ap_grant_sum=known_node_ap,known_combined_ap_grant_sum=known_ap_grant+known_node_ap,
                   node_arrival_reference_state_scope='conditional_plan_only',
                   node_arrival_reference_state=[{'node_id':n['id'],'light_arrival_declaration':deepcopy(n['light_arrival_declaration'])}
                       for n in plan_graph['nodes'] if 'light_arrival_declaration' in n],
                   inventory_reference_state=stock,passive_reference_state=passives,
                   nominal_position=cursor,nominal_final_ap=ap,complete_declared_conditions=conditions_known and not stopped,
                   stopped_reason=stopped,actual_final_position=None,actual_final_inventory=None,actual_final_ap=None,
                   limits=deepcopy(reference_data()['limits'])+[
                       '账本只对声明方案扣减已证使用次数，不更新本局持有或清空记忆。',
                       '随机落点、未知次数/资格或明确AP不足会停止依赖链，后续步骤保留为未求值。',
                       '居民随移动更新、节点完成/战斗结算、零AP处理与其他费用仍未知，静态声明图不证明实际连续链。',
                       '首次羽瞰点组件只在临时方案中标为已领，不更新本局；再次到达的AP规则未证。',
                       '付款到0或到达AP未知时停止可续行依赖链；尾链保留声明起点及独立条件参考，不断言实际必结束。'])


def region_transition(transition,inventory=None,remaining_ap=None,exit_node_type=None,goal_success=None):
    """Conditional expiry and exit-resource dispositions, keeping portal exceptions."""
    if transition not in ('main_region_advance','portal_enter','portal_return'):
        raise ValueError('转移需要main_region_advance、portal_enter或portal_return。')
    _integer(remaining_ap,'剩余行动力',optional=True)
    if goal_success is not None and type(goal_success) is not bool:raise ValueError('目标成功需要布尔值或留空。')
    if transition=='main_region_advance' and exit_node_type not in ('FINAL','EVACUATE','BATTLE_BOSS'):
        raise ValueError('主区域转移需要明确险路尽头、险路小径或险路恶敌原类型。')
    if transition!='main_region_advance' and exit_node_type is not None:
        raise ValueError('秘境进出不是主区域出口，不填写主区域出口类型。')
    if inventory is None:inventory=[]
    if not isinstance(inventory,list) or len(inventory)>1000:raise ValueError('零件库存需要至多1000项对象列表。')
    rows=[];seen=set();conditional_losses=[];preserved=[]
    for ordinal,entry in enumerate(inventory,1):
        if not isinstance(entry,dict):raise ValueError('库存条目需要对象。')
        item=_item(entry.get('item_id'));instance=entry.get('instance_id',f'inventory:{ordinal}')
        if not isinstance(instance,str) or not instance or instance in seen:raise ValueError('库存实例标识需要唯一非空文字。')
        seen.add(instance);remaining=entry.get('remaining_uses');_integer(remaining,'剩余使用次数',optional=True)
        if remaining is not None and item['kind']!='MOVE':raise ValueError('remaining_uses只用于加工品；概念体另有激活次数。')
        if remaining is not None and remaining>item['raw']['count']:
            raise ValueError('剩余次数超过原件初始次数；额外来源尚未核验。')
        temporary='无法被携带至下一区域' in item['usage']
        expires=temporary and transition=='main_region_advance'
        portal_preserved=temporary and transition in ('portal_enter','portal_return')
        row={'instance_id':instance,'item_id':item['id'],'name':item['name'],'kind':item['kind'],
             'remaining_uses_declared':remaining,'source_stated_main_region_expiry':temporary,
             'expires_if_transition_succeeds':expires,'preserved_by_portal_exception':portal_preserved,
             'transition_success_declared':goal_success,'already_depleted_declared':remaining==0,
             'actual_retained':None,'source_selector':item['source_selector']}
        rows.append(row)
        if expires:conditional_losses.append(instance)
        elif portal_preserved:preserved.append(instance)
    resources={'source_rule_ap_conversion':None,'source_rule_carried_ap':None,'hope_conversion_ratio':None,
               'hope_gain':None,'next_region_total_ap':None,'named_item_grants':[]}
    if transition=='main_region_advance':
        if exit_node_type in ('FINAL','BATTLE_BOSS'):resources['source_rule_ap_conversion']=remaining_ap
        if exit_node_type=='FINAL':
            from .event_planning import final_ap_conversion
            reference=final_ap_conversion(remaining_ap)
            resources['hope_conversion_ratio']=reference['conversion_ratio_reference']
            resources['hope_gain_reference']=reference['hope_gain_reference']
            resources['conversion_original_choice_records']=reference['original_choice_records']
        elif exit_node_type=='EVACUATE':resources['source_rule_carried_ap']=remaining_ap
        if exit_node_type in ('FINAL','EVACUATE'):
            resources['named_item_grants']=[{'kind':'MOVE','quantity':1,'actual_pool_known':False,
                                            'rarity_constraint_known':False,'actual_granted':None}]
    return _result(transition=transition,exit_node_type=exit_node_type,goal_success_declared=goal_success,
                   remaining_ap_declared=remaining_ap,inventory_conditions=rows,
                   losses_if_transition_succeeds=conditional_losses,preserved_by_explicit_portal_exception=preserved,
                   resources=resources,route_rule_source=deepcopy(ROUTE_RULES_SOURCE),
                   actual_transition_completed=None,actual_inventory_after=None,
                   limits=deepcopy(reference_data()['limits'])+[
                       '只有重弹簧和小八界的跨主区域损坏被描述明确列出；其他零件没有新增过期规则。',
                       '秘境进出不损坏这两种暂存加工品，包括秘境获得的；不把秘境当下一主区域。',
                       '险路尽头的原choices明确等量希望，只在FINAL列1:1参考；首领出口比率与新区域总AP不借用此规则。'])


RESIDENT_NAMED_EXCLUSIONS=('BATTLE_SHOP','SCRAP_SHOP','EVACUATE','FINAL','DOOR',
                           'STORY','STORY_HIDDEN','BATTLE_SAVAGE')


def _resident_destination(node):
    types,basis=_type_candidates(node)
    if node.get('repeatable_declared') is True:return False,'declared_repeatable_node'
    if types and all(key in RESIDENT_NAMED_EXCLUSIONS for key in types):return False,'source_named_node_exclusion'
    if types and all(key=='EMPTY' for key in types) and node.get('completed_declared') is True:
        return False,'player_completed_clearing_exclusion'
    if not types:return None,'original_node_type_unknown'
    return None,'no_named_exclusion; full_destination_eligibility_unknown'


def resident_candidates(graph,post_node=None,residents=None,moves=1,floor=None,difficulty=None,
                        recall_mode=None,player_positions=None):
    """Initial connected-distance pool and independent bounded movement candidates."""
    nodes,start=_graph(graph);adjacency=_adjacency(graph,nodes)
    _integer(moves,'玩家移动次数',minimum=1)
    if moves>10:raise ValueError('居民候选展开最多10次移动。')
    if floor is not None and (type(floor) is not int or floor not in range(1,7)):
        raise ValueError('主层需要1–6的整数或留空。')
    _integer(difficulty,'保密等级',optional=True)
    if recall_mode is not None and type(recall_mode) is not bool:raise ValueError('追忆模式需要布尔值或留空。')
    gate=_and(None if floor is None else floor not in (1,6),None if difficulty is None else difficulty>=4)
    spawn=[];excluded=[]
    if post_node is not None:
        if not isinstance(post_node,str) or post_node not in nodes:raise ValueError('据点需要地图中的明确节点。')
        post_types,_=_type_candidates(nodes[post_node])
        if post_types and 'BATTLE_SAVAGE' not in post_types:raise ValueError('声明据点的明确原类型不是居民据点。')
        distances={post_node:0};queue=deque([post_node])
        while queue:
            current=queue.popleft()
            if distances[current]>=5:continue
            for other in adjacency[current]:
                if other not in distances:distances[other]=distances[current]+1;queue.append(other)
        for key,node in nodes.items():
            types,basis=_type_candidates(node);empty=None if not types else all(t=='EMPTY' for t in types)
            row={'node_id':key,'connected_distance':distances.get(key),
                 'initial_clearing_type_matches':empty,'type_basis':basis,'actual_spawn':None,
                 'probability':None,'known_post_gate_matches':gate}
            if key not in distances or empty is False or gate is False:
                row['exclusion_reasons']=[label for condition,label in ((key not in distances,'beyond_five_connected_steps'),
                    (empty is False,'not_original_clearing'),(gate is False,'source_post_gate_mismatch')) if condition]
                excluded.append(row)
            else:spawn.append(row)
    if residents is None:residents=[]
    if not isinstance(residents,list) or len(residents)>100:raise ValueError('居民位置需要至多100项对象列表。')
    if player_positions is not None:
        if (not isinstance(player_positions,list) or len(player_positions)>moves or
            any(not isinstance(key,str) or key not in nodes for key in player_positions)):
            raise ValueError('玩家移动后位置需要地图节点列表，长度不能超过移动次数。')
    movements=[];seen=set();occupied={step:set() for step in range(1,moves+1)}
    for ordinal,resident in enumerate(residents,1):
        if not isinstance(resident,dict) or not isinstance(resident.get('node_id'),str) or resident['node_id'] not in nodes:
            raise ValueError('居民需要地图中的位置。')
        identity=resident.get('id',f'resident:{ordinal}')
        if not isinstance(identity,str) or not identity or identity in seen:raise ValueError('居民标识需要唯一非空文字。')
        seen.add(identity);positions={resident['node_id']};steps=[]
        for step in range(1,moves+1):
            candidates={};rejects=[];fallbacks=[]
            for current in sorted(positions):
                found=False
                for other in sorted(adjacency[current]):
                    status,basis=_resident_destination(nodes[other])
                    row={'from':current,'to':other,'destination_condition_matches':status,'basis':basis,
                         'actual_selected':None,'probability':None}
                    if status is False:rejects.append(row)
                    else:candidates.setdefault(other,[]).append(row);found=True
                if not found:fallbacks.append({'from':current,'possible_position':current,
                                             'condition':'无未排除相邻节点；停留/其他回退规则未知'})
            positions=set(candidates);occupied[step].update(positions)
            steps.append({'movement_step':step,'candidate_positions':sorted(positions),
                          'navigation_candidates':[row for values in candidates.values() for row in values],
                          'source_excluded_transitions':rejects,'unresolved_fallbacks':fallbacks,
                          'actual_position':None})
        movements.append({'resident_id':identity,'initial_position_declared':resident['node_id'],'steps':steps})
    risk=[]
    for step,positions in occupied.items():
        player=player_positions[step-1] if player_positions is not None and step<=len(player_positions) else None
        risk.append({'movement_step':step,'possible_occupied_union':sorted(positions),
                     'player_position_declared':player,'source_candidate_overlap':None if player is None else player in positions,
                     'actual_collision_or_blockage':None})
    maximum=min(3,len(spawn)) if post_node is not None else None
    return _result(post_node=post_node,spawn_candidates=spawn,excluded_spawn_candidates=excluded,
                   source_maximum_residents=3,initial_count_upper_bound=maximum,
                   recalled_count_source_candidates=None if recall_mode is False else list(range((maximum if maximum is not None else 3)+1)),
                   actual_initial_count=None,known_post_gate_matches=gate,movement_candidates=movements,
                   player_route_risk=risk,resident_count_declaration_conflicts_source_max=len(residents)>3,
                   joint_collision_resolution_verified=False,route_rule_source=deepcopy(ROUTE_RULES_SOURCE),
                   limits=deepcopy(reference_data()['limits'])+[
                       '初始仅沿已声明连线计算距居民据点5步以内空地；类型未知仍保留，不用直线距离代替。',
                       '每次移动后相邻一格候选逐步展开；居民之间的碰撞、同步顺序、回退和实际选择未知。',
                       '临时占領不改变概念体原节点归属；候选并集不证明全部位置可以同时被占领。'])


COMMANDS={'items':item_catalog,'targets':movement_targets,'effects':movement_effects,
          'zones':zone_catalog,'budget':zone_budget,'valuation':goods_valuation,'options':movement_options,
          'itinerary':itinerary,'transition':region_transition,'residents':resident_candidates}
COMMANDS['settlements']=settlements

from .route_comparison import compare_routes
COMMANDS["compare-routes"]=compare_routes

from .route_search import search_routes
COMMANDS["search-routes"]=search_routes
