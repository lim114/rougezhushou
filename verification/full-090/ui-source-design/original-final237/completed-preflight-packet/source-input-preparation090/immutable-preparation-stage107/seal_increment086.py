"""Seal the completed bounded086 API stage using only saved bytes and stdlib.

This script never imports the project, its cases module, Qt, or Wine.  It leaves
the earlier source-stage documents and immutable snapshots unchanged.
"""
import ast
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MF = HERE / 'public-artifacts-manifest-stage-increment086.json'
HAND = HERE / 'handoff-stage-increment086.json'
REBUILD = HERE / 'public125-rebuild-ui090-section086.json'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def describe(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}

def read(name):
    return json.loads((HERE / name).read_bytes())

def verify_row(row):
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], row

assert not MF.exists() and not HAND.exists(), 'A sealed stage must not be overwritten'
root = read('root086-ui090-source-proof.json')
summary = read('api-ui090-section086-summary.json')
review = read('review-saved086/saved44-review-receipt.json')
runner = read('pending-runner-static-proof090.json')
contracts = read('source-producer-contracts090-section086.json')
assert root['root_commit'] == summary['root_source_commit'] == review['base_commit'] == '0f27027e7e1f49c08f298706b599e310e299238b'
assert root['maintenance_python_json_files'] == len(root['files']) == 724
assert root['public_files'] == 125
assert summary['actual_API_calls'] == summary['successful_results'] == 44
assert summary['unique_requested_calculation_inputs'] == 31
assert summary['formatter_text_requests'] == 132
assert summary['actual_formatter_function_entries'] == 176
assert summary['formatter_entry_counts'] == {'format_estimate': 44, 'format_report_default': 88, 'format_report_technical': 44}
assert summary['catalog_helper_entries_internally_observed'] == {'API': 221}
assert summary['external_product_helper_calls'] == 0
assert summary['expected_error_rows'] == 0 and summary['source_drift'] == []
assert all(summary[key] == 0 for key in ('Qt_calls', 'Wine_calls', 'tests_run', 'old_source36_or4217_API_cases_repeated'))
assert review['status'] == 'FINAL_PASS_SAVED_ONLY_STRICT44'
assert review['records_strict_native_decode_to_wholepublic'] == 44
assert review['same_native_pairs'] == 9 and review['different_native_pairs'] == 13
assert all(review[key] == 0 for key in ('new_API_calls', 'new_formatter_calls', 'new_project_helper_calls', 'Qt', 'Wine', 'tests', 'tracked_edits'))
for row in review['bound_author_artifacts']:
    verify_row(row)
for name, expected in (
    ('review-producers086/manifest.json', '3055f3bdcd2379b0875af8cabaf3488e0fb8e463d6df16db7c5e18140fc9dc87'),
    ('review-increment086/manifest.json', 'a3e0050b902825462d8b0b51734130ad28f72ee81ef7f46368b79ea2f15f2759'),
    ('review-saved086/manifest.json', '745f3052e93b5a00d8c57b195380f0f3e2752e8dbbd9fb7474cc272cd5ff0b1a'),
    ('preparation-source-only-stage090-086/immutable-snapshot-manifest.json', '0b270f78b4fce3828ab952f776c89a73a611bf3dff98033230de308e4daff627')):
    assert describe(HERE / name)['sha256'] == expected, name
    for row in read(name)['files']:
        verify_row(row)
transport = read('preparation-source-only-stage090-086/transport-proof.json')
assert transport['original_stage_files'] == 35
for row in transport['files']:
    verify_row(row)
assert describe(HERE / 'preparation-source-only-stage090-086/initial-stage-manifest-original.json')['sha256'] == 'a8fd84f2d3c6a097d3a44d020779de92186b63240947086a29345497b17bb25d'
assert describe(HERE / 'preparation-source-only-stage090-086/initial-stage-handoff-original.json')['sha256'] == '63dce20860e17c60c63ee4e6e0b8e537ca84c7d357fc9312b98e096986f23f38'

candidate = HERE / 'wine-ui-smoke-090.py'
actual = HERE / 'actual085-runner-preserved.py'
assert describe(candidate)['sha256'] == runner['candidate_runner_sha256'] == summary['pending090_runner_sha256'] == 'd5d2c41049c604c14b598426a06b16d54b1012d9b66da18a02a9937ec50198dc'
assert describe(actual)['sha256'] == runner['actual085_base_sha256'] == 'b6976652eb50e06909cca68490b0b9d3e11ea81fbc9a73ca87efcbb10354e306'
guard = "if __name__ == '__main__' and True:\n    raise RuntimeError('UI090 sources and API contract remain pending; Qt execution is forbidden')\n\n"
pending_text = candidate.read_text()
assert pending_text.startswith(guard)
inverse = pending_text[len(guard):]
for old, new in runner['output_renames'].items():
    inverse = inverse.replace(new, old)
assert inverse.encode() == actual.read_bytes(), 'Entire4217 old body must be byte-exact'
for name in ('wine-ui-smoke-090.py', 'prepare_increment086.py', 'preflight_ui090_section086.py', 'cases090_section086.py'):
    ast.parse((HERE / name).read_bytes())

fullpath = HERE / 'api-ui090-section086.json.gz'
assert describe(fullpath)['sha256'] == summary['full_receipt_sha256'] == '3b8dcf9afa046360e1fdbb7f7e004ee968dc7fe8b4fb15ee7b9dd1e6b1761db8'
decoded = gzip.decompress(fullpath.read_bytes())
assert len(decoded) == review['decoded_gzip']['bytes'] and sha(decoded) == review['decoded_gzip']['sha256']

rebuildrows = []
for row in root['files']:
    relative = row['source_path']
    if not relative.startswith('rouge/'):
        continue
    path = HERE / 'public-schema-086-ui090' / relative
    raw = path.read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert blob == row['git_blob_sha1']
    assert sha(raw) == root['public_source_sha256'][relative]
    rebuildrows.append({
        'root_relative_path': relative, 'git_blob_sha1': blob,
        'excluded_source_path': str(path), 'reconstruction_archive_path': 'public-schema-086-ui090/' + relative,
        'bytes': len(raw), 'sha256': sha(raw)})
assert len(rebuildrows) == 125
REBUILD.write_text(json.dumps({
    'status': 'PASS_ALL125_FROZEN_PUBLIC_FILES_BYTE_EXACT_NAMED_ROOT086_GIT_BLOBS',
    'named_root_commit': root['root_commit'], 'file_count': 125,
    'total_bytes': sum(row['bytes'] for row in rebuildrows),
    'reconstruct_using': 'git cat-file blob <git_blob_sha1> from the named root086 objects; place exact bytes at reconstruction_archive_path',
    'duplicate_public_package_body_omitted_from_main_manifest': True,
    'source_proof': describe(HERE / 'root086-ui090-source-proof.json'),
    'root_source_proof_rows': 724, 'files': rebuildrows,
    'API_helpers_formatter_tests_Qt_Wine_calls': 0,
    'current_root_head_may_advance_independently': True}, ensure_ascii=False, indent=2) + '\n')

def archivable(path):
    return path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts and 'public-schema-086-ui090' not in path.parts and path != MF

existing = [path for path in HERE.rglob('*') if archivable(path)]
count = len(existing) + 1  # the new handoff is added before the final scan
handoff = {
    'status': 'SEALED_SECTION086_INCREMENT_API44_AND_STRICT_SAVED_REVIEW_UI090_PENDING',
    'stage_section': 86, 'named_root086_commit': root['root_commit'],
    'named_maintenance_source_files': 724, 'named_public_source_files': 125,
    'product_sha256': {key: root['public_source_sha256'][key] for key in ('rouge/damage.py', 'rouge/operator_engine.py')},
    'API_execution': summary,
    'independent_saved_only_review': describe(HERE / 'review-saved086/saved44-review-receipt.json'),
    'independent_saved_only_manifest': describe(HERE / 'review-saved086/manifest.json'),
    'independent_saved_only_handoff': describe(HERE / 'review-saved086/handoff-final.json'),
    'independent_saved_only_calls': {'API': 0, 'helper': 0, 'formatter': 0, 'Qt': 0, 'Wine': 0, 'tests': 0},
    'full_saved_native_JSON_3text_receipt': describe(fullpath),
    'receipt_lossless_decoded': review['decoded_gzip'],
    'bounded44_API_contract_failures': 0, 'bounded44_product_failures': 0,
    'bounded44_API_repeats': 0, 'same_issue_three_failed_attempts_rule_triggered': False,
    'source_contract': describe(HERE / 'source-producer-contracts090-section086.json'),
    'source_proof': describe(HERE / 'root086-ui090-source-proof.json'),
    'excluded_public125_rebuild_proof': describe(REBUILD),
    'immutable_initial_source_stage': {
        'original_artifact_count': 35, 'snapshot_manifest_rows': 38,
        'original_manifest': describe(HERE / 'preparation-source-only-stage090-086/initial-stage-manifest-original.json'),
        'original_handoff': describe(HERE / 'preparation-source-only-stage090-086/initial-stage-handoff-original.json'),
        'manifest': describe(HERE / 'preparation-source-only-stage090-086/immutable-snapshot-manifest.json'),
        'source_archive_transport': describe(HERE / 'preparation-source-only-stage090-086/transport-proof.json'),
        'original_live_source_paths_are_historical_use_exact_transport_snapshot': True,
        'all_original_bytes_preserved_before_live_mutations': True},
    'pending_UI090': {
        'runner': describe(candidate), 'earliest_entry_guard_true': True,
        'guard_precedes_imports_Qt': True, 'new_cases_wired': 0,
        'actual085_runner': describe(actual), 'preserved_actual085_checks': 4217,
        'preserved_actual085_numbered_skills': 87, 'all_old_body_inverse_byte_exact': True,
        'output_renames': runner['output_renames'],
        'API44_pass_does_not_claim_actual_UI_case_execution': True,
        'all_final86_90_source_frozen': False, 'ready_for_actual_execution': False,
        'UI090_Qt_calls': 0, 'UI090_Wine_calls': 0,
        'future_root_sole_window_execution_required': True},
    'limited_pending087_old4217_choices_static': describe(HERE / 'old4217-choices-static090.json'),
    'later_sections87_90_products_used_for_new_API': False,
    'unknown88_89_draft_behaviors_written_or_called': False,
    'original_preparation_diagnostics_all_included': True,
    'tracked_product_files_modified_by_this_agent': False,
    'checkpoint': describe(HERE / 'CHECKPOINT.md'),
    'public_manifest': {'source_path': str(MF), 'format_version': 1, 'files': count,
        'row_schema': ['source_path', 'archive_path', 'bytes', 'sha256']},
    'next_action': 'Stop writes to this sealed stage. On root followup first verify and snapshot all stage artifacts plus original manifest/handoff before live changes; extend only actual authorized87–90 scopes without rerunning passed44 or old4217. Root alone executes finalUI090 after all actual sources and final saved contracts freeze.',
    'archive_scope': 'Section086 actual bounded44 API typed/JSON/three-text evidence, exact724 named source and public125 reconstruction, strict saved-only independent review, immutable original35 source-stage preparation and complete source/archive transport, guarded4217 unchanged candidate, real producers and bounded pairs, all initial and incremental preparation diagnostics; fullUI090 pending.'}
HAND.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
rows = []
for path in sorted(HERE.rglob('*')):
    if archivable(path):
        row = describe(path)
        row['archive_path'] = path.relative_to(HERE).as_posix()
        rows.append({key: row[key] for key in ('source_path', 'archive_path', 'bytes', 'sha256')})
assert len(rows) == count
assert len({row['archive_path'] for row in rows}) == count
MF.write_text(json.dumps({
    'format_version': 1, 'status': handoff['status'], 'scope': handoff['archive_scope'],
    'files': rows, 'file_count': count, 'total_bytes': sum(row['bytes'] for row in rows),
    'original_stage35_and_transport_snapshot_included': True,
    'all_original_and_incremental_preparation_diagnostics_included': True,
    'duplicate_public125_body_omitted_exact_reconstruction_proof_included': True,
    'API_actualcalls': 44, 'unique_requested_inputs': 31,
    'text_requests': 132, 'actual_formatter_function_entries': 176,
    'API_passed_not_full_UI090_pass': True, 'Qt_Wine_calls': 0,
    'row_schema': ['source_path', 'archive_path', 'bytes', 'sha256']}, ensure_ascii=False, indent=2) + '\n')
for row in rows:
    verify_row(row)
print(json.dumps({'status': handoff['status'], 'files': count,
    'bytes': sum(row['bytes'] for row in rows), 'manifest': describe(MF),
    'handoff': describe(HAND), 'pending_runner': describe(candidate),
    'independent_review': handoff['independent_saved_only_review']}, ensure_ascii=False))
