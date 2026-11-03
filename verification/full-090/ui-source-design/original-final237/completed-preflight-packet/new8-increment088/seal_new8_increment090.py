"""Immutable new8 evidence packet, retaining both failures and source-only stages."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / 'public-artifacts-manifest-new8-increment090.json'
HANDOFF = HERE / 'handoff-new8-increment090.json'
assert not MANIFEST.exists() and not HANDOFF.exists()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def describe(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

independent = HERE / 'review-final-saved8/receipt.json'
independent_manifest = HERE / 'review-final-saved8/manifest.json'
assert sha(independent.read_bytes()) == '4fa07a764b4efbf28d77ae802c2d58a844d08b2a4565e7899bd7f076283c55e2'
assert sha(independent_manifest.read_bytes()) == '9dcba4b916bec228452034cdb282a0c97bb3871860cfe6994e6fc800b74f719f'
for row in json.loads(independent_manifest.read_bytes())['files']:
    path = independent_manifest.parent / row['path']
    actual = describe(path)
    assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
summary_path = HERE / 'api-ui090-section088-new8-summary.json'
summary = json.loads(summary_path.read_bytes())
assert summary['passed'] is True and summary['record_count'] == 8
assert summary['ledger']['actual_public_calculation_requests'] == 8
assert summary['ledger']['formatter_actual_entries'] == 32
source_stage = Path('/workspace/.continuation/root-transport-preparation090/public-artifacts-manifest-input-preparation090.json')
assert sha(source_stage.read_bytes()) == '2baa273240109b09d8d4446752a877a2ae8b298848745399cdf1f78034f91047'
source_rows = json.loads(source_stage.read_bytes())['files']
assert len(source_rows) == 142
save(HANDOFF, {
    'format_version': 1, 'status': 'FINAL_NEW8_API_AND_SAVED_ONLY_REVIEW_STABLE_GUI_PENDING',
    'manifest_path': str(MANIFEST), 'new8_summary': describe(summary_path),
    'new8_full_lossless_output': summary['result_gzip'],
    'independent_final_receipt': describe(independent),
    'independent_final_manifest': describe(independent_manifest),
    'actual_source_commit': '3a59aa0c3d09199caea14de3c5fe89781225a8d6',
    'actual_root088_commit': '66df88c3274e37ba0f176adcd862a439a6f99767',
    'actual_public_source_count': 126, 'actual_maintained_source_count': 728,
    'execution_segments_actual_API_requests': [3, 2, 3],
    'execution_segments_explicit_text_requests': [9, 6, 9],
    'execution_segments_actual_formatter_entries': [12, 8, 12],
    'ledger': summary['ledger'], 'completed_requests_reexecuted': 0,
    'prepared_shape_harness_failed_attempts': 2, 'product_failures': 0,
    'same_problem_third_attempt_defer_threshold_reached': False,
    'same_call_engine_return_trace_actual_records': [4, 5, 6, 7, 8],
    'record3_actual_engine_return_trace_claimed_or_backfilled': False,
    'whole_saved3_and_saved5_prefixes_and_all_original_counterexamples_preserved': True,
    'all8_raw_output_checkpoint_saved_before_final_prepared_assertions': True,
    'source_before_after_zero_drift': True,
    'original_source_only_stage142': describe(source_stage),
    'original107_snapshot110_and_nested35_38_unchanged': True,
    'public126_package_body_excluded_from_archive': True,
    'public126_package_rebuild': str(HERE / 'actual-root089-ui090-source-proof.json'),
    'Qt_Wine_RunState_constructor_apply_actual_calls': 0,
    'actual_root090_static_transport_and_final_GUI_still_pending_at_this_stage': True,
    'next_step': 'Bind actual root090730 maintained source and require all126 public bytes unchanged; never repeat new8. Wire a separate actual MainWindow runner, root alone executes once after final formal static review.',
})
rows = []
for path in sorted(HERE.rglob('*')):
    if not path.is_file() or path == MANIFEST or '__pycache__' in path.parts:
        continue
    if path.is_relative_to(HERE / 'public-schema-actual-root089'):
        continue
    raw = path.read_bytes()
    rows.append({'source_path': str(path), 'archive_path': 'new8-increment088/' + path.relative_to(HERE).as_posix(),
        'bytes': len(raw), 'sha256': sha(raw)})
for row in source_rows:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    rows.append({**row, 'archive_path': 'source-input-preparation090/' + row['archive_path']})
rows.append({**describe(source_stage), 'archive_path': 'source-input-preparation090/' + source_stage.name})
assert len({row['archive_path'] for row in rows}) == len(rows)
save(MANIFEST, {'format_version': 1, 'status': 'FINAL_IMMUTABLE_NEW8_EVIDENCE_GUI_PENDING',
    'file_count': len(rows), 'total_bytes': sum(r['bytes'] for r in rows),
    'manifest_self_excluded': True, 'public_package_rebuild_from_named_git_proof_included': True,
    'files': rows})
print(json.dumps({'manifest': describe(MANIFEST), 'handoff': describe(HANDOFF),
    'file_count': len(rows), 'total_bytes': sum(r['bytes'] for r in rows),
    'actual_API_requests': 8, 'actual_explicit_text_requests': 24,
    'actual_formatter_entries': 32, 'actual_Qt_Wine': 0}, ensure_ascii=False))
