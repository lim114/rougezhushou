"""Complete public JSON/old errors against one frozen source per process."""
import copy
import gzip
import itertools
import json
import sys
from pathlib import Path

source, output = map(Path, sys.argv[1:3])
sys.path.insert(0, str(source))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import format_report

OP = 'char_1037_amiya3'
cases = []


def scenario(**extra):
    return {'operator': OP, 'skill': 1, 'skill_rank': 7, 'elite': 0,
            'level': 1, 'base_attack': 1000, 'window_seconds': 10, **extra}


def add(label, args):
    cases.append({'label': label, 'scenario': args})


for elite, skill, rank, potential, mode, window in itertools.product(
        (0, 1, 2), (1, 2), (1, 7, 10), range(1, 7), ('frames', 'continuous'), (None, 0, 1, 10)):
    args = scenario(elite=elite, skill=skill, skill_rank=rank, potential=potential,
                    timing_mode=mode, window_seconds=window)
    if window is None:
        del args['window_seconds']
    add('medical-form-cultivation-all-potentials-ranks-skills-windows', args)
for cultivation, skill, stage, mode, window in itertools.product(
        ((0, 50), (1, 70), (2, 49), (2, 50)), (1, 2), (1, 2, 3),
        ('frames', 'continuous'), (0, 10)):
    add('module-three-stages-cultivation-boundary', scenario(elite=cultivation[0], level=cultivation[1],
        skill=skill, module_id='uniequip_002_amiya3', module_level=stage, timing_mode=mode, window_seconds=window))
for elite, skill, mode, extra in itertools.product((0, 1, 2), (1, 2), ('frames', 'continuous'), (
        {'base_attack': 0}, {'healing_targets': 0}, {'healing_targets': 2},
        {'timing': {'target_disappears_seconds': 0}}, {'timing': {'target_windows': []}},
        {'timing': {'interruptions': [[0, 100]]}}, {'timing': {'target_windows': [[3, 5]]}},
        {'effects': [{'kind': 'hp_pct', 'value': 1}]},
        {'effects': [{'kind': 'attack_pct', 'value': .5}]},
        {'relic_ids': ['rogue_6_relic_legacy_81']}, {'enemy_resistance': 100},
        {'skill_duration_seconds': 0}, {'skill_duration_seconds': 1},
        {'inventory_status': {'complete': False, 'recognized': 0}},
        {'unconfirmed_training': ['本局实际培养']}, {'base_hp': 0})):
    add('actual-body-and-target-life-other-pending-and-ignored-hp-field', scenario(
        elite=elite, skill=skill, timing_mode=mode, **extra))
for mode, invalid in itertools.product(('frames', 'continuous'), (
        {'elite': True}, {'level': True}, {'potential': True}, {'skill_rank': True},
        {'elite': -1}, {'level': 0}, {'potential': 0}, {'skill': 0}, {'skill': 3},
        {'module_id': 'uniequip_002_amiya3', 'module_level': True},
        {'module_id': 'uniequip_002_amiya3', 'module_level': 4},
        {'module_id': 'uniequip_002_haruka', 'module_level': 1},
        {'window_seconds': -1}, {'timing_mode': 'unknown'}, {'healing_targets': True},
        {'elite': 0, 'skill': 2, 'amiya_hit_targets': True},
        {'elite': 1, 'skill': 2, 'amiya_hit_targets': True},
        {'elite': 1, 'skill': 2, 'amiya_hit_targets': 'unknown'},
        {'elite': 1, 'skill': 2, 'amiya_hit_targets': 0},
        {'effects': [{'kind': 'hp_pct', 'value': -1}]})):
    add('old-errors-and-prior-skill-gate-order', scenario(**{'timing_mode': mode, **invalid}))
for owner, profile in catalog()['operators'].items():
    for skill in range(1, len(profile['skills']) + 1):
        for mode in ('frames', 'continuous'):
            add('all-default-owners-skills-qualified-control', {'operator': owner, 'skill': skill, 'timing_mode': mode})

cached = json.dumps(catalog(), sort_keys=True, ensure_ascii=False)
outcomes = []
for case in cases:
    args = copy.deepcopy(case['scenario'])
    original = json.dumps(args, sort_keys=True, ensure_ascii=False)
    try:
        result = calculate_damage(args)
        outcome = {'result': result, 'text_report': format_report(result)}
    except Exception as exc:
        outcome = {'error_type': type(exc).__name__, 'error': str(exc)}
    assert json.dumps(args, sort_keys=True, ensure_ascii=False) == original
    outcomes.append({**case, 'outcome': outcome})
assert json.dumps(catalog(), sort_keys=True, ensure_ascii=False) == cached
with gzip.open(output, 'wt', encoding='utf-8') as f:
    json.dump(outcomes, f, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
print(json.dumps({'cases': len(outcomes), 'fresh_public_calls': len(outcomes),
    'successes': sum('result' in c['outcome'] for c in outcomes),
    'errors': sum('error' in c['outcome'] for c in outcomes), 'inputs_and_catalog_unchanged': True}))
