"""Independent narrow ordinary public calls on an explicit frozen source."""
import copy
import gzip
import json
import sys
from pathlib import Path

source, output = map(Path, sys.argv[1:3])
sys.path.insert(0, str(source))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import format_report

cases = []
for mode in ('frames', 'continuous'):
    for extra in (
        {'window_seconds': 0}, {}, {'potential': 6}, {'skill_rank': 1},
        {'timing': {'target_disappears_seconds': 0}},
        {'timing': {'target_windows': []}}, {'healing_targets': 0},
        {'level': 50, 'module_id': 'uniequip_002_amiya3', 'module_level': 3},
        {'elite': 1, 'base_attack': 0},
        {'elite': 1, 'timing': {'target_disappears_seconds': 0}},
        {'elite': 1, 'skill': 2, 'base_attack': 0},
        {'elite': 1, 'skill': 2, 'timing': {'target_disappears_seconds': 0}},
        {'elite': 2, 'base_attack': 0},
        {'elite': 2, 'skill': 2, 'timing': {'target_disappears_seconds': 0}},
        {'elite': 2, 'skill': 2, 'timing': {'target_windows': []}},
        {'elite': 2, 'skill': 2, 'healing_targets': 0},
        *({'elite': 2, 'level': level, 'module_id': 'uniequip_002_amiya3',
           'module_level': stage} for level in (49, 50) for stage in (1, 2, 3)),
        {'elite': True}, {'skill': 2, 'amiya_hit_targets': True}, {'skill_rank': 8},
        {'elite': 1, 'skill': 2, 'amiya_hit_targets': True}, {'window_seconds': -1},
        *({'operator': op, 'elite': 2, 'skill': skill}
          for op in ('char_002_amiya', 'char_1001_amiya2') for skill in (1, 2)),
    ):
        cases.append({'operator': 'char_1037_amiya3', 'skill': 1, 'skill_rank': 7,
                      'elite': 0, 'level': 1, 'base_attack': 1000,
                      'window_seconds': 10, 'timing_mode': mode, **extra})

canonical = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False)
original_catalog = canonical(catalog())
rows = []
for args in cases:
    given = copy.deepcopy(args)
    try:
        result = calculate_damage(given)
        outcome = {'result': result, 'text_report': format_report(result)}
    except Exception as exc:
        outcome = {'error_type': type(exc).__name__, 'error': str(exc)}
    assert canonical(given) == canonical(args)
    rows.append({'scenario': args, 'outcome': outcome})
assert canonical(catalog()) == original_catalog
with output.open('xb') as f:
    f.write(gzip.compress(canonical(rows).encode(), compresslevel=9, mtime=0))
print(json.dumps({'pairs_one_side': len(rows), 'fresh_public_calls': len(rows),
                  'accepted': sum('result' in r['outcome'] for r in rows),
                  'errors': sum('error' in r['outcome'] for r in rows),
                  'inputs_catalog_unchanged': True}))
