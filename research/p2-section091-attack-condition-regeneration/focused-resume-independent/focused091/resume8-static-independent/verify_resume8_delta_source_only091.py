from pathlib import Path, PurePosixPath
import ast
import gzip
import hashlib
import json

BASE = Path('/workspace/.continuation/ui-091-focused-resume8-v2')
OUT = Path('/workspace/.continuation/p2-focused-mainwindow-091-resume8-independent')
MF = BASE / 'public-artifacts-manifest-focused-resume8-v2-091.json'
RUNNER = BASE / 'wine-focused-mainwindow-091-resume8-v2.py'
PARENT = Path('/workspace/.continuation/ui-091-focused-final/wine-focused-mainwindow-091-final.py')
EXPECTED_MF_SHA = '96565dc88486d03b019e0794605fc81001c14945f4393b64fbb6b91514362ac6'
EXPECTED_RUNNER_SHA = 'd1a5a8337f2ee9bdb4a1afa3eefd60892b958504a27011a5618ea73e2f63e902'
EXPECTED_PARENT_SHA = '648389a4dafefc8775d39b07f79eb895689a4a417dc2155dc8118679b30552c5'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def descriptor(path):
    data = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(data), 'sha256': sha(data)}

def literals(tree):
    result = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('PLAN', 'SOURCE_HASHES', 'PENDING_PREPARATION', 'WARM_EXPECTED'):
                    result[target.id] = ast.literal_eval(node.value)
    return result

def json_exact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

mf_data = MF.read_bytes()
assert sha(mf_data) == EXPECTED_MF_SHA
mf = json.loads(mf_data)
assert mf['format_version'] == 1 and len(mf['files']) == mf['file_count'] == 11
archives = set()
total = 0
for row in mf['files']:
    path = PurePosixPath(row['archive_path'])
    assert not path.is_absolute() and '..' not in path.parts
    assert row['archive_path'] not in archives
    archives.add(row['archive_path'])
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256'], row['source_path']
    total += len(data)
assert total == mf['total_bytes'] == 569845

new = RUNNER.read_bytes()
old = PARENT.read_bytes()
assert len(new) == 175801 and sha(new) == EXPECTED_RUNNER_SHA
assert len(old) == 114326 and sha(old) == EXPECTED_PARENT_SHA
proof = json.loads((BASE / 'exact-byte-delta-and-native-recovery-proof091.json').read_bytes())
changes = proof['changes']
assert len(changes) == 11 and len({c['label'] for c in changes}) == 11
reverse = new.decode('utf-8')
for change in reversed(changes):
    assert reverse.count(change['new']) == 1, change['label']
    reverse = reverse.replace(change['new'], change['old'], 1)
assert reverse.encode('utf-8') == old

new_text = new.decode('utf-8')
new_tree = ast.parse(new_text)
old_tree = ast.parse(old.decode('utf-8'))
new_literals = literals(new_tree)
old_literals = literals(old_tree)
assert new_literals['PENDING_PREPARATION'] is old_literals['PENDING_PREPARATION'] is False
assert json_exact(new_literals['PLAN']) == json_exact(old_literals['PLAN'])
assert new_literals['SOURCE_HASHES'] == old_literals['SOURCE_HASHES']
assert len(new_literals['SOURCE_HASHES']) == 730
assert json_exact(new_literals['PLAN']) == json_exact(json.loads((BASE / 'focused-window-state-plan091.json').read_bytes()))
rows = new_literals['PLAN']['rows']
remaining = rows[16:]
assert len(rows) == 24 and len(remaining) == 8
assert sum(r.get('numerical_result_expected', True) for r in remaining) == 5
assert sum(not r.get('numerical_result_expected', True) for r in remaining) == 3
assert sum(r.get('explicit_click', False) for r in remaining) == 4
assert sum(r.get('numerical_result_expected', True) for r in remaining) * 3 == 15
assert rows[15]['id'] == 'amiya-natural-return-retains-false'
assert rows[15]['checked'] is False

descriptors = json.loads((BASE / 'run1-evidence-source-descriptors091.json').read_bytes())
for row in descriptors['files']:
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256']
archive = Path('/workspace/.compat/wine-focused-mainwindow-091-records.json.gz')
archive_data = archive.read_bytes()
assert sha(archive_data) == 'b818640c119c187d0baab2380422ebfef321151e88f86a6bb34cf0768c58793c'
saved = json.loads(gzip.decompress(archive_data))
original_row = saved['states'][15]
assert original_row['passed'] is True and original_row['id'] == rows[15]['id']
expected = {key: original_row[key] for key in ('scenario_native_before', 'result_native_before')}
assert json_exact(new_literals['WARM_EXPECTED']) == json_exact(expected)
assert json_exact(json.loads((BASE / 'warm-reference-original-last-passed-state091.json').read_bytes())) == json_exact(original_row)
warm_contract = json.loads((BASE / 'warm-reference-native-exact-contract091.json').read_bytes())
assert json_exact(warm_contract['native_expected']) == json_exact(expected)

fixture_change = next(c for c in changes if c['label'] == 'only fixture correction required id')
assert fixture_change['new'] == fixture_change['old'].replace("={'fields':", "={'id':owner,'fields':", 1)
warm_change = next(c for c in changes if c['label'] == 'exact warm recovery then only eight remaining states')
warm = warm_change['new']
for text in (
    "checkbox.setChecked(False);app.processEvents()",
    "train(PLAN['rows'][15]);app.processEvents()",
    "warm_raw=window.damage_result['scenario'];warm_result=window.damage_result['result']",
    "'scenario':copy.deepcopy(warm_raw),'result':copy.deepcopy(warm_result)",
    "'scenario_native':native(warm_raw),'result_native':native(warm_result)",
    "'actual_entries':delta(warm_before,entry_counts),'explicit_helper_or_formatter_requests':0",
    "assert warm_state['scenario_native']==WARM_EXPECTED['scenario_native_before']",
    "assert warm_state['result_native']==WARM_EXPECTED['result_native_before']",
    "warm_state['passed']=True",
    "receipt['post_warm_actual_entries']=dict(entry_counts)",
    "phase_before=dict(entry_counts)",
    "for row in PLAN['rows'][16:]:",
):
    assert text in warm, text
assert warm.index("assert warm_state['result_native']") < warm.index("phase_before=dict(entry_counts)") < warm.index("for row in PLAN['rows'][16:]")
assert not any(name in warm for name in ('format_estimate(', 'format_report(', 'calculate_damage(', '.click(', 'explicit_text_requests+=', 'explicit_buttons+='))
checkpoint_change = next(c for c in changes if c['label'] == 'save warm recovery in lossless checkpoint')
assert "'warm_recovery':warm_state" in checkpoint_change['new']
assert "assert len(states)==len(checks)==8" in new_text
assert "assert explicit_buttons==4 and explicit_text_requests==15" in new_text
assert "RECEIPT=OUT/'wine-focused-mainwindow-091-resume8-v2.json'" in new_text
assert "CHECKPOINT=OUT/'wine-focused-mainwindow-091-resume8-v2-records.json.gz'" in new_text
assert "path=OUT/'wine-focused-mainwindow-failure-091-resume8-v2.png'" in new_text
assert "'wine-focused-deepcolor-091.png':'wine-focused-deepcolor-091-resume8-v2.png'" in new_text

receipt = {
    'format_version': 1,
    'status': 'FINAL_RESUME8_DELTA_STATIC_PASS',
    'blockers': [],
    'author_public_manifest': descriptor(MF),
    'runner': descriptor(RUNNER),
    'parent_runner': descriptor(PARENT),
    '11_manifest_artifacts_safe_archive_paths_bytes_sha': True,
    '11_span_exact_reverse_whole_parent_bytes': True,
    'PLAN_and_SOURCE_HASHES_AST_literal_unchanged': True,
    'source_guard_730': 'Identical parent AST literal; no fresh730-product hash audit or old23-file packet rerun in this delta review.',
    'fixture_only_change': 'id:owner added to external direct operator_observations fixture; source product unchanged.',
    'source_contract': 'Already recorded app.py861/868 producer retains id, operator_summary.py8 consumes id. No new eligibility rule or mechanism added.',
    'original_failed_run1_preserved': descriptors['files'],
    'original16_successful_states_not_suite_replayed': True,
    'warm_control': {
        'original_index_zero_based': 15,
        'id': original_row['id'],
        'raw_gzip_exact_sha_bound': descriptor(archive),
        'both_full_saved_native_trees_equal_AST_expected': True,
        'current_controls': 'common setup then real checkbox False and existing train(row15); exact native scenario and result assertions precede post-warm phase reset/remaining loop.',
        'checkpoint_saves_actual_warm_input_result_native_entries_and_pass': True,
        'new_explicit_helper_formatter_button_requests': 0,
        'automatic_API_and_formatter_entries': 'Profile measured warm delta separately; root must inspect actual outcomes and equality.',
        'scope': 'One former passed state is deliberately recreated as recovery control. The original16 acceptance states and their48 explicit texts are not replayed. Literal handoff old_passed_states_reexecuted=false is limited to acceptance-suite replay, not this warm control.',
    },
    'remaining_focus': {'states': 8, 'result_states': 5, 'early_states': 3, 'explicit_buttons': 4, 'explicit_three_text_requests': 15, 'original_plan_rows_16_through_23_unchanged': True},
    'output_scope': 'New receipt/checkpoint/DeepcolorPNG/failurePNG names; old continuousPNG reused with exact descriptor. Warm payload saved separately from8 accepted-state count.',
    'counters_and_unknown_boundaries': 'Parent limited static formal unchanged: main-thread hooked Python function entries are not successful calculation counts; action-level talent observations do not certify native SP clock; root verifies actual outcomes/results/lossless saves.',
    'new_project_calls': {'API': 0, 'helper': 0, 'formatter': 0, 'constructor': 0, 'tests': 0, 'Qt': 0, 'Wine': 0},
    'new_product_or_tracked_changes': 0,
    'author_runner_import_or_execution': False,
    'current_delta_audit_preparation_failures': 0,
    'earlier_independent_preparation_error': 'One saved-receipt schema key assumption (records vs lossless_records/states), recorded separately and resolved without project calls.',
    'root_actual_fixture_issue_ledger': 'Original run1 missing-id fixture attempt1 failed after16 successful states; authorized corrected resume execution will be attempt2, not yet observed here.',
    'actual_runtime_resume_pass_claimed': False,
}
path = OUT / 'delta-source-native-recovery-receipt091.json'
path.write_bytes((json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps({'status': receipt['status'], 'manifest_files': 11, 'manifest_bytes': total, 'remaining_states': 8, 'new_project_calls': receipt['new_project_calls'], 'receipt': descriptor(path)}))
