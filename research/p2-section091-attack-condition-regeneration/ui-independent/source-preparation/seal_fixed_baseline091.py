"""Read two pinned Git blobs and seal static baseline facts; no project imports."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
DEST = Path(__file__).resolve().parent
COMMIT = '2cbc45f03f99ed4f04b9c7e2612b58542f909168'
EXPECTED = {
    'rouge/app.py': ('e349a7bba46a93a177a07522bac53df8ccc897dd',
                     '6a107fa37d2c21b9160131aa8c901fc2342ef7a422c3134dc0579ea24f4b56a2'),
    'scripts/verify_damage_ui.py': ('0bdc43563bbcff6c1d59d8dbfaa100e0256b3e43',
                                   '3b8ff41400002ff8616cb99690e47dcea9793b32bcdaa3ceb2bea20150fa396b'),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def new_json(name, value):
    path = DEST / name
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


sources = []
for name, (expected_blob, expected_sha) in EXPECTED.items():
    blob = git('rev-parse', COMMIT + ':' + name).decode().strip()
    assert blob == expected_blob, name
    data = git('cat-file', 'blob', blob)
    assert sha(data) == expected_sha, name
    ast.parse(data)
    path = DEST / 'fixed-source' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), str(path)
    path.write_bytes(data)
    sources.append({'fixed_commit': COMMIT, 'git_path': name, 'git_blob': blob,
                    'source_path': str(path), 'bytes': len(data), 'sha256': sha(data),
                    'original_bytes_and_line_endings_preserved': True})

receipt = {
    'format_version': 1,
    'status': 'FINAL_STABLE_FIXED_BASELINE_STATIC_PREPARATION',
    'fixed_commit': COMMIT,
    'sources': sources,
    'only_two_pinned_Git_blobs_read_for_source_review': True,
    'mutable_worktree_or_author_pending_source_read': False,
    'new_API_helper_tests_Qt_Wine_calls': 0,
    'project_imports': 0,
    'draft_written_or_future_code_reviewed': False,
    'actual_Qt_entry_counts_observed': None,
    'source_invariants': {
        'default': {'path': 'rouge/app.py', 'lines': [566, 567, 568],
                    'widget': 'self.continuous_attacks = QCheckBox', 'checked_default': True},
        'original_visibility': {'path': 'rouge/app.py', 'lines': [953, 960, 968],
                                'predicate': "current.get('sp_type')=='INCREASE_WHEN_ATTACK'",
                                'rank_source': "self.skill_rank_value()-1",
                                'application': 'setRowVisible; no setChecked/reset in visibility path'},
        'hidden_value_retained_and_serialized': {
            'path': 'rouge/app.py', 'lines': [1026, 1028],
            'producer': 'self.continuous_attacks.isChecked()',
            'unconditional_in_scenario': True,
            'hidden_state_reset_in_app_source': False,
            'baseline_direct_toggled_calculate_connection': False,
            'meaning': 'Existing widget checked state remains available when hidden and is included in '
                       'the next calculation; this is not evidence of disk persistence or actual Qt execution.'},
        'existing_bool_signal_construction_order': {
            'path': 'rouge/app.py', 'lines': [665, 666, 667],
            'order': ['QCheckBox(label)', 'setChecked(default)',
                      'widget.toggled.connect(lambda:self.calculate())'],
            'frame_timing_signal_line': 613,
            'target_buff_test_signal_line': 632,
            'source_level_initialization_fact': 'Defaults are assigned before the model checkbox '
                                                'calculation connection is attached; no callback count is claimed.'},
        'actual_UI_calculation_method': {
            'path': 'rouge/app.py', 'method': 'MainWindow.calculate', 'definition_line': 1005,
            'calculate_button_connect_line': 708, 'damage_function_call_line': 1150,
            'construction_order': 'MainWindow.__init__ adds make_damage_tab at line124; the tab creates '
                                  'damage_text/raw_damage/damage_technical at 710/713/716 and returns at721; '
                                  '__init__ calls update_operator at143 after tab construction.',
            'other_deferral_pattern': "update_operator uses hasattr(self,'attack') at792 and "
                                      "hasattr(self,'raw_damage') at847 before triggering calculate",
            'early_returns': [
                {'lines': [1012, 1013, 1014], 'condition': 'op is None'},
                {'lines': [1015, 1019, 1020], 'condition': "op not in catalog()['operators']"},
                {'lines': [1021, 1022, 1023], 'condition': 'self.skill.currentData() is None'}],
            'early_return_limit': 'calculate first clears damage_result, reads the selected operator, '
                                  'syncs animation references and optionally target buffs before these '
                                  'returns. It has no universal constructor-readiness guard. Existing '
                                  'source patterns do not prove arbitrary premature invocation is safe.',
            'exception_path': {'lines': [1156, 1157, 1158],
                               'effect': 'damage_result=None; show error text'}},
        'original_verify_damage_ui_visibility_assertion': {
            'path': 'scripts/verify_damage_ui.py', 'predicate_line': 39,
            'predicate': "app_module.catalog()['operators'][op]['skills'][skill-1]['levels'][-1]['sp_type']=='INCREASE_WHEN_ATTACK'",
            'widget_assertion_line': 43, 'label_assertion_line': 45,
            'assertion_form': 'isHidden()!=visible',
            'level_source_difference': 'The old verify predicate reads the last catalog skill level; '
                                       'the app predicate reads the currently selected skill rank.',
            'script_executed': False},
    },
    'mechanics_qualification_or_future_implementation_reviewed': False,
    'prep_errors_in_this_bounded_task': [],
}
new_json('fixed-baseline-source-receipt091.json', receipt)
note = DEST / 'NOTE.md'
assert not note.exists()
note.write_text('仅静审固定提交 2cbc45f 的 app.py 与 verify_damage_ui.py Git blob，原字节和换行已保存。'
                'checkbox 默认 True；原显示条件仅 Attack；隐藏不重置 checked，calculate 无条件读取此值。'
                'baseline 尚无该 checkbox 的 toggled→calculate 连接。\n\n'
                '现有 bool 控件先设置默认值，再连接 lambda:self.calculate。实际方法为 calculate()；'
                '早退之前仍会同步动画/目标强化，不能把早退当作任意构造阶段调用安全的证明。'
                '原 UI 校验 predicate 在 39 行，widget/label 断言在 43/45 行。所有项目调用为零。\n', encoding='utf-8')
files = []
for path in sorted(DEST.rglob('*')):
    if path.is_file():
        data = path.read_bytes()
        files.append({'source_path': str(path.resolve()), 'archive_path': path.relative_to(DEST).as_posix(),
                      'bytes': len(data), 'sha256': sha(data)})
new_json('public-artifacts-manifest-source-preparation091.json', {
    'format_version': 1, 'status': 'FINAL_STABLE', 'files': files,
    'file_count': len(files), 'total_bytes': sum(x['bytes'] for x in files),
    'manifest_self_excluded': True})
print(json.dumps({'status': receipt['status'], 'files': len(files),
                  'receipt_sha256': sha((DEST / 'fixed-baseline-source-receipt091.json').read_bytes()),
                  'manifest_sha256': sha((DEST / 'public-artifacts-manifest-source-preparation091.json').read_bytes())}))
