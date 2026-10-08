"""Twelve new ordinary guard inputs, native typed tree and three real reports."""
import copy
import gzip
import json
import sys
from pathlib import Path

source, output = map(Path, sys.argv[1:3])
sys.path.insert(0, str(source))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents
from rouge.estimate import format_estimate
from rouge.reporting import format_report


def typed(value):
    if value is None:
        return ['none']
    if isinstance(value, bool):
        return ['bool', value]
    if isinstance(value, int):
        return ['int', value]
    if isinstance(value, float):
        return ['float', repr(value)]
    if isinstance(value, str):
        return ['str', value]
    if isinstance(value, (list, tuple)):
        return ['tuple' if isinstance(value, tuple) else 'list', [typed(v) for v in value]]
    if isinstance(value, dict):
        return ['dict', [[typed(k), typed(v)] for k, v in value.items()]]
    raise TypeError(type(value).__name__)


FIELD = 'low_cost_healing_target'
changes = [
    {'elite': 1, 'level': 50, 'skill_rank': 4, 'timing_mode': 'continuous', FIELD: '\x00'},
    {'level': 40, 'module_id': 'uniequip_002_susuro', 'module_level': 3,
     'skill': 2, 'casts_used': 1, 'healing_targets': 0, FIELD: ''},
    {'base_attack': 0, 'timing': {'target_disappears_seconds': 0}, FIELD: 'False'},
    {'elite': 0, 'level': 40, 'skill_rank': 1,
     'module_id': 'uniequip_002_susuro', 'module_level': 3, FIELD: 'false'},
    {'operator': 'char_2025_shu', 'skill_rank': 7, FIELD: 'false'},
    {'operator': 'char_196_sunbr', 'skill': 2, 'skill_rank': 7, FIELD: '0'},
    {'elite': 1, 'level': 50, 'skill': 2, 'skill_rank': 7, 'timing_mode': 'continuous',
     'timing': {'target_disappears_seconds': 0}, FIELD: True},
    {'level': 40, 'module_id': 'uniequip_002_susuro', 'module_level': 2, FIELD: {'enabled': False}},
    {'elite': 1, 'level': 50, 'skill_rank': 1, 'healing_targets': True, FIELD: 'true'},
    {'skill': 2, 'casts_used': -1, FIELD: 'false'},
    {'level': 40, 'module_id': 'uniequip_002_susuro', 'module_level': 1, 'healing_targets': 0},
    {'healing_targets': 101, FIELD: 'false'},
]
catalog_before = typed(catalog())
rows = []
for index, extra in enumerate(changes):
    scenario = {'operator': 'char_298_susuro', 'skill': 1, 'elite': 2, 'level': 70,
                'potential': 6, 'skill_rank': 10, 'base_attack': 1000,
                'window_seconds': 13, 'timing_mode': 'frames', **extra}
    args = copy.deepcopy(scenario)
    row = {'label': 'independent-' + str(index), 'scenario': scenario}
    try:
        result = calculate_damage(args)
        talents, parts = selected_talents(catalog()['operators'][args['operator']], args)
        row.update(result=result, typed_result=typed(result), estimate_text=format_estimate(result),
                   report_text=format_report(result), technical_report_text=format_report(result, technical=True),
                   actual_source_selection={'selected_talents': talents, 'module_parts': parts})
    except (ValueError, TypeError) as exc:
        row['error'] = {'type': type(exc).__name__, 'message': str(exc)}
    assert typed(args) == typed(scenario)
    assert typed(catalog()) == catalog_before
    rows.append(row)
raw = json.dumps(rows, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
with output.open('xb') as f:
    f.write(gzip.compress(raw, compresslevel=9, mtime=0))
print(json.dumps({'public_calls': 12, 'successes': sum('result' in r for r in rows),
                  'errors': sum('error' in r for r in rows),
                  'input_catalog_native_types_unchanged': True, 'three_real_reports': True}))
