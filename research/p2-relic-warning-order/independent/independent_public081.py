"""Small reviewer public guard batch on new seeds with no candidate injection."""
import copy
import gzip
import json
import os
import sys
from pathlib import Path

source, output = map(Path, sys.argv[1:3])
sys.path.insert(0, str(source))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report

R = 'rogue_6_relic_legacy_81'
C = 'rogue_6_relic_legacy_82'
M = 'rogue_6_relic_legacy_83'
cases = [
    {'operator': 'char_1037_amiya3', 'skill': 1, 'elite': 0, 'skill_rank': 1,
     'window_seconds': 0, 'healing_targets': 0, 'relic_ids': [M, C, R]},
    {'operator': 'char_110_deepcl', 'skill': 1, 'base_attack': 0, 'relic_ids': [C, R, 'rogue_6_relic_legacy_5']},
    {'operator': 'char_206_gnosis', 'skill': 2, 'relic_ids': ['rogue_6_relic_legacy_80', 'rogue_6_relic_hand_1', C, R]},
    {'operator': 'mechanist', 'skill': 3, 'relic_ids': ['unrecognized_reviewer_source', 'rogue_6_relic_legacy_62', R, 'rogue_6_relic_legacy_61', C]},
    {'operator': 'char_1037_amiya3', 'skill': 1, 'healing_targets': True, 'relic_ids': [R, C]},
    {'operator': 'char_1037_amiya3', 'skill': 1, 'elite': True, 'relic_ids': [R, C]},
    {'operator': 'mechanist', 'skill': 3, 'char_buff_ids': False, 'relic_ids': [R, C]},
    {'operator': 'char_1037_amiya3', 'skill': 1, 'relic_ids': [R, R]},
]
canonical = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
catalog_before = canonical(catalog())
rows = []
for index, scenario in enumerate(cases):
    given = copy.deepcopy(scenario)
    refs = []
    def trace(frame, event, arg):
        if event == 'line' and frame.f_code.co_name == 'prepare' and frame.f_code.co_filename.endswith('/rouge/relics.py') and 'candidates' in frame.f_locals and not refs:
            refs.append({key: copy.deepcopy(frame.f_locals[key]) for key in ('rules', 'effects', 'token_effects', 'candidates')})
        return trace
    row = {'index': index, 'label': 'reviewer-' + str(index), 'scenario': scenario}
    try:
        sys.settrace(trace)
        result = calculate_damage(given)
        sys.settrace(None)
        row.update(result=result, estimate_text=format_estimate(result), report_text=format_report(result),
                   technical_report_text=format_report(result, technical=True))
    except (ValueError, TypeError) as exc:
        sys.settrace(None)
        row['error'] = {'type': type(exc).__name__, 'message': str(exc)}
    row['candidate_references'] = refs
    assert canonical(given) == canonical(scenario)
    assert canonical(catalog()) == catalog_before
    rows.append(row)
with output.open('xb') as f:
    f.write(gzip.compress(canonical(rows).encode(), compresslevel=9, mtime=0))
print(json.dumps({'seed': os.environ['PYTHONHASHSEED'], 'public_calls': 8,
                  'accepted': sum('result' in r for r in rows), 'errors': sum('error' in r for r in rows),
                  'inputs_catalog_unchanged': True, 'trace_readonly_no_rule_injection': True}))
