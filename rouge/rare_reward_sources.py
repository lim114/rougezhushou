"""Conditional enemy-documentation rewards at exact fixed SPAWN sources.

A reference is not an observed kill, selected random member or received relic.
The community quantity is never substituted for an unverified actual total.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from .battle_preview import battle_data, route_reference


@lru_cache(maxsize=1)
def rare_reward_data():
    return json.loads((Path(__file__).with_name('data') / 'rare-reward-sources.json').read_text(encoding='utf-8'))


def documented_reward_rule(entity_id, refs):
    data = rare_reward_data()
    if entity_id not in data['identities']:
        raise ValueError('Unknown original mimic enemy ID.')
    doc = data['documented_outcomes'].get(entity_id)
    levels = sorted({r['raw']['level'] for r in refs
        if type(r.get('raw', {}).get('level')) is int and r['raw']['level'] >= 0})
    quantities = [doc['documented_reward_by_level'].get(str(level)) for level in levels] if doc else []
    quantity = quantities[0] if quantities and all(v == quantities[0] and v is not None for v in quantities) else None
    complete_refs = bool(refs) and len(levels) > 0 and all(type(r.get('raw', {}).get('level')) is int
        and r['raw']['level'] >= 0 and r['raw'].get('id') == entity_id
        and r['raw'].get('useDb') is True for r in refs)
    if not complete_refs:
        quantity = None
    source = deepcopy(doc) if doc else {'url': data['sources']['selected_original']['file'],
        'scope': 'Original identity only; no supported reward quantity documentation.'}
    return {'entity_id': entity_id, 'name': data['identities'][entity_id]['name'],
        'referenced_levels': levels, 'all_fixed_level_candidates_documented': complete_refs and bool(quantities) and None not in quantities,
        'action_level_binding_unique': len(levels) == 1 and complete_refs,
        'quantity_source': source, 'actual_reward': None,
        'outcomes': [{'condition': 'defeated_and_battle_settlement',
            'condition_label': '该敌人被击倒后战斗结算；当前模式实际执行未证',
            'resource': 'random_relic', 'quantity': quantity,
            'complete_item_pool_known': False, 'actual_quantity': None}],
        'quantity_scope_notice': '数量仅为对应固定级别的敌人文档参考；未证明本实例实际掉落、完整收藏品池或当前服务器结算脚本。',
        'current_rogue6_server_script_verified': False, 'complete_relic_pool_known': False}


def rare_stage_reward_sources(stage_id):
    if not isinstance(stage_id, str) or not stage_id:
        raise ValueError('Need an exact fixed stage ID.')
    stage = battle_data()['stages'].get(stage_id)
    data = rare_reward_data()
    index = data['stages'].get(stage_id)
    if stage is None or index is None:
        raise ValueError('Unknown fixed rare-reward stage.')
    level = data['levels'][index['level_key']]
    if stage['level_source']['sha256'] != level['source']['sha256'] or stage['name'] != index['name'] or stage['difficulty'] != index['difficulty']:
        raise ValueError('Fixed reward level/stage identity changed.')
    rows = []
    for raw in level['actions']:
        row = deepcopy(raw)
        row['kind'] = 'rare_enemy_action'
        row['display_cell'] = None
        row['position_source_selector'] = None
        if not row['branch']:
            route_index = row['raw'].get('routeIndex')
            route = route_reference(stage, route_index)
            row['display_cell'] = deepcopy(route['start'])
            if row['display_cell'] is not None:
                row['position_source_selector'] = f'$.routes[{route_index}].startPosition'
            row['nominal_route_reference'] = route
        else:
            row['nominal_route_reference'] = None
        row['rule'] = documented_reward_rule(row['entity_id'], row['enemy_db_refs'])
        row['candidate_group_reference'] = next((deepcopy(g) for g in level['random_groups']
            if g['queue_id'] == row['queue_id'] and g['group_key'] == row['random_group_key']), None)
        row.update(actual_activation=None, actual_outcome=None, actual_reward=None,
            quantity_is_total=False, actual_spawn_level=None, actual_defeated_count=None,
            actual_received_relic=None, probability=None)
        rows.append(row)
    return {'stage_id': stage_id, 'stage_name': stage['name'], 'rows': rows,
        'random_groups': deepcopy(level['random_groups']),
        'initial_enemy_records': deepcopy(level['initial_enemy_records']),
        'source': deepcopy(level['source']), 'actual_reward_total': None,
        'complete_settlement_pool_known': False, 'probability': None,
        'mimic_source_ids': list(data['mimic_ids']),
        'unreferenced_mimic_ids': list(data['unreferenced_mimic_ids']),
        'database_reference_is_spawn_proof': False, 'limits': list(data['limits'])}


def enemy_reward_reference(stage_id, entity_id, level):
    """Selected fixed enemy documentation, hidden for unrelated enemies."""
    stage = battle_data()['stages'].get(stage_id)
    if stage is None or type(level) is not int or level < 0:
        raise ValueError('Need an exact fixed enemy and grade.')
    if not any(e['id'] == entity_id and e['level'] == level for e in stage['enemies']):
        raise ValueError('The enemy grade is not referenced by the fixed stage.')
    data = rare_reward_data()
    if entity_id not in data['identities']:
        return None
    result = rare_stage_reward_sources(stage_id)
    index = data['stages'][stage_id]
    refs = [r for r in data['levels'][index['level_key']]['enemy_db_refs']
        if r['raw'].get('id') == entity_id and type(r['raw'].get('level')) is int
        and r['raw']['level'] == level]
    sources = [deepcopy(r) for r in result['rows'] if r['entity_id'] == entity_id]
    return {'entity_id': entity_id, 'level': level,
        'rule': documented_reward_rule(entity_id, refs), 'fixed_spawn_sources': sources,
        'fixed_spawn_reference_count': len(sources), 'actual_spawned': None,
        'actual_defeated': None, 'actual_received': None,
        'actual_quantity': None, 'complete_relic_pool_known': False,
        'scope': 'fixed_enemy_documentation_reference', 'database_reference_is_spawn_proof': False}
