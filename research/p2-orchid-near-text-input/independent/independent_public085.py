"""Twelve different real input pairs, with native trees before JSON encoding."""
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
    if isinstance(value, dict): return ['dict', [[typed(k), typed(v)] for k, v in value.items()]]
    raise TypeError(type(value).__name__)

FIELD = 'near_previous_deployment'
MOD = 'uniequip_002_orchd2'
changes = [
    {'elite': 1, 'level': 43, 'skill': 2, 'skill_rank': 6, FIELD: '\x00'},
    {'level': 59, 'skill': 3, 'module_id': MOD, 'module_level': 3, 'timing_mode': 'continuous', FIELD: ''},
    {'level': 60, 'module_id': MOD, 'module_level': 2,
     'relic_ids': ['rogue_6_relic_legacy_97'], FIELD: 'False'},
    {'level': 60, 'skill': 3, 'module_id': MOD, 'module_level': 3, 'window_seconds': 0, FIELD: '未知'},
    {'elite': 0, 'level': 43, 'skill_rank': 1, 'module_id': MOD, 'module_level': 3, FIELD: 'false'},
    {'operator': 'char_4202_haruka', 'skill': 3, FIELD: ''},
    {'elite': 1, 'level': 43, 'skill': 2, 'skill_rank': 6, 'timing_mode': 'continuous', FIELD: {'enabled': False}},
    {'level': 60, 'module_id': MOD, 'module_level': 1, 'double_charge': 'false',
     'relic_ids': ['rogue_6_relic_legacy_97'], FIELD: False},
    {'level': 60, 'skill': 3, 'module_id': MOD, 'module_level': 3,
     'relic_ids': ['rogue_6_relic_artifact_6'], FIELD: True},
    {'elite': 0, 'level': 43, 'skill': 2, 'skill_rank': 1, FIELD: 'false'},
    {'elite': 1, 'level': 43, 'skill_rank': 10, FIELD: 'false'},
    {'timing': {'windup_frames': -3}, FIELD: ''},
]
cases = [{'label': 'independent-085-' + str(index), 'scenario': {
    'operator': 'char_1048_orchd2', 'skill': 1, 'skill_rank': 10, 'elite': 2, 'level': 90,
    'potential': 6, 'base_attack': 1093, 'window_seconds': 17.3, 'timing_mode': 'frames', **change}}
    for index, change in enumerate(changes)]
canon = lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
old = json.loads((OUT.with_name('p2-orchid-near-text-085') / 'public-baseline085.json').read_bytes())['records']
assert len({canon(row['scenario']) for row in cases}) == 12
assert not ({canon(row['scenario']) for row in cases} & {canon(row['scenario']) for row in old})
cached = typed(catalog()); rows = []
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
    assert typed(args) == typed(case['scenario']) and typed(catalog()) == cached
    rows.append(row)
raw = json.dumps(rows, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
with destination.open('xb') as handle: handle.write(gzip.compress(raw, compresslevel=9, mtime=0))
print(json.dumps({'public_calls': 12, 'successes': sum('result' in r for r in rows),
    'errors': sum('error' in r for r in rows), 'distinct_from_all197_author_inputs': True,
    'caller_and_catalog_native_types_preserved': True, 'three_actual_reports': True,
    'native_type_tree_saved_before_JSON_encoding': True}))
