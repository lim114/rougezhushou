"""Independent frozen71 and saved38 verification, entirely standard-library I/O."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-crew-count-boolean-089-draft')
MANIFEST_SHA = 'bd067b62de388092018288d2d240ac22f3701d5e081a5b0f5210e6edf33adbc5'
HANDOFF_SHA = 'eddb63c2ed94cfac12bdc329b1d11e5d9e260b77fc4e420be9f3dc6d93c1228c'
TARGET = OUT / 'author-final71-snapshots'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def native(value):
    kind = type(value)
    if kind is dict:
        return {'type': 'dict', 'items': [[native(k), native(v)] for k, v in value.items()]}
    if kind in (list, tuple):
        return {'type': kind.__name__, 'items': [native(v) for v in value]}
    if kind is float:
        return {'type': 'float', 'hex': value.hex()}
    assert kind in (str, int, bool, type(None)), kind
    return {'type': kind.__name__, 'value': value}

def assert_tree(value, tree):
    assert native(value) == tree

manifest_bytes = (AUTHOR / 'author-review-manifest089.json').read_bytes()
handoff_bytes = (AUTHOR / 'author-review-handoff089.json').read_bytes()
assert sha(manifest_bytes) == MANIFEST_SHA and sha(handoff_bytes) == HANDOFF_SHA
manifest = json.loads(manifest_bytes)
handoff = json.loads(handoff_bytes)
assert manifest['version'] == 1 and len(manifest['files']) == 71
TARGET.mkdir(exist_ok=False)
imported = []
for row in manifest['files']:
    source = Path(row['source_path'])
    assert source.is_absolute() and '.local' not in source.parts
    assert any(source.is_relative_to(root) for root in (
        AUTHOR, Path('/workspace/.continuation/p2-crew-count-boolean-089-source'),
        Path('/workspace/.continuation/p2-section089-crew-count-source-lead')))
    relative = Path(row['archive_path'])
    assert not relative.is_absolute() and '..' not in relative.parts
    data = source.read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256'], source
    destination = TARGET / relative
    assert not destination.exists()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    imported.append({**row, 'snapshot_path': str(destination),
                     'review_archive_path': destination.relative_to(OUT).as_posix()})
assert sum(row['bytes'] for row in imported) == 868620
(TARGET / 'author-review-manifest089.json').write_bytes(manifest_bytes)

summary = json.loads((AUTHOR / 'new-test-summary089.json').read_bytes())
compressed = (AUTHOR / 'new-tests-native-records089.json.gz').read_bytes()
raw = gzip.decompress(compressed)
assert len(compressed) == summary['saved_gzip_bytes'] and sha(compressed) == summary['saved_gzip_sha256']
assert len(raw) == summary['decoded_bytes'] and sha(raw) == summary['decoded_sha256']
payload = json.loads(raw)
records = payload['records']
assert len(records) == 38
roles = Counter(record['role'] for record in records)
assert roles == {'constructor_new': 12, 'constructor_reload': 2,
                 'seed_apply': 12, 'subject_apply': 12}
for key, value in payload['summary'].items():
    assert summary[key] == value
assert summary['status'] == 'PASS' and summary['tests_run'] == 7
assert summary['errors'] == summary['failures'] == summary['skips'] == 0

subjects, per_file, ignored = [], {}, []
for record in records:
    assert '.local' not in Path(record['file_path']).parts
    for field in ('state_before', 'state_after', 'return_value'):
        assert_tree(record[field], record[field + '_typed'])
    for field in ('disk_before', 'disk_after'):
        disk = record[field]
        if disk is None:
            continue
        data = disk['UTF8_raw_bytes'].encode('utf-8')
        assert len(data) == disk['bytes'] and sha(data) == disk['sha256']
        decoded = json.loads(data)
        assert native(decoded) == native(disk['JSON'])
        assert_tree(decoded, disk['JSON_typed'])
    if record['method'] == '__init__':
        assert record['return_value'] is None and record['state_before'] is None
        if record['role'] == 'constructor_new':
            assert record['disk_before'] is record['disk_after'] is None
            assert record['state_after']['crew_count'] is None
        else:
            assert record['disk_before'] == record['disk_after']
            for key in ('id', 'started_at', 'last_read', 'operators', 'crew_count',
                        'history', 'resources', 'config', 'relics'):
                assert native(record['state_after'][key]) == native(record['disk_before']['JSON'][key])
        continue
    assert record['method'] == 'apply'
    for field in ('observed_before', 'observed_after'):
        assert_tree(record[field], record[field + '_typed'])
    assert record['observed_before_typed'] == record['observed_after_typed']
    assert record['caller_whole_typed_unchanged'] is True
    start = record['state_before']['started_at']
    assert record['state_after']['id'] == record['state_before']['id']
    assert record['state_after']['started_at'].hex() == start.hex()
    if record['return_value'] is False:
        assert record['role'] == 'subject_apply'
        assert record['state_before_typed'] == record['state_after_typed']
        assert record['disk_before'] == record['disk_after']
        ignored.append(record['sequence'])
    else:
        assert record['return_value'] is True
        assert record['captured_at'] == start + (1 if record['role'] == 'seed_apply' else 2)
        assert record['state_after']['last_read'] == record['captured_at']
        assert record['state_after_typed'] == record['disk_after']['JSON_typed']
    per_file.setdefault(record['file_path'], []).append(record)
    if record['role'] == 'subject_apply':
        observed, before, after = record['observed_before'], record['state_before'], record['state_after']
        count = observed.get('crew_count')
        expected_count = before['crew_count'] if count is None or type(count) is bool else count
        assert native(after['crew_count']) == native(expected_count)
        if type(count) is bool:
            missing = set(before['operators']) - {member['id'] for member in observed['operators']}
            for owner in missing:
                assert after['operators'][owner]['present'] is before['operators'][owner]['present']
            assert not any(event['kind'] == 'operator_no_longer_present'
                           for event in after['history'][len(before['history']):])
        subjects.append({'sequence': record['sequence'], 'file_path': record['file_path'],
            'run_id': before['id'], 'started_at': start, 'started_at_hex': start.hex(),
            'captured_at': record['captured_at'], 'return': record['return_value'],
            'input_count_native': native(count), 'count_after_native': native(after['crew_count']),
            'present_after': [owner for owner, member in after['operators'].items() if member['present']]})
assert len(per_file) == 12 and len(subjects) == 12 and len(ignored) == 2
for group in per_file.values():
    assert [record['role'] for record in group] == ['seed_apply', 'subject_apply']
    assert group[0]['state_after_typed'] == group[1]['state_before_typed']
    assert group[0]['disk_after'] == group[1]['disk_before']
assert len({subject['run_id'] for subject in subjects}) == 12

receipt = {'status': 'PASS_AUTHOR71_BYTES_AND_SAVED38_STRICT_NATIVE_JSON_DISK_ONLY',
    'manifest_sha256': MANIFEST_SHA, 'handoff_sha256': HANDOFF_SHA,
    'imported_files': 71, 'imported_bytes': 868620,
    'saved_gzip_sha256': sha(compressed), 'decoded_sha256': sha(raw),
    'saved_record_count': 38, 'actual_saved_roles': dict(roles),
    'subject_groups': subjects, 'exact_ignored_subjects': ignored,
    'natural_UUID_time_retained': True, 'cross_case_normalization': False,
    'count_bool_local_guard_contract': 'Bool accepted as unread local observation; positive fields still merge; prior count/type retained.',
    'new_calls_this_review': {'RunState_constructor': 0, 'RunState_apply': 0, 'helper': 0,
        'damage_app_API': 0, 'formatter': 0, 'tests': 0, 'recognition': 0,
        'network': 0, 'Qt': 0, 'Wine': 0, 'real_local': 0, 'tracked': 0},
    'imported_file_bindings': imported}
with (OUT / 'author71-saved38-review089.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'status': receipt['status'], 'files': 71, 'bytes': 868620,
                  'records': 38, 'groups': 12, 'new_RunState_calls': 0}))
