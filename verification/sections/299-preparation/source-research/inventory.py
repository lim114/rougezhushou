"""CACHE ONLY: read fixed public spawn group declarations; no application imports."""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PATHS = (
    'PROJECT_PROGRESS.md', 'rouge/battle_planning.py', 'rouge/battle_preview.py',
    'rouge/battle_view.py', 'rouge/offline_tools_view.py',
    'rouge/battle_reward_planning.py', 'rouge/rare_reward_sources.py',
    'rouge/data/battle-previews.json', 'rouge/data/battle-reward-reference.json',
    'rouge/data/rare-reward-source-reference.json',
    'tests/test_battle_planning_161_170.py',
)

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

data = json.loads((ROOT / 'rouge/data/battle-previews.json').read_bytes())
pins = {p: digest(ROOT / p) for p in PATHS if (ROOT / p).is_file()}
groups = []
packages = []
actions = Counter()
source_levels = {}
examples = []
group_keys_at_multiple_queues = []
for sid, stage in data['stages'].items():
    stage_groups = defaultdict(list)
    stage_packages = defaultdict(list)
    name_by_id = defaultdict(set)
    level_by_id = defaultdict(set)
    for enemy in stage['enemies']:
        name_by_id[enemy['id']].add(enemy['name'])
        level_by_id[enemy['id']].add(enemy['level'])
    for wave in stage['waves']:
        for fragment in wave['fragments']:
            queue = f"w{wave['index']}.f{fragment['index']}"
            for ordinal, row in enumerate(fragment['actions']):
                action = row['action']
                actions[action['actionType']] += 1
                member = {
                    'action_id': row['id'], 'action_type': action['actionType'],
                    'entity_key': action.get('key'),
                    'names': sorted(name_by_id.get(action.get('key'), ())),
                    'referenced_levels': sorted(level_by_id.get(action.get('key'), ())),
                    'declared_count': action.get('count'),
                    'raw_weight': action.get('weight'),
                    'package_key': action.get('randomSpawnGroupPackKey'),
                    'group_key': action.get('randomSpawnGroupKey'),
                    'hidden_group': action.get('hiddenGroup'),
                    'source_selector': f"$.waves[{wave['index']-1}].fragments[{fragment['index']-1}].actions[{ordinal}]",
                    'full_original_action': action,
                    'actual_selected': None,
                    'probability': None,
                }
                if action.get('randomSpawnGroupKey'):
                    stage_groups[(queue, action['randomSpawnGroupKey'])].append(member)
                if action.get('randomSpawnGroupPackKey'):
                    stage_packages[(queue, action['randomSpawnGroupPackKey'])].append(member)
    for (queue, key), members in stage_groups.items():
        group = {'stage_id': sid, 'stage_name': stage['name'], 'queue_id': queue,
                 'group_key': key, 'members': members,
                 'original_level': stage['level_source'], 'actual_selected': None,
                 'probabilities': None, 'mutual_exclusivity_or_number_selected': None}
        groups.append(group)
        if any(m['action_type'] == 'SPAWN' for m in members) and len(members) > 1:
            examples.append(group)
    for (queue, key), members in stage_packages.items():
        packages.append({'stage_id': sid, 'stage_name': stage['name'],
                         'queue_id': queue, 'package_key': key,
                         'members': members, 'actual_cooccurrence': None})
    keys = defaultdict(set)
    for queue, key in stage_groups:
        keys[key].add(queue)
    for key, queues in keys.items():
        if len(queues) > 1:
            group_keys_at_multiple_queues.append({'stage_id': sid, 'group_key': key,
                                                  'queues': sorted(queues)})
    source_levels[stage['level_source']['sha256']] = stage['level_source']['url']

examples.sort(key=lambda group: (not any(m['action_type'] == 'EMPTY' for m in group['members']),
                                group['stage_id'], group['queue_id'], group['group_key']))
result = {
    'kind': 'CACHE_ONLY_299_FIXED_SPAWN_RELATION_INVENTORY_NOT_PRODUCT_VALIDATION',
    'application_imported': False, 'Qt_tests_game_chat_Git_mutation': False,
    'source_sha256': pins,
    'fixed_stages': len(data['stages']),
    'unique_level_sha256': len(source_levels),
    'main_action_type_counts': dict(actions),
    'queue_scoped_group_records': len(groups),
    'stages_with_groups': len({g['stage_id'] for g in groups}),
    'groups_containing_spawn': sum(any(m['action_type'] == 'SPAWN' for m in g['members']) for g in groups),
    'groups_containing_empty_action': sum(any(m['action_type'] == 'EMPTY' for m in g['members']) for g in groups),
    'queue_scoped_packages': len(packages),
    'stages_with_packages': len({g['stage_id'] for g in packages}),
    'same_group_key_multiple_queues': group_keys_at_multiple_queues,
    'source_level_sha256_to_url': source_levels,
    'examples': examples[:8],
    'all_group_membership_references': groups,
    'all_package_membership_references': packages,
    'no_new_mechanism_claim': True,
    'counts_are_fixed_source_records_not_enemy_counts_probabilities_or_gameplay_observations': True,
}
for path, expected in pins.items():
    assert digest(ROOT / path) == expected, path
target = OUT / 'inventory.json'
target.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({k: v for k, v in result.items() if k not in (
    'source_sha256', 'examples', 'all_group_membership_references',
    'all_package_membership_references', 'source_level_sha256_to_url',
    'same_group_key_multiple_queues')}, ensure_ascii=False))
print('output_sha256=' + digest(target))
