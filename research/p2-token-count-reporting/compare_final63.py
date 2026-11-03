"""Strict public-JSON comparison; numeric 1 and 1.0 remain distinct."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P / 'draft63'))
sys.dont_write_bytecode = True
from rouge.damage import calculate_damage


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False,
                      separators=(',', ':'))


def difference(left, right, path=''):
    if type(left) is not type(right):
        return [{'path': path, 'before': left, 'after': right}]
    if isinstance(left, dict):
        assert left.keys() == right.keys(), path
        return [d for k in left for d in difference(left[k], right[k], path + '/' + k)]
    if isinstance(left, list):
        assert len(left) == len(right), path
        return [d for i, v in enumerate(left) for d in difference(v, right[i], path + '/' + str(i))]
    return [] if left == right else [{'path': path, 'before': left, 'after': right}]


baseline = json.loads((P / 'validation-after61/baseline61.json').read_text())
draft = json.loads((P / 'validation-after61/draft63.json').read_text())
before, after = baseline['records'], draft['records']
counts = Counter()
repairs, changed, original_dtype_controls, inactive, errors = [], [], [], [], []
for old, new in zip(before, after):
    assert old['id'] == new['id']
    counts[old['status'] + '_to_' + new['status']] += 1
    raw = old['input'].get('summon_count')
    if old['status'] == new['status'] == 'raised':
        assert canonical(old['exception']) == canonical(new['exception'])
        errors.append(old['id'])
    elif old['status'] == 'raised' and new['status'] == 'returned':
        assert old['input']['operator'] == 'char_110_deepcl' and type(raw) is str
        assert old['exception'] == {'type': 'TypeError', 'message': "can't multiply sequence by non-int of type 'float'"}
        repairs.append(old['id'])
    else:
        assert old['status'] == new['status'] == 'returned'
        d = difference(old['result'], new['result'])
        nonreport_old = {k: v for k, v in old['result'].items() if k != 'report'}
        nonreport_new = {k: v for k, v in new['result'].items() if k != 'report'}
        assert canonical(nonreport_old) == canonical(nonreport_new)
        if d:
            assert old['input']['operator'] == 'char_110_deepcl' and type(raw) is str
            assert all(row['path'].startswith('/report/') and row['before'] == raw
                       and type(row['after']) is int and row['after'] == int(float(raw)) for row in d)
            changed.append({'id': old['id'], 'differences': d})
        else:
            counts['whole_strict_json_unchanged'] += 1
        if type(raw) in (int, float):
            assert not d
            original_dtype_controls.append({'id': old['id'], 'raw_type': type(raw).__name__})
        if old['context'].startswith('inactive/'):
            assert not d
            inactive.append(old['id'])

lookup = {(canonical(r['input']), r['synthetic_guard_fixture']): r for r in after
          if r['status'] == 'returned' and type(r['input'].get('summon_count')) is int}
pairs, extra = [], []
for row in after:
    args = row['input']
    if row['status'] != 'returned' or args['operator'] != 'char_110_deepcl' or type(args.get('summon_count')) is not str:
        continue
    numeric = {**args, 'summon_count': int(float(args['summon_count']))}
    control = lookup.get((canonical(numeric), row['synthetic_guard_fixture']))
    if control is not None:
        assert canonical(row['result']) == canonical(control['result'])
        pairs.append({'string_id': row['id'], 'numeric_id': control['id'], 'whole_strict_json_equal': True})
    else:
        # The original extra-probe set contains float controls, not int controls.
        # Eight missing integer controls are real additional public API calls.
        assert not row['synthetic_guard_fixture']
        result = calculate_damage(numeric)
        assert canonical(row['result']) == canonical(result)
        extra.append({'string_id': row['id'], 'numeric_input': numeric,
                      'numeric_result': result, 'whole_strict_json_equal': True})
assert len(before) == len(after) == 538
assert len(repairs) == 80 and len(changed) == 68
assert len(original_dtype_controls) == 168
assert len(pairs) == 140 and len(extra) == 8
assert len(errors) == 133
receipt = {'scope': 'Strict full public JSON, including int/float dtype; no Python numeric-equality substitution',
           'calls_replayed': 1076, 'additional_integer_control_calls': len(extra),
           'counts': dict(counts), 'repaired_original_report_typeerrors': repairs,
           'report_only_raw_string_to_integer_changes': changed,
           'unchanged_original_numeric_dtype_controls': original_dtype_controls,
           'unchanged_inactive_controls': inactive, 'unchanged_original_errors': errors,
           'string_integer_strict_pairs': pairs, 'additional_integer_controls': extra,
           'source_receipt_hashes': {name: hashlib.sha256((P / 'validation-after61' / name).read_bytes()).hexdigest()
                                     for name in ('baseline61.json', 'draft63.json')},
           'gui_executed': False, 'wine_executed': False}
path = P / 'validation-after61/strict-comparison.json'
path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
print(json.dumps({'receipt': str(path), 'replayed_calls': 1076, 'additional_calls': len(extra),
                  'repairs': len(repairs), 'raw_string_report_changes': len(changed),
                  'numeric_dtype_unchanged': len(original_dtype_controls),
                  'inactive_unchanged': len(inactive), 'errors_unchanged': len(errors),
                  'whole_string_integer_pairs': len(pairs) + len(extra), 'counts': dict(counts)}))
