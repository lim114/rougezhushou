"""Close the complete account workflow only after root runtime and visual checks."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
OUT = Path('/workspace/.compat')
ARCHIVE = 'research/p2-section093-account-cache-safety'
BASE = 'f509d186e501bfcfd042e45b46e398ec756840ec'
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save_new(path, value):
    with path.open('xb') as stream:
        stream.write((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())
saved_path, verifier_path, verifier_log = map(Path, sys.argv[1:4])
saved = json.loads(saved_path.read_bytes())
actual_path = OUT / 'wine-account-window-093.json'
actual = json.loads(actual_path.read_bytes())
source_path = LOCAL / 'root-source-093.json'
source = json.loads(source_path.read_bytes())
visual_path = LOCAL / 'root-account093-visual-review.json'
visual = json.loads(visual_path.read_bytes())
shell_status = json.loads((LOCAL / 'root-wine093-shell-status-unavailable.json').read_bytes())
assert shell_status['actual_shell_primary_exit_code'] is None
assert shell_status['actual_shell_primary_exit_code_captured'] is False
assert shell_status['actual_runtime_receipt_complete_PASS'] is True
assert shell_status['stdout_final_pass_line_matches_receipt'] is True
assert shell_status['actual_receipt_sha256'] == digest(actual_path)
assert shell_status['runtime_log_sha256'] == digest(LOCAL / 'root-window-093.log')
assert saved['passed'] is actual['passed'] is actual['workflow_complete'] is visual['passed'] is True
assert saved['project_calls'] == 0
assert actual['source_drift'] == []
assert actual['source_sha256_before'] == actual['source_sha256_after'] == source['source_sha256_after']
assert source['current_maintained'] == 732 and source['unchanged_maintained'] == 728
for path in (actual_path, OUT / actual['records']['file']):
    assert saved['input_bindings'][str(path)] == {'bytes': path.stat().st_size, 'sha256': digest(path)}
for name, expected in source['source_sha256_after'].items():
    assert digest(ROOT / name) == expected
assert digest(ROOT / 'PROJECT_PROGRESS.md') == '85979acbfd41b7de256c3c75d855875d40d9881027f1cf569b0403c04106b58b'
assert actual['actual_function_entries']['MainWindow.__init__'] == 31
assert actual['numeric_state_success_count'] + actual['actual_existing_error_count'] + actual['actual_natural_early_return_count'] == 132
assert actual['explicit_button_requests'] == 2
assert actual['explicit_three_text_requests'] == 3 * actual['numeric_state_success_count']
assert actual['actual_API_outcomes']['raised_exception'] == actual['actual_API_outcomes']['returned_non_dict_or_unobserved_unwind'] == 0
assert len(visual['screenshots']) == 3 and visual['actual_view_image_tool_used'] is True
for item in visual['screenshots']:
    assert digest(OUT / item['file']) == item['sha256']

execution = {'format_version': 1, 'passed': True, 'root_tool_session_id': 67075,
    'related_primary_exit_code': 0, 'selected_primary_exit_code': 0,
    'actual_wine_primary_exit_code': None, 'actual_wine_primary_exit_code_captured': False,
    'actual_wine_runtime_receipt_complete_PASS': True, 'saved_only_verifier_primary_exit_code': 0,
    'Wine_shell_exit_limitation': 'Original tool session disappeared after completion; root preserves null shell status, exact final PASS stdout, complete receipt, saved-only review and actual PNG review. No successful prefix was replayed; full095 fresh validation remains required before commit/push.',
    'actual_wine_runner': '/workspace/.continuation/ui-093-account-cache-final/wine-account-window-093-final.py',
    'actual_wine_runner_sha256_prelaunch_and_postlaunch': 'aab214ac2903d6023fb6e44f78593e06ebeda120bc9fcf2300b2ef2a88ef5053',
    'runner_binding_evidence': 'root prelaunch hash check and explicit sole-process launch; original runtime receipt does not itself bind runner hash',
    'related': {'run': 64, 'passed': 64, 'skipped': 0, 'errors': 0, 'failures': 0},
    'selected': {'run': 1094, 'passed': 1093, 'skipped': 1, 'errors': 0, 'failures': 0},
    'actual_window': {'fresh_MainWindows': 31, 'states': 132,
        'numerical': actual['numeric_state_success_count'], 'expected_JSON_errors_before_API': actual['actual_existing_error_count'],
        'natural_early_return': actual['actual_natural_early_return_count'],
        'API_outcomes': actual['actual_API_outcomes'], 'API_by_phase_and_request': actual['actual_API_by_phase_and_request'],
        'actual_function_entries': actual['actual_function_entries'], 'explicit_buttons': 2,
        'explicit_three_texts': actual['explicit_three_text_requests'], 'success_PNGs_actually_viewed': 3},
    'source732_current_unchanged_after_all_checks': True,
    'tests_API_entry_counts_not_instrumented': True,
    'B2_Wine_coverage': 'masked old S3 only; standalone inert99 variant covered by actual Linux tests, not Wine',
    'source_counts_and_source_review_are_not_runtime_PASS': True,
    'complete_repository_validation': False, 'native_windows_game_verified': False}
runner_path = Path(execution['actual_wine_runner'])
assert digest(runner_path) == execution['actual_wine_runner_sha256_prelaunch_and_postlaunch']
save_new(LOCAL / 'root-execution-summary093.json', execution)

helper = ROOT / 'research/p2-section092-observation-window-workflow/root/root-archive092.py'
raw = helper.read_bytes()
assert raw == subprocess.check_output(['git', 'show', BASE + ':' + helper.relative_to(ROOT).as_posix()], cwd=ROOT)
namespace = {}
text = raw.decode()
assert text.count('phase = sys.argv[1]') == 1
exec(compile(text.split('phase = sys.argv[1]', 1)[0], str(helper), 'exec'), namespace)
row = namespace['row']
review_dir = LOCAL / 'ui-093-account-cache-final-independent-review'
review_mf = review_dir / 'public-artifacts-manifest-final-review093.json'
assert digest(review_mf) == 'ef8b88be4816a306c89b37ea3e1ef94bc977339da8062deb9d43b25b1d68e40c'
rows = []
for item in json.loads(review_mf.read_bytes())['files']:
    observed = row(Path(item['source_path']), item['archive_path'])
    assert observed == item
    rows.append(observed)
rows.append(row(review_mf, 'account093/final-independent-review/' + review_mf.name))
future = json.loads((LOCAL / 'root-future095-qualified-source-append093.json').read_bytes())
rows += future['files']
rows += json.loads((LOCAL / 'root-equips-feasibility095-source-append093.json').read_bytes())['files']
rows += json.loads((LOCAL / 'root-design095-source-append093.json').read_bytes())['files']
rows += json.loads((LOCAL / 'root-candidate094-source-append093.json').read_bytes())['files']
rows += json.loads((LOCAL / 'root-additional-source-append093.json').read_bytes())['files']
rows += json.loads((LOCAL / 'root-future096-qualified-source-append093.json').read_bytes())['files']
for name in ('wine-account-window-093.json', 'wine-account-window-093-records.json.gz',
             'wine-account-isolation-093.png', 'wine-account-recovery-093.png', 'wine-account-run-priority-093.png'):
    rows.append(row(OUT / name, 'account093/runtime/' + name))
for path in (saved_path, verifier_path, verifier_log, visual_path):
    rows.append(row(path, 'root/' + path.name))
for name in ('root-window-093.log', 'root-execution-summary093.json', 'root-archive-prepared093.json',
             'ROOT_CURRENT_WORK_093_WINE_RUNNING.json', 'ROOT_CURRENT_WORK_093_DEEP_BOUNDARY_RUNNING.json', 'root-equips-feasibility095-source-append093.json', 'root-design095-source-append093.json', 'root-future095-qualified-source-append093.json', 'root-additional-source-append093.json', 'root-candidate094-source-append093.json', 'ROOT_CURRENT_WORK_093_BATCH_POLICY_PENDING.json',
             'finish_section_batch_snapshot.py', 'record_section_batch_snapshot.py', 'root-future096-qualified-source-append093.json', 'root-batch-archive-source-review093.json', 'root-shell-status-boundary-source-review093.json', 'root-wine093-shell-status-unavailable.json', 'root-commit-cadence-change093.json', 'root-cloud-push-authorization093.json', 'root-remote-branch-check-before095.log', 'root-fetch-main-before095.log'):
    rows.append(row(LOCAL / name, 'root/' + name))
rows.append(row(Path(__file__), 'root/' + Path(__file__).name))
save_new(LOCAL / 'root-archive-append-spec093.json', {'format_version': 1, 'files': rows})

numeric = actual['numeric_state_success_count']
early = actual['actual_natural_early_return_count']
errors = actual['actual_existing_error_count']
api = actual['actual_API_outcomes']['returned_dict']
calculate = actual['actual_function_entries']['MainWindow.calculate']
summary = ('完成账户缓存安全使用完整功能组：启动、浏览、等级/技能切换、计算与样本摘要统一使用已校核账户视图；'
    '原盘损坏及不安全记录永久会话保护，不建目录/临时文件、不覆盖原件；合法新观察恢复可用事实，本局成员优先级及RunState不变。'
    '深500层合法未知附加JSON保留原生产者浅容器语义，避免整树deepcopy崩溃；跨解锁后的旧坏技能并集回退合法incoming，保留未知培养预览，不虚构事实。'
    'v1独审B1/B2原失败证据保留，v2十二合同SOURCE通过后接入实际92Git；39新增测试方法包含深层与两种跨解锁控制。'
    '相关64项全通过；Linux精选1094项1093通过/1历史跳过，0失败/错误。'
    f'一次Wine进程31个独立真实MainWindow，132状态通过（{numeric}数值/{errors}既有JSON错误/{early}自然早返回）；'
    f'{calculate}次calculate/{api}API返回dict，2按钮/{3*numeric}显式文本/3成功PNG实际查看，完整native/JSON/caller/原盘/本局记录校核，732源码零漂移。'
    '94输入刷新、95模组资料报告/全量方案及96培养情景条件来源说明仅来源准备，不计完成；原生Windows/game/chat及未知consumer/时钟未认证。')
spec = {'number': 93, 'topic': '账户缓存安全读取、原件保护与合法新观察恢复完整流程', 'summary': summary,
    'next_action': '自动在已验收实际93工作树快照上完成94既有13输入的刷新与状态使用完整功能组，随后在已验收实际94工作树快照上实现95所选模组资料与覆盖边界报告；95完成后全量可用Linux/Wine/窗口通过后统一commit并自动继续下一组。P2真正完成才转P3，未知consumer/时钟保留',
    'limitations': 'Wine为Linux上的真实Windows二进制兼容验证；原生Windows/game/chat及缺失私人历史样本未验。B2 Wine只覆盖masked旧S3；inert99独立变体仅实际Linux回归。来源审查不等同运行通过。原Wine工具session完成后未保留最终shell状态，退出码记录null；最终PASS输出与132完整收据、独立saved校核及3PNG绑定，未重跑成功前缀。95仍须fresh全量PASS后才commit/push。',
    'changed_paths': ['rouge/app.py', 'rouge/account_cache.py', 'tests/test_account_cache_093.py', 'scripts/verify_cloud.py'],
    'related_scope': 'test_account_cache_093/training_input_types/run_config_validation/run_crew_count_boolean_input: 64 actual tests',
    'root_source_script': str(LOCAL / 'root-integrate093.py'),
    'commit_message': 'Protect account cache originals and recover valid observed training safely',
    'verification': {'passed': True, 'workflow_complete': True, 'research_archive': ARCHIVE, 'source_receipt': ARCHIVE + '/root-source-093.json', 'root_prior_commit': BASE,
        'new_test_methods': 39, 'registry_change': True, 'maintained_source_files': 732, 'unchanged_maintained_source_files': 728,
        'new_maintained_source_files': ['rouge/account_cache.py', 'tests/test_account_cache_093.py'],
        'author_and_source_review_project_calls': 0, 'actual_window_verified_by_root': True,
        'actual_window_receipt': ARCHIVE + '/account093/runtime/wine-account-window-093.json',
        'actual_window_typed_native_records': ARCHIVE + '/account093/runtime/wine-account-window-093-records.json.gz',
        'actual_window_saved_record_review': ARCHIVE + '/root/' + saved_path.name,
        'actual_window_visual_review': ARCHIVE + '/root/' + visual_path.name,
        'actual_states': 132, 'actual_fresh_MainWindows': 31, 'actual_numeric_states': numeric,
        'actual_expected_JSON_error_states': errors, 'actual_natural_early_return_states': early,
        'actual_MainWindow_calculate_entries': calculate, 'actual_API_outcomes': actual['actual_API_outcomes'],
        'actual_API_by_phase_and_request': actual['actual_API_by_phase_and_request'],
        'actual_explicit_buttons': 2, 'actual_explicit_three_text_requests': 3*numeric, 'actual_success_PNGs_viewed': 3,
        'actual_Wine_primary_shell_exit_code': None, 'actual_Wine_primary_shell_exit_code_captured': False,
        'actual_Wine_final_stdout_and_complete_receipt_consistent': True,
        'source_after_checks_and_window_unchanged': True, 'tests_API_counts_not_instrumented': True,
        'native_windows_game_verified': False, 'complete_repository_validation': False,
        'PROJECT_PROGRESS_remaining_only_unchanged_sha256': digest(ROOT / 'PROJECT_PROGRESS.md'),
        'future_source_preparations_not_completed_sections': [94, 95, 96]}}
save_new(LOCAL / 'section093-spec.json', spec)
print(json.dumps({'actual_window_verified_by_root': True, 'append_files': len(rows), 'section_spec_prepared': True, 'project_calls': 0}))
