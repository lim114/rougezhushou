"""Archive an already executed pure readback; do not execute its reader."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FULL = ROOT / 'verification/full-290'
DEST = FULL / 'legacy4-component-readback-evidence'
AUDIT = FULL / 'legacy4-component-readback-evidence-readback.json'
SOURCE = ROOT / '.cache/p3-full290-summary-prep'
PRIOR_MANIFEST = FULL / 'legacy-retry-attempt4/archive-manifest.json'
REPORT = FULL / 'legacy4-component-readback.json'
PRIOR_SHA = 'f307d8b47ea246c0983853b78b60cbd14246f68c0766b688d64cf242aaac5929'
REPORT_SHA = 'cca99dcf1d9cba8471a8aa8f11c31af0b0a04ffb4b4095e8fed25b568171a3a4'
SOURCES = {
    'executed-reader/readback_final_legacy4_component.py': ('readback_final_legacy4_component.py', 'd0128da450240927af7572991eb3e7a5edc10b0c93a30f0324b7e95ea1f05ccb'),
    'executed-reader/build_final_A3_summary_candidate.py': ('build_final_A3_summary_candidate.py', 'ecd97b6c11a4e4721ea2a3d55f2f702134951b14586a643260626e0ea1055f2c'),
    'executed-reader/build_summary_candidate.py': ('build_summary_candidate.py', 'c4cd99c2b2a83a42c07c7eee94d40faf36536a88ddcf1f67c30b49f5b8cedcd5'),
}


def digest(raw):
    return sha256(raw).hexdigest()


def read_regular(path, boundary=ROOT):
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(boundary.resolve()):
        raise ValueError('Not a regular allowlisted file: ' + str(path))
    return path.read_bytes()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def archive_snapshot():
    raw = read_regular(PRIOR_MANIFEST)
    if digest(raw) != PRIOR_SHA:
        raise ValueError('Sealed legacy4 manifest changed')
    declared = json.loads(raw)['files']
    if len(declared) != 233:
        raise ValueError('Sealed legacy4 member count changed')
    snapshot = {}
    for name in declared:
        path = PRIOR_MANIFEST.parent / name
        value = read_regular(path, PRIOR_MANIFEST.parent)
        snapshot[name] = {'sha256': digest(value), 'bytes': len(value)}
        if snapshot[name] != {k: declared[name][k] for k in ('sha256', 'bytes')}:
            raise ValueError('Existing sealed member differs: ' + name)
    return snapshot


def main():
    if DEST.exists() or AUDIT.exists():
        raise ValueError('Fresh evidence destinations required; never overwrite')
    prior_before = archive_snapshot()
    report_before = read_regular(REPORT)
    if digest(report_before) != REPORT_SHA:
        raise ValueError('Existing public component report changed')
    items = {}
    for target, (relative, expected) in SOURCES.items():
        path = SOURCE / relative
        raw = read_regular(path)
        if digest(raw) != expected:
            raise ValueError('Exact executed source changed: ' + relative)
        items[target] = (raw, path.relative_to(ROOT).as_posix())
    execution = SOURCE / 'final-legacy4-component-readback-execution'
    if {p.name for p in execution.iterdir()} != {'stdout.log', 'stderr.log', 'process.exit', 'process.json'}:
        raise ValueError('Unexpected readback execution inventory')
    for name in ('stdout.log', 'stderr.log', 'process.exit', 'process.json'):
        path = execution / name
        items['actual-execution/' + name] = (read_regular(path), path.relative_to(ROOT).as_posix())
    process = json.loads(items['actual-execution/process.json'][0])
    if process['kind'] != 'ACTUAL_PURE_LEGACY4_COMPONENT_READBACK_PROCESS' or process['actual_observed_subprocess_returncode'] != 0 or process['exit_derived_from_receipt'] is not False:
        raise ValueError('Original actual process record is not successful pure readback')
    if process['producer_sha256_before'] != SOURCES['executed-reader/readback_final_legacy4_component.py'][1] or process['producer_sha256_after'] != process['producer_sha256_before']:
        raise ValueError('Original process source binding differs')
    if process['final_summary_builder_main_or_close_called'] is not False or process['tests_GUI_or_calculation_run'] is not False:
        raise ValueError('Readback boundaries differ')
    if items['actual-execution/process.exit'][0] != b'0\n' or items['actual-execution/stderr.log'][0] != b'':
        raise ValueError('Actual readback exit/stderr differ')
    stdout = json.loads(items['actual-execution/stdout.log'][0])
    if stdout['sha256'] != REPORT_SHA or stdout['archive_members_verified'] != 233 or stdout['final_full_pass_claimed'] is not False:
        raise ValueError('Actual stdout does not bind the existing report')
    items['component-report-original.json'] = (report_before, REPORT.relative_to(ROOT).as_posix())
    note = {
        'kind': 'APPEND_ONLY_ARCHIVAL_ORCHESTRATION_EXPLANATION_NOT_ORIGINAL_RAW',
        'separate_original_orchestration_json_existed': False,
        'actual_execution_authority': 'actual-execution/process.json',
        'actual_process_record_contains': ['argv', 'actual_observed_subprocess_returncode', 'producer_sha256_before', 'producer_sha256_after'],
        'explanation': 'The original execution directory contains exactly stdout.log, stderr.log, process.exit and process.json. No separate raw orchestration file is reconstructed or claimed. The exact original process.json is the actual execution/orchestration record.',
        'source_copies_rebased_or_rewritten': False,
        'reader_reexecuted_by_archival': False,
        'summary_builder_main_or_close_executed_by_archival': False,
        'additional_tests_or_GUI_executed': False,
        'additional_validation_count': 0,
        'final_full_pass_claimed': False,
    }
    items['orchestration-record-note.json'] = (json_bytes(note), 'new append-only archival explanation; not original execution raw')
    items['archival-producer/archive_legacy4_component_readback.py'] = (read_regular(Path(__file__)), Path(__file__).resolve().relative_to(ROOT).as_posix())
    DEST.mkdir()
    files = {}
    for name, (raw, original) in items.items():
        path = DEST / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as target:
            target.write(raw)
        files[name] = {'sha256': digest(raw), 'bytes': len(raw), 'source': original}
    manifest = {
        'kind': 'EXACT_ALREADY_EXECUTED_LEGACY4_COMPONENT_READBACK_EVIDENCE_ARCHIVE',
        'explicit_allowlist_only': True,
        'files': files,
        'source_component_report_sha256': REPORT_SHA,
        'sealed_original_archive_manifest_sha256': PRIOR_SHA,
        'sealed_original_member_count': 233,
        'raw_separate_orchestration_missing_not_reconstructed': True,
        'reader_reexecuted': False,
        'new_test_count': 0,
        'final_full_pass_claimed': False,
    }
    manifest_path = DEST / 'archive-manifest.json'
    with manifest_path.open('xb') as target:
        target.write(json_bytes(manifest))
    actual_manifest_raw = read_regular(manifest_path)
    actual_manifest = json.loads(actual_manifest_raw)
    for name, record in actual_manifest['files'].items():
        raw = read_regular(DEST / name, DEST)
        if digest(raw) != record['sha256'] or len(raw) != record['bytes']:
            raise ValueError('New evidence member readback failed: ' + name)
    if archive_snapshot() != prior_before or read_regular(REPORT) != report_before:
        raise ValueError('Existing sealed evidence changed during archival')
    audit = {
        'kind': 'PURE_ARCHIVAL_HASH_READBACK_NOT_ADDITIONAL_VALIDATION',
        'evidence_manifest': manifest_path.relative_to(ROOT).as_posix(),
        'evidence_manifest_sha256': digest(actual_manifest_raw),
        'all_allowlisted_member_sha256_and_sizes_match': True,
        'archived_member_count': len(actual_manifest['files']),
        'original_233_members_unchanged': True,
        'original_component_report_sha256_unchanged': REPORT_SHA,
        'original_archive_manifest_sha256_unchanged': PRIOR_SHA,
        'raw_execution_returncode': process['actual_observed_subprocess_returncode'],
        'reader_reexecuted': False,
        'new_test_count': 0,
        'final_full_pass_claimed': False,
    }
    with AUDIT.open('xb') as target:
        target.write(json_bytes(audit))
    print(json.dumps({'archive_manifest': manifest_path.relative_to(ROOT).as_posix(), 'manifest_sha256': digest(actual_manifest_raw), 'member_count': len(files), 'readback': AUDIT.relative_to(ROOT).as_posix(), 'readback_sha256': digest(read_regular(AUDIT)), 'originals_unchanged': True, 'reader_reexecuted': False, 'new_test_count': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
