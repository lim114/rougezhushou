"""Pure saved-only evidence binding; never imports or invokes project code."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def native(value):
    if type(value) is dict:
        return {'type': 'dict', 'items': [[native(k), native(v)] for k, v in value.items()]}
    if type(value) in (list, tuple):
        return {'type': type(value).__name__, 'items': [native(v) for v in value]}
    if type(value) is float:
        return {'type': 'float', 'hex': value.hex()}
    return {'type': type(value).__name__, 'value': value}


def decode(tree):
    kind = tree['type']
    if kind == 'dict':
        return {decode(k): decode(v) for k, v in tree['items']}
    if kind in ('list', 'tuple'):
        items = [decode(v) for v in tree['items']]
        return tuple(items) if kind == 'tuple' else items
    if kind == 'float':
        return float.fromhex(tree['hex'])
    assert kind in ('NoneType', 'bool', 'int', 'str'), kind
    value = tree['value']
    assert type(value).__name__ == kind
    return value


def bind_native(public, tree):
    decoded = decode(tree)
    assert native(decoded) == tree
    projection = json.loads(json.dumps(decoded, ensure_ascii=False, allow_nan=False))
    assert native(projection) == native(public)


def bind_disk(record):
    if record is None:
        return
    raw = record['UTF8_raw_bytes'].encode('utf-8')
    assert len(raw) == record['bytes'] and digest(raw) == record['sha256']
    parsed = json.loads(raw)
    assert native(parsed) == native(record['JSON'])
    bind_native(record['JSON'], record['JSON_typed'])


summary = json.loads((OUT / 'new-test-summary089.json').read_bytes())
compressed = (OUT / 'new-tests-native-records089.json.gz').read_bytes()
assert len(compressed) == summary['saved_gzip_bytes']
assert digest(compressed) == summary['saved_gzip_sha256']
raw = gzip.decompress(compressed)
assert len(raw) == summary['decoded_bytes'] and digest(raw) == summary['decoded_sha256']
saved = json.loads(raw)
assert saved['summary'] == {k: v for k, v in summary.items() if k not in
                           ('saved_gzip_bytes', 'saved_gzip_sha256', 'decoded_bytes', 'decoded_sha256')}
records = saved['records']
assert [r['sequence'] for r in records] == list(range(1, 39))
roles = Counter(r['role'] for r in records)
assert roles == summary['budget_expected'] == summary['actual_explicit_entry_roles']
methods = Counter(r['method'] for r in records)
assert methods == {'__init__': 14, 'apply': 24}
assert summary['actual_RunState_file_entries']['__init__'] == 14
assert summary['actual_RunState_file_entries']['apply'] == 24
subjects = []
ignored = 0
reloads = 0
for record in records:
    assert Path(record['file_path']).is_relative_to(OUT / 'runtime')
    for key in ('state_before', 'state_after', 'return_value'):
        bind_native(record[key], record[key + '_typed'])
    for key in ('disk_before', 'disk_after'):
        bind_disk(record[key])
    if record['method'] == 'apply':
        for key in ('observed_before', 'observed_after'):
            bind_native(record[key], record[key + '_typed'])
        assert record['observed_before_typed'] == record['observed_after_typed']
        assert record['caller_whole_typed_unchanged'] is True
        assert type(record['return_value']) is bool
        assert record['disk_after'] is not None
        assert native(record['disk_after']['JSON']) == native(record['state_after'])
        if record['return_value'] is False:
            ignored += 1
            assert record['role'] == 'subject_apply'
            assert record['state_before_typed'] == record['state_after_typed']
            assert record['disk_before'] == record['disk_after']
        if record['role'] == 'subject_apply':
            old = record['state_before']
            new = record['state_after']
            crew = record['observed_before']['crew_count']
            if type(crew) is bool and record['return_value'] is True:
                assert native(new['crew_count']) == native(old['crew_count'])
                assert {k for k, v in new['operators'].items() if v['present']} == {
                    k for k, v in old['operators'].items() if v['present']}
                assert not any(e['kind'] == 'operator_no_longer_present'
                               for e in new['history'][len(old['history']):])
            subjects.append({'sequence': record['sequence'], 'input_crew_typed': native(crew),
                             'returned': record['return_value'], 'before_crew_typed': native(old['crew_count']),
                             'after_crew_typed': native(new['crew_count']),
                             'present_ids': sorted(k for k, v in new['operators'].items() if v['present'])})
    elif record['role'] == 'constructor_reload':
        reloads += 1
        assert record['disk_before'] is not None
        old = record['disk_before']['JSON']
        new = record['state_after']
        for key in ('id', 'started_at', 'last_read', 'operators', 'crew_count',
                    'history', 'resources', 'config', 'relics'):
            assert native(old[key]) == native(new[key]), key
assert ignored == 2 and reloads == 2 and len(subjects) == 12
assert summary['status'] == 'PASS' and summary['tests_run'] == 7
assert summary['errors'] == summary['failures'] == summary['skips'] == 0
freeze = json.loads((OUT / 'draft-freeze089.json').read_bytes())
for row in freeze['files'] + [freeze['section_patch'], freeze['registry_proposal']]:
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and digest(data) == row['sha256']
receipt = {'status': 'PASS_SAVED_ONLY', 'records': 38, 'constructor_entries_saved': 14,
           'apply_entries_saved': 24, 'caller_trees_unchanged': 24,
           'early_ignored_state_and_disk_exact': 2, 'reload_saved_key_scopes_verified': 2,
           'subjects': subjects, 'compressed_sha256': digest(compressed), 'compressed_bytes': len(compressed),
           'decoded_sha256': digest(raw), 'decoded_bytes': len(raw),
           'native_reencoding_and_separate_JSON_projection': True,
           'new_RunState_helper_API_tests_formatter_Qt_Wine_calls': 0,
           'clock_scope': 'Actual UUID/time retained. No cross-case normalization or full reload state equality claimed.',
           'freeze_product_test_patch_and_registryproposal_exact': True}
with (OUT / 'saved-only-check089.json').open('x', encoding='utf-8') as handle:
    json.dump(receipt, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps({'status': receipt['status'], 'records': 38, 'new_calls': 0}))
