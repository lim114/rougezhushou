"""Zero project calls: audit original56-related log versus frozen full090 evidence."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
LOCAL = Path('/workspace/.continuation')
FULL_REF = '2cbc45f03f99ed4f04b9c7e2612b58542f909168'
classification_path = LOCAL / 'root-related-091-availability.json'
log_path = LOCAL / 'root-related-091.log'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
classification_raw = classification_path.read_bytes()
classification = json.loads(classification_raw)
log_raw = log_path.read_bytes(); log = log_raw.decode('utf-8')
assert classification['format_version'] == 1
assert classification['status'] == 'AVAILABLE_RELATED_CHECKS_PASS_WITH_TWO_HISTORICAL_UNAVAILABLE'
assert classification['original_runner'] == {
    'path': str(log_path), 'sha256': sha(log_raw), 'exit_code': 1,
    'tests_run': 56, 'passed': 54, 'failures': 0, 'errors': 2}
labels = re.findall(r'^(test_\w+) \(([^)]+)\) \.\.\. (\w+).*$', log, re.MULTILINE)
assert len(labels) == 56 and len({identity for _, identity, _ in labels}) == 56
assert sum(outcome == 'ok' for _, _, outcome in labels) == 54
assert sum(outcome == 'ERROR' for _, _, outcome in labels) == 2
assert all(outcome in ('ok', 'ERROR') for _, _, outcome in labels)
assert re.search(r'^Ran 56 tests in [0-9.]+s$', log, re.MULTILINE)
assert log.rstrip().endswith('FAILED (errors=2)')
assert log.count('FileNotFoundError: [Errno 2] No such file or directory:') == 2
assert classification['available'] == {'run': 54, 'passed': 54, 'skipped': 0, 'failures': 0, 'errors': 0}
assert classification['available_checks_passed'] is True and classification['unavailable_count'] == 2
assert classification['complete_related_validation'] is False and classification['new_project_calls'] == 0
assert classification['not_rerun_or_reconstructed'] is True
error_ids = {'tests.' + identity for _, identity, outcome in labels if outcome == 'ERROR'}
assert error_ids == {item['test'] for item in classification['unavailable']}

fulls = {}
references = []
for name in ('linux.json', 'wine.json'):
    relative = 'verification/full-090/' + name
    path = ROOT / relative; raw = path.read_bytes()
    committed = subprocess.check_output(['git', 'show', f'{FULL_REF}:{relative}'], cwd=ROOT)
    assert raw == committed
    fulls[name] = json.loads(raw)
    references.append({'source_path': str(path), 'sha256': sha(raw), 'bytes': len(raw),
                       'fixed_git_ref': FULL_REF, 'Git_blob_bytes_exact': True})
assert sha((LOCAL / 'linux-full-090.json').read_bytes()) == references[0]['sha256']
assert classification['historical_classification_source'] == {
    'path': str(LOCAL / 'linux-full-090.json'), 'sha256': references[0]['sha256']}
logical_fixture = '.cache/game-data/roguelike_topic_table.json'
def fixture(reason):
    assert '[Errno 2]' in reason and 'No such file or directory:' in reason
    normalized = re.sub(r'\\+', '/', reason)
    assert normalized.endswith(logical_fixture + "'")
    return logical_fixture
matches = []
for item in classification['unavailable']:
    assert item['kind'] == 'unmigrated_cache'
    assert fixture(item['reason']) == logical_fixture
    short_id = item['test'].removeprefix('tests.')
    method = short_id.rsplit('.', 1)[-1]
    header = f'ERROR: {method} ({short_id})'
    assert header in log
    block = log.split(header, 1)[1].split('======================================================================', 1)[0]
    assert "FileNotFoundError: " + item['reason'] in block
    facts = {}
    for name, full in fulls.items():
        records = [row for row in full['unavailable'] if row['test'] == item['test']]
        assert len(records) == 1 and records[0]['kind'] == 'unmigrated_cache'
        assert fixture(records[0]['reason']) == logical_fixture
        if name == 'linux.json': assert records[0] == item
        facts[name] = records[0]
    matches.append({'test': item['test'], 'original_related_outcome': 'ERROR',
                    'classified_unavailable_not_passed_or_skipped': True, 'historical_full090': facts})
unchanged = []
for relative in ('tests/test_sp_sources_066.py', 'scripts/build_relic_mechanics.py'):
    raw = (ROOT / relative).read_bytes()
    assert raw == subprocess.check_output(['git', 'show', f'{FULL_REF}:{relative}'], cwd=ROOT)
    unchanged.append({'path': relative, 'sha256': sha(raw), 'same_as_full090_Git_bytes': True})
receipt = {
    'format_version': 1, 'status': 'FINAL_PASS_STATIC_RELATED091_AVAILABILITY_CLASSIFICATION',
    'classification': {'source_path': str(classification_path), 'sha256': sha(classification_raw),
                       'bytes': len(classification_raw)},
    'original_log': {'source_path': str(log_path), 'sha256': sha(log_raw), 'bytes': len(log_raw),
                     'tests_run': 56, 'passes': 54, 'errors': 2, 'failures': 0, 'skips': 0,
                     'summary_preserved': 'FAILED (errors=2)', 'root_recorded_exit_code': 1,
                     'exit_status_not_reexecuted_or_independently_reconstructed_from_text': True},
    'available_result': {'checks': 54, 'passed': 54, 'errors': 0, 'failures': 0},
    'unavailable_result': {'checks': 2, 'original_errors': 2, 'counted_as_passed': False,
                           'counted_as_skipped': False, 'same_two_full090_Linux_Wine_ids_and_fixture': True},
    'matches': matches, 'full090_original_bytes': references,
    'fixture_producer_and_tests_same_as_full090': unchanged,
    'complete_related_validation': False,
    'scope': 'Static evidence classification is accurate. Available54 passed; original56-run remains54passes/2errors. Two missing historical-cache cases are unavailable, not test successes or skips. No independent OS exitstatus claim or current fixture-content verification is inferred from logs.',
    'new_API_projecthelper_test_Qt_Wine_network_calls': 0,
    'historical_tests_or_54_passed_checks_reexecuted': False,
    'historical_fixture_read_download_or_reconstructed': False,
    'tracked_or_Deepcolor_final35_files_modified': False,
}
target = OUT / 'independent-availability-receipt091.json'
with target.open('x') as handle:
    handle.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
files = []
for path in (Path(__file__).resolve(), target):
    raw = path.read_bytes()
    files.append({'source_path': str(path), 'archive_path': path.name, 'bytes': len(raw), 'sha256': sha(raw)})
manifest = OUT / 'public-artifacts-manifest-v1.json'
with manifest.open('x') as handle:
    handle.write(json.dumps({'format_version': 1, 'status': receipt['status'], 'files': files,
                             'manifest_self_excluded': True}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'receipt': str(target), 'receipt_sha256': sha(target.read_bytes()),
                  'manifest': str(manifest), 'manifest_sha256': sha(manifest.read_bytes()),
                  'file_count': len(files), 'bytes': sum(row['bytes'] for row in files),
                  'new_project_calls': 0}))
