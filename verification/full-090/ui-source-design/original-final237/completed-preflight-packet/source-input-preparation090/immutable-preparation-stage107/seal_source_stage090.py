"""Seal source-only090 stage, requiring no product imports or execution."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / 'public-artifacts-manifest-stage-source090.json'
HANDOFF = HERE / 'handoff-stage-source090.json'
def read(name):
    return json.loads((HERE / name).read_bytes())
def description(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

source = read('named-root085-source-proof090.json')
runner = read('pending-runner-static-proof090.json')
contracts = read('source-producer-contracts090.json')
plans = read('small-explicit-pair-plan090.json')
review = read('review-producers086/source-producer-review086.json')
assert source['root_commit'] == contracts['root_commit'] == review['approved_actual085_commit'] == '9ef5a469673502754db3be320a8eece9a7fd18d4'
assert contracts['fields'] == review['field_count'] == 12 and contracts['owners'] == review['owner_count'] == 8
assert contracts['direct_literal_consumers'] == 17
assert plans['pair_groups'] == 22 and plans['planned_UI_states'] == 44 and plans['case_states_wired_into_runner'] == 0
assert runner['old4217_complete_body_exact_after_only_guard_removal_and_seven_output_suffix_inverse']
assert runner['earliest_entry_guard'] and not runner['ready_for_actual_execution']
assert runner['candidate_runner_sha256'] == description(HERE / 'wine-ui-smoke-090.py')['sha256']
assert runner['actual085_base_sha256'] == review['actual085_runner_sha256'] == description(HERE / 'actual085-runner-preserved.py')['sha256']
assert review['status'] == 'PASS_SOURCE_ONLY_REAL_QCHECKBOX_PRODUCERS_12_FIELDS_PENDING_UI090'
assert all(value == 0 for value in review['calls'].values())
for name in ('prepare_source_stage090.py', 'close_existing_source090.py', 'wine-ui-smoke-090.py'):
    ast.parse((HERE / name).read_bytes())
for row in read('review-producers086/manifest.json')['files']:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']

def archivable(path):
    return path.is_file() and '__pycache__' not in path.parts and path != MANIFEST
count = len([path for path in HERE.rglob('*') if archivable(path)]) + (not HANDOFF.exists())
handoff = {
    'status': 'SEALED_SOURCE_ONLY_STAGE_PENDING_REAL_FINAL86_90',
    'root_actual085_commit': source['root_commit'],
    'preserved_actual085_runner_sha256': runner['actual085_base_sha256'],
    'preserved_actual085_skills': 87, 'preserved_actual085_checks': 4217,
    'pending090_runner': description(HERE / 'wine-ui-smoke-090.py'),
    'earliest_entry_guard_true': True, 'complete4217_body_inverse_exact': True,
    'seven_output_suffixes_renamed085_to090': runner['output_renames'],
    'authorized_source_section': 86, 'source86_product_final': False,
    'sections87_90_known': False, 'fields': 12, 'owners': 8, 'consumer_sites': 17,
    'declarative_pair_groups': 22, 'declarative_UI_states': 44, 'new_runner_cases_wired': 0,
    'historical_source36_is_reused_saved_only_not_current_fresh': True,
    'raw240_12module_36API_or_finite_audits_repeated': False,
    'all_new_calls': {'application_API': 0, 'production_helper': 0, 'formatter': 0,
        'tests': 0, 'Qt': 0, 'Wine': 0}, 'tracked_mutations': False,
    'independent_producer_review': description(HERE / 'review-producers086/source-producer-review086.json'),
    'independent_manifest': description(HERE / 'review-producers086/manifest.json'),
    'artifacts': {name: description(HERE / name) for name in (
        'named-root085-source-proof090.json', 'pending-runner-static-proof090.json',
        'source-producer-contracts090.json', 'historical-saved36-field-projection090.json',
        'existing085-orchid-shape-reference090.json', 'small-explicit-pair-plan090.json', 'CHECKPOINT.md')},
    'public_manifest': {'source_path': str(MANIFEST), 'format_version': 1, 'files': count,
        'row_schema': ['source_path', 'archive_path', 'bytes', 'sha256']},
    'ready_for_actual_execution': False, 'new_API_preflight_passed': False,
    'next_action': 'Stop new execution; wait root final86 source and later87–90 real scopes before expanding and any explicitly authorized API preflight. Root alone runs finalQt/Wine.',
    'archive_scope': 'Bounded source-only090 preparation, actual085-preserved body, guarded candidate, exact named source, 12-field static contracts, small declarative pairs, saved evidence projections, independent source-only review and all initial preparation diagnostics.'}
HANDOFF.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
rows = []
for path in sorted(HERE.rglob('*')):
    if archivable(path):
        row = description(path)
        row['archive_path'] = path.relative_to(HERE).as_posix()
        rows.append({key: row[key] for key in ('source_path', 'archive_path', 'bytes', 'sha256')})
assert len(rows) == count
MANIFEST.write_text(json.dumps({'format_version': 1, 'scope': handoff['archive_scope'],
    'files': rows, 'file_count': count, 'total_bytes': sum(row['bytes'] for row in rows),
    'source_only_stage': True, 'API_helpers_formatter_tests_Qt_Wine_calls': 0,
    'original_preparation_diagnostics_included': True}, ensure_ascii=False, indent=2) + '\n')
for row in rows:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
print(json.dumps({'status': handoff['status'], 'files': count,
    'bytes': sum(row['bytes'] for row in rows), 'manifest': description(MANIFEST),
    'handoff': description(HANDOFF), 'pending_runner': description(HERE / 'wine-ui-smoke-090.py')}, ensure_ascii=False))
