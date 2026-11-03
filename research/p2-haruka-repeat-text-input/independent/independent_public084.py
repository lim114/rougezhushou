"""Twelve distinct real public input pairs; native types and three complete texts."""
import copy
import gzip
import json
import sys
from pathlib import Path

source, destination = map(Path, sys.argv[1:3])
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(source))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents
from rouge.estimate import format_estimate
from rouge.reporting import format_report

def typed(value):
    if value is None: return ['none']
    if isinstance(value, bool): return ['bool', value]
    if isinstance(value, int): return ['int', value]
    if isinstance(value, float): return ['float', repr(value)]
    if isinstance(value, str): return ['str', value]
    if isinstance(value, (list, tuple)):
        return ['tuple' if isinstance(value, tuple) else 'list', [typed(v) for v in value]]
    if isinstance(value, dict):
        return ['dict', [[typed(k), typed(v)] for k, v in value.items()]]
    raise TypeError(type(value).__name__)

FIELD = 'haruka_repeat'
changes = [
    {'elite': 1, 'level': 43, 'skill_rank': 6, 'timing_mode': 'continuous', FIELD: '\x00'},
    {'level': 59, 'module_id': 'uniequip_002_haruka', 'module_level': 3,
     'healing_targets': 2, 'relic_ids': ['rogue_6_relic_legacy_97'], FIELD: ''},
    {'level': 60, 'module_id': 'uniequip_002_haruka', 'module_level': 3,
     'relic_ids': ['rogue_6_relic_legacy_105', 'rogue_6_relic_legacy_97'], FIELD: 'FALSE'},
    {'base_attack': 0, 'timing': {'target_disappears_seconds': 0}, FIELD: ' 未定义 '},
    {'skill': 1, FIELD: 'false'},
    {'skill': 3, 'timing_mode': 'continuous', FIELD: ''},
    {'operator': 'char_298_susuro', 'skill': 2, 'skill_rank': 7, FIELD: '0'},
    {'elite': 1, 'level': 43, 'skill_rank': 6, 'window_seconds': 0, FIELD: True},
    {'level': 59, 'module_id': 'uniequip_002_haruka', 'module_level': 2,
     'healing_targets': 2, FIELD: {'enabled': False}},
    {'bubble_bursts': 10002, 'relic_ids': ['rogue_6_relic_legacy_97'], FIELD: 'true'},
    {'timing': {'windup_frames': -3}, FIELD: ''},
    {'elite': 0, 'level': 43, 'skill_rank': 1, FIELD: 'false'},
]
cases = []
for index, change in enumerate(changes):
    cases.append({'label': 'independent-084-' + str(index), 'scenario': {
        'operator': 'char_4202_haruka', 'skill': 2, 'elite': 2, 'level': 70,
        'potential': 6, 'skill_rank': 10, 'base_attack': 1027,
        'window_seconds': 13.7, 'timing_mode': 'frames', **change}})
canonical = lambda value: json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
author_cases = json.loads((OUT.with_name('p2-haruka-repeat-text-input-084') / 'public-cases84.json').read_bytes())
assert len({canonical(row['scenario']) for row in cases}) == 12
assert not ({canonical(row['scenario']) for row in cases} & {canonical(row['scenario']) for row in author_cases})
catalog_before = typed(catalog())
rows = []
for case in cases:
    args = copy.deepcopy(case['scenario']); row = copy.deepcopy(case)
    try:
        result = calculate_damage(args)
        talents, parts = selected_talents(catalog()['operators'][args['operator']], args)
        row.update(result=result, typed_result=typed(result), estimate_text=format_estimate(result),
            report_text=format_report(result), technical_report_text=format_report(result, technical=True),
            actual_source_selection={'selected_talents': talents, 'module_parts': parts})
    except (ValueError, TypeError) as exc:
        row['error'] = {'type': type(exc).__name__, 'message': str(exc)}
    assert typed(args) == typed(case['scenario'])
    assert typed(catalog()) == catalog_before
    rows.append(row)
raw = json.dumps(rows, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
with destination.open('xb') as handle:
    handle.write(gzip.compress(raw, compresslevel=9, mtime=0))
print(json.dumps({'public_calls': 12, 'successes': sum('result' in r for r in rows),
    'errors': sum('error' in r for r in rows), 'distinct_from_all_216_author_inputs': True,
    'caller_and_catalog_native_types_unchanged': True, 'three_actual_reports_complete': True}))
