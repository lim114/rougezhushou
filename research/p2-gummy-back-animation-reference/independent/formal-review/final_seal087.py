"""One-time final byte manifest; no repeated verification execution or product calls."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
AUTHOR = ROOT.parents[1] / 'p2-gummy-back-animation-reference-087-draft'
MANIFEST = ROOT / 'final-public-artifacts-manifest087.json'
HANDOFF = ROOT / 'final-handoff087.json'
assert not MANIFEST.exists() and not HANDOFF.exists()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

numeric_path = ROOT / 'independent-numeric-and-test-review087.json'
static_path = ROOT / 'static-source-and-saved35-review087.json'
numeric = json.loads(numeric_path.read_text())
static = json.loads(static_path.read_text())
assert numeric['status'] == 'PASS_INDEPENDENT12_PAIRS_AND_7_NEW_TESTS'
assert static['status'] == 'PASS_STATIC_AND_SAVED_0_NEW_API'
assert numeric['API_ledger']['total_actual_fresh_public_API_calls'] == 35
assert static['original923_literal_bytes_and_exact_JSON_types_values_preserved'] == 923

child = ROOT / 'source-subreview'
child_files = {'source-handoff087.json': 'eedbb06b98478ec9546df79bf82df4accf0be32f526e71c9d1da23bc87503662',
    'v1-public-files-manifest087.json': 'f264a96c1ef2f7a658e111041dc27bcd2fd993afcbf69c9251a0baca545466dc',
    'static-source-receipt087.json': '5524c4710a3497c80f12ccd6a4e3c8e4ececca41b401ddd1b3ee6f6073665bbf'}
for name, expected in child_files.items():
    assert sha(child / name) == expected
child_manifest = json.loads((child / 'v1-public-files-manifest087.json').read_text())
assert len(child_manifest['files']) == 9
for row in child_manifest['files']:
    path = Path(row['path'])
    assert path.parent == child
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']

prepared_manifest_path = BASE / 'source-preparation-manifest087.json'
assert sha(prepared_manifest_path) == '4f60389e71644ba05d4cf2d6ac6720f8c5682e469aaa1d5cd181c180c41bfc5f'
prepared_manifest = json.loads(prepared_manifest_path.read_text())
for row in prepared_manifest['files']:
    path = BASE / row['archive_path']
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']

freeze_path = AUTHOR / 'author-freeze087.json'
assert sha(freeze_path) == 'f19a69e6dcba6c1368910a0b7c529af1f0e7083f3d4e3561ab5e5c8ad9559b1a'
freeze = json.loads(freeze_path.read_text())
for row in freeze['source_files']:
    p = Path(row['draft_source_path'])
    assert p.stat().st_size == row['draft_bytes'] and sha(p) == row['draft_sha256']
assert sha(Path(freeze['patch']['source_path'])) == freeze['patch']['sha256']
for name in ['root86-transport-receipt.json', 'root86-verify_cloud.py', 'registered-verify_cloud087.py']:
    src = AUTHOR / name
    dst = ROOT / 'author-snapshots' / name
    shutil.copy2(src, dst)
    assert src.read_bytes() == dst.read_bytes()

dump(ROOT / 'author-saved-native-scope087.json', {
    'version': 1, 'original_frozen_author_matrix_label_preserved': 'unchanged_accepted_whole_typed_and_3texts',
    'actual_saved_scope': 'Complete decoded JSON value/type and all three texts; before-JSON native tree was not saved by the author collector',
    'native_before_JSON_saved_by_author': False,
    'author_formatter_direct_text_requests': 126, 'author_formatter_actual_entry_count_measured': None,
    'actual_native_and_formatter_instrumentation_is_independent_only': True,
    'author_passed_collector_matrix_or_source_rerun': False,
    'source_of_evidence': 'Unchanged author collect_matrix.py imports/call path and immutable saved rows'})
dump(ROOT / 'optional-local-completed-process-discovery087.json', {
    'version': 1, 'stage': 'Optional local process-status discovery after the two successful collectors',
    'command': 'ps -o pid,etime,%cpu,rss,args -C python', 'exit_code': 1,
    'actual_stdout': '    PID     ELAPSED %CPU   RSS COMMAND\n',
    'finding': 'No matching live Python process after collectors had exited 0',
    'product_parser_or_API_failure': False, 'repeated_product_calls': 0})

timestamp = datetime.now(timezone.utc).isoformat()
receipts = [static_path, numeric_path, child / 'static-source-receipt087.json']
dump(HANDOFF, {
    'version': 1, 'status': 'FINAL_SEALED_PASS_SOURCE_SAVED_NATIVE_NUMERIC_AND_NEW_TESTS',
    'sealed_at_utc': timestamp, 'archive_root': str(BASE),
    'author_freeze_sha256': sha(freeze_path), 'author_baseline_commit': freeze['author_baseline_commit'],
    'actual_root86_transport_commit': '0f27027e7e1f49c08f298706b599e310e299238b',
    'source_files': freeze['source_files'], 'product_patch': freeze['patch'],
    'registry_proposal_sha256': 'b2da5be3e6d309d97a01746161e63fa450f62ff5f9abb9c26fbfcd7abb91b3e8',
    'transport_scope': 'Only three approved product paths and one registry line. Retain root86 damage/engine; combined root regression is root-owned.',
    'review_receipts': [{'source_path': str(path), 'archive_path': str(path.relative_to(BASE)),
        'bytes': path.stat().st_size, 'sha256': sha(path)} for path in receipts],
    'immutable_source_preparation_manifest_sha256': sha(prepared_manifest_path),
    'immutable_child_static_files_verified': child_files,
    'original923_record_literal_and_JSON_types_values_exact': True,
    'new_Back_record_count': 5, 'new_counts': static['new_counts'],
    'native_game_binding_or_clock_inferred': False,
    'historical_reader_identity_rootcause_totalattempt_EOF_render_inferred': False,
    'author_saved35_scope': '16 complete strict JSON value/type+3texts same, 9 exact old errors, 10 explicit Back successes; no original before-JSON native data',
    'independent_actual_new_calls': numeric['API_ledger'],
    'independent12pair_counts': numeric['counts'], 'new7test_result': numeric['new_tests_actual_result'],
    'independent_three_text_requests': 48, 'independent_actual_profiled_formatter_entries': 64,
    'direct_cache_snapshot_helper_requests': 12,
    'reference_helper_body_entry_counts': numeric['production_reference_helper_body_entries_separately_recorded'],
    'complete_native_tree_files': 64,
    'caller_type_values_unchanged_all35_and_cached_trees_all24': True,
    'preparation': {'local_product_patch_filename_lookup_failure': 1,
        'static_checker_integral_metadata_vs_original_float_fields_failure': 1,
        'static_checker_second_attempt_exact_passed': True,
        'preparation_fixes_changed_product_or_sealed_preparation': False,
        'optional_no_live_python_discovery_exit1': 1,
        'child_manifest_path_schema_packaging_failure': 1,
        'child_manifest_not_mutated_and_final_composite_v1_rows_canonical': True,
        'child_read_inventory_truncation_is_not_product_failure': True,
        'all_failed_preparation_API_calls': 0},
    'source_parser_compile_network_Qt_Wine_tracked_changes': 0,
    'manifest_path': str(MANIFEST), 'manifest_self_excluded': True,
    'all_root_independent_preparation_and_formal_files_included': True,
    'no_further_writes': True, 'no_passed_API_formatter_test_source_parser_or_comparator_rerun': True})
files = []
for path in sorted(BASE.rglob('*')):
    if not path.is_file() or path == MANIFEST:
        continue
    files.append({'source_path': str(path), 'archive_path': str(path.relative_to(BASE)),
        'bytes': path.stat().st_size, 'sha256': sha(path)})
dump(MANIFEST, {'version': 1, 'status': 'FINAL_STABLE', 'sealed_at_utc': timestamp,
    'archive_root': str(BASE), 'file_count': len(files), 'total_bytes': sum(row['bytes'] for row in files),
    'manifest_self_excluded': True, 'handoff_included': True, 'files': files})
for row in files:
    path = Path(row['source_path'])
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
print(json.dumps({'status': 'FINAL_STABLE_NO_FURTHER_WRITES',
    'file_count': len(files), 'total_bytes': sum(row['bytes'] for row in files),
    'manifest_path': str(MANIFEST), 'manifest_sha256': sha(MANIFEST),
    'handoff_path': str(HANDOFF), 'handoff_sha256': sha(HANDOFF),
    'total_fresh_API_calls': 35, 'formatter_entries': 64}))
