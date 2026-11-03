"""Readonly complete-result cooperative checkbox contract audit."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'frozen'))
from rouge.catalog import catalog
from rouge.damage import calculate_damage

VALUES = [('absent', None), ('false_bool', False), ('true_bool', True),
          ('zero_int', 0), ('one_int', 1), ('zero_float', 0.0), ('one_float', 1.0),
          ('null', None), ('empty_text', ''), ('blank_text', ' '), ('false_text', 'false'),
          ('upper_false_text', 'False'), ('unknown_text', 'unknown'), ('zero_text', '0'),
          ('one_text', '1'), ('null_text', 'null'), ('two_int', 2), ('negative_int', -1),
          ('empty_list', []), ('nonempty_list', [False]), ('empty_dict', {}),
          ('nonempty_dict', {'enabled': False})]
CONTROL_VALUES = [row for row in VALUES if row[0] in
                  ('absent', 'false_bool', 'true_bool', 'zero_int', 'one_int', 'null',
                   'false_text', 'unknown_text', 'zero_text')]
records = {}


def add(name, plain, values):
    for label, value in values:
        args = deepcopy(plain)
        if label != 'absent':
            args['cooperative'] = deepcopy(value)
        records[name + ':' + label] = {'scenario': args}


for mode in ('frames', 'continuous'):
    for rank in (1, 7, 10):
        add(f'active:{mode}:rank{rank}:default',
            {'operator': 'silverash', 'skill': 3, 'skill_rank': rank,
             'base_attack': 1000, 'window_seconds': 10, 'timing_mode': mode}, VALUES)
    for scope, extra in (
            ('no_window', {}), ('zero_window', {'window_seconds': 0}),
            ('short_window', {'window_seconds': .1}), ('two_point_four', {'window_seconds': 2.4}),
            ('life_zero', {'window_seconds': 10, 'timing': {'target_disappears_seconds': 0}}),
            ('empty_targets', {'window_seconds': 10, 'timing': {'target_windows': []}}),
            ('preexisting_fragile', {'window_seconds': 10, 'preexisting_fragile': True}),
            ('external_damage_taken', {'window_seconds': 10,
                'effects': [{'kind': 'damage_taken', 'damage_type': 'physical', 'value': .5}]}),
            ('wine_and_finite_speed', {'window_seconds': 10,
                'relic_ids': ['rogue_6_relic_legacy_97', 'rogue_6_relic_legacy_105']})):
        add(f'active:{mode}:rank10:{scope}',
            {'operator': 'silverash', 'skill': 3, 'base_attack': 1000,
             'timing_mode': mode, **extra}, CONTROL_VALUES)
    for elite in (0, 1):
        add(f'locked:{mode}:E{elite}',
            {'operator': 'silverash', 'skill': 3, 'elite': elite, 'skill_rank': 7,
             'base_attack': 1000, 'timing_mode': mode}, CONTROL_VALUES)
    for scope, plain in (
            ('wine_incoming_unknown', {'operator': 'char_1042_phatm2', 'skill': 2,
                                      'enemy_attack_count': 20}),
            ('shield_clock_unknown', {'operator': 'mechanist', 'skill': 2,
                                      'shield_break_count': 2}),
            ('four_sui_clock_unknown', {'operator': 'char_2025_shu', 'skill': 3,
                                        'four_sui': True})):
        add(f'inactive_boundary:{mode}:{scope}',
            {'base_attack': 1000, 'window_seconds': 10, 'timing_mode': mode, **plain}, CONTROL_VALUES)
    for operator, profile in catalog()['operators'].items():
        for skill in range(1, len(profile['skills']) + 1):
            if operator == 'silverash' and skill == 3:
                continue
            add(f'inactive:{mode}:{operator}:S{skill}',
                {'operator': operator, 'skill': skill, 'base_attack': 1000,
                 'window_seconds': 10, 'timing_mode': mode}, CONTROL_VALUES)

before_catalog = deepcopy(catalog())
for name, row in records.items():
    args = row['scenario']
    original = deepcopy(args)
    try:
        row['outcome'] = {'result': calculate_damage(args), 'error': None}
    except Exception as error:
        row['outcome'] = {'result': None, 'error': {'type': type(error).__name__, 'message': str(error)}}
    assert args == original, name
assert catalog() == before_catalog

checks = []
for name, row in records.items():
    prefix, label = name.rsplit(':', 1)
    if name.startswith(('inactive:', 'inactive_boundary:', 'locked:')):
        control = prefix + ':absent'
        assert row['outcome'] == records[control]['outcome'], name
        checks.append({'case': name, 'control': control, 'complete_outcomes_equal': True})
    elif label in ('zero_int', 'zero_float', 'null', 'empty_text', 'empty_list', 'empty_dict', 'absent'):
        control = prefix + ':false_bool'
        assert row['outcome'] == records[control]['outcome'], name
        checks.append({'case': name, 'control': control, 'complete_outcomes_equal': True})
    elif label not in ('false_bool', 'true_bool'):
        control = prefix + ':true_bool'
        assert row['outcome'] == records[control]['outcome'], name
        checks.append({'case': name, 'control': control, 'complete_outcomes_equal': True,
                       'differs_from_false_control': row['outcome'] != records[prefix + ':false_bool']['outcome']})

examples = []
for mode in ('frames', 'continuous'):
    prefix = f'active:{mode}:rank10:default:'
    for label in ('false_bool', 'true_bool', 'false_text', 'unknown_text', 'zero_text'):
        outcome = records[prefix + label]['outcome']
        assert outcome['error'] is None
        r = outcome['result']
        examples.append({'case': prefix + label, 'total_damage': r['total_damage'],
                         'components': [{'name': c['name'], 'hits': c['hits'],
                                         'total': c['total']} for c in r['components']]})
with gzip.open(ROOT / 'public-full-outcomes.json.gz', 'wt', encoding='utf-8') as out:
    json.dump({'baseline_head': '0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb', 'cases': records,
               'all_inputs_and_catalog_preserved': True}, out, ensure_ascii=False, indent=2)
    out.write('\n')
(ROOT / 'full-outcome-control-checks.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'public-counterexamples.json').write_text(json.dumps(examples, ensure_ascii=False, indent=2) + '\n')
summary = {'readonly': True, 'public_calls': len(records),
           'successes': sum(v['outcome']['error'] is None for v in records.values()),
           'old_error_outcomes': sum(v['outcome']['error'] is not None for v in records.values()),
           'strict_complete_outcome_control_checks': len(checks),
           'inactive_and_locked_variants_identical_to_absent': True,
           'numeric_zero_one_null_compatibility_preserved': True,
           'all_nonempty_texts_match_true_in_active_s3': True,
           'caller_and_catalog_unchanged': True, 'patch_written': False,
           'native_clock_or_numeric_model_inferred': False}
(ROOT / 'audit-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(summary, ensure_ascii=False))
