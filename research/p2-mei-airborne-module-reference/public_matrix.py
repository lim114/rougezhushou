"""Fresh ordinary public calls; retain every complete JSON result or old error."""
import copy
import gzip
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source, output = map(Path, sys.argv[1:3])
sys.path.insert(0, str(source))
from rouge.catalog import catalog
from rouge.damage import calculate_damage

cases = []
def add(label, args):
    cases.append({'label': label, 'scenario': args})

for stage, skill, rank, potential, mode, window, defense in itertools.product(
        (1, 2, 3), (1, 2), (1, 7, 10), (1, 5, 6), ('frames', 'continuous'),
        (None, 0, 1, 10), (0, 200, 10000)):
    args = {'operator': 'char_133_mm', 'skill': skill, 'skill_rank': rank,
            'elite': 2, 'level': 40, 'base_attack': 1000, 'potential': potential,
            'module_id': 'uniequip_002_mm', 'module_level': stage,
            'timing_mode': mode, 'enemy_defense': defense}
    if window is not None:
        args['window_seconds'] = window
    add('qualified-all-levels-ranks-potentials-windows-defense', args)
for stage, skill, rank, mode, training in itertools.product(
        (1, 2, 3), (1, 2), (1, 7), ('frames', 'continuous'),
        ((0, 45), (1, 60), (2, 39), (2, 40), (2, 60))):
    add('training-and-skill-qualification', {'operator': 'char_133_mm', 'skill': skill,
        'skill_rank': rank, 'elite': training[0], 'level': training[1],
        'module_id': 'uniequip_002_mm', 'module_level': stage, 'timing_mode': mode})
for skill, rank, mode in itertools.product((1, 2), (1, 7, 10), ('frames', 'continuous')):
    add('no-module', {'operator': 'char_133_mm', 'skill': skill, 'skill_rank': rank, 'timing_mode': mode})
for stage, skill, mode, constraint in itertools.product((1, 2, 3), (1, 2), ('frames', 'continuous'), (
        {'timing': {'target_disappears_seconds': 0}}, {'timing': {'target_windows': []}},
        {'timing': {'interrupt_windows': [[0, 100]]}},
        {'timing': {'target_windows': [[3, 5]]}, 'window_seconds': 10},
        {'window_seconds': 0}, {'enemy_weight': 0}, {'enemy_name': '飞行目标'},
        {'enemy_is_airborne': True}, {'enemy_is_airborne': False}, {'enemy_is_airborne': 'false'},
        {'effects': [{'kind': 'attack_pct', 'value': .5}, {'kind': 'damage_taken', 'damage_type': 'physical', 'value': .2}]},
        {'relic_ids': ['rogue_6_relic_fight_1']}, {'relic_ids': ['rogue_6_relic_fight_2']},
        {'unconfirmed_training': ['本局实际培养']}, {'inventory_status': {'complete': False, 'recognized': 0}})):
    add('unchanged-math-clock-scope-and-no-flight-inference', {'operator': 'char_133_mm', 'skill': skill,
        'module_id': 'uniequip_002_mm', 'module_level': stage, 'timing_mode': mode, **constraint})
for operator, profile in catalog()['operators'].items():
    for skill in range(1, len(profile['skills']) + 1):
        for mode in ('frames', 'continuous'):
            add('other-owner-or-default-no-module', {'operator': operator, 'skill': skill, 'timing_mode': mode})
for skill, mode, invalid in itertools.product((1, 2), ('frames', 'continuous'), (
        {'elite': True}, {'level': True}, {'potential': True}, {'module_level': True},
        {'module_level': 0}, {'module_level': 4}, {'module_id': 'uniequip_002_cammou'},
        {'skill_rank': True}, {'skill_rank': 11}, {'elite': 1, 'level': 60},
        {'timing_mode': 'unknown'}, {'window_seconds': -1})):
    add('old-error-order', {'operator': 'char_133_mm', 'skill': skill,
        'module_id': 'uniequip_002_mm', 'module_level': 1, 'timing_mode': mode, **invalid})

cached_before = json.dumps(catalog(), sort_keys=True, ensure_ascii=False)
outcomes = []
for index, case in enumerate(cases):
    args = copy.deepcopy(case['scenario'])
    original = copy.deepcopy(args)
    try:
        result = calculate_damage(args)
        outcome = {'result': result}
    except Exception as exc:
        outcome = {'error_type': type(exc).__name__, 'error': str(exc)}
    assert args == original, ('scenario mutation', index)
    outcomes.append({**case, 'outcome': outcome})
assert json.dumps(catalog(), sort_keys=True, ensure_ascii=False) == cached_before
with gzip.open(output, 'wt', encoding='utf-8') as f:
    json.dump(outcomes, f, ensure_ascii=False, separators=(',', ':'))
print(json.dumps({'cases': len(outcomes), 'successes': sum('result' in x['outcome'] for x in outcomes),
                  'errors': sum('error' in x['outcome'] for x in outcomes),
                  'input_and_catalog_unchanged': True}))
