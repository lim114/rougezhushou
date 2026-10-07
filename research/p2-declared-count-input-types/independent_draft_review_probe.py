"""Small independent public checks, separately named from the main matrix."""
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).parent
package = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(package))
from rouge.damage import calculate_damage

def request(operator='mechanist', skill=3, **extra):
    return {'operator': operator, 'skill': skill, 'skill_rank': 10,
            'base_attack': 1000, 'companion_attack': 2000,
            'window_seconds': 10, **extra}

cases = []
for operator, skill, field in (('mechanist', 2, 'shield_break_count'),
                               ('mechanist', 3, 'charge_count'),
                               ('silverash', 2, 'activation_count'),
                               ('silverash', 2, 'deployment_stacks')):
    for mode, value in (('frames', True), ('continuous', False)):
        cases.append((f'active:{field}:{mode}:{value}',
                      request(operator, skill, timing_mode=mode, **{field: value})))
for label, extra in (('invalid_skill', {'skill': False}),
                     ('invalid_rank', {'skill_rank': True}),
                     ('invalid_elite', {'elite': True}),
                     ('invalid_level', {'level': True}),
                     ('invalid_potential', {'potential': True})):
    args = request(charge_count=True)
    args.update(extra)
    cases.append((label, args))
cases.append(('locked_skill', request('mechanist', 2, elite=0, skill_rank=7,
                                     shield_break_count=True)))
cases.extend([
    ('inactive_legacy', request('mechanist', 1, shield_break_count=True)),
    ('inactive_legacy_omitted', request('mechanist', 1)),
    ('inactive_extended', request('char_298_susuro', 1, shield_break_count=True,
                                 charge_count=True, activation_count=True, deployment_stacks=True)),
    ('inactive_extended_omitted', request('char_298_susuro', 1)),
    ('shield_numeric_string', request('mechanist', 2, shield_break_count='1.0')),
    ('shield_integer', request('mechanist', 2, shield_break_count=1)),
    ('shield_integer_float', request('mechanist', 2, shield_break_count=1.0)),
    ('charge_existing_string_error', request(charge_count='1.0')),
    ('active_bool_plus_invalid_enemy', request(charge_count=True, enemy_defense=-1)),
    ('inactive_bool_plus_invalid_enemy', request('mechanist', 1, charge_count=True,
                                                enemy_defense=-1)),
])
records = []
for name, args in cases:
    original = copy.deepcopy(args)
    try:
        result = calculate_damage(args)
        outcome = {'accepted': True, 'result_sha256': hashlib.sha256(
            json.dumps(result, ensure_ascii=False, sort_keys=True).encode()).hexdigest()}
    except Exception as exc:
        outcome = {'accepted': False, 'error_type': type(exc).__name__, 'error': str(exc)}
    assert args == original
    records.append({'name': name, 'scenario': args, **outcome})

path = root / 'draft/tests/test_declared_count_input_types.py'
spec = importlib.util.spec_from_file_location('independent_count_tests', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
test_result = unittest.TestResult()
unittest.defaultTestLoader.loadTestsFromTestCase(module.DeclaredCountInputTypesTests).run(test_result)
tests = {'methods_run': test_result.testsRun, 'failures': len(test_result.failures),
         'errors': len(test_result.errors), 'skipped': len(test_result.skipped)}
head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd='/workspace/rougezhushou',
                      check=True, text=True, capture_output=True).stdout.strip()
payload = {'captured_utc': datetime.now(timezone.utc).isoformat(),
           'package_root': str(package), 'observed_production_head': head,
           'package_damage_sha256': hashlib.sha256((package/'rouge/damage.py').read_bytes()).hexdigest(),
           'new_tests_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
           'public_probe_calls': len(records), 'records': records, 'independent_new_tests': tests,
           'tracked_files_edited': False, 'native_validation_performed': False}
output.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'output': str(output), 'public_probe_calls': len(records), 'tests': tests}))
