import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from rouge.catalog import catalog
from rouge.damage import calculate_damage

OUT = Path(sys.argv[2])
ACTIVE = {('mechanist', 2): ('shield_break_count',),
          ('mechanist', 3): ('charge_count',),
          ('silverash', 2): ('activation_count', 'deployment_stacks')}
FIELDS = ('shield_break_count', 'charge_count', 'activation_count', 'deployment_stacks')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def evaluate(scenario):
    original = canonical(scenario)
    try:
        value = {'accepted': True, 'result': calculate_damage(scenario)}
    except (ValueError, TypeError, OverflowError) as error:
        value = {'accepted': False, 'error_type': type(error).__name__, 'error': str(error)}
    assert canonical(scenario) == original
    return value


rows = []
catalog_before = digest(catalog())
for operator, profile in catalog()['operators'].items():
    for skill in range(1, len(profile['skills']) + 1):
        for mode in ('frames', 'continuous'):
            basic = {'operator': operator, 'skill': skill, 'skill_rank': 10,
                     'base_attack': 1000, 'companion_attack': 2000,
                     'window_seconds': 10, 'timing_mode': mode}
            for field in FIELDS:
                for value in (False, True):
                    request = {**basic, field: value}
                    result = evaluate(request)
                    control = evaluate({**basic, field: int(value)})
                    omitted = evaluate(basic)
                    active = field in ACTIVE.get((operator, skill), ())
                    if not active:
                        assert result == control == omitted
                    rows.append({'kind': 'active_bool' if active else 'inactive_bool',
                                 'scenario': request, 'accepted': result['accepted'],
                                 'outcome_sha256': digest(result),
                                 'integer_control_sha256': digest(control),
                                 'omitted_control_sha256': digest(omitted),
                                 'outcome': result if active else None})

numeric_values = (0, 1, 2, 8, 100, 1000, 0.0, 1.0, 2.0, '0', '1', '2',
                  '1.0', ' 2 ', '1e0', -1, -.5, 1.5, '0.5',
                  float('nan'), float('inf'), None, 'bad')
for (operator, skill), fields in ACTIVE.items():
    for field in fields:
        for mode in ('frames', 'continuous'):
            for value in numeric_values:
                request = {'operator': operator, 'skill': skill, 'skill_rank': 10,
                           'base_attack': 1000, 'companion_attack': 2000,
                           'window_seconds': 10, 'timing_mode': mode, field: value}
                result = evaluate(request)
                rows.append({'kind': 'non_bool_numeric_and_existing_errors',
                             'scenario': request, 'accepted': result['accepted'],
                             'outcome_sha256': digest(result), 'outcome': result})
            for rank in (1, 7, 10):
                for count in (0, 1, 2):
                    for context in ({}, {'window_seconds': 0},
                                    {'timing': {'target_disappears_seconds': 0}},
                                    {'skill_duration_seconds': 20}):
                        request = {'operator': operator, 'skill': skill, 'skill_rank': rank,
                                   'base_attack': 1000, 'companion_attack': 2000,
                                   'timing_mode': mode, field: count, **context}
                        result = evaluate(request)
                        rows.append({'kind': 'existing_integer_scope', 'scenario': request,
                                     'accepted': result['accepted'],
                                     'outcome_sha256': digest(result), 'outcome': result})

for mode in ('frames', 'continuous'):
    for value in (False, True):
        for operator, skill, field in (('silverash', 3, 'cooperative'),
                                       ('silverash', 3, 'preexisting_fragile'),
                                       ('char_298_susuro', 2, 'low_cost_healing_target')):
            request = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                       'window_seconds': 10, 'timing_mode': mode, field: value}
            result = evaluate(request)
            assert result['accepted']
            rows.append({'kind': 'real_boolean_option', 'scenario': request,
                         'accepted': True, 'outcome_sha256': digest(result), 'outcome': result})

assert digest(catalog()) == catalog_before
result = {'package_root': sys.argv[1], 'cases': len(rows),
          'primary_public_calls': len(rows),
          'extra_bool_control_calls': sum(row['kind'] in ('active_bool', 'inactive_bool') for row in rows) * 2,
          'total_public_calls': len(rows) + sum(row['kind'] in ('active_bool', 'inactive_bool') for row in rows) * 2,
          'catalog_unchanged': True, 'caller_inputs_unchanged': True, 'records': rows}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: value for key, value in result.items() if key != 'records'}))
