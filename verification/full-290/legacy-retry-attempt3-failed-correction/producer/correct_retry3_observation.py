"""Append factual correction only; preserve sealed failure/archive bytes."""
import ast
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'verification/full-290/legacy-retry-attempt3-failed'
NEW = ROOT / 'verification/full-290/legacy-retry-attempt3-failed-correction'
OLD_MANIFEST_SHA = 'a303bbe52ed0ac55476eb1714d1d820f2e11ccbfb10f06c024699e53861b06e9'
WINDOW_SHA = 'ada33b2f07d42b43c930059bd08fe01f3b88f9865001221c289760929befb9db'
STDERR_SHA = '05a0347bfe2fadc897fc13427e41d687bcf7f08693dfd918cc0fb96aeaf6c543'
HRESULT_URL = 'https://learn.microsoft.com/en-us/windows/win32/seccrypto/common-hresult-values'
NTSTATUS_URL = 'https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/596a1078-e883-4972-9bbc-49e60bebca55'


def demand(condition, message):
    if condition is not True:
        raise ValueError(message)


def regular(path):
    demand(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT), 'regular public evidence only')
    return path


def digest(path):
    return sha256(regular(path).read_bytes()).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def verify_old():
    demand(digest(OLD / 'archive-manifest.json') == OLD_MANIFEST_SHA, 'sealed failed archive manifest unchanged')
    manifest = json.loads((OLD / 'archive-manifest.json').read_bytes())
    for name, entry in manifest['files'].items():
        relative = Path(name)
        demand(not relative.is_absolute() and '..' not in relative.parts and '\\' not in name
               and (OLD / relative).resolve().is_relative_to(OLD), 'safe exact original member')
        demand(digest(OLD / relative) == entry['sha256'] and (OLD / relative).stat().st_size == entry['bytes'],
               'old sealed bytes unchanged: ' + name)
    return manifest


def main():
    demand(not NEW.exists() and not (HERE / 'FAILED-RETRY3-CORRECTION.json').exists(), 'new append-only correction destinations')
    original = verify_old()
    window_path, stderr_path = OLD / 'executed-legacy-bundle/window.py', OLD / 'legacy/supervisor.json.stderr.log'
    demand(digest(window_path) == WINDOW_SHA and digest(stderr_path) == STDERR_SHA, 'actual executed window and complete stderr')
    window, stderr = window_path.read_text(encoding='utf8'), stderr_path.read_text(encoding='utf8')
    tree = ast.parse(window)
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
             and isinstance(node.func.value, ast.Name) and node.func.value.id == 'platform' and node.func.attr == 'platform']
    main_try = next(node for node in tree.body if isinstance(node, ast.Try) and node.lineno == 1307)
    demand(len(calls) == 1 and calls[0].lineno == 1267 and main_try.finalbody[0].lineno == 3507
           and not any(node is calls[0] for statement in main_try.finalbody for node in ast.walk(statement)),
           'single platform metadata call before main try, absent from finally')
    lines = window.splitlines()
    demand(lines[3505].strip() == 'finally:' and lines[1328].strip()
           == 'app=QApplication([]);window=module.MainWindow();window.show();app.processEvents()',
           'exact actual finally keyword and compound startup line')
    raw_blocks = re.split(r'(?=Windows fatal exception: code 0x)', stderr)
    blocks = []
    for block in raw_blocks:
        code = re.match(r'Windows fatal exception: code (0x[0-9a-fA-F]+)', block)
        if code:
            blocks.append({'code': code[1].lower(),
                'window_frame_lines': [int(value) for value in re.findall(r'window\.py", line (\d+)', block)],
                'contains_platform_wmi_frame': '_wmi_query' in block})
    demand(blocks and blocks[-1]['code'] == '0xc000070a' and blocks[-1]['window_frame_lines'] == [1329]
           and any(row['code'] == '0x8007000e' and 1267 in row['window_frame_lines']
                   and row['contains_platform_wmi_frame'] for row in blocks), 'complete chronological fatal-block observations')
    historical = json.loads((OLD / 'failure-observation.json').read_bytes())
    demand(historical['window_finalizer_line1267_in_stack'] is True
           and historical['finalizer_crash_may_mask_prior_exception'] is True, 'identify exact historical incorrect observations')
    correction = {'kind': 'APPEND_ONLY_RETRY3_FAILURE_OBSERVATION_CORRECTION',
        'at_utc': datetime.now(timezone.utc).isoformat(),
        'sealed_original_archive': str(OLD.relative_to(ROOT)).replace('\\', '/'),
        'sealed_original_manifest_sha256': OLD_MANIFEST_SHA,
        'historical_observation': {'path': str((OLD / 'failure-observation.json').relative_to(ROOT)).replace('\\', '/'),
            'sha256': digest(OLD / 'failure-observation.json'), 'original_record_retained_unchanged': True},
        'withdrawn_observations': {
            'window_finalizer_line1267_in_stack': 'Incorrect: line1267 is receipt initialization before the main try, not finally.',
            'finalizer_crash_may_mask_prior_exception': 'Unsupported for this log/source; withdrawn, not a diagnosed causal explanation.'},
        'verified_source': {'path': str(window_path.relative_to(ROOT)).replace('\\', '/'), 'sha256': WINDOW_SHA,
            'platform_platform_call_count': 1, 'platform_platform_call_line': 1267,
            'receipt_initialization_line': 1262, 'main_try_line': 1307,
            'finally_keyword_line': 3506, 'finally_last_line': main_try.end_lineno,
            'platform_call_in_main_finally': False, 'compound_Qt_startup_line': 1329,
            'compound_Qt_startup_expression': lines[1328].strip()},
        'verified_stderr': {'path': str(stderr_path.relative_to(ROOT)).replace('\\', '/'),
            'sha256': STDERR_SHA, 'bytes': stderr_path.stat().st_size, 'fatal_blocks_in_recorded_order': blocks},
        'official_code_names': [
            {'code': '0x8007000E', 'name': 'E_OUTOFMEMORY', 'source': HRESULT_URL,
             'supported_meaning': 'A necessary memory allocation failed; this code alone does not establish physical RAM exhaustion.'},
            {'code': '0xC000070A', 'name': 'STATUS_THREADPOOL_HANDLE_EXCEPTION', 'source': NTSTATUS_URL,
             'supported_meaning': 'The documented status relates to an exception while waiting on a thread-pool handle; it does not locate the failing native callee.'}],
        'causality_limits': {'WMI_as_final_root_cause_established': False,
            'specific_QApplication_MainWindow_show_or_processEvents_callee_identified': False,
            'original_try_exception_masked_by_finally_established': False,
            'physical_RAM_exhaustion_proved': False, 'fresh_RAM_measurement_performed_by_this_correction': False,
            'root_reported_later_memory_observation_reproduced_as_our_own_measurement': False,
            'absence_of_another_functional_problem_proved': False},
        'unchanged_outcome': {'actual_child_exit': 3221227274, 'actual_supervisor_exit': 1,
            'complete_legacy_passed': False, 'typed_passed': False},
        'raw_or_old_manifest_rewritten': False, 'production_private_state_or_tests_modified': False,
        'tests_GUI_or_new_attempt_started': False}
    excerpt_sections = []
    for first, last in ((1261, 1273), (1307, 1332), (3506, 3534)):
        excerpt_sections.append('\n'.join(f'{index}: {lines[index - 1]}' for index in range(first, last + 1)))
    official_receipt = {'kind': 'OFFICIAL_DOCUMENTATION_NAME_LOOKUP_NOT_NATIVE_DIAGNOSIS',
        'accessed_utc': datetime.now(timezone.utc).isoformat(),
        'actual_tools': 'web search_query; open Microsoft Common HRESULT Values; find STATUS_THREADPOOL_HANDLE_EXCEPTION in MS-ERREF',
        'sources': [{'url': HRESULT_URL, 'title': 'Common HRESULT Values', 'verified_pair': ['0x8007000E', 'E_OUTOFMEMORY']},
            {'url': NTSTATUS_URL, 'title': '[MS-ERREF]: NTSTATUS Values', 'verified_pair': ['0xC000070A', 'STATUS_THREADPOOL_HANDLE_EXCEPTION']}],
        'full_remote_pages_copied': False, 'error_code_name_is_not_a_root_cause_proof': True}
    note = ('# 旧窗口重试3失败观察更正（追加）\n\n'
        '原sealed archive及stderr保持不变。此前“WMI/finally栈”及可能在finally遮蔽原异常的表述有误，应撤回。\n\n'
        '实际window.py的唯一platform.platform()在1267行receipt初始化中；主try从1307行开始，finally为3506–3534行，finally没有该调用。'
        '完整stderr先记录若干1267行平台/WMI栈，最后0xc000070a栈落在1329行：QApplication、MainWindow、show、processEvents共用一行。'
        '仅据该复合行不能区分具体失败调用，也不能把较早的WMI栈直接当作最终根因。\n\n'
        f'官方将0x8007000E命名为[E_OUTOFMEMORY]({HRESULT_URL})，表示必要的内存分配失败；此码本身不能证明整机物理RAM耗尽。'
        f'最终0xC000070A的官方名称是[STATUS_THREADPOOL_HANDLE_EXCEPTION]({NTSTATUS_URL})；名称不是本次具体native根因的定位。\n\n'
        'root另有后续内存观测，但本更正没有重新采样，也不把该时点观测冒充崩溃瞬间状态。'
        '根因仍待调查；不能据此证明或排除另一个功能问题。child3221227274/supervisor1、完整验收及typed未通过的结果不变。\n\n'
        '对应原件SHA、精确行位和按记录顺序分组的fatal栈见correction.json，所列源行见window-line-excerpts.txt。\n')
    payloads = {'correction.json': encode(correction), 'CORRECTION.md': note.encode('utf8'),
        'window-line-excerpts.txt': ('\n\n'.join(excerpt_sections) + '\n').encode('utf8'),
        'official-source-receipt.json': encode(official_receipt),
        'producer/correct_retry3_observation.py': Path(__file__).read_bytes()}
    NEW.mkdir()
    manifest = {'kind': 'APPEND_ONLY_FACT_CORRECTION_NOT_FAILURE_ARCHIVE_REWRITE', 'files': {},
        'original_failed_archive_manifest_sha256': OLD_MANIFEST_SHA, 'validation_pass_claimed': False}
    for name, raw in payloads.items():
        path = NEW / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(raw)
        manifest['files'][name] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
    demand(verify_old() == original, 'old131 sealed members remain unchanged after correction')
    with (HERE / 'FAILED-RETRY3-CORRECTION.json').open('xb') as stream:
        stream.write(payloads['correction.json'])
    with (NEW / 'archive-manifest.json').open('xb') as stream:
        stream.write(encode(manifest))
    print(json.dumps({'public_correction': str(NEW / 'correction.json'),
        'correction_sha256': digest(NEW / 'correction.json'),
        'new_manifest_sha256': digest(NEW / 'archive-manifest.json'),
        'old_manifest_unchanged': digest(OLD / 'archive-manifest.json') == OLD_MANIFEST_SHA,
        'validation_pass_claimed': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
