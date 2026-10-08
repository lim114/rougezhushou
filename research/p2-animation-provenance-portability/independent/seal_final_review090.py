"""Package immutable independent results; zero verifier/application calls."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MF = HERE / 'manifest-independent090.json'
HAND = HERE / 'handoff-independent090.json'
FORMAL = HERE / 'final-independent-review090.json'

def desc(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def read(name):
    return json.loads((HERE / name).read_bytes())

assert not MF.exists() and not HAND.exists() and not FORMAL.exists()
fresh = read('fresh-four-direct-verifier-receipt090.json')
static = read('independent-static-review090.json')
saved = read('saved-only-and-Back5-review090.json')
assert all(receipt['passed'] is True for receipt in (fresh, static, saved))
assert fresh['fresh_verifier_function_entries'] == fresh['fresh_direct_verifier_entries'] == 4
assert fresh['fresh_CLI_invocations'] == 0 and saved['fresh_verifier_function_entries'] == 0
assert fresh['unexpected_errors'] == fresh['product_failures'] == 0
for risk in fresh['risks']:
    actual = desc(Path(risk['saved_record']['source_path']))
    assert actual == risk['saved_record']
for row in read('public-fixture-root619-reconstruction090.json')['files']:
    actual = desc(Path(row['source_path']))
    assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
plan = read('risk-plan-frozen090.json')
assert desc(Path(plan['candidate_script']['source_path'])) == plan['candidate_script']
formal = {
    'format_version': 1, 'status': 'FINAL_PASS_FROZEN_PORTABLE_PROVENANCE090_INDEPENDENT', 'passed': True,
    'candidate_baseline_actual_root619_commit': '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0',
    'root89_transport_and_registry_final_rebase_pending_outside_this_frozen_review': True,
    'product_scope': 'New stdlib read-only metadata verifier CLI, six new author tests and README append only; no gameplay/data/default/animation controls change',
    'frozen_product_files': read('author-bound/review-freeze090.json')['product_files'],
    'product_patch': desc(HERE / 'author-bound/product090.patch'),
    'author_immutable_manifest': desc(HERE / 'author-bound/archivable-author-review-manifest090.json'),
    'author_immutable_handoff': desc(HERE / 'author-bound/author-review-handoff090.json'),
    'author_original_rows_verified': 62, 'source_original_rows_verified': 28,
    'source28_original_manifest': desc(HERE / 'source28-bound/public-artifacts-manifest-source090.json'),
    'risk_plan': desc(HERE / 'risk-plan-frozen090.json'),
    'static_receipt': desc(HERE / 'independent-static-review090.json'),
    'fresh_receipt': desc(HERE / 'fresh-four-direct-verifier-receipt090.json'),
    'saved_only_receipt': desc(HERE / 'saved-only-and-Back5-review090.json'),
    'fresh_verifier_function_entries': 4, 'fresh_direct_verifier_entries': 4, 'fresh_CLI_invocations': 0,
    'actual_verify_entry_profile_frame_counter_verified': True,
    'distinct_frozen_risks_detected': 4, 'unexpected_errors': 0,
    'author_old_verifier28_or_six_tests_reexecuted': False,
    'source28_087_oldmatrices_or_reader_calls_reexecuted': False,
    'all_eight_original_public_inputs_and_each_mutated_temporary_input_unchanged_by_candidate': True,
    'manifest_pin_and_six_real_leaves_never_modified_or_rehashed': True,
    'source28_ten_py_and_public_input_scope_not_full301_102_certification': True,
    'five_Back_whole_typed_and_float_hex_full_source_derivation_checked': True,
    'existing923_wholeCRLF_inverse_checked_against_real_archived_baseline': True,
    'genericSkill_no_number_and_runtime_flags_strictFalse_preserved': True,
    'application_API_calls': 0, 'project_helper_calls': 0, 'formatter_calls': 0,
    'source_skeleton_parser_calls': 0, 'network_calls': 0, 'Qt_calls': 0, 'Wine_calls': 0,
    'unittest_methods_executed': 0, 'tracked_or_private_state_mutations': 0,
    'maintenance_verifier_four_separately_counted_not_application_API': True,
    'scope_limitations': ['Pinned section087 metadata/five-record snapshot only',
        'Future additions return outside-supported scope, not auto-certified',
        'Fixed hash-pinned manifest makes mutated manifest internals unreachable; no claim of runtime coverage for invented adjustable manifest source',
        'Native skill/normal/skin binding, lifecycle clocks, rendering/atlas/texture, EOF and historical parser root cause remain unverified'],
    'preparation_diagnostics': desc(HERE / 'preparation-diagnostics090.json'),
    'stop_changes_after_seal': True}
FORMAL.write_text(json.dumps(formal, ensure_ascii=False, indent=2) + '\n')

def included(path):
    return path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts and 'public-fixture090' not in path.parts and 'runtime-public-only' not in path.parts and path != MF

count = len([path for path in HERE.rglob('*') if included(path)]) + 1
handoff = {
    'status': formal['status'], 'passed': True, 'independent_receipt': desc(FORMAL),
    'fresh_verifier_function_entries': 4, 'fresh_direct_verifier_entries': 4, 'fresh_CLI_invocations': 0,
    'application_API_helper_formatter_parser_network_Qt_Wine_calls': 0,
    'author28_and_source28_preserved_not_reexecuted': True,
    'excluded_duplicate_eight_named_root619_public_inputs_reconstruction': desc(HERE / 'public-fixture-root619-reconstruction090.json'),
    'all_four_full_changed_public_reference_inputs_gzip_and_exception_readonly_proof_included': True,
    'all_initial_preparation_scripts_trace_diagnostics_included': True,
    'public_manifest': {'source_path': str(MF), 'format_version': 1, 'files': count,
        'row_schema': ['source_path', 'archive_path', 'bytes', 'sha256']},
    'checkpoint': desc(HERE / 'CHECKPOINT.md'),
    'root89_product_source_and_registry_transport_pending_to_actual_root_not_reviewer_tracked_action': True,
    'root_owns_tracked_apply_and_all_actualQt_Wine': True,
    'next_action': 'Root/author may hash-verify and copy this frozen packet; perform only additive actual89 source/registry transport and root validation. No rerun of passed author28 or reviewer4 is needed or authorized here.',
    'stop_writes': True}
HAND.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
rows = []
for path in sorted(HERE.rglob('*')):
    if included(path):
        row = desc(path)
        row['archive_path'] = path.relative_to(HERE).as_posix()
        rows.append({key: row[key] for key in ('source_path', 'archive_path', 'bytes', 'sha256')})
assert len(rows) == count and len({r['archive_path'] for r in rows}) == count
MF.write_text(json.dumps({'format_version': 1, 'status': formal['status'], 'files': rows,
    'file_count': count, 'total_bytes': sum(row['bytes'] for row in rows),
    'includes_formal_receipt_and_all_preparation_diagnostics': True,
    'full_four_changed_inputs_gzip_included': True,
    'duplicate_named_root619_eight_inputs_omitted_exact_reconstruction_proof_included': True,
    'fresh_verifier_entries': 4, 'application_API_Qt_Wine_calls': 0}, ensure_ascii=False, indent=2) + '\n')
for row in rows:
    actual = desc(Path(row['source_path']))
    assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
print(json.dumps({'status': formal['status'], 'passed': True, 'files': count,
    'bytes': sum(row['bytes'] for row in rows), 'manifest': desc(MF),
    'handoff': desc(HAND), 'independent_receipt': desc(FORMAL)}, ensure_ascii=False))
