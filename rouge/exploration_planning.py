"""Offline exploration references over explicit graph and inventory declarations.

These functions never read or mutate run state. Range membership, declared
resources and source-backed subtotals are separate from actual game eligibility.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path


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
    types,basis=_type_candidates(node)
    if not types: return None,'node_type_unknown'
    # Group membership is not serialized in this public original table. Preserve
    # every grouped candidate unless the caller explicitly declares the group.
    # Exact enum restrictions (shops, WISH, SACRIFICE) are directly testable.
    if any(key in allowed for key in ('EVENTS','BATTLES')):
        group=node.get('scrap_category')
        if group is None: return None,'original_group_membership_unknown'
        if group not in ('EVENTS','BATTLES','EMPTY'): raise ValueError('scrap_category需要EVENTS、BATTLES或EMPTY。')
        return group in allowed,'declared_scrap_category'
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


COMMANDS={'items':item_catalog,'targets':movement_targets,'effects':movement_effects}
