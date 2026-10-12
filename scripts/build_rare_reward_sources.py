"""Build fixed rare-enemy SPAWN references, never selecting random members."""
from pathlib import Path
import copy
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/p3-rare-rewards'


def checked(path, sha):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError('The fixed rare-reward evidence changed: ' + path.name)
    return json.loads(raw)


def extract_level(level, identities):
    rows = []
    groups = []
    for queue in level['queues_with_rare_spawns']:
        path = queue['source_selector']
        actions = queue['raw_actions']
        is_branch = path.startswith('$.branches[')
        grouped = {}
        for i, action in enumerate(actions):
            group = action.get('randomSpawnGroupKey')
            if group:
                grouped.setdefault(group, []).append({'source_selector': path + f'.actions[{i}]',
                    'action_id': path + f'.actions[{i}]', 'raw': copy.deepcopy(action),
                    'name': identities.get(action.get('key'), {}).get('name'),
                    'is_empty_key': not bool(action.get('key'))})
            if action.get('actionType') != 'SPAWN' or action.get('key') not in identities:
                continue
            rows.append({'id': 'rare:' + path + f'.actions[{i}]',
                'source_selector': path + f'.actions[{i}]', 'queue_id': path,
                'entity_id': action['key'], 'name': identities[action['key']]['name'],
                'raw': copy.deepcopy(action), 'branch': is_branch,
                'enemy_db_refs': [copy.deepcopy(r) for r in level['enemy_db_refs'] if r['raw'].get('id') == action['key']],
                'random_group_key': group,
                'package_key': action.get('randomSpawnGroupPackKey')})
        wanted = {r['random_group_key'] for r in rows if r['queue_id'] == path and r['random_group_key']}
        for group in sorted(wanted):
            groups.append({'queue_id': path, 'group_key': group,
                'members': grouped[group], 'actual_choice': None, 'probabilities': None})
    return {'source': copy.deepcopy(level['source']), 'actions': rows, 'random_groups': groups,
        'enemy_db_refs': copy.deepcopy(level['enemy_db_refs']),
        'initial_enemy_records': copy.deepcopy(level['initial_enemy_records']),
        'database_reference_is_spawn_proof': False}


def build(write=False):
    receipt = json.loads((BASE / 'source-receipt.json').read_text(encoding='utf-8'))
    original_source = receipt['sources']['selected_original']
    docs_source = receipt['sources']['documented_outcomes']
    original = checked(ROOT / original_source['file'], original_source['sha256'])
    docs = checked(ROOT / docs_source['file'], docs_source['sha256'])
    identities = {}
    for key in original['mimic_ids']:
        record = original['database_identities'][key]
        if record['raw']['Key'] != key:
            raise ValueError('Mimic original identity changed.')
        zero = next(v['enemyData'] for v in record['raw']['Value'] if v['level'] == 0)
        if not zero['name']['m_defined'] or not zero['prefabKey']['m_defined'] or zero['prefabKey']['m_value'] != key:
            raise ValueError('No explicit original base name/prefab identity.')
        identities[key] = {'name': zero['name']['m_value'],
            'source_selector': record['source_selector'],
            'database_levels': [r['level'] for r in record['raw']['Value']]}
    for key, doc in docs.items():
        if key not in identities or identities[key]['name'] != doc['name']:
            raise ValueError('Documentation name does not match the original identity.')
        if any(str(level) not in doc['documented_reward_by_level'] for level in doc['documented_levels']):
            raise ValueError('A grade does not have explicit reward documentation.')
        if doc['short_quote'] != '被击倒后，在战斗结算时掉落1件收藏品':
            raise ValueError('Review the revised outcome fact before building.')
        if any(type(value) is not int or value != 1 for value in doc['documented_reward_by_level'].values()):
            raise ValueError('Serialized quantities do not match the explicit short source fact.')
    levels = {key: extract_level(row, identities) for key, row in original['levels'].items()}
    entities = sorted({r['entity_id'] for level in levels.values() for r in level['actions']})
    output = {'schema_version': 1, 'game_commit': original['game_commit'],
        'sources': copy.deepcopy(receipt['sources']), 'mimic_ids': original['mimic_ids'],
        'identities': identities, 'documented_outcomes': docs,
        'stages': original['stages'], 'levels': levels,
        'fixed_spawn_entity_ids': entities,
        'unreferenced_mimic_ids': [k for k in original['mimic_ids'] if k not in entities],
        'limits': receipt['limits'], 'license': receipt['license']}
    if write:
        path = ROOT / 'rouge/data/rare-reward-sources.json'
        path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    return output


if __name__ == '__main__':
    result = build(write=True)
    print(json.dumps({'stages': len(result['stages']), 'levels': len(result['levels']),
        'source_mimics': len(result['mimic_ids']), 'fixed_spawn_entities': result['fixed_spawn_entity_ids'],
        'unreferenced_mimics': result['unreferenced_mimic_ids'],
        'unique_level_actions': sum(len(l['actions']) for l in result['levels'].values()),
        'unique_queue_groups': sum(len(l['random_groups']) for l in result['levels'].values())}))
