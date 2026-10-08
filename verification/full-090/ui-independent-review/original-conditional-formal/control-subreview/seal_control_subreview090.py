"""Seal an already completed static review; never import or execute project code."""
import ast
import hashlib
import json
from pathlib import Path

DEST = Path(__file__).resolve().parent
ROOT = Path('/workspace/rougezhushou')
PACKET = Path('/workspace/.continuation/ui-090-final')
RUNNER = PACKET / 'wine-ui-smoke-090-final.py'
EXPECTED = 'bb35222b37dbbdb4416f415a011f3a0b678c5285729ac0bccb76ec8ba336983a'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


runner_bytes = RUNNER.read_bytes()
assert sha(runner_bytes) == EXPECTED
tree = ast.parse(runner_bytes)
frozen = next(ast.literal_eval(n.value) for n in ast.walk(tree)
              if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_SOURCE090'
                                                   for t in n.targets))
project_paths = ['rouge/app.py', 'rouge/operator_options.py', 'rouge/animation_reference.py',
                 'rouge/data/catalog.json', 'rouge/data/operator-profiles.json',
                 'rouge/data/original-animation-references.json']
bindings = []
for name in project_paths:
    path = ROOT / name
    data = path.read_bytes()
    assert sha(data) == frozen[name], name
    bindings.append({'source_path': str(path), 'bytes': len(data), 'sha256': sha(data)})
for name in ['wine-ui-smoke-090-final.py', 'saved52-UI-producer-inputs-and-public-projections090.json',
             'Back5-current-data-and-actual-choice-plan090.json']:
    path = PACKET / name
    data = path.read_bytes()
    bindings.append({'source_path': str(path), 'bytes': len(data), 'sha256': sha(data)})

receipt = {
    'format_version': 1,
    'status': 'FINAL_STABLE_STATIC_CONTROL_SCOPE_PASSED',
    'actual_root_commit': '5e2ff697402d06e78b239e01f0b4307b50dd5633',
    'runner_sha256': EXPECTED,
    'static_scope_passed': True,
    'control_scope_blockers': [],
    'actual_UI_execution': False,
    'new_API_helper_formatter_Qt_Wine_test_calls': 0,
    'project_imports': 0,
    'runner_execution_or_import': False,
    'saved_numeric_results_reverified': False,
    'inputs': bindings,
    'reviewed_checks': {
        'AST_runner_rows_equal_sealed_plan': True,
        'row_count': 52,
        'rows_by_section': {'86': 44, '88': 8},
        'all_52_training_fields_exist_and_levels_skills_ranks_modules_are_UI_expressible': True,
        'all_44_option_fields_are_real_bool_default_checkboxes': True,
        'all_44_option_serialization_flags_match_OPTIONS_skill_membership': True,
        'all_requested_active_option_values_fit_actual_widget_types_and_ranges': True,
        'hidden_option_fields_are_omitted_from_inputs_and_app_scenario': True,
        'continuous_attacks_is_always_serialized_from_actual_checkbox_even_when_hidden': True,
        'new_8_checkbox_values_are_native_bool_and_equal_widget_checked': True,
        'new_8_continuous_visibility_source': {
            'mechanist_S1': 'INCREASE_WHEN_ATTACK: visible',
            'amiya_E2_S1': 'INCREASE_WITH_TIME: hidden',
            'chen3_S3': 'INCREASE_WITH_TIME: hidden',
            'amiya_E0_S1': 'INCREASE_WITH_TIME: hidden'},
        'two_JSON_timing_pairs': ['amiya_E2_S1: target_disappears_seconds=5.75',
                                  'amiya_E0_S1: target_windows=[]'],
        'window_12_75_is_expressible_by_two_decimal_spinbox': True,
        'timing_JSON_parsed_as_dict_and_retained_when_animation_combos_are_None': True,
        'three_text_path': 'Each row explicitly formats estimate/default/technical; estimate equals default; '
                           'actual QPlainTextEdit default, technical checkbox True, then default restored '
                           'must match the same result. Native scenario/result preservation assertions follow.',
        'training_producer_scope': 'Synthetic account observation fields are injected through existing train() '
                                   'and run training is disabled; no native OCR, account ownership, or actual '
                                   'in-game cultivation proof is claimed.',
        'Back5_plan_equals_current_original_animation_records': True,
        'Back4_controls': 'S1/S2 x normal/skill, each combo selects actual Back:Attack, checks actual data '
                          'and label, then restores default None.',
        'Back_Attack_eligibility': 'Source choices() requires selectable_as_conventional_reference and '
                                 'Attack prefix; both normal and skill roles accept Attack.',
        'generic_Back_Skill_exclusion': 'Unnumbered Skill fails Attack prefix and numbered Skill regex; '
                                       'excluded for normal and both numbered skill combos despite its '
                                       'conventional-reference metadata flag being true.',
        'Back_default_item': '沿用现有参考（未绑定动作）, currentData None',
        'Back_Attack_expected_label': '背面 · 普通攻击 · 出手16帧 / 动画40帧',
        'native_animation_binding_claimed': False,
    },
    'source_line_evidence': {
        'runner': [1271, 1528, 1915, 2942, 2952, 2970, 2981, 3000, 3010, 3018, 3022, 3052],
        'app': [566, 609, 665, 767, 779, 802, 949, 1026, 1035, 1140, 1145, 1162, 1206],
        'animation_reference': [13, 17, 19, 20, 21, 26, 42]},
    'coverage_observation_for_parent_total_review': {
        'code_line': 3034,
        'condition': "row090['kind']=='coveredmodule'",
        'actual_matching_pair_id': 'coveredmodule:oblvns-ranged-skill-vs-normal',
        'literal_row_indexes_zero_based': [26, 27],
        'actual_kind_both_rows': 'qualification',
        'special_trace_guard_reachable_for_this_pair': False,
        'effect': 'The specialized normal-plan/ranged-condition/note-count trace assertions are not '
                  'executed by these two rows. Generic checkbox/raw-scenario/projection/three-text '
                  'assertions remain reachable. Parent owns coverage acceptance; sealed runner unchanged.'},
    'preparation_diagnostics': [
        {'kind': 'oversized_read_only_search_output', 'effect': 'Initial rg matched giant literal lines; '
         'display was truncated. Later reads used AST literal extraction and bounded source excerpts.'},
        {'kind': 'static_display_script_error', 'error': "KeyError: 'kind'",
         'cause': 'New 8 rows intentionally lack the old44 kind field; display treated layouts alike.',
         'resolution': 'Read new8 keys separately; no product code, saved numeric result or GUI executed.'}],
}
write_json(DEST / 'control-static-receipt090.json', receipt)
note = DEST / 'NOTE.md'
assert not note.exists()
note.write_text('52 行（44＋8）的培养、真实 checkbox、JSON 与三文本展示路径静审通过；Back4 只选择实际 Attack，'
                'generic Skill 不进入正常或编号技能 combo。所有项目调用为零，尚未执行 GUI。\n\n'
                '已交总审的覆盖观察：coveredmodule pair 的 kind 为 qualification，3034 行 coveredmodule 专项 trace '
                'guard 不可达。通用控件与三文本断言仍可达；未改动封存 runner。\n', encoding='utf-8')
files = []
for path in sorted(DEST.iterdir()):
    if not path.is_file():
        continue
    data = path.read_bytes()
    files.append({'source_path': str(path.resolve()), 'archive_path': path.name,
                  'bytes': len(data), 'sha256': sha(data)})
write_json(DEST / 'public-artifacts-manifest.json', {
    'format_version': 1, 'status': 'FINAL_STABLE', 'files': files,
    'file_count': len(files), 'total_bytes': sum(x['bytes'] for x in files),
    'manifest_self_excluded': True})
print(json.dumps({'status': receipt['status'], 'files': len(files),
                  'receipt_sha256': sha((DEST / 'control-static-receipt090.json').read_bytes()),
                  'manifest_sha256': sha((DEST / 'public-artifacts-manifest.json').read_bytes())}))
