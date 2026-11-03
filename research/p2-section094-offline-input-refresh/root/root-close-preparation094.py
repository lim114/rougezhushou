"""Accept the whole refresh workflow only after actual runtime, saved and pixel checks."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
OUT = Path('/workspace/.compat')
ARCHIVE = 'research/p2-section094-offline-input-refresh'
BASE = 'f509d186e501bfcfd042e45b46e398ec756840ec'
FINAL = LOCAL / 'ui-094-offline-input-refresh-final-v2'
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save_new(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

saved_path, verifier_path, verifier_log = map(Path, sys.argv[1:4])
formal_mf = Path(sys.argv[4])
formal_sha = sys.argv[5]
formal_handoff = sys.argv[6]
saved = json.loads(saved_path.read_bytes())
actual_path = OUT / 'wine-focused-inputs-094.json'
actual = json.loads(actual_path.read_bytes())
source_path = LOCAL / 'root-source-094.json'
source = json.loads(source_path.read_bytes())
visual_path = LOCAL / 'root-focused094-visual-review.json'
visual = json.loads(visual_path.read_bytes())
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
assert saved['passed'] is actual['passed'] is actual['workflow_complete'] is visual['passed'] is True
assert saved['project_calls'] == 0 and actual['source_drift'] == []
assert source['current_maintained'] == 732 and source['unchanged_maintained'] == 731
assert actual['source_sha256_before'] == actual['source_sha256_after'] == source['source_sha256_after']
for rel, expected in source['source_sha256_after'].items():
    assert digest(ROOT / rel) == expected
for name in ('root-related-094.exit-code', 'root-selected-094.exit-code', 'root-window-094.exit-code', 'root-saved-focused094-review.exit-code'):
    assert (LOCAL / name).read_text().strip() == '0', name
for path in (actual_path, OUT / actual['records']['file']):
    assert saved['input_bindings'][str(path)] == {'bytes': path.stat().st_size, 'sha256': digest(path)}
counts = saved['actual']
assert counts['states'] == 90 and counts['fresh_MainWindows'] == 2
assert counts['affected_value_changes'] == counts['manual_buttons'] == 62
assert sum(counts[key] for key in ('numerical_affected_changes', 'existing_API_exception_changes',
    'existing_preAPI_JSON_error_changes', 'natural_early_return_changes')) == 62
assert len(visual['screenshots']) == 3 and visual['actual_view_image_tool_used'] is True
assert [item['file'] for item in visual['screenshots']] == [item['file'] for item in actual['actual_PNGs']]
for item in visual['screenshots']:
    assert digest(OUT / item['file']) == item['sha256']
assert digest(ROOT / 'PROJECT_PROGRESS.md') == '85979acbfd41b7de256c3c75d855875d40d9881027f1cf569b0403c04106b58b'
assert digest(FINAL / 'wine-focused-inputs-094-final.py') == 'cdc58d5efa9dd88512be87035b786c87ab58606646266258846854f379c498be'

execution = {'format_version': 1, 'passed': True,
    'actual_related_primary_exit_code': 0, 'actual_selected_primary_exit_code': 0,
    'actual_Wine_primary_exit_code': 0, 'actual_saved_verifier_primary_exit_code': 0,
    'external_primary_exit_artifacts_captured': True,
    'actual_executed_FINAL_runner': str(FINAL / 'wine-focused-inputs-094-final.py'),
    'actual_runner_prelaunch_and_postlaunch_sha256': digest(FINAL / 'wine-focused-inputs-094-final.py'),
    'runtime_receipt_alone_does_not_self_identify_runner_or_plan': True,
    'related_run_and_passed': 40, 'selected_run': 1094, 'selected_passed': 1093, 'selected_historical_skip': 1,
    'actual_saved_consistency_counts': counts, 'actual_function_entries': actual['actual_function_entries'],
    'actual_API_outcomes': actual['actual_API_outcomes'],
    'actual_API_by_phase_and_request': actual['actual_API_by_phase_and_request'],
    'actual_final_close_tail_not_control_callback_credit': saved['final_close_tail'],
    'actual_PNGs_viewed': 3, 'maintained_source732_unchanged_after_checks': True,
    'native_Windows_game_chat_verified': False, 'complete_repository_validation': False,
    'previous93_unavailable_shell_status_remains_unavailable': True,
    'source_correction_v1_bytes_issue_only': 'Original v1 JSON transport source blocker preserved; corrected v2 byte evidence does not claim bytes have an ordinary JSON_projection.'}
save_new(LOCAL / 'root-execution-summary094.json', execution)
helper = ROOT / 'research/p2-section092-observation-window-workflow/root/root-archive092.py'
raw = helper.read_bytes()
assert raw == subprocess.check_output(['git', 'show', BASE + ':' + helper.relative_to(ROOT).as_posix()], cwd=ROOT)
ns = {}
text = raw.decode()
assert text.count('phase = sys.argv[1]') == 1
exec(compile(text.split('phase = sys.argv[1]', 1)[0], str(helper), 'exec'), ns)
row, sealed = ns['row'], ns['sealed']
rows = sealed(FINAL / 'public-artifacts-manifest-focused-inputs094.json',
    '38c0f67d66b6d0510a2eade04ecd5818511026f5fb63bc3a0abce08a2fbfdc32',
    'window094/final', 'local_artifact_dict', ['handoff-focused-inputs094.json'])
rows += sealed(formal_mf, formal_sha, '', 'source_archive_rows', [formal_handoff])
for path in (actual_path, OUT / actual['records']['file']):
    rows.append(row(path, 'window094/runtime/' + path.name))
for metadata in actual['actual_PNGs']:
    path = OUT / metadata['file']
    rows.append(row(path, 'window094/runtime/' + path.name))
for path in (saved_path, verifier_path, verifier_log, visual_path):
    rows.append(row(path, 'root/' + path.name))
for name in ('root-execution-summary094.json', 'root-archive-prepared094.json',
    'ROOT_CURRENT_WORK_094_LINUX_PASS_FINAL_REVIEW_PENDING.json', 'ROOT_CURRENT_WORK_094_WINE_RUNNING.json', 'root-related-094.exit-code',
    'root-selected-094.exit-code', 'root-window-094.exit-code', 'root-saved-focused094-review.exit-code',
    'root-window-094.log', 'root-window-094-prelaunch.json', 'root-verify-saved094.sh', 'root-batch-archive-source-review094.json', 'finish_section_batch_snapshot.py',
    'record_section_batch_snapshot.py'):
    rows.append(row(LOCAL / name, 'root/' + name))
rows.append(row(Path(__file__), 'root/' + Path(__file__).name))
save_new(LOCAL / 'root-archive-append-spec094.json', {'format_version': 1, 'files': rows})

summary = ('完成13项局外情景输入的自动刷新完整流程：10个数值和3个布尔控件在真实值改变后自动计算；'
    '连接安排在全部控件、输出与默认值已构造后，不改变默认、数学、校验和本局优先级。'
    '覆盖部署经过、受疗人数、敌防法抗、协同与脆弱、冲锋、破屏、持续确认、开启次数、协同攻击和层数；'
    '保留隐藏/禁用原值、持续确认门、动态字段消费者覆盖、人数clamp与原错误，不猜原生时钟。'
    '相关40项全通过，Linux精选1094项1093通过/1历史跳过，0失败/错误。'
    f'实际Wine2个独立窗口，90状态、62真实值改变及62真实按钮通过；数值自动/手动分支完整native/caller/JSON/三文本一致，错误与自然早返回分支核对实际None、状态文字和API计数，'
    f'实测{counts["API_entries"]}次API入口/{counts["three_text_requests"]}显式文本，3PNG实际查看（2数值上下文、1既有错误上下文）；'
    '原始byte/None以独立完整hex证据保存，内存/原盘/本局持久状态核对，732源码零漂移。'
    '原窗口v1的source-only字节JSON阻塞保留；修正v2与三处绑定单独封存，来源准备不算运行。'
    '95资料报告、后续96条件资格说明及full095设计仍未完成；原生Windows/game/chat与未知机制未认证。')
spec = {'number': 94, 'topic': '十三项局外情景输入自动刷新与状态边界完整流程', 'summary': summary,
    'next_action': '自动在已验收实际94工作树快照及完整93/94归档链上，实现95所选模组原件资料和计算覆盖边界报告；保留全部既有数值及报告内容。95验收后fresh全量可用Linux/Wine/window，PASS后统一commit并推送origin codex/p2-development，再自动进入下一组。P2真正完成才转P3，未知consumer/时钟保持未知',
    'limitations': 'Wine兼容验证不代表原生Windows/game/desktop；2数值PNG与1既有错误PNG实际查看，数值/调用事实来自完整保存记录而非像素。93原Wine shell状态仍null，不用94shell0倒填。full095未运行、95及96来源准备不计完成。',
    'changed_paths': ['rouge/app.py'], 'related_scope': 'charge_reference/shield_break_reference/myrtle_healing_targets/training_input_types/healing_subtotal_scaling: 40 actual tests',
    'root_source_script': str(LOCAL / 'root-integrate094.py'),
    'commit_message': 'Refresh offline scenario previews for all existing inputs',
    'verification': {'passed': True, 'workflow_complete': True, 'research_archive': ARCHIVE,
        'source_receipt': ARCHIVE + '/root-source-094.json', 'root_prior_commit': BASE,
        'new_test_methods': 0, 'registry_change': False, 'maintained_source_files': 732,
        'unchanged_maintained_source_files': 731, 'new_maintained_source_files': [],
        'actual_base_section': 93, 'actual_window_verified_by_root': True,
        'actual_window_receipt': ARCHIVE + '/window094/runtime/' + actual_path.name,
        'actual_window_typed_native_records': ARCHIVE + '/window094/runtime/' + actual['records']['file'],
        'actual_window_saved_record_review': ARCHIVE + '/root/' + saved_path.name,
        'actual_window_visual_review': ARCHIVE + '/root/' + visual_path.name,
        'actual_states': 90, 'actual_fresh_MainWindows': 2, 'actual_value_changes': 62,
        'actual_manual_buttons': 62, 'actual_saved_counts': counts,
        'actual_Wine_primary_shell_exit_code': 0, 'actual_Wine_primary_shell_exit_code_captured': True,
        'actual_API_outcomes': actual['actual_API_outcomes'],
        'actual_API_by_phase_and_request': actual['actual_API_by_phase_and_request'],
        'actual_PNGs_viewed': 3, 'source_after_checks_and_window_unchanged': True,
        'tests_API_counts_not_instrumented': True, 'native_windows_game_verified': False,
        'complete_repository_validation': False,
        'PROJECT_PROGRESS_remaining_only_unchanged_sha256': digest(ROOT / 'PROJECT_PROGRESS.md'),
        'future_source_preparations_not_completed_sections': [95, 96]}}
save_new(LOCAL / 'section094-spec.json', spec)
print(json.dumps({'actual94_complete_gates_passed': True, 'append_files': len(rows), 'project_calls': 0}))
