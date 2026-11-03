"""Seal the source-only preparation stage; no product imports or calls."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / 'public-artifacts-manifest-input-preparation090.json'
HANDOFF = HERE / 'handoff-input-preparation090.json'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def describe(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}

assert not MANIFEST.exists() and not HANDOFF.exists(), 'Do not reseal an immutable stage'
plan = HERE / 'additional8-input-plan090.json'
assert sha(plan.read_bytes()) == '31beb7f95a256172591226127562324be6625317fd1ad406baa84851130dd521'
native = HERE / 'saved89-native-proof090.json'
assert sha(native.read_bytes()) == 'bfbb7b1afedbf0b63fd8e2ab5ac858a40ad1358fc17f3febe20b643655cfaea0'
range_proof = HERE / 'input-range-proof090.json'
assert sha(range_proof.read_bytes()) == '70339b0e40112720104cf0293e90bd1ce10e74c6b1a9275466774ba6fa81aea3'
original_snapshot = HERE / 'immutable-preparation-stage107/immutable-snapshot-stage107-manifest.json'
assert sha(original_snapshot.read_bytes()) == '19ee423295b4367fb3fbfc4f2ba69b766eeede55c82e10df1f3dd58586c05dba'
snapshot_rows = json.loads(original_snapshot.read_bytes())['files']
assert len(snapshot_rows) == 110
for row in snapshot_rows:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
saved89 = json.loads((HERE / 'saved89-five-state-UI-consumer-design090.json').read_bytes())
original38 = saved89['original_saved38']
raw38 = Path(original38['source_path']).read_bytes()
assert sha(raw38) == original38['sha256'] and len(raw38) == original38['bytes']
saved_dir = HERE / 'saved89'
saved_dir.mkdir()
copied38 = saved_dir / 'original-author38-native-records089.json.gz'
copied38.write_bytes(raw38)
save(saved_dir / 'original38-source-archive-map090.json', {
    'status': 'EXACT_PUBLISHED_SYNTHETIC_AUTHOR38_COPY_NOT_REEXECUTED',
    'original_source_path': original38['source_path'],
    'archive_path': copied38.relative_to(HERE).as_posix(),
    **describe(copied38), 'native_proof_reused_without_rerun': describe(native),
    'RunState_constructor_apply_or_application_calls': 0,
})
review = HERE / 'review-input-plan/manifest.json'
assert review.exists(), 'Independent source-only plan review must be sealed first'
review_receipt = HERE / 'review-input-plan/receipt.json'
assert review_receipt.exists()
assert sha(review.read_bytes()) == '7cfb1756020d397b88b7f702cdee0624ba829516cbfbe1cc924fce376bbe2732'
assert sha(review_receipt.read_bytes()) == '57ae87e74612c162baaa04308dca2817bda0df324d58c0492a12cf2e5a8af313'
for row in json.loads(review.read_bytes())['files']:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
save(HANDOFF, {
    'format_version': 1,
    'status': 'FINAL_SOURCE_ONLY_INPUT_PREPARATION_RUNTIME_AND_ACTUAL_ROOT088_TRANSPORT_PENDING',
    'manifest_path': str(MANIFEST),
    'original107_snapshot_manifest': describe(original_snapshot),
    'original107_artifacts': 107, 'original107_new_snapshot_manifest_rows': 110,
    'original107_new_snapshot_files_including_manifest': 111,
    'original35_nested38_and_original107_files_remain_immutable': True,
    'new_inputs_plan': describe(plan), 'widget_range_proof': describe(range_proof),
    'independent_plan_manifest': describe(review),
    'independent_plan_receipt': describe(review_receipt),
    'saved89_native_proof': describe(native),
    'new_damage_API_budget': 8, 'new_unique_arguments': 8,
    'explicit_three_text_request_budget': 24,
    'formatter_delegate_entries_expected_if_source_unchanged_but_not_measured': 32,
    'new_damage_API_actual_calls': 0, 'new_formatter_actual_calls': 0,
    'new_Qt_Wine_calls': 0, 'new_RunState_constructor_calls': 0,
    'new_RunState_apply_calls': 0, 'product_helpers_tests_network_calls': 0,
    'actual_baseline_producer_commit': '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0',
    'actual088_089_090_root_source_freeze_complete': False,
    'next_resume': [
        'Receive named actual root088 tag and transport public source with exact gitblob proof.',
        'Freeze final-source result contracts and adapter before the single authorized new8 API batch.',
        'Save native and JSON outputs, caller inputs before/after, three texts and actual instrumentation; reuse completed requests only.',
        'Use saved-only independent review; actual89/90 later freeze whole rootsource with no API rerun.',
        'Only after all actual86–90 final sources, wire pending runner while preserving full old4217 literal body; root alone runs actual MainWindow.',
    ],
    'Amiya_empty_target_expressible_by_actual_QPlainTextEdit_but_Qt_not_run': True,
    'saved89_five_states': 'Exact published synthetic public-state replay for future real window membership/training consumers; not apply pipeline, OCR or native departure.',
    'initial_diagnostics_and_failed_reader_scripts_retained': True,
    'same_problem_three_failed_attempts_deferred_required_when_reached': True,
})
rows = []
for path in sorted(HERE.rglob('*')):
    if not path.is_file() or path == MANIFEST or '__pycache__' in path.parts:
        continue
    raw = path.read_bytes()
    rows.append({'source_path': str(path), 'archive_path': path.relative_to(HERE).as_posix(),
                 'bytes': len(raw), 'sha256': sha(raw)})
save(MANIFEST, {'format_version': 1,
    'status': 'IMMUTABLE_SOURCE_ONLY_INPUT_PREPARATION_STAGE_RUNTIME_PENDING',
    'file_count': len(rows), 'total_bytes': sum(r['bytes'] for r in rows),
    'manifest_self_excluded': True, 'files': rows})
print(json.dumps({'status': 'FINAL_SOURCE_ONLY_PREPARATION_SEALED_NO_PRODUCT_CALLS',
    'manifest': describe(MANIFEST), 'handoff': describe(HANDOFF),
    'file_count': len(rows), 'total_bytes': sum(r['bytes'] for r in rows)}, ensure_ascii=False))
