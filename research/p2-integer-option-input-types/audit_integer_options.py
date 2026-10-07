"""Read-only public type/query audit against immutable HEAD58 sources."""
import ast
import copy
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
PACKAGE = OUT / 'frozen'
sys.dont_write_bytecode = True
sys.path.insert(0, str(PACKAGE))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import Combat
from rouge.operator_options import OPTIONS

engine = (PACKAGE / 'rouge/operator_engine.py').read_text()
calls = []
for node in ast.walk(ast.parse(engine)):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == 'option' and any(k.arg == 'integer'
            and isinstance(k.value, ast.Constant) and k.value.value is True
            for k in node.keywords)):
        calls.append({'field': node.args[0].value, 'line': node.lineno,
                      'call': ast.get_source_segment(engine, node)})
calls.sort(key=lambda row: row['line'])
known_guarded = {'healing_targets', 'amiya_hit_targets', 'stolen_enemy_count'}
fields = {row['field'] for row in calls} - known_guarded
assert len(calls) == 28 and len(fields) == 24
controls = []
checkboxes = []
for operator, entries in OPTIONS.items():
    for key, label, default, maximum, skills in entries:
        row = {'operator': operator, 'field': key, 'label': label,
               'default': default, 'default_type': type(default).__name__,
               'ui_maximum': maximum, 'skills': list(skills)}
        if key in fields:
            assert type(default) is int
            controls.append(row)
        elif type(default) is bool:
            checkboxes.append(row)
assert {row['field'] for row in controls} == fields
assert not {row['field'] for row in checkboxes} & fields

trace = []
original_option = Combat.option
def observed_option(self, key, default=0, maximum=None, integer=False):
    trace.append({'field': key, 'raw_type': type(self.s.get(key, default)).__name__,
                  'integer': integer, 'maximum': maximum})
    return original_option(self, key, default, maximum, integer)
Combat.option = observed_option

rows = []
values = [('false', False), ('true', True), ('zero', 0), ('one', 1),
          ('float_zero', 0.0), ('float_one', 1.0), ('string_zero', '0'),
          ('string_one', '1'), ('string_decimal', '1.0'), ('fraction', .5)]
def evaluate(args, row):
    before = copy.deepcopy(args)
    trace.clear()
    try:
        outcome = {'accepted': True, 'result': calculate_damage(args)}
    except Exception as error:
        outcome = {'accepted': False, 'error_type': type(error).__name__, 'error': str(error)}
    assert args == before
    row.update(scenario=before, outcome=outcome, trace=copy.deepcopy(trace))
    rows.append(row)
    return row

for control in controls:
    for skill in control['skills']:
        assert skill <= len(catalog()['operators'][control['operator']]['skills'])
        for mode in ('frames', 'continuous'):
            for label, value in values:
                args = {'operator': control['operator'], 'skill': skill,
                        'base_attack': 1000, 'window_seconds': 10,
                        'timing_mode': mode, control['field']: value}
                if control['field'] == 'ghost_casts':
                    args['ghost_count'] = 1
                evaluate(args, {'group': 'active_integer', 'field': control['field'],
                                'identity': label, 'control': control})

# Preserve query-dependent scope: an existing inactive count is not globally
# validated merely because its public key is present.
for field in sorted(fields):
    for mode in ('frames', 'continuous'):
        for label, value in [('absent', ...), ('false', False), ('true', True)]:
            args = {'operator': 'silverash', 'skill': 3, 'base_attack': 1000,
                    'window_seconds': 10, 'timing_mode': mode}
            if value is not ...:
                args[field] = value
            evaluate(args, {'group': 'inactive_other_operator', 'field': field, 'identity': label})

for mode in ('frames', 'continuous'):
    for label, value in [('absent', ...), ('false', False), ('true', True)]:
        args = {'operator': 'char_1035_wisdel', 'skill': 1, 'base_attack': 1000,
                'window_seconds': 10, 'timing_mode': mode, 'ghost_count': 0}
        if value is not ...:
            args['ghost_casts'] = value
        evaluate(args, {'group': 'inactive_query_gate', 'field': 'ghost_casts', 'identity': label})

for control in checkboxes:
    for skill in control['skills']:
        for mode in ('frames', 'continuous'):
            for label, value in [('false', False), ('true', True)]:
                args = {'operator': control['operator'], 'skill': skill,
                        'base_attack': 1000, 'window_seconds': 10,
                        'timing_mode': mode, control['field']: value}
                evaluate(args, {'group': 'real_checkbox', 'field': control['field'],
                                'identity': label, 'control': control})

Combat.option = original_option
counts = Counter()
findings = []
for row in rows:
    queried = any(t['field'] == row['field'] and t['integer'] for t in row['trace'])
    row['field_queried_as_integer'] = queried
    counts[row['group'] + ('_accepted' if row['outcome']['accepted'] else '_error')] += 1
    if row['group'] == 'active_integer' and row['identity'] in ('false', 'true'):
        counts['active_raw_bool_queried' if queried else 'active_raw_bool_not_queried'] += 1
        if queried and row['outcome']['accepted']:
            findings.append({'operator': row['scenario']['operator'],
                             'skill': row['scenario']['skill'],
                             'timing_mode': row['scenario']['timing_mode'],
                             'field': row['field'], 'value': row['scenario'][row['field']]})
for row in rows:
    if row['group'].startswith('inactive') and row['identity'] != 'absent':
        absent = next(x for x in rows if x['group'] == row['group']
                      and x['field'] == row['field'] and x['identity'] == 'absent'
                      and x['scenario']['timing_mode'] == row['scenario']['timing_mode'])
        assert row['outcome'] == absent['outcome']
        assert not row['field_queried_as_integer']

freeze = json.loads((OUT / 'freeze.json').read_text())
assert all(hashlib.sha256((PACKAGE / rel).read_bytes()).hexdigest() == sha
           for rel, sha in freeze['public_source_hashes'].items())
summary = {'baseline_head': freeze['baseline_head'], 'integer_call_sites': calls,
           'unique_integer_keys': 27, 'excluded_section54_keys': sorted(known_guarded),
           'remaining_integer_keys': sorted(fields), 'integer_controls': controls,
           'checkbox_controls': checkboxes, 'counts': dict(counts),
           'accepted_queried_raw_bool_findings': findings, 'source_drift': [],
           'caller_input_unchanged': True, 'runtime_trace_does_not_change_source': True,
           'no_patch_created': True, 'private_state_read': False, 'native_validation': False}
(OUT / 'type-audit-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
payload = {'baseline_head': freeze['baseline_head'], 'import_package': str(PACKAGE),
           'complete_public_cases': rows, 'no_private_state_read': True}
raw = (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode()
(OUT / 'baseline-public-results.json').write_bytes(raw)
compressed = gzip.compress(raw, compresslevel=9, mtime=0)
(OUT / 'baseline-public-results.json.gz').write_bytes(compressed)
assert gzip.decompress(compressed) == raw
(OUT / 'compression-receipt.json').write_text(json.dumps({
    'source_sha256': hashlib.sha256(raw).hexdigest(), 'source_bytes': len(raw),
    'gzip_sha256': hashlib.sha256(compressed).hexdigest(), 'gzip_bytes': len(compressed),
    'decompression_verified': True}, indent=2) + '\n')
print(json.dumps({'public_cases': len(rows), 'counts': dict(counts),
                  'bool_findings': len(findings), 'source_drift': []}))
