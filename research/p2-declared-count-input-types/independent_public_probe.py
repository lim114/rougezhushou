"""Read-only public probes; write only the requested external review artifact."""
import copy
import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

package = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(package))
from rouge.damage import calculate_damage

active = {('mechanist', 2): ('shield_break_count',),
          ('mechanist', 3): ('charge_count',),
          ('silverash', 2): ('activation_count', 'deployment_stacks')}
fields = ('shield_break_count', 'charge_count', 'activation_count', 'deployment_stacks')
values = (False, True, 0, 1, 2, 3, 30, 1.0, 2.0, 1.5, -1,
          '0', '1', '1.0', '2', '2.0', '1e0', '', 'x', None,
          float('nan'), float('inf'))
records = []

def scenario(operator, skill, mode):
    return {'operator': operator, 'skill': skill, 'skill_rank': 10, 'elite': 2,
            'base_attack': 1000, 'companion_attack': 1000,
            'window_seconds': 10, 'timing_mode': mode}

def check(args):
    frozen = copy.deepcopy(args)
    try:
        r = calculate_damage(args)
        result = {'accepted': True,
                  'total_damage': r.get('total_damage'),
                  'result_sha256': hashlib.sha256(json.dumps(r, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                  'components': [{k: c.get(k) for k in ('name', 'hits', 'total', 'actual_total')}
                                 for c in r.get('components', [])],
                  'charge_reference': r.get('charge_reference'),
                  'shield_break_reference': r.get('shield_break_reference')}
    except Exception as exc:
        result = {'accepted': False, 'error_type': type(exc).__name__, 'error': str(exc)}
    for key in args:
        if isinstance(args[key], float) and math.isnan(args[key]):
            assert math.isnan(frozen[key])
        else:
            assert args[key] == frozen[key]
    return result

for (operator, skill), used in active.items():
    for field in used:
        for mode in ('frames', 'continuous'):
            for value in values:
                args = {**scenario(operator, skill, mode), field: value}
                records.append({'kind': 'active', 'operator': operator, 'skill': skill,
                                'mode': mode, 'field': field, 'raw_type': type(value).__name__,
                                'raw_repr': repr(value), **check(args)})

for operator, skill in (('mechanist', 1), ('mechanist', 2), ('mechanist', 3),
                        ('silverash', 1), ('silverash', 2), ('silverash', 3),
                        ('kaltsit', 1), ('kaltsit', 2), ('kaltsit', 3),
                        ('char_298_susuro', 1)):
    for mode in ('frames', 'continuous'):
        base = scenario(operator, skill, mode)
        reference = check(base)
        for field in fields:
            if field in active.get((operator, skill), ()):
                continue
            for value in (False, True, '1.0', 'x', 3):
                outcome = check({**base, field: value})
                records.append({'kind': 'inactive', 'operator': operator, 'skill': skill,
                                'mode': mode, 'field': field, 'raw_type': type(value).__name__,
                                'raw_repr': repr(value),
                                'matches_same_root_baseline': outcome == reference, **outcome})

root_head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd='/workspace/rougezhushou',
                           check=True, capture_output=True, text=True).stdout.strip()
hashes = {}
for name in ('rouge/damage.py', 'rouge/estimate.py', 'rouge/charge_reference.py', 'rouge/shield_break_reference.py'):
    p = package / name
    if p.is_file():
        hashes[name] = hashlib.sha256(p.read_bytes()).hexdigest()
payload = {'captured_utc': datetime.now(timezone.utc).isoformat(),
           'observed_production_head': root_head, 'package_root': str(package),
           'package_source_hashes': hashes, 'public_calls': len(records), 'records': records,
           'tracked_files_edited': False, 'native_mechanism_tested': False}
output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'output': str(output), 'public_calls': len(records),
                  'active_calls': sum(x['kind'] == 'active' for x in records),
                  'inactive_calls': sum(x['kind'] == 'inactive' for x in records),
                  'active_bool_accepted': sum(x['kind'] == 'active' and x['raw_type'] == 'bool' and x['accepted'] for x in records),
                  'inactive_bool_accepted': sum(x['kind'] == 'inactive' and x['raw_type'] == 'bool' and x['accepted'] for x in records)}))
