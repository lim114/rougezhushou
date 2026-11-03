"""Complete ordinary public outcomes from one immutable source tree per process."""
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

OP = 'char_4202_haruka'
MODULE = 'uniequip_002_haruka'
cases = []


def add(label, args):
    cases.append({'label': label, 'scenario': args})


def scenario(**extra):
    return {'operator': OP, 'skill': 1, 'skill_rank': 7, 'elite': 1,
            'level': 1, 'base_attack': 1000, 'window_seconds': 10,
            'bubble_bursts': 1, **extra}


for cultivation, rank, potential, mode, bursts in itertools.product(
        ((0, 1), (1, 1), (1, 2)), (1, 4, 7), range(1, 7),
        ('frames', 'continuous'), (0, 1, 2, '1.0', '1e0')):
    add('locked-talent-real-skills-all-potentials-ranks-legal-counts', scenario(
        elite=cultivation[0], skill=cultivation[1], skill_rank=rank,
        potential=potential, timing_mode=mode, bubble_bursts=bursts))

for skill, rank, potential, mode, bursts in itertools.product(
        (1, 2, 3), (1, 7, 10), range(1, 7), ('frames', 'continuous'), (0, 1, 2)):
    add('e2-genuine-unknown-complete-old-output', scenario(elite=2, skill=skill,
        skill_rank=rank, potential=potential, timing_mode=mode, bubble_bursts=bursts))

for cultivation, stage, skill, potential, mode in itertools.product(
        ((0, 50), (1, 80), (2, 59), (2, 60)), (1, 2, 3), (1, 2),
        (1, 5), ('frames', 'continuous')):
    add('module-all-stages-unlock-boundary-no-new-talent-grant', scenario(
        elite=cultivation[0], level=cultivation[1], module_id=MODULE,
        module_level=stage, skill=skill, potential=potential, timing_mode=mode))

constraints = (
    {'window_seconds': None}, {'window_seconds': 0}, {'window_seconds': 1},
    {'timing': {'target_disappears_seconds': 0}}, {'timing': {'target_windows': []}},
    {'timing': {'interruptions': [[0, 100]]}},
    {'timing': {'target_windows': [[3, 5]]}},
    {'healing_targets': 0}, {'healing_targets': 2}, {'healing_targets': 3},
    {'haruka_repeat': True}, {'haruka_repeat': False}, {'base_attack': 0},
    {'relic_ids': ['rogue_6_relic_legacy_81']},
    {'effects': [{'kind': 'attack_pct', 'value': .5}]},
    {'enemy_resistance': 90}, {'unconfirmed_training': ['本局培养']},
    {'inventory_status': {'complete': False, 'recognized': 0}},
)
for cultivation, mode, extra, bursts in itertools.product(
        ((0, 1), (1, 1), (1, 2), (2, 1), (2, 2), (2, 3)),
        ('frames', 'continuous'), constraints, (0, 2)):
    args = scenario(elite=cultivation[0], skill=cultivation[1],
                    timing_mode=mode, bubble_bursts=bursts, **extra)
    if args['window_seconds'] is None:
        del args['window_seconds']
    add('window-target-life-ordinary-recipient-effects-and-native-clock-scope', args)

for cultivation, mode, bursts in itertools.product(
        ((0, 1), (1, 1), (1, 2), (2, 1), (2, 2), (2, 3)),
        ('frames', 'continuous'), ('0', '0.0', '0e0', '2.0', 10000)):
    add('valid-parser-aliases-zero-types-and-max-retained-declaration', scenario(
        elite=cultivation[0], skill=cultivation[1], timing_mode=mode, bubble_bursts=bursts))

for cultivation, mode, invalid in itertools.product(
        ((0, 1, 7), (1, 1, 7), (1, 2, 7), (2, 3, 10),
         (0, 2, 7), (0, 3, 7), (1, 3, 7), (1, 1, 10)),
        ('frames', 'continuous'), (True, False, -1, .5, 10001, 'unknown', 'nan', 'inf')):
    add('unchanged-burst-validation-and-older-skill-qualification-order', scenario(
        elite=cultivation[0], skill=cultivation[1], skill_rank=cultivation[2],
        timing_mode=mode, bubble_bursts=invalid))

for mode, invalid in itertools.product(('frames', 'continuous'), (
        {'elite': True}, {'level': True}, {'potential': True},
        {'skill_rank': True}, {'module_level': True, 'module_id': MODULE},
        {'skill': 0}, {'skill': 4}, {'potential': 0}, {'elite': -1},
        {'timing_mode': 'unknown'}, {'window_seconds': -1},
        {'module_id': 'uniequip_002_mm', 'module_level': 1},
        {'healing_targets': True}, {'levitate_triggers': True, 'skill': 3, 'elite': 2})):
    add('prior-qualification-and-unrelated-old-errors', scenario(**{'timing_mode': mode, **invalid}))

for operator, profile in catalog()['operators'].items():
    for skill in range(1, len(profile['skills']) + 1):
        for mode in ('frames', 'continuous'):
            add('all-default-owners-skills-no-manual-bubbles', {
                'operator': operator, 'skill': skill, 'timing_mode': mode})
for operator in ('char_133_mm', 'char_1035_wisdel', 'char_2025_shu'):
    for mode in ('frames', 'continuous'):
        add('foreign-owner-ignores-bubble-field', {
            'operator': operator, 'skill': 1, 'bubble_bursts': True, 'timing_mode': mode})


def invoke(args):
    original = json.dumps(args, sort_keys=True, ensure_ascii=False)
    try:
        outcome = {'result': calculate_damage(args)}
    except Exception as exc:
        outcome = {'error_type': type(exc).__name__, 'error': str(exc)}
    assert json.dumps(args, sort_keys=True, ensure_ascii=False) == original
    return outcome


cached_before = json.dumps(catalog(), sort_keys=True, ensure_ascii=False)
outcomes = []
calls = 0
for case in cases:
    args = copy.deepcopy(case['scenario'])
    outcome = invoke(args)
    calls += 1
    entry = {**case, 'outcome': outcome}
    # Gate expectation comes from the verified raw PHASE_2/level1 talent
    # candidates, not a calculated reference flag or a zero attack value.
    if (args['operator'] == OP and args.get('elite', 2) < 2
            and 'result' in outcome and float(args.get('bubble_bursts', 0)) > 0):
        control = copy.deepcopy(args)
        control['bubble_bursts'] = 0
        entry['zero_count_control'] = {'scenario': control, 'outcome': invoke(control)}
        calls += 1
    outcomes.append(entry)
assert json.dumps(catalog(), sort_keys=True, ensure_ascii=False) == cached_before
with gzip.open(output, 'wt', encoding='utf-8') as f:
    json.dump(outcomes, f, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
print(json.dumps({'cases': len(outcomes), 'fresh_public_calls': calls,
                  'successes': sum('result' in x['outcome'] for x in outcomes),
                  'errors': sum('error' in x['outcome'] for x in outcomes),
                  'zero_count_controls': sum('zero_count_control' in x for x in outcomes),
                  'input_and_catalog_unchanged': True}))
