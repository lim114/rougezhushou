"""Bind successful runtime evidence and assemble the section92 closure specification."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import subprocess

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
OUT = Path('/workspace/.compat')
ARCHIVE = 'research/p2-section092-observation-window-workflow'
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save_new(path, value):
    with path.open('xb') as stream:
        stream.write((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())
source = json.loads((LOCAL / 'root-source-092.json').read_bytes())
saved = json.loads((LOCAL / 'root-focused092-saved-verification.json').read_bytes())
actual = json.loads((OUT / 'wine-focused-window-092.json').read_bytes())
assert saved['passed'] is actual['passed'] is True
assert saved['API_entries'] == 47 and saved['API_outcomes'] == {'returned_dict': 44, 'raised_exception': 3}
for name, expected in source['source_sha256_after'].items():
    assert digest(ROOT / name) == expected
assert digest(ROOT / 'PROJECT_PROGRESS.md') == '85979acbfd41b7de256c3c75d855875d40d9881027f1cf569b0403c04106b58b'
visual = {
    'format_version': 1, 'passed': True, 'reviewer': 'root',
    'reviewed_at': datetime.now(timezone.utc).isoformat(),
    'actual_view_image_tool_used': True,
    'source_receipt': digest(LOCAL / 'root-source-092.json'),
    'saved_records_receipt': digest(LOCAL / 'root-focused092-saved-verification.json'),
    'screenshots': [
        {'file': 'wine-focused-window-zero-092.png', 'sha256': digest(OUT / 'wine-focused-window-zero-092.png'),
         'visible': 'Actual project damage tab: observation total0 and damage observation window0.00 seconds. Positive full-skill and cycle reference rows remain; no window-average DPS row.'},
        {'file': 'wine-focused-window-friendly-092.png', 'sha256': digest(OUT / 'wine-focused-window-friendly-092.png'),
         'visible': 'Actual project damage tab: friendly medical skill, positive observation healing7140, treatment observation window6.00 seconds, window average HPS1190.'},
    ],
    'other_saved_notes_not_claimed_visible_in_screenshots': True,
    'native_windows_game_verified': False,
    'project_calls_during_visual_review': 0,
}
save_new(LOCAL / 'root-focused092-visual-review.json', visual)
execution = {
    'format_version': 1, 'passed': True,
    'related_primary_exit_code': 0, 'selected_primary_exit_code': 0,
    'actual_wine_primary_exit_code': 0, 'saved_only_verifier_primary_exit_code': 0,
    'related': {'run': 61, 'passed': 61, 'skipped': 0, 'errors': 0, 'failures': 0},
    'selected': {'run': 1055, 'passed': 1054, 'skipped': 1, 'errors': 0, 'failures': 0},
    'actual_window': {'states': 19, 'numerical': 15, 'expected_errors': 4, 'API_entries': 47, 'API_returned_dict': 44, 'API_expected_ValueError': 3,
                      'MainWindow_calculate_entries': 48, 'explicit_buttons': 2, 'explicit_three_texts': 45, 'success_PNGs_actually_viewed': 2,
                      'focused_API_entries': 38, 'focused_automatic_entries_including_expected_errors': 36},
    'full_typed_native_and_JSON_caller_and_result_bindings_verified': True,
    'maintained_current_source_map': source['source_sha256_after'],
    'source730_current_unchanged_after_all_checks': True,
    'Wine_X_connection_closed_after_exit0_is_teardown_not_failed_check': True,
    'tests_API_entry_counts_not_instrumented': True,
    'complete_repository_validation': False, 'native_windows_game_verified': False,
}
save_new(LOCAL / 'root-execution-summary092.json', execution)
spec_module = importlib.util.spec_from_file_location('archive092_saved_only', LOCAL / 'root-archive092.py')
# Load helper definitions without executing its command dispatch or a project import.
namespace = {}
helper_source = (LOCAL / 'root-archive092.py').read_text()
assert helper_source.count('phase = sys.argv[1]') == 1
exec(compile(helper_source.split('phase = sys.argv[1]', 1)[0], str(LOCAL / 'root-archive092.py'), 'exec'), namespace)
rows = namespace['sealed'](LOCAL / 'ui-092-focused-final-independent-review/manifest.json',
    'ae709b88d4318ae0412b3a4d346b5ffa610bebd067e7edfc87c4612e9cadd3f8', '', 'source_archive_rows', ['handoff.json'])
for item in rows:
    if Path(item['source_path']).name in ('manifest.json', 'handoff.json'):
        item['archive_path'] = 'focused092/independent-review/' + Path(item['source_path']).name
for name in ('wine-focused-window-092.json', 'wine-focused-window-092-records.json.gz', 'wine-focused-window-zero-092.png', 'wine-focused-window-friendly-092.png'):
    rows.append(namespace['row'](OUT / name, 'focused092/runtime/' + name))
for name in ('root-window-092.log', 'root-focused092-saved-verification.log', 'root-focused092-saved-verification.json',
             'root-focused092-visual-review.json', 'root-execution-summary092.json', 'root-archive-prepared092.json',
             'root-saved-only-verifier-strengthening092.json', 'root-verify-focused092.before-strict-projection-and-last-entry.py',
             'finish_section092.py', 'record_section.py'):
    rows.append(namespace['row'](LOCAL / name, 'root/' + name))
rows.append(namespace['row'](Path(__file__), 'root/' + Path(__file__).name))
save_new(LOCAL / 'root-archive-append-spec092.json', {'format_version': 1, 'files': rows})
summary = ('完成观察窗口与时序输入使用流程：窗口开关及秒数改动自动重算，控件明确观察范围和30Hz参考边界；'
           '伤害零秒/治疗报告显示实际已计窗口长度，零秒继续省略窗口平均DPS/HPS，保留技能周期、友方与未知时钟说明。'
           '两产品按实际91Git原件及四完整逆比较独审接入，730维护文件中728不变，无新增测试或登记改动。'
           '相关61项全通过，Linux精选1055项1054通过/1历史跳过，0失败/错误。'
           '一次真实Wine窗口19状态全通过（15数值/4预期错误），48次calculate、47API入口44返回dict/3预期ValueError；'
           '2按钮/45显式文本/2成功PNG实际查看，完整native/JSON/caller逐项绑定、源码零漂移。'
           '新源93账户缓存合同、94输入刷新及95全量迁移方案仅准备，不计完成；原环境恢复、历史失败与修订规则撤回如实保留。')
spec = {
    'number': 92, 'topic': '观察窗口刷新、零秒与治疗报告及供靶时序使用流程',
    'summary': summary,
    'next_action': '自动进入第93节账户缓存安全使用完整功能组：修复正式独审发现的深层ignoredJSON复制崩溃与合法partial观察恢复边界；基于实际92Git运输，完成合同重审、fresh回归、原盘保护和真实窗口再存档。94既有输入刷新随后推进，95后全量可用Linux/Wine/window并自动继续；P2真正完成才转P3',
    'limitations': 'Wine是Linux上的真实Windows二进制兼容验证，原生Windows/game/chat及缺失私人历史样本未验；未知原生时钟及隐藏机制继续保留，未来来源准备不算进度。',
    'changed_paths': ['rouge/app.py', 'rouge/reporting.py'],
    'related_scope': 'six existing modules: report/friendly-scope/timing/Gnosis lifetime/Amiya continuous lifetime/healing subtotal scaling',
    'root_source_script': str(LOCAL / 'root-integrate092.py'),
    'commit_message': 'Complete observation window refresh and damage/healing report workflow',
    'verification': {
        'research_archive': ARCHIVE, 'source_receipt': ARCHIVE + '/root-source-092.json',
        'root_prior_commit': '59961ec3d633ac91b01014fb06b357d45e5979f7',
        'new_tests': 0, 'registry_change': False,
        'maintained_source_files': 730, 'unchanged_maintained_source_files': 728,
        'author_public_API_entries': 8, 'author_external_formatter_requests': 24, 'author_actual_formatter_entries': 32,
        'independent_project_calls': 0, 'UI_preparation_and_source_review_project_calls': 0,
        'actual_window_verified_by_root': True,
        'actual_window_receipt': ARCHIVE + '/focused092/runtime/wine-focused-window-092.json',
        'actual_window_typed_native_records': ARCHIVE + '/focused092/runtime/wine-focused-window-092-records.json.gz',
        'actual_window_saved_record_review': ARCHIVE + '/root/root-focused092-saved-verification.json',
        'actual_window_visual_review': ARCHIVE + '/root/root-focused092-visual-review.json',
        'actual_states': 19, 'actual_numeric_states': 15, 'actual_expected_error_states': 4,
        'actual_MainWindow_calculate_entries': 48, 'actual_API_entries': 47,
        'actual_API_returned_dict': 44, 'actual_API_expected_ValueError': 3,
        'actual_explicit_buttons': 2, 'actual_explicit_three_text_requests': 45, 'actual_success_PNGs_viewed': 2,
        'actual_focused_API_entries': 38, 'actual_focused_automatic_API_entries_including_expected_errors': 36,
        'startup_and_common_API_entries': 9,
        'source_after_checks_and_window_unchanged': True, 'tests_API_counts_not_instrumented': True,
        'native_windows_game_verified': False, 'complete_repository_validation': False,
        'PROJECT_PROGRESS_remaining_only_unchanged_sha256': digest(ROOT / 'PROJECT_PROGRESS.md'),
        'future_source_preparations_not_completed_sections': [93, 94, 95],
    },
}
save_new(LOCAL / 'section092-spec.json', spec)
print(json.dumps({'actual_window_verified_by_root': True, 'append_files': len(rows), 'section_spec_prepared': True, 'project_calls': 0}))
