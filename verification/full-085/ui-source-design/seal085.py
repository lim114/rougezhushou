"""Seal public085 source/API/static proof for root's sole actual Qt run."""
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
COMMIT = '2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'
REVIEW = HERE / 'review-final085/final-static-and-saved1154-review085.json'
MANIFEST = HERE / 'archivable-public-manifest.json'
HANDOFF = HERE / 'handoff.json'

def read(name):
    return json.loads((HERE / name).read_bytes())

def file_description(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip() == COMMIT
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=REPO, text=True).strip() == 'codex/p2-development'
subprocess.run(['git', 'diff', '--quiet'], cwd=REPO, check=True)
subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=REPO, check=True)
static = read('runner-static-review.json')
freeze = read('public-source-freeze-085.json')
root = read('root-source-085-proof.json')
rebuild = read('public-package-rebuild-proof085.json')
mapping = read('artifact-mapping-and-old3063-proof085.json')
review = json.loads(REVIEW.read_bytes())
api = json.loads(gzip.decompress((HERE / 'public-schema-final-085.json.gz').read_bytes()))
summary = read('public-schema-final-085-summary.json')
runner = HERE / 'wine-ui-smoke-085.py'
digest = file_description(runner)['sha256']
assert freeze['base_commit'] == root['root_commit'] == rebuild['root_source_commit'] == review['root_commit'] == api['root_commit'] == COMMIT
assert len(root['files']) == root['maintenance_python_json_files'] == 723
assert len(freeze['source_sha256']) == len(rebuild['files']) == rebuild['public_source_files'] == 125
assert static['old3063_complete_body_reconstructed_exactly'] and static['syntax_valid']
assert not static['sections83_85_pending'] and static['ready_for_actual_execution']
assert static['base_skills'] == 87 and static['total_case_design_count'] == 4217
assert digest == static['runner_sha256'] == review['final_runner_sha256'] == mapping['runner_sha256']
assert review['status'] == 'PASS_FINAL_STATIC_AND_ALL_SAVED1154_0_NEW_PRODUCT_CALLS'
assert all(review[name] == 0 for name in ('reviewer_application_API_calls', 'reviewer_formatter_calls',
    'reviewer_production_helper_calls', 'reviewer_Qt_calls', 'reviewer_Wine_calls'))
assert review['saved_result_gzip_sha256'] == summary['full_receipt_sha256'] == file_description(HERE / 'public-schema-final-085.json.gz')['sha256']
assert api['source_drift'] == [] and api['source_hashes'] == freeze['source_sha256']
assert api['calls'] == len(api['records']) == api['case_design_records'] == static['new_case_design_count'] == 1154
assert api['successful_result_rows'] == 1130 and api['expected_existing_error_rows'] == 24
assert api['formatter_text_requests'] == 3390 and api['actual_formatter_function_entries'] == 4520
assert api['formatter_entry_counts'] == {'format_estimate': 1130, 'format_report_default': 2260, 'format_report_technical': 1130}
assert api['unique_requested_calculation_inputs'] == 1086
assert api['sections'] == static['new_case_design_by_section'] == {'81': 136, '82': 216, '83': 450, '84': 88, '85': 264}
assert not api['GUI_executed'] and not api['Wine_executed']
assert mapping['old3063_complete_body_reconstructed_exactly'] and len(mapping['output_mappings']) == 7
assert rebuild['all_bytes_equal'] and rebuild['source_drift'] == []
for row in root['files']:
    raw = (REPO / row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], row['source_path']
for row in rebuild['files']:
    raw = (HERE / 'public-schema-085' / row['path']).read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], row['path']

review_manifest = HERE / 'review-final085/final-public-artifacts-manifest085.json'
review_handoff = HERE / 'review-final085/final-handoff085.json'
assert review_manifest.is_file() and review_handoff.is_file(), 'Independent finalstable package must be sealed first.'
review_rows = json.loads(review_manifest.read_bytes())['files']
for row in review_rows:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], row['source_path']

def archivable(path):
    if not path.is_file():
        return False
    relative = path.relative_to(HERE)
    return '__pycache__' not in relative.parts and relative.parts[0] != 'public-schema-085' and path != MANIFEST

file_count = len([path for path in HERE.rglob('*') if archivable(path)]) + (not HANDOFF.exists())
artifacts = {name: file_description(HERE / name) for name in (
    'wine-ui-smoke-085.py', 'runner-static-review.json', 'root-source-085-proof.json',
    'root-context-085-preserved.json', 'public-source-freeze-085.json',
    'public-package-rebuild-proof085.json', 'root-source-compatibility-085.json',
    'artifact-mapping-and-old3063-proof085.json', 'public-schema-final-085.json.gz',
    'public-schema-final-085-summary.json', 'public-schema-final-085-failure.json.gz',
    'public-schema-resume085-failure.json.gz', 'saved69-reassertion085.json',
    'saved581-reassertion085.json', 'remaining-contract-field-audit085.json',
    'review-final085/final-static-and-saved1154-review085.json',
    'review-final085/final-public-artifacts-manifest085.json', 'review-final085/final-handoff085.json')}
handoff = {
    'status': 'READY_FOR_ROOT_SOLE_ACTUAL_QT_WINE_EXECUTION',
    'root_source_commit': COMMIT, 'root_maintenance_python_json_files': 723,
    'public_source_files': 125, 'runner': file_description(runner),
    'preserved_actual080_skills': 87, 'preserved_actual080_checks': 3063,
    'base_actual080_sha256': static['base080_sha256'],
    'old3063_complete_body_reconstructed_exactly': True,
    'old3063_inverse_allows_new_wrapper_metadata_and_only_seven_output_suffix_renames': True,
    'new_case_design_by_section': static['new_case_design_by_section'],
    'new_case_design_records': 1154, 'planned_actual_checks': 4217,
    'actual_new_API_requests': 1154, 'unique_requested_calculation_inputs': 1086,
    'equal_API_input_for_68_technical_checkbox_pairs': True,
    'successful_API_results': 1130, 'exact_existing_threshold_ValueError_rows': 24,
    'saved_three_report_text_requests': 3390, 'actual_formatter_function_entries': 4520,
    'formatter_entry_counts': api['formatter_entry_counts'],
    'estimate_dispatcher_delegates_to_default_report': True,
    'actual_API_call_attribution': api['actual_API_call_attribution'],
    'external_original_result_qualification_data_helpers': 480,
    'external_saved581_reassertion_qualification_data_helpers': 216,
    'API_contract_counterexamples': [
        {'problem': 'Mechanist S3 damage-only legacy output excludes top-level total_healing',
         'failed_attempts': 1, 'correction': 'Require exact absent top-level field and explicit estimate.window_healing0 only for that existing owner/skill/zero-window shape.',
         'full_saved_file': 'public-schema-final-085-failure.json.gz', 'saved_prefix_reasserted_0_API': 69},
        {'problem': 'Selected enemy output spreads target enemy_id; record.id is preview lookup only',
         'failed_attempts': 1, 'correction': 'Require exact processed enemy_id/stage_id/level and actual BOSS metadata; no missing-key fallback.',
         'full_saved_file': 'public-schema-resume085-failure.json.gz', 'saved_prefix_reasserted_0_API': 581}],
    'API_preparation_import_failure': {'interpreter': 'systempython', 'missing_import': 'cv2', 'API_calls': 0,
        'preserved_directory': 'preparation085-system-python-import', 'subsequent_interpreter': '/workspace/rougezhushou/.venv/bin/python'},
    'source_drift': [], 'author_GUI_or_Wine_executed': False,
    'independent_status': review['status'], 'actual_UI_still_required': True,
    'native_Windows_game_desktop_verified': False,
    'output_mappings': mapping['output_mappings'], 'artifacts': artifacts,
    'public_manifest': {'source_path': str(MANIFEST), 'format_version': 1, 'files': file_count,
        'row_schema': ['source_path', 'archive_path', 'bytes', 'sha256']},
    'excluded_duplicate_public_package_directories': ['public-schema-085'],
    'excluded_runtime_cache': ['__pycache__'],
    'duplicate_public125_reconstruction_proof': 'public-package-rebuild-proof085.json',
    'archive_scope': 'All public085 design, static source proofs, full compressed saved API results, three-text evidence, original preparation diagnostics, counterexamples, saved-only reassertion and independent review; omit only reconstructable public125 package and runtime bytecode caches.',
    'limits': ['Saved API/static checks permit root actual MainWindow verification and are not GUI pass.',
               'Wine compatibility does not establish native Windows/game/desktop behavior.',
               'Unknown clock, target, native composition and actual redeployment/attachment boundaries retain source-derived None or false.']}
HANDOFF.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
rows = []
for path in sorted(HERE.rglob('*')):
    if archivable(path):
        row = file_description(path)
        row['archive_path'] = path.relative_to(HERE).as_posix()
        rows.append({name: row[name] for name in ('source_path', 'archive_path', 'bytes', 'sha256')})
assert len(rows) == file_count
manifest = {'format_version': 1, 'scope': handoff['archive_scope'], 'root_source_commit': COMMIT,
            'files': rows, 'all_initial_and_preparation_diagnostics_included': True,
            'excluded_duplicate_public_package_directories': ['public-schema-085'],
            'excluded_runtime_cache': ['__pycache__']}
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
for row in rows:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
print(json.dumps({'status': handoff['status'], 'files': len(rows),
                  'archive_bytes': sum(row['bytes'] for row in rows),
                  'runner': file_description(runner), 'handoff': file_description(HANDOFF),
                  'manifest': file_description(MANIFEST), 'independent_review': file_description(REVIEW),
                  'actual_API_requests': 1154, 'planned_actual_UI_checks': 4217}, ensure_ascii=False))
