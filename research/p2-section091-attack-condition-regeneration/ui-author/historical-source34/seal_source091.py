"""Freeze a bounded read-only candidate; stdlib only, no product calls."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MF = HERE / 'manifest-source091.json'
HAND = HERE / 'handoff-source091.json'

def description(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def read(name):
    return json.loads((HERE / name).read_bytes())

assert not MF.exists() and not HAND.exists()
receipt = read('visibility-source-receipt091.json')
assert receipt['status'] == 'POSITIVE_READ_ONLY_P2_UI_DECLARATION_CANDIDATE_FUTURE91_PENDING'
assert all(value == 0 for value in receipt['source_call_counts'].values())
source = read('source-reconstruction091.json')
assert len(source['files']) == source['file_count'] == 13
assert all(row['source088_matrix60_bytes_equal_named_current87'] for row in source['files'])
for row in source['files']:
    if row.get('copied_source_path'):
        actual = description(Path(row['copied_source_path']))
        assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
for row in read('saved-evidence-transport091.json')['files']:
    actual = description(Path(row['source_path']))
    assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
astproof = read('app-continuous-control-all-references091.json')
assert [row['method'] for row in astproof['direct_widget_method_calls']] == ['setChecked', 'isChecked']
assert astproof['direct_widget_method_calls'][0]['expression'] == 'self.continuous_attacks.setChecked(True)'

def included(path):
    return path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts and path != MF

count = len([p for p in HERE.rglob('*') if included(p)]) + 1
handoff = {
    'status': 'SEALED_READ_ONLY_POSITIVE_CANDIDATE091_PENDING_AFTER_FULL90',
    'candidate_section': 91, 'numbered_section_completed': False,
    'named_actual87_root_commit': source['named_root_commit'],
    'source_receipt': description(HERE / 'visibility-source-receipt091.json'),
    'source_gitblob_and_rebuild_proof': description(HERE / 'source-reconstruction091.json'),
    'source_files_bound': 13, 'public_py_exact_copies': 10, 'large_normalized_JSON_rebuild_metadata': 3,
    'producer_exhaustive_AST': description(HERE / 'app-continuous-control-all-references091.json'),
    'existing_saved_output_projection': description(HERE / 'existing-saved-output-projection091.json'),
    'existing_source16_and_baseline60_full_gz_bytes_copied_not_recalculated': True,
    'native_bool_hidden_positive': 'Amiya E2S1 saved False15/30/60 vsTrue6.000000000000002/11.2/41.2; actual GUI transition not run',
    'warrior_attack_SP_positive': 'char1050chen3 S3+legacy67 saved nativebool initial7 vs2.9999999999999996, final recharge/cycle unchanged in that bounded input',
    'minimal_qualification_note': 'E0/E1 Amiya attack credit0 differs from referenceflag consumer; warrior selector has no elite gate; noSP and retired received118 do not imply outgoing activation.',
    'future_visibility_candidates': {
        'safe_conservative': "Valid implemented selected skill sp_type in {'INCREASE_WHEN_ATTACK','INCREASE_WITH_TIME'}",
        'precise_pending_shared_processed_qualification': 'Attack-SP or natural Amiya actual source/reference consumer or natural extended owner with actual prepare-resolved active attack_sp; not implemented here'},
    'new_calls': receipt['source_call_counts'],
    'tracked_or_private_state_mutations': 0, 'product_draft_created': False,
    'UI090107_and_initial35_snapshot38_unchanged_by_this_task': True,
    'all_preparation_diagnostics_original_scripts_trace_included': True,
    'same_issue_three_failed_attempts_rule_triggered': False,
    'checkpoint': description(HERE / 'CHECKPOINT.md'),
    'public_manifest': {'source_path': str(MF), 'format_version': 1, 'files': count,
        'row_schema': ['source_path', 'archive_path', 'bytes', 'sha256']},
    'next_action': 'Stop writing candidate091. Root may choose an explicitly bounded product scope only after full90; no preflight or Qt execution is authorized by this source-only package.',
    'scope': 'Named actual87 source-only declaration gap with immutable source/saved88 transport, exact real checkbox/visibility/serialization/cross-owner flow, qualification boundaries and conservative future visibility options; no91 product or execution.'}
HAND.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
rows = []
for path in sorted(HERE.rglob('*')):
    if included(path):
        row = description(path)
        row['archive_path'] = path.relative_to(HERE).as_posix()
        rows.append({key: row[key] for key in ('source_path', 'archive_path', 'bytes', 'sha256')})
assert len(rows) == count and len({row['archive_path'] for row in rows}) == count
MF.write_text(json.dumps({'format_version': 1, 'scope': handoff['scope'], 'files': rows,
    'file_count': count, 'total_bytes': sum(row['bytes'] for row in rows),
    'new_API_helper_formatter_tests_Qt_Wine_calls': 0,
    'candidate_not_completed_section': True, 'original_diagnostics_included': True}, ensure_ascii=False, indent=2) + '\n')
for row in rows:
    actual = description(Path(row['source_path']))
    assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
print(json.dumps({'status': handoff['status'], 'files': count,
    'bytes': sum(row['bytes'] for row in rows), 'manifest': description(MF),
    'handoff': description(HAND), 'receipt': handoff['source_receipt']}, ensure_ascii=False))
