"""Source-only design preparation; no project imports or calls."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
BASE = '59961ec3d633ac91b01014fb06b357d45e5979f7'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def put(name, data):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)


def js(name, obj):
    put(name, (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode())


sources = {}
blobs = {}
names = ('rouge/app.py', 'rouge/operator_summary.py', 'rouge/catalog.py',
         'rouge/timing.py', 'rouge/relics.py', 'rouge/damage.py',
         'rouge/operator_recognition.py', 'rouge/visual_recognition.py',
         'tests/test_view_catalog_045.py', 'tests/test_training_input_types.py',
         'tests/test_ui_refresh_045.py')
for name in names:
    blob = git('show', BASE + ':' + name)
    working = (ROOT / name).read_bytes()
    put('fixed-git/' + name, blob)
    blobs[name] = blob
    sources[name] = {'commit': BASE, 'git_blob': git('rev-parse', BASE + ':' + name).decode().strip(),
                     'bytes': len(blob), 'sha256': sha(blob),
                     'working_read_sha256': sha(working), 'working_equal_fixed': blob == working}
    if working != blob:
        put('working-read/' + name, working)

app = ast.parse(blobs['rouge/app.py'].decode())
function_scope = {}
for node in ast.walk(app):
    if isinstance(node, ast.FunctionDef) and node.name in (
        'calculate', 'update_operator', 'current_operator_state', 'training_conditions',
        'skill_rank_value', 'apply_operator_observation', 'update_base_attack'):
        function_scope[node.name] = {'start_line': node.lineno, 'end_line': node.end_lineno,
                                     'try_lines': [n.lineno for n in ast.walk(node) if isinstance(n, ast.Try)]}
assert function_scope['calculate']['try_lines'][0] == 1080
assert not function_scope['update_operator']['try_lines']
assert not function_scope['current_operator_state']['try_lines']
js('static-source-scope.json', {
    'fixed_commit': BASE, 'sources': sources, 'function_scope': function_scope,
    'private_paths_read': [],
    'operator_state_path_is_source_literal_only': True,
    'fixed_calculate_first_try_line': 1080,
    'normal_producer_includes_id': {'app_lines': [861, 868],
                                   'operator_recognition_scope': 'operator_profile',
                                   'visual_recognition_scope': 'operator_profile'},
    'runtime_execution_performed': False,
})

cases = []
def case(name, cache, route, failure, boundary):
    cases.append({'name': name, 'public_constructed_cache': cache,
                  'user_route': route, 'source_predicted_current_failure': failure,
                  'intended_recovery_boundary': boundary,
                  'product_runtime_checked': False})

startup = 'Open application; default branch selects kaltsit; startup update_operator reads current_operator_state.'
for name, value in [('null', None), ('array', []), ('boolean', True), ('number', 3), ('text', 'cache')]:
    case('cache_root_' + name, value, startup,
         'json.loads succeeds; operator_observations.get is not available on this type.',
         'Reject malformed account-cache root in memory; preserve original file and show account data unavailable.')
for name, value in [('null', None), ('array', []), ('text', 'record')]:
    case('record_' + name, {'kaltsit': value}, startup,
         'current_operator_state returns malformed account record; update_operator expects state.get.',
         'Quarantine this record only; other valid account records remain usable.')
for field in ('fields', 'skill_ranks'):
    for name, value in [('null', None), ('array', []), ('text', 'broken')]:
        record = {'id': 'kaltsit', 'fields': {}, 'skill_ranks': {}, field: value}
        case(field + '_' + name, {'kaltsit': record}, startup,
             'Present malformed container reaches .get/.items before numeric calculation try.',
             'Present invalid container is damaged data; absent container keeps the existing empty-default behavior.')
for name, record in [
    ('missing_id', {'fields': {}, 'skill_ranks': {}}),
    ('wrong_id', {'id': 'kaltsit', 'fields': {}, 'skill_ranks': {}}),
]:
    case(name, {'char_285_medic2': record}, 'Select existing Lancet-2 profile branch after opening.',
         'Unimplemented-profile early path calls format_operator_observation on cached record; missing id raises KeyError, mismatched id labels another operator.',
         'Treat cached identity as unconfirmed; never infer an observed identity from JSON key. Existing explicit GUI preview identity remains labeled as preview.')
case('captured_at_null', {'kaltsit': {'id': 'kaltsit', 'fields': {}, 'captured_at': None}}, startup,
     'time.localtime(None) itself accepts current time; later captured_at comparison with a number can raise TypeError in producer merge.',
     'Missing timestamp keeps zero default; explicit invalid timestamp is not evidence of observation time.')
case('captured_at_text', {'kaltsit': {'id': 'kaltsit', 'fields': {}, 'captured_at': 'bad'}}, startup,
     'time.localtime(text) rejects the string before calculate try.',
     'Quarantine invalid timestamp; do not replace it with current time or claim freshly read facts.')
case('elite_text', {'kaltsit': {'id': 'kaltsit', 'fields': {'elite': '2'}}}, startup,
     'profile.phases[elite] rejects text before public operator_attributes validation.',
     'Validate active account cultivation against existing catalog leaf types/gates; no string-to-number coercion.')
case('rank_text', {'kaltsit': {'id': 'kaltsit', 'fields': {}, 'skill_ranks': {'2': '7'}}}, startup,
     'update_skill_options subtracts one from supplied skill rank before calculate try.',
     'Malformed supplied skill-rank value is not a confirmed rank; valid omitted ranks retain current labeled-preview default.')
case('sources_array', {'kaltsit': {'id': 'kaltsit', 'fields': {}, 'sources': []}},
     'Open app, then receive an ordinary valid operator_profile observation for kaltsit.',
     'apply_operator_observation dictionary-unpacks saved.sources; array is not a mapping.',
     'Validate optional merge metadata containers while preserving missing defaults; subsequent observations may update memory but cannot overwrite the damaged original file.')
case('field_times_null', {'kaltsit': {'id': 'kaltsit', 'fields': {}, 'field_times': None}},
     'Open app, then receive an ordinary valid operator_profile observation for kaltsit.',
     'apply_operator_observation dictionary-unpacks saved.field_times; explicit null is not a mapping.',
     'Treat present malformed metadata as damaged; no fabricated field timestamps.')
js('public-constructed-cases.json', {'kind': 'static prediction only; not runtime results or tests',
                                   'cases': cases, 'case_count': len(cases)})

js('reviewable-group-design.json', {
    'status': 'SOURCE_ONLY_DESIGN_PENDING_AUTHOR_AND_ROOT_VALIDATION',
    'scope': 'Account-profile cache loading, browsing, report identity/source status and preservation of unreadable original cache; GUI JSON behavior is a compatibility control.',
    'normal_product_data_bug_claim': False,
    'normal_producer_loses_id_claim': False,
    'group_actions': [
        'Read/account-use boundary separates a missing file from an existing unreadable or structurally damaged file. A missing file permits ordinary future saves; damaged originals set a preservation flag.',
        'Validate account root and each selected record identity/container independently. Retain valid records and unknown extra keys exactly; quarantine damaged records and show their account source unavailable. Do not silently synthesize observed id, timestamp or cultivation.',
        'Present malformed fields, rank and merge-metadata containers are invalid; missing fields/skill_ranks/sources/time maps retain current empty defaults. Any broader active-leaf validation must reuse exact existing profile limits and show which field is unconfirmed.',
        'All browsing, supported calculation and unimplemented/no-skill/overview early paths use the same safe account view. Empty/invalid account facts use existing explicit preview defaults and source notice; no RunState or recruitment/event changes.',
        'A subsequent ordinary valid operator observation keeps current timestamp/order and merge semantics in memory. Existing damaged account file remains byte-identical and is not silently replaced by an incomplete clean map.',
        'Surface a concise status such as account cache unavailable, original file retained, using labeled profile preview; no technical traceback or asserted fresh account state.'
    ],
    'allowed_files_for_author_review': ['rouge/app.py', 'new narrowly scoped account-cache validation helper if useful'],
    'formatter_strategy': 'Prefer validation at the app account-use boundary; preserve format_operator_observation public strict identity contract unless separate concrete evidence authorizes a change.',
    'GUI_JSON_current_behavior': {
        'timing': 'Whitespace skips parse; nonblank legal JSON must be dict. Syntax/type errors have distinct timing text and are caught inside calculate.',
        'relic_context': 'Only current needed conditions cause parse; nonblank parsed value must be dict; other keys are filtered; hidden/inactive text stays ignored.',
        'error_result': 'calculate clears damage_result at entry and in exception handler. Successful prior result is not retained as current calculation.',
        'preview_scope': 'Per operator/skill text is restored under blocked signals; preview values never write RunState.',
        'confirmed_new_parse_defect': False},
    'compatibility': [
        'Keep catalog/damage/timing/relic numerical files and API exception ordering unchanged for this group.',
        'Do not normalize all public API None/falsy aliases into errors. Existing module_id=None ignores module_level alternatives; leaf aliases require case-specific existing controls.',
        'Recognizers use scope=operator_profile and tests also use account; do not require scope=account.',
        'Valid partial account records with absent fields/ranks/timestamps stay accepted under existing defaults; supplied null and absence are distinct only where the consumer actually requires a mapping/number.',
        'Selected GUI identity is explicit preview metadata; absent cached observed identity is not repaired into a confirmed observation.',
        'Unknown ignored record keys and source strings remain preserved; no schema upgrade or global account/run-state coercion.'
    ],
    'meaningful_validation_contract': {
        'source_before_changes': 'Exact frozen source hashes and existing producer/caller paths; independent review of identity, missing-vs-present distinctions and write protection.',
        'public_saved_before_after': 'Root/author run representative complete public outputs for valid records and GUI contexts; native types, numerical leaves, notes, errors and input immutability preserved. No need to reexecute previous broad source matrices.',
        'focused_account_boundary_checks': 'Use only temporary public fixtures for malformed root, malformed record containers, identity mismatch, active invalid leaf and mixed good/bad cache. Verify good records survive and no malformed facts enter cultivation.',
        'disk_and_run_protection': 'Original corrupted fixture bytes unchanged after startup, browsing, failed calculation and subsequent valid temporary observation. Temporary RunState memory/files unchanged by these previews; no private files read.',
        'valid_producer_control': 'Apply ordinary id-bearing operator_profile records, merge increasing/older timestamps using original ordering, preserve valid id/fields/ranks/source/timestamp and normal save behavior on a clean temporary file.',
        'actual_MainWindow': 'Root alone uses real project window under available Wine: open/browse/recalculate malformed-cache fixture, then valid/invalid timing and needed/inactive relic JSON, overview/no-skill/unimplemented early paths, visible field-specific errors and recovery. Record actual calls and screenshots.',
        'GUI_text_controls': 'Whitespace, {}, malformed syntax, null/false/0/[] top-level, target_windows=[], valid target ranges, active context required-condition error and inactive stale context ignored; return to valid text recovers. Keep existing API aliases as independent unchanged controls.',
        'tests': 'Only meaningful boundary tests if new validation requires them; no implementation-mirroring tests and no source-only prep counted as section completion.'},
    'unresolved_design_constraints': [
        'Exact user-facing notice and leaf-validation breadth are review choices, not source-established game mechanics.',
        'No automatic repair/overwrite route for damaged originals is proposed; a future explicit repair action would need separately reviewable scope.',
        'Foreign scope/run-only metadata in account cache must not be promoted into current-run evidence. Keep real run merge outside this change.'
    ],
    'counts': {'project_API': 0, 'project_helpers': 0, 'tests': 0, 'Qt': 0, 'Wine': 0,
               'network': 0, 'private_reads': 0, 'tracked_edits': 0},
})

js('preparation-diagnostics.json', {
    'kind': 'read preparation only; no product failures or runtime validation',
    'events': [
        {'problem': 'Guessed nonexistent operator_observations.py in an initial bounded rg call', 'attempts': 1,
         'exit_code': 2, 'recovery': 'rg --files identified actual operator_summary.py; subsequent reads use that path.'},
        {'problem': 'Guessed nonexistent config.py while locating OPERATOR_STATE literal', 'attempts': 1,
         'exit_code': 2, 'recovery': 'Used existing app.py literal only; no configuration/private files read.'},
        {'problem': 'A sampling-script occurrence search and several combined reads exceeded output budgets', 'attempts': 1,
         'recovery': 'Stopped broad script scans, used exact named test files and AST ranges. Truncated output not treated as exhaustive evidence.',
         'full_console_saved': False},
    ],
    'same_unresolved_problem_three_attempts': False,
    'earlier_negative093_packet_touched': False,
})
js('handoff-source-receipt.json', {
    'fixed_product_commit': BASE,
    'head_at_seal': git('rev-parse', 'HEAD').decode().strip(),
    'branch_at_seal': git('branch', '--show-current').decode().strip(),
    'prepared_utc': datetime.now(timezone.utc).isoformat(),
    'new_positive_scope': 'Robustness for publicly constructed damaged account-cache input, not loss of id by normal producer.',
    'GUI_JSON_parse_only_finding': 'Bounded negative; existing controls already have field-specific syntax/type validation.',
    'source_only': True, 'product_draft_created': False, 'section093_completed': False,
    'private_files_read': False, 'old_negative_packet_stopwrite_respected': True,
})

put('NOTE.md', '''# P2账户档案损坏输入工作流：来源准备与完整功能组设计

固定产品为59961ec3d633ac91b01014fb06b357d45e5979f7。所有材料只读源码和公开构造，0项目API/helper/tests/Qt/Wine/网络/私人文件读取，0tracked修改。本包不是第93节完成，也不包含产品补丁。

GUI时序与适用藏品JSON已有专属语法/type错误、空白略过、非适用藏品文本忽略和damage_result=None处理，不制造重复解析修复；本组用其作为保持兼容的完整流程控制。

真正可推进的健壮性范围是账户缓存的合法JSON但损坏结构。init只捕获读取/JSON错误，顶层及record容器没有使用前检查；默认kaltsit和切换档案会进入current_operator_state/update_operator，早于calculate的try。正常app producer明确保留id，真实recognizer scope是operator_profile；缺id、错误容器与身份错配均为公开构造的损坏缓存，不是正常合法producer漏洞。

完整组同时解决只读加载与逐record隔离、未知来源显示、浏览/重算恢复、后续有效采样的内存合并以及损坏原件不被自动覆盖。RunState、本局事件、识别算法和公共计算输入/alias/order均不改。缺字段的既有默认与显式错误类型必须区分，不能将选中的GUI预览身份自动包装成确认过的缓存身份。

public-constructed-cases.json全部为静态预测而非执行结果。captured_at=null的特殊边界已明确：time.localtime(None)接受当前时间，风险在后续数值比较，不能编造为启动TypeError。reviewable-group-design.json给出完整有意义的验收合同和需独立审阅的设计选择。根代理决定正式作者、执行窗口和集成。
'''.encode())

rows = []
for path in sorted(OUT.rglob('*')):
    if path.is_file():
        data = path.read_bytes()
        rows.append({'source_path': str(path), 'archive_path': path.relative_to(OUT).as_posix(),
                     'bytes': len(data), 'sha256': sha(data)})
js('public-artifacts-manifest-v1.json', {'schema_version': 1,
                                      'status': 'FINAL_SOURCE_DESIGN_V1_STOPWRITE', 'files': rows})
manifest = (OUT / 'public-artifacts-manifest-v1.json').read_bytes()
js('final-handoff093.json', {'status': 'FINAL_SOURCE_DESIGN_V1_STOPWRITE', 'packet_dir': str(OUT),
                            'manifest': 'public-artifacts-manifest-v1.json', 'manifest_sha256': sha(manifest),
                            'payload_files': len(rows), 'payload_bytes': sum(r['bytes'] for r in rows),
                            'manifest_and_handoff_self_excluded': True, 'project_calls': 0,
                            'product_patch': None, 'section093_completed': False,
                            'normal_producer_id_loss_claim': False})
print(json.dumps({'payload_files': len(rows), 'payload_bytes': sum(r['bytes'] for r in rows),
                  'manifest_sha256': sha(manifest),
                  'handoff_sha256': sha((OUT / 'final-handoff093.json').read_bytes())}))
