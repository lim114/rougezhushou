"""Independent small public boundary matrix; never edit either package."""
import copy
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

package = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

catalog_before = canonical(catalog())
cases = []
profiles = [('caster_initial', 'char_002_amiya', 1, {}),
            ('medical_enemy_heal', 'char_1037_amiya3', 1, {}),
            ('legacy_friend', 'kaltsit', 1, {}),
            ('legacy_fallback', 'kaltsit', 2, {'healing_targets': 1}),
            ('legacy_no_friend', 'kaltsit', 2, {'healing_targets': 0}),
            ('extended_friend', 'char_298_susuro', 1, {}),
            ('declared_collision', 'mechanist', 3, {'charge_count': 2}),
            ('declared_counter', 'char_1044_hsgma2', 1, {'incoming_hits': 2})]
for label, operator, skill, extra in profiles:
    for mode in ('frames', 'continuous'):
        for lifetime in (0, '0', '0.0', '-0'):
            cases.append((f'{label}:{mode}:{repr(lifetime)}', label, mode, repr(lifetime),
                          {'operator': operator, 'skill': skill, 'base_attack': 1000,
                           'timing_mode': mode, 'timing': {'target_disappears_seconds': lifetime}, **extra}))
for mode in ('frames', 'continuous'):
    for lifetime in (False, True, None, '-1', 'nan', 'bad'):
        cases.append((f'invalid_lifetime:{mode}:{repr(lifetime)}', 'invalid_lifetime', mode, repr(lifetime),
                      {'operator': 'kaltsit', 'skill': 2, 'base_attack': 1000,
                       'timing_mode': mode, 'timing': {'target_disappears_seconds': lifetime}}))
    for label, timing in [('omitted', {}), ('positive_numeric', {'target_disappears_seconds': 2.5}),
                          ('positive_string', {'target_disappears_seconds': '2.5'}),
                          ('nested_string_zero', {'units': {'token_10001_deepcl_tentac': {'target_disappears_seconds': '0'}}})]:
        cases.append((f'control:{mode}:{label}', 'control', mode, label,
                      {'operator': 'char_002_amiya', 'skill': 1, 'base_attack': 1000,
                       'timing_mode': mode, 'timing': timing}))
    for lifetime in (0, '0'):
        for label, invalid in [('windup_bool', {'windup_frames': True}),
                               ('invalid_window', {'target_windows': [[0, 0]]}),
                               ('movement_not_array', {'movement_windows': 'bad'})]:
            cases.append((f'invalid_timing:{mode}:{repr(lifetime)}:{label}', 'invalid_timing', mode, label,
                          {'operator': 'kaltsit', 'skill': 2, 'base_attack': 1000, 'timing_mode': mode,
                           'timing': {'target_disappears_seconds': lifetime, **invalid}}))
    for lifetime in (0, '0'):
        cases.append((f'nested_isolation:{mode}:{repr(lifetime)}', 'nested_isolation', mode, repr(lifetime),
                      {'operator': 'char_4202_haruka', 'skill': 1, 'base_attack': 1000, 'timing_mode': mode,
                       'timing': {'target_disappears_seconds': lifetime, 'target_windows': [[0, 10]],
                                  'movement_windows': [[2, 3]],
                                  'units': {'token_10001_deepcl_tentac': {'target_disappears_seconds': '2.5'}},
                                  'sp_events': {'initial': [{'at_seconds': 0, 'type': 'damage'}], 'cycle': []}}}))
records = []
for name, category, mode, value_label, args in cases:
    original = copy.deepcopy(args)
    timing_id = id(args['timing'])
    nested_ids = {key: id(value) for key, value in args['timing'].items() if isinstance(value, (list, dict))}
    try:
        result = calculate_damage(args)
        skill = result['estimate']['skill']
        outcome = {'accepted': True, 'result_sha256': hashlib.sha256(canonical(result).encode()).hexdigest(),
                   'damage': result.get('total_damage'), 'healing': result.get('total_healing'),
                   'initial': skill.get('initial_seconds'), 'recharge': skill.get('recharge_seconds'),
                   'cycle': skill.get('cycle_seconds'), 'duration': skill.get('duration_seconds'),
                   'cast_healing': skill.get('total_healing'),
                   'charge_reference': result.get('charge_reference'),
                   'counter_reference': [{k: c[k] for k in ('name','conditional_hits_reference','conditional_damage_reference') if k in c}
                                         for c in result.get('components',[]) if 'conditional_hits_reference' in c]}
    except Exception as exc:
        outcome = {'accepted': False, 'error_type': type(exc).__name__, 'error': str(exc)}
    assert args == original and id(args['timing']) == timing_id
    assert all(id(args['timing'][key]) == value for key, value in nested_ids.items())
    records.append({'name': name, 'category': category, 'mode': mode, 'value_label': value_label,
                    'scenario': args, 'caller_unchanged': True, 'nested_identity_unchanged': True, **outcome})
assert canonical(catalog()) == catalog_before
payload = {'utc': datetime.now(timezone.utc).isoformat(), 'package_root': str(package),
           'observed_production_head': subprocess.run(['git','rev-parse','HEAD'],cwd='/workspace/rougezhushou',check=True,text=True,capture_output=True).stdout.strip(),
           'public_calls': len(records), 'catalog_unchanged': True, 'records': records,
           'damage_sha256': hashlib.sha256((package/'rouge/damage.py').read_bytes()).hexdigest()}
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'output':str(out),'public_calls':len(records),'catalog_unchanged':True}))
