"""Complete paired public outcomes, with immutable package selection."""
import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--package', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
OUT = Path(__file__).resolve().parent
package = Path(args.package).resolve()
assert package in (OUT / 'frozen', OUT / 'draft')
sys.dont_write_bytecode = True
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
import rouge.damage
assert Path(rouge.damage.__file__).resolve().is_relative_to(package)
RID = 'rogue_6_relic_cargo_10'
OMIT = object()
values = [('omitted', OMIT), ('none', None), ('negative', 'non_emergency'),
          ('positive', 'emergency_hire'), ('unknown_name', 'unknown'),
          ('wrong_bool', True), ('wrong_number', 0), ('wrong_list', [])]
cases = []
for op, profile in catalog()['operators'].items():
    for skill in range(1, len(profile['skills']) + 1):
        for mode in ('frames', 'continuous'):
            for held in (False, True):
                for label, value in values:
                    scenario = {'operator': op, 'skill': skill,
                                'base_attack': 1000, 'enemy_defense': 0,
                                'window_seconds': 3, 'timing_mode': mode,
                                'relic_ids': [RID] if held else []}
                    if value is not OMIT:
                        scenario['recruitment_kind'] = copy.deepcopy(value)
                    cases.append({'id': f'roster/{op}/{skill}/{mode}/{held}/{label}',
                                  'group': 'roster', 'identity': label, 'held': held,
                                  'scenario': scenario})

extra_values = [('empty', ''), ('short_name', 'emergency'), ('case', 'EMERGENCY_HIRE'),
                ('spaces', ' emergency_hire '), ('false', False), ('one', 1),
                ('float_zero', 0.0), ('float_one', 1.0), ('object', {}),
                ('nested_name', {'kind': 'emergency_hire'}),
                ('list_name', ['emergency_hire']), ('none', None)]
for op, skill in (('silverash', 3), ('mechanist', 3), ('char_110_deepcl', 1)):
    for mode in ('frames', 'continuous'):
        for relic_ids, context in (([RID], {}),
                (['rogue_6_relic_cargo_2'], {'parts_count': 0}),
                (['rogue_6_relic_legacy_60'], {'gold': 25})):
            for label, value in extra_values:
                scenario = {'operator': op, 'skill': skill,
                            'window_seconds': 3, 'timing_mode': mode,
                            'relic_ids': relic_ids, 'relic_context': context,
                            'recruitment_kind': copy.deepcopy(value)}
                cases.append({'id': f'types/{op}/{skill}/{mode}/{relic_ids[0]}/{label}',
                              'group': 'types', 'identity': label, 'held': RID in relic_ids,
                              'scenario': scenario})

for mode in ('frames', 'continuous'):
    for timing in ({}, {'target_disappears_seconds': 0}, {'target_windows': []}):
        for window in (0, 3):
            for flag in (0, 1):
                for label, value in [('none', None), ('unknown_name', 'unknown'),
                                     ('negative', 'non_emergency'),
                                     ('positive', 'emergency_hire')]:
                    scenario = {'operator': 'silverash', 'skill': 3,
                                'window_seconds': window, 'timing_mode': mode,
                                'timing': timing, 'relic_ids': [RID],
                                'relic_context': {'emergency_hire': flag},
                                'recruitment_kind': value}
                    cases.append({'id': f'boundary/{mode}/{timing}/{window}/{flag}/{label}',
                                  'group': 'boundary', 'identity': label, 'held': True,
                                  'scenario': scenario})

source_paths = list(sorted((package / 'rouge').rglob('*.py')))
source_paths += list(sorted((package / 'rouge').rglob('*.json')))
before = {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in source_paths}
mechanics_before = copy.deepcopy(mechanics())
for row in cases:
    scenario = copy.deepcopy(row['scenario'])
    original = copy.deepcopy(scenario)
    try:
        row['outcome'] = {'accepted': True, 'result': calculate_damage(scenario)}
    except Exception as error:
        row['outcome'] = {'accepted': False, 'error_type': type(error).__name__,
                          'error': str(error)}
    assert scenario == original, row['id']
after = {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in source_paths}
assert before == after
assert mechanics() == mechanics_before
output = {'frozen_baseline_head': '15e0fa455aad05d27303428299d24d15db4c572c',
          'package': str(package), 'damage_import': rouge.damage.__file__,
          'source_hashes': before, 'cases': cases, 'cases_run': len(cases),
          'input_unchanged': True, 'shared_mechanics_unchanged': True,
          'source_drift': [], 'private_state_read': False, 'game_actions': 0,
          'native_validation': False}
Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: output[key] for key in (
    'package', 'damage_import', 'cases_run', 'input_unchanged',
    'shared_mechanics_unchanged', 'source_drift')}, ensure_ascii=False))
