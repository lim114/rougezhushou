import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
old_path = ROOT / 'history' / 'gummy-visible-production-record.json'
new_path = ROOT / 'parse-Front-result.json'
operation_path = ROOT / 'parse-Front-operation.json'
old = json.loads(old_path.read_text())['operator']['records']
new = json.loads(new_path.read_text())
operation = json.loads(operation_path.read_text())
assert operation['reader_returned'] is True and operation['full_skeleton_parser_calls'] == 1
assert operation['after_read_byte_invariance']['input_unchanged'] and operation['after_read_byte_invariance']['resource_file_unchanged']
assert {record['animation'] for record in old} == {record['name'] for record in new['animations']}
assert len(old) == len(new['animations']) == 9
by_name = {record['name']: record for record in new['animations']}
comparisons = []
for record in old:
    actual = by_name[record['animation']]
    expected_events = [{'name': event['name'], 'seconds': event['seconds']} for event in record['events']]
    actual_events = [{'name': event['name'], 'seconds': event['seconds']} for event in actual['events']]
    assert record['spine_version'] == new['skeleton']['spine_version'] == '3.8.99'
    assert record['duration']['seconds'] == actual['duration_seconds']
    assert expected_events == actual_events
    assert record['source']['sha256'] == new['resource']['sha256']
    assert record['source']['bytes'] == new['resource']['bytes']
    assert record['source']['git_blob'] == new['resource']['git_blob_sha1']
    comparisons.append({'animation': record['animation'], 'version_exact': True, 'duration_seconds_exact': True, 'event_names_and_seconds_exact': True, 'source_identity_exact': True, 'duration_seconds': actual['duration_seconds'], 'events': actual_events})
receipt = {
    'version': 1, 'operation': 'Saved-source Front control comparison only; no fresh reader or application invocation',
    'read_inputs': [{'source_path': str(p), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in (old_path, new_path, operation_path)],
    'front_source_records_compared': 9, 'compared_fields': ['spine_version', 'duration_seconds', 'event_names_and_seconds', 'source_bytes_sha256_git_blob'],
    'scope': 'Exact agreement of these fields does not establish historical parser identity, atlas/render validity, new event clocks or native bindings',
    'comparisons': comparisons, 'passed': True,
    'fresh_skeleton_parser_calls': 0, 'application_API_helper_formatter_test_Qt_Wine_calls': 0,
}
(ROOT / 'front-control-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'passed': True, 'records': 9, 'fresh_parser_calls': 0}, indent=2))
