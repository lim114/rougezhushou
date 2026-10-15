"""Archive exact prior offline3 pure-reader execution; do not run the reader."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FULL = ROOT / 'verification/full-290'
DEST = FULL / 'offline3-component-readback-evidence'
AUDIT = FULL / 'offline3-component-readback-evidence-readback.json'
SOURCE = ROOT / '.cache/p3-full290-review'
PRIOR_MANIFEST = FULL / 'offline-attempt3/archive-manifest.json'
REPORT = FULL / 'offline3-component-readback.json'
PRIOR_SHA = '466140d8659dad24bcdcd8ef58a91ade08cd406105531347e6f4ae69ebef5305'
REPORT_SHA = 'dc49bbbc472fee42e26329c0a00a0dc87b06414a05176ad70ba07d33040b7e48'
READER_SHA = '195cdd84a9a40359f4b48dd3a7ae21978340f061a83218e909e6202d85c6f813'


def digest(value):
    return sha256(value).hexdigest()


def fail(condition, message):
    if condition is not True:
        raise ValueError(message)


def raw(path, boundary=ROOT):
    fail(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(boundary.resolve()), 'unsafe/nonregular file: ' + str(path))
    return path.read_bytes()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def snapshot_original_archive():
    value = raw(PRIOR_MANIFEST)
    fail(digest(value) == PRIOR_SHA, 'sealed final offline3 manifest changed')
    files = json.loads(value)['files']
    fail(len(files) == 213, 'original sealed offline archive member count changed')
    observed = {}
    for name, record in files.items():
        data = raw(PRIOR_MANIFEST.parent / name, PRIOR_MANIFEST.parent)
        observed[name] = {'sha256': digest(data), 'bytes': len(data)}
        fail(observed[name] == {key: record[key] for key in ('sha256', 'bytes')}, 'sealed original member: ' + name)
    return observed


def main():
    fail(not DEST.exists() and not AUDIT.exists(), 'fresh evidence destinations required; never overwrite')
    before = snapshot_original_archive()
    report = raw(REPORT)
    fail(digest(report) == REPORT_SHA, 'existing component receipt changed')
    reader_path = SOURCE / 'audit_actual_final_offline3.py'
    reader = raw(reader_path)
    fail(digest(reader) == READER_SHA, 'exact executed reader source changed')
    items = {'executed-reader/audit_actual_final_offline3.py': (reader, reader_path.relative_to(ROOT).as_posix())}
    directory = SOURCE / 'final-offline3-component-readback-execution'
    fail({path.name for path in directory.iterdir()} == {'stdout.log', 'stderr.log', 'process.exit', 'process.json'}, 'original readback execution inventory changed')
    for name in ('stdout.log', 'stderr.log', 'process.exit', 'process.json'):
        path = directory / name
        items['actual-execution/' + name] = (raw(path), path.relative_to(ROOT).as_posix())
    process = json.loads(items['actual-execution/process.json'][0])
    fail(process['kind'] == 'ACTUAL_PURE_OFFLINE3_COMPONENT_READBACK_PROCESS' and process['actual_observed_subprocess_returncode'] == 0 and process['exit_derived_from_receipt'] is False, 'actual prior readback process authority')
    fail(process['producer_sha256_before'] == process['producer_sha256_after'] == READER_SHA and process['tests_GUI_or_calculation_run'] is False and process['final_summary_builder_or_close_called'] is False, 'actual reader source and operation boundary')
    fail(items['actual-execution/process.exit'][0] == b'0\n' and items['actual-execution/stderr.log'][0] == b'', 'exact original exit/stderr')
    stdout = json.loads(items['actual-execution/stdout.log'][0])
    fail(stdout['sha256'] == REPORT_SHA and stdout['archive_members_verified'] == 213 and stdout['final_combined_full_pass_claimed'] is False and stdout['additional_test_count'] == 0, 'actual prior stdout report binding')
    items['component-report-original.json'] = (report, REPORT.relative_to(ROOT).as_posix())
    note = {
        'kind': 'APPEND_ONLY_ARCHIVAL_ORCHESTRATION_EXPLANATION_NOT_ORIGINAL_RAW',
        'original_separate_orchestration_json_existed': False,
        'actual_execution_authority': 'actual-execution/process.json',
        'explanation': 'The original execution contains exactly stdout.log, stderr.log, process.exit and process.json. The exact process.json records actual argv, observed subprocess returncode and producer SHA before/after. No separate original orchestration file is reconstructed.',
        'source_copies_rewritten': False,
        'reader_reexecuted_by_archival': False,
        'new_test_count': 0,
        'final_summary_or_close_executed': False,
        'final_combined_full_pass_claimed': False,
    }
    items['orchestration-record-note.json'] = (encode(note), 'new append-only archival explanation; not original execution raw')
    items['archival-producer/archive_offline3_component_readback.py'] = (raw(Path(__file__)), Path(__file__).resolve().relative_to(ROOT).as_posix())
    DEST.mkdir()
    files = {}
    for name, (value, source) in items.items():
        path = DEST / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(value)
        files[name] = {'sha256': digest(value), 'bytes': len(value), 'source': source}
    manifest = {
        'kind': 'EXACT_ALREADY_EXECUTED_OFFLINE3_COMPONENT_READBACK_EVIDENCE_ARCHIVE',
        'explicit_allowlist_only': True,
        'files': files,
        'source_component_receipt_sha256': REPORT_SHA,
        'sealed_original_archive_manifest_sha256': PRIOR_SHA,
        'sealed_original_member_count': 213,
        'raw_separate_orchestration_missing_not_reconstructed': True,
        'reader_reexecuted': False,
        'new_test_count': 0,
        'final_combined_full_pass_claimed': False,
    }
    manifest_path = DEST / 'archive-manifest.json'
    with manifest_path.open('xb') as stream:
        stream.write(encode(manifest))
    manifest_raw = raw(manifest_path)
    actual = json.loads(manifest_raw)
    for name, record in actual['files'].items():
        value = raw(DEST / name, DEST)
        fail(digest(value) == record['sha256'] and len(value) == record['bytes'], 'new archive member hash/size: ' + name)
    fail(snapshot_original_archive() == before and raw(REPORT) == report, 'original sealed members/component receipt changed')
    audit = {
        'kind': 'PURE_ARCHIVAL_HASH_READBACK_NOT_ADDITIONAL_VALIDATION',
        'evidence_manifest': manifest_path.relative_to(ROOT).as_posix(),
        'evidence_manifest_sha256': digest(manifest_raw),
        'all_allowlisted_member_sha256_and_sizes_match': True,
        'archived_member_count': len(files),
        'original_213_members_unchanged': True,
        'original_component_receipt_sha256_unchanged': REPORT_SHA,
        'original_archive_manifest_sha256_unchanged': PRIOR_SHA,
        'original_actual_readback_returncode': process['actual_observed_subprocess_returncode'],
        'reader_reexecuted': False,
        'new_test_count': 0,
        'final_combined_full_pass_claimed': False,
    }
    with AUDIT.open('xb') as stream:
        stream.write(encode(audit))
    print(json.dumps({'archive_manifest': manifest_path.relative_to(ROOT).as_posix(), 'manifest_sha256': digest(manifest_raw), 'member_count': len(files), 'readback': AUDIT.relative_to(ROOT).as_posix(), 'readback_sha256': digest(raw(AUDIT)), 'originals_unchanged': True, 'reader_reexecuted': False, 'new_test_count': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
