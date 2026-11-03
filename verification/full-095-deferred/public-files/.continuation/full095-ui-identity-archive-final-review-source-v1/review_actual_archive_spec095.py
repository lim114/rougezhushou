#!/usr/bin/env python3
"""Independent stdlib metadata/Source review. Never imports or executes a target.

Deferred: Root must first supply the actual completed archive spec and its SHA.
The report qualifies that physical spec and the frozen archive helper Source;
it does not run archives, codecs, repository checks, Wine, tests, or Git.
"""
import argparse
import ast
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
COMPAT = Path('/workspace/.compat')
HEAD = 'f509d186e501bfcfd042e45b46e398ec756840ec'
BRANCH = 'codex/p2-development'
HELPER = {'path': str(LOCAL / 'full095-batch-archive-ui-cache-source-v1/archive_full095_pending.py'), 'bytes': 47117, 'sha256': 'd93ca9bb4c50248f73337ef7b6535402e3925ec1aedd80d2e74dbe78853f0936'}
SOURCE_BASE_BINDING = {'path': str(LOCAL / 'full095-regression-ui-cache-resume-final-v1/actual-full095-source-binding.json'), 'bytes': 448896, 'sha256': 'b83ab67ca978d1b1b9e393c6d4e2cfb6c77e3bf9600af9d7ae87fe40975dbb84'}
BINDING = '__ACTUAL_UI_IDENTITY_RETRY_BINDING_FULL_REF_PENDING__'
EARLY = {'path': str(LOCAL / 'full095-ui-cache-metadata-independent-source-review-v1/formal-source-review-metadata-ui-cache095-v1.json'), 'bytes': 12107, 'sha256': '60bedf5325f607d56132f53de4776122a34a7612562793b4ecb8613e6af36ca1'}
TEMPLATE = {'path': '/workspace/.continuation/full095-archive-ui-identity-spec-source-v1/archive-spec-template-ui-identity095.json', 'bytes': 16286, 'sha256': 'c15ee01de8315148389a9d2c93dbcbf1057aa3a5bed5038f3f99c98b5762019d'}
JOBS = ('linux_full', 'wine_full', 'linux_selected', 'wine_selected', 'linux_pip', 'wine_pip', 'wine_ui', 'saved_review')
UI_POINTERS = {'passed': '/passed', 'complete_ui': '/complete_ui_validation', 'private_isolation': '/private_state_isolated', 'native_windows': '/native_windows_verified', 'source_drift': '/source_drift', 'game_captures': '/game_captures', 'chat_requests': '/chat_requests', 'source_before': '/source_sha256', 'source_after': '/source_sha256_after', 'checks': '/checks', 'actual_checks': '/total_actual_checks'}
SEEN = {}
CHECKS = []


def demand(value, message):
    if not value:
        raise ValueError(message)


def record(name, finding):
    CHECKS.append({'id': name, 'passed': True, 'finding': finding})


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def physical_ref(path):
    p = Path(path)
    demand(p.is_absolute() and str(p) == str(p.resolve()), 'Canonical absolute file path required: ' + str(p))
    demand(stat.S_ISREG(p.lstat().st_mode) and not p.is_symlink(), 'Regular non-symlink file required: ' + str(p))
    h = hashlib.sha256()
    count = 0
    with p.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
            count += len(chunk)
    reference = {'path': str(p), 'bytes': count, 'sha256': h.hexdigest()}
    demand(str(p) not in SEEN or SEEN[str(p)] == reference, 'Input changed during review: ' + str(p))
    SEEN[str(p)] = reference
    return reference


def bound(reference):
    demand(set(reference) == {'path', 'bytes', 'sha256'} and type(reference['bytes']) is int, 'Exact file reference required')
    demand(physical_ref(reference['path']) == reference, 'Physical bytes/SHA differ: ' + reference['path'])
    return Path(reference['path']).read_bytes()


def document(reference):
    return json.loads(bound(reference))


def relative(path):
    p = PurePosixPath(path)
    demand(type(path) is str and path and not p.is_absolute() and '..' not in p.parts and '.' not in p.parts and str(p) == path and '\\' not in path, 'Safe explicit relative archive path required')
    return path


def pointer(value, path):
    demand(type(path) is str and path.startswith('/'), 'Exact JSON pointer required')
    for token in path[1:].split('/'):
        key = token.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if type(value) is list else value[key]
    return value


def instant(value):
    t = datetime.fromisoformat(value)
    demand(t.tzinfo is not None, 'Timezone required in actual timestamp')
    return t


def function_bytes(raw):
    text = raw.decode('utf-8')
    lines = text.splitlines(keepends=True)
    return {node.name: ''.join(lines[node.lineno - 1:node.end_lineno]).encode('utf-8') for node in ast.parse(text).body if isinstance(node, ast.FunctionDef)}


def projection(proof, contract, reference, visual=False):
    value = pointer(proof, contract['pointer'])
    kind = contract['projection']
    demand(kind in ('full_ref', 'bytes_sha256') and (not visual or kind == 'full_ref'), 'Qualified proof projection differs')
    if kind == 'full_ref':
        demand(value == reference, 'Proof full reference differs')
    else:
        demand(type(value) is dict and value.get('bytes') == reference['bytes'] and value.get('sha256') == reference['sha256'] and ('path' not in value or value['path'] == reference['path']), 'Proof bytes/SHA/path differ')


def source_basis():
    early = document(EARLY)
    demand(early['source_gate_passed'] is True and early['runtime_pass'] is False and early['passed_checks'] == 28 and early['failed_checks'] == 0 and early['blockers'] == [], 'Frozen independent Source basis differs')
    demand(early['actual_completed_archive_spec_sha256'] is None and early['actual_completed_archive_spec_review_passed'] is False, 'Early Source basis may not contain a future actual-spec PASS')
    demand(early['actual_source_binding'] == SOURCE_BASE_BINDING and early['helpers']['archive_helper'] == HELPER, 'Independent basis binding/helper pins differ')
    helper_raw = bound(HELPER)
    inverse = document(early['inverses']['archive_helper'])
    original_raw = bound(inverse['original'])
    demand(inverse['candidate'] == HELPER and len(inverse['changes']) == 1, 'Only the qualified format3 admission delta is allowed')
    change = inverse['changes'][0]
    before = base64.b64decode(change['before_base64'], validate=True)
    after = base64.b64decode(change['after_base64'], validate=True)
    demand(helper_raw.count(after) == 1 and helper_raw.replace(after, before, 1) == original_raw, 'Whole helper inverse differs')
    old = function_bytes(original_raw)
    new = function_bytes(helper_raw)
    demand(set(old) == set(new) and len(old) == 22 and {key for key in old if old[key] != new[key]} == {'collect'}, 'Unchanged helper functions differ')
    demand(old['formal_gate'] == new['formal_gate'] and b"actual_binding.get('actual_ui_retry') is True" in after and b"actual_binding.get('root_spec_projection_from_ui_retry') is True" in after, 'Actual helper/spec formal gate or format3 flags differ')
    compile(helper_raw, HELPER['path'], 'exec')  # Syntax only; this code object is never executed.
    old_formal = document(early['old_archive_formal'])
    demand(old_formal['source_gate_passed'] is True and old_formal['runtime_pass'] is False, 'Original independent Source qualification differs')
    for reference in [*early['helpers'].values(), *early['manifests'].values(), *early['inverses'].values()]:
        bound(reference)
    record('frozen_source_basis', 'Exact early Source review, three helpers/manifests/inverses and old independent qualification remain physical and unchanged.')
    record('whole_helper_inverse_and_formal_gate', 'One exact inverse restores all 46894 original helper bytes (SHA256 1845b5bf5d3cd4f6d7b2122e7d5ce05ac5b1395ab1cdd41782e4112c4187c552); 21/22 functions including formal_gate remain whole bytes, and format3 requires both retry flags.')
    binding = document(BINDING)
    demand(binding['recovery_spec']['prior_ui_retry']['binding'] == SOURCE_BASE_BINDING, 'Original early-review b83 Source basis must remain the exact prior identity ancestor')
    return binding, document(TEMPLATE)


def review(spec_reference):
    binding, template = source_basis()
    spec = document(spec_reference)
    demand(spec['format_version'] == 1 and spec['section'] == 95 and spec['status'] == 'ROOT_ACTUAL_FULL095_BINDINGS_READY' and spec['expected_HEAD_before_batch_commit'] == HEAD and spec['branch'] == BRANCH, 'Actual completed section95 spec required')
    demand(spec['primary_exit_roles'] == template['primary_exit_roles'] and spec['sections'] == template['sections'] and spec['contracts']['context'] == template['contracts']['context'] and spec['contracts']['ui'] == UI_POINTERS, 'Original qualified role/pointer/chain schema differs')
    bindings = spec['bindings']
    demand(set(template['bindings']) <= set(bindings), 'Original archive roles are missing')
    refs, raw_json, archives = {}, {}, {}
    for role, item in bindings.items():
        demand(item['public'] is True and item['kind'] in ('json', 'text', 'binary'), 'Unresolved or unqualified public binding: ' + role)
        reference = {'path': item['source_path'], 'bytes': item['bytes'], 'sha256': item['sha256']}
        demand(physical_ref(reference['path']) == reference, 'Actual bound file differs: ' + role)
        refs[role] = reference
        if item['kind'] == 'json':
            raw_json[role] = json.loads(Path(reference['path']).read_bytes())
        path = relative(item['archive_path'])
        demand(path not in ('archive-manifest.json', 'git-index-payload-closure.json') and (path not in archives or archives[path] == reference), 'Archive binding collision')
        archives[path] = reference
    for role, item in template['bindings'].items():
        if item['source_path'] is not None:
            demand(bindings[role] == item, 'Frozen initial role differs: ' + role)
    demand(refs['context_source_binding'] == BINDING and refs['ui_final_runner'] == binding['root_spec']['ui']['runner'], 'Current actual context/UI Source binding differs')
    demand(refs['context_final_runner']['sha256'] == '__ACTUAL_UI_IDENTITY_RETRY_CONTEXT_RUNNER_SHA256_PENDING__', 'Final context Source runner differs')
    demand(refs['ui_preflight'] == binding['recovery_spec']['root_ui_prelaunch'], 'Actual Root UI prelaunch differs')
    record('actual_spec_schema_and_physical_bindings', 'Actual ready spec uses unchanged role/pointer schema; every declared file is a regular file with its exact physical bytes/SHA and safe archive destination.')
    record('current_source_pins', 'Completed spec binds the actual Root-sealed identity binding/context, exact identity producer and genuine third UI prelaunch.')
    actual = binding['actual_inputs']
    recovery = binding['recovery_spec']
    source = raw_json['source095_guard']
    start, final = raw_json['context_start'], raw_json['context_final']
    demand(binding['format_version'] == 3 and binding['actual_ui_retry'] is binding['root_spec_projection_from_ui_retry'] is binding['actual_ui_identity_retry'] is True and binding['available_checks_passed'] is False, 'Source binding must remain Source-only qualified format3')
    demand(source['passed'] is True and source['source_sha256_after'] == actual['source_sha256'] and source['current_maintained'] == len(actual['source_sha256']) == 735, 'Archived accepted guard/source735 metadata differs')
    demand(final['status'] == 'PASS_ACTUAL_FULL095_AVAILABLE_NOT_NATIVE_WINDOWS' and final['section'] == 95 and final['actual_base_HEAD'] == HEAD and final['available_checks_passed'] is final['complete_ui_validation'] is final['fresh_selected_executed_linux_and_wine'] is True and final['selected_reuse_performed'] is final['native_windows'] is False, 'Actual final available context gates differ')
    demand(start['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED' and start['source_sha256'] == final['source_sha256'] == final['source_sha256_after'] == actual['source_sha256'] and final['source_drift'] == [], 'Entire before/after context Source equality differs')
    demand(start['binding'] == final['binding'] == BINDING and start['final_context_runner'] == final['final_context_runner'] == refs['context_final_runner'], 'Start/final context Source references differ')
    original = document(recovery['original']['context'])
    prior = document(recovery['prior_recovery']['context'])
    demand(start['started_at'] == final['started_at'] == original['started_at'] and start['recovery_started_at'] == final['recovery_started_at'] == prior['recovery_started_at'] and start['ui_retry_started_at'] == final['ui_retry_started_at'], 'Actual original/recovery/UI epochs differ')
    began, resume, retry, identity, ended = [instant(value) for value in (start['started_at'], start['recovery_started_at'], start['ui_retry_started_at'], start['ui_identity_retry_started_at'], final['completed_at'])]
    demand(began <= resume <= retry <= identity <= ended and start['actual_ui_retry'] is final['actual_ui_retry'] is True
           and start['actual_ui_identity_retry'] is final['actual_ui_identity_retry'] is True
           and start['ui_identity_retry_started_at'] == final['ui_identity_retry_started_at'], 'Actual identity retry timing differs')
    for key, original_key in (('original_context', 'context'), ('original_source_binding', 'binding'), ('original_context_runner', 'runner')):
        demand(start[key] == final[key] == recovery['original'][original_key], 'Original epoch reference differs')
    for key in ('preserved_passed_executions', 'prior_failed_execution', 'prior_recovery', 'prior_incomplete_ui', 'prior_selected_failed_execution', 'preserved_recovery_passed_executions', 'prior_ui_retry', 'prior_incomplete_ui_cache'):
        demand(start[key] == final[key] == recovery[key], 'Preserved actual history differs: ' + key)
    for key in ('prior_failed_wine_full_preserved', 'recovery_contract_projection_verified', 'prior_incomplete_ui_preserved', 'prior_failed_wine_selected_preserved', 'prior_recovery_started_at_preserved', 'ui_retry_contract_projection_verified', 'prior_ui_retry_started_at_preserved', 'prior_incomplete_ui_cache_preserved', 'ui_identity_retry_contract_projection_verified'):
        demand(final[key] is True, 'Actual final closure preservation gate differs: ' + key)
    record('completed_context_and_source735', 'Real completed context retains available-only scope, no native Windows claim, and exact accepted735 before/after Source maps.')
    record('separate_actual_epoch_bounds', 'Original start and recovery times remain exact; the actual retry time bounds only new UI/saved rows.')
    witness = raw_json['root_primary_exits']
    demand(witness['format_version'] == 2 and witness['section'] == 95 and witness['actual_root_observed_primary_exits'] is True and set(witness['executions']) == set(JOBS) and final['actual_root_primary_exits'] == witness and type(final['physical_primary_exit_files_verified']) is int and final['physical_primary_exit_files_verified'] == 8 and final['exact_execution_contracts_verified'] is True, 'Exactly eight actual primary proofs required')
    demand(set(actual['execution_contracts']) == set(JOBS), 'Exact eight launch contracts required')
    paths = actual['global_output_plan']['paths']
    refs_by_path = {reference['path']: reference for reference in refs.values()}
    status_paths = []
    for job in JOBS:
        row, contract = witness['executions'][job], actual['execution_contracts'][job]
        demand(row['actual_root_observed_primary_exit'] is row['primary_exit_code_captured'] is row['fresh_execution'] is True and type(row['primary_exit_code']) is int and row['primary_exit_code'] == 0, 'Actual integer captured primary zero required: ' + job)
        demand(all(row[key] == contract[key] for key in ('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index')) and row['cwd'] == str(ROOT), 'Actual launch contract differs: ' + job)
        role = spec['primary_exit_roles'][job]
        demand(row['exit_code_file'] == refs[role] and refs[role]['path'] == contract['exit_code_path'] and bound(refs[role]) in (b'0\n', b'0\r\n'), 'Actual physical primary zero sink differs: ' + job)
        demand(row['stdout_log'] == refs_by_path.get(paths[contract['stdout_key']]), 'Actual stdout omitted or differs: ' + job)
        if row['runner'] is not None:
            demand(refs_by_path.get(row['runner']['path']) == row['runner'], 'Actual executed runner omitted: ' + job)
        demand(began <= instant(row['started_at']) <= instant(row['completed_at']) <= ended, 'Execution outside actual original completed epoch')
        if job in ('wine_full', 'wine_selected'):
            demand(instant(row['started_at']) >= resume, 'Wine execution predates recovery')
        if job in ('wine_ui', 'saved_review'):
            demand(instant(row['started_at']) >= identity, 'UI/saved execution predates new identity retry')
        if job == 'saved_review':
            demand(row['output_receipt'] == refs['ui_saved_review'] and row['output_receipt']['path'] == paths['saved_review_receipt'], 'Eighth real output receipt differs')
        status_paths.append(refs[role]['path'])
    demand(len(set(status_paths)) == len(set(spec['primary_exit_roles'].values())) == 8, 'Eight distinct actual primary status files required')
    record('eight_genuine_zero_rows', 'All eight actual captured integer-zero rows bind exact launch Source/contracts, canonical physical zero files, stdout, output receipts and actual timestamps.')
    for group in ('preserved_passed_executions', 'preserved_recovery_passed_executions'):
        for job, row in recovery[group].items():
            demand(witness['executions'][job] == document(row['observation']) and refs_by_path.get(row['observation']['path']) == row['observation'], 'Previously observed successful row altered or omitted: ' + job)
    demand(set(recovery['preserved_passed_executions']) == {'linux_full', 'linux_selected', 'linux_pip', 'wine_pip'} and set(recovery['preserved_recovery_passed_executions']) == {'wine_full', 'wine_selected'}, 'Preserved six successful jobs differ')
    for key in ('prior_failed_execution', 'prior_selected_failed_execution'):
        failure = document(recovery[key]['observation'])
        demand(type(failure['primary_exit_code']) is int and failure['primary_exit_code'] == 1 and failure['primary_exit_code_captured'] is True and bound(failure['exit_code_file']) in (b'1\n', b'1\r\n'), 'Actual failed primary one was changed')
        demand(refs_by_path.get(recovery[key]['observation']['path']) == recovery[key]['observation'] and refs_by_path.get(failure['stdout_log']['path']) == failure['stdout_log'] and refs_by_path.get(failure['exit_code_file']['path']) == failure['exit_code_file'], 'Failed attempt evidence omitted')
    incomplete = document(recovery['prior_incomplete_ui'])
    demand(incomplete['primary_exit_code'] is None and incomplete['primary_exit_code_captured'] is False and incomplete['raw_primary_status_absent'] is incomplete['final_UI_receipt_absent'] is True and incomplete['native_outcome'] == 'pending' and refs_by_path.get(recovery['prior_incomplete_ui']['path']) == recovery['prior_incomplete_ui'], 'Original unavailable UI was incorrectly turned into zero')
    cache_loss = document(recovery['prior_incomplete_ui_cache'])
    demand(cache_loss['primary_exit_code'] is None and cache_loss['primary_exit_code_captured'] is False
           and cache_loss['raw_primary_status_absent'] is cache_loss['final_UI_receipt_absent'] is True
           and cache_loss['native_outcome'] == 'pending'
           and refs_by_path.get(recovery['prior_incomplete_ui_cache']['path']) == recovery['prior_incomplete_ui_cache'], 'Second unavailable UI must remain bound, null, uncaptured and pending')
    cache_chunks = cache_loss['all_closed_compressed_chunk_refs_verified']
    demand(len(cache_chunks) == 2310 and all(refs_by_path.get(row['path']) == row and physical_ref(row['path']) == row for row in cache_chunks), 'All actual second-lost compressed history must remain archived Source metadata')
    record('six_preserved_rows_and_honest_failure_history', 'Four original and two recovery zero rows remain byte-bound observations; Wine failures retain actual primary one, and original UI retains null/uncaptured/absent/pending evidence.')
    for role in ('linux_full', 'wine_full'):
        receipt = raw_json[role]
        scope = receipt['source_sha256']
        demand(receipt['available_checks_passed'] is True and receipt['failures'] == receipt['errors'] == 0 and receipt['source_drift'] == [] and len(scope) == 342 and all(actual['source_sha256'].get(key) == value for key, value in scope.items()) and receipt['wine_compatibility'] is (role == 'wine_full') and receipt['native_windows_integration_verified'] is False, 'Actual full receipt scope differs')
        demand(type(receipt['complete_repository_validation']) is bool and type(receipt['unavailable']) is list and receipt['unavailable_records'] == len(receipt['unavailable']) and (not receipt['unavailable'] or receipt['complete_repository_validation'] is False), 'Honest full unavailable classifications differ')
    demand(final['complete_repository_validation'] is (raw_json['linux_full']['complete_repository_validation'] and raw_json['wine_full']['complete_repository_validation']), 'Actual repository completeness differs')
    for role in ('linux_selected', 'wine_selected'):
        demand(spec['selected_receipt_kinds'][role] == 'last_json_line', 'Qualified selected receipt schema differs')
        value = json.loads(bound(refs[role]).decode().strip().splitlines()[-1])
        demand(value['passed'] is True and value['failures'] == value['errors'] == 0 and type(value['tests_run']) is type(value['skipped']) is int and 0 <= value['skipped'] <= value['tests_run'], 'Actual selected counters differ')
    for role in ('linux_pip_log', 'wine_pip_log'):
        demand('No broken requirements found.' in bound(refs[role]).decode(errors='replace'), 'Actual dependency log differs')
    record('full_selected_dependency_receipts', 'Physical actual receipts retain available full PASS, exact342 Source subset, honest unavailable/native boundaries, selected counters and dependency results.')
    for role, ptr in spec['context_check_links'].items():
        demand(pointer(final, ptr) == refs[role], 'Final exact evidence link differs: ' + role)
    ui, extra, saved, visual = [raw_json[key] for key in ('ui_receipt', 'ui_extra_acceptance', 'ui_saved_review', 'ui_visual_review')]
    expected_ui_scope = {key: actual['source_sha256'][key] for key in actual['UI_expected_own_source_keys']}
    demand(ui['passed'] is ui['complete_ui_validation'] is ui['private_state_isolated'] is True and ui['native_windows_verified'] is False and ui['source_drift'] == [] and ui['game_captures'] == ui['chat_requests'] == 0 and ui['source_sha256'] == ui['source_sha256_after'] == expected_ui_scope and len(expected_ui_scope) == 129, 'Actual UI scope/source129 differs')
    demand(type(ui['checks']) is list and len(ui['checks']) == ui['total_actual_checks'] == final['ui_checks'] == spec['expected_actual_UI_checks'] and len(ui['checks']) > 0, 'Actual UI physical count differs')
    expected_assertions = [{'pointer': '/source_guard095/sha256', 'expected': refs['source095_guard']['sha256']}, {'pointer': '/source_guard095/before', 'expected': actual['source_sha256']}, {'pointer': '/source_guard095/after', 'expected': actual['source_sha256']}, {'pointer': '/source_guard095/source_drift', 'expected': []}, {'pointer': '/source_guard095/read_error', 'expected': None}, {'pointer': '/legacy085_prefix4217_and090_additional66_preserved', 'expected': True}, {'pointer': '/legacy090_source_fields_are_historical', 'expected': True}, {'pointer': '/historical093_original_Wine_shell_status', 'expected': None}]
    demand(spec['actual_UI_source_contract_assertions'] == expected_assertions and all(pointer(ui, row['pointer']) == row['expected'] for row in expected_assertions), 'Exact current UI Source assertions differ')
    record('actual_ui_complete_and_source_assertions', 'Physical complete isolated UI receipt supplies actual counts, exact129 before/after Source subset and all eight original guard/history assertions.')
    demand(saved['passed'] is saved['actual_fullUI_saved_evidence_verified'] is saved['actual_UI_primary_exit0_verified'] is saved['original_pending_and_final_inverse_exact'] is saved['actual_phase_ledger_verified'] is True and saved['status'] == 'PASS_SAVED_ONLY_ACTUAL_FULL095_UI_EVIDENCE' and saved['validation_kind'] == 'SAVED_ONLY' and saved['project_calls'] == 0 and saved['native_Windows_game_chat_verified'] is saved['complete_full095_or_section_validation'] is False, 'Actual Saved strict scope differs')
    demand(saved['input_spec'] == refs['ui_saved_input_spec'] and refs['ui_saved_input_spec']['path'] == actual['execution_contracts']['saved_review']['argv'][3] and refs['ui_saved_verifier'] == actual['execution_contracts']['saved_review']['runner'], 'Actual Saved control/source differs')
    control = raw_json['ui_saved_input_spec']
    demand(refs['source095_guard'] in control['ui_binding_input_refs'], 'Real archived section95 guard missing from Saved control')
    record('strict_saved_control_and_archived_guard', 'Actual Saved proof has strict Saved-only true fields, exact executed input/source and the real archived95 guard registered before execution.')
    acceptance = final['actual_ui_acceptance']
    demand(acceptance['actual_ui_receipt'] == refs['ui_receipt'] and extra['format_version'] == 2 and extra['section'] == 95 and extra['actual_ui_receipt'] == refs['ui_receipt'] and extra['artifacts'] == acceptance['artifacts'] and extra['primary_exit_witness'] == refs['root_primary_exits'], 'Physical original and normalized acceptance differ')
    outputs, png_roles = spec['actual_UI_output_roles'], spec['actual_PNG_roles']
    artifacts = {row['file']['path']: row for row in acceptance['artifacts']}
    demand(type(outputs) is list and outputs and len(outputs) == len(set(outputs)) == len(artifacts) and {refs[role]['path'] for role in outputs} == set(artifacts) and len(artifacts) == len(acceptance['artifacts']) and all(artifacts[refs[role]['path']]['file'] == refs[role] for role in outputs), 'Exact actual output set differs')
    for row in binding['root_spec']['ui']['required_saved_outputs']:
        demand(row['path'] in artifacts and artifacts[row['path']]['kind'] == row['kind'], 'Required current UI output omitted')
    physical_native = set()
    for name in actual['global_output_plan']['fresh_evidence_directories']:
        directory = Path(name)
        demand(directory.is_dir() and not directory.is_symlink(), 'Actual native directory missing')
        for p in directory.rglob('*'):
            mode = p.lstat().st_mode
            demand(not p.is_symlink() and (stat.S_ISDIR(mode) or stat.S_ISREG(mode)), 'Native namespace contains symlink/special file')
            if stat.S_ISREG(mode):
                physical_native.add(str(p))
    declared_native = set()
    for row in ui['full_native095']['files']:
        path = str(COMPAT / relative(row['file']))
        reference = {'path': path, 'bytes': row['bytes'], 'sha256': row['sha256']}
        demand(path not in declared_native and refs_by_path.get(path) == reference and artifacts.get(path) == {'kind': 'native-evidence', 'file': reference}, 'Receipt native artifact differs/omitted')
        declared_native.add(path)
    demand(declared_native == physical_native and physical_native, 'All actual native files must be covered exactly')
    index_ref = refs_by_path[binding['root_spec']['ui']['required_saved_outputs'][1]['path']]
    index = document(index_ref)
    demand(index['outcome'] == 'passed' and index['pending_entry_sequences'] == [] and type(index['chunks']) is list and index['chunks'] and index['source_guard_sha256'] == refs['source095_guard']['sha256'], 'Actual native index remains pending or guard differs')
    png_paths = {path for path, row in artifacts.items() if row['kind'] == 'screenshot'}
    demand(len(png_roles) == len(set(png_roles)) == len(png_paths) == 4 and set(png_roles) <= set(outputs) and {refs[role]['path'] for role in png_roles} == png_paths, 'Exact four current PNG roles differ')
    for path, row in artifacts.items():
        demand(saved['checked_file_refs'].get(path) == row['file'], 'Actual Saved did not bind every artifact')
    for role in png_roles:
        with Path(refs[role]['path']).open('rb') as stream:
            demand(stream.read(8) == b'\x89PNG\r\n\x1a\n', 'Actual PNG signature differs')
    record('all_native_and_exact_four_png_bindings', 'All regular native namespace files equal physical receipt/spec/Saved references; completed index is passed with no pending entries, and exactly four current PNGs have real signatures.')
    demand(visual['passed'] is visual['actual_root_view_image'] is True and visual['actual_PNGs_viewed'] == 4 and visual['native_Windows_game_chat_verified'] is False and visual['actual_runtime_receipt'] == refs['ui_receipt'] and len(visual['screenshots']) == 4, 'Actual Root visual proof differs')
    viewed = set()
    for row in visual['screenshots']:
        demand(row['actual_root_view_image'] is True and type(row['observed']) is str and row['observed'].strip() and row['file']['path'] in png_paths and row['file'] == artifacts[row['file']['path']]['file'] and row['file']['path'] not in viewed, 'Actual Root per-image row differs')
        viewed.add(row['file']['path'])
    demand(viewed == png_paths, 'Actual Root did not cover current four PNGs')
    record('four_genuine_root_visual_rows', 'Physical Root review records actual view_image for each current PNG, exact fullrefs and visible observations, without a native Windows claim.')
    common = {'ui_receipt': refs['ui_receipt'], 'ui_runner': refs['ui_final_runner'], 'source_guard': refs['source095_guard']}
    proofs = acceptance['receipts']
    demand(len(proofs) == len(extra['receipts']) == 2 and {row['kind'] for row in proofs} == {row['kind'] for row in extra['receipts']} == {'saved-validation', 'visual-review'}, 'Exact saved and visual normalized proofs required')
    for row in proofs:
        is_visual = row['kind'] == 'visual-review'
        proof = visual if is_visual else saved
        role = 'ui_visual_review' if is_visual else 'ui_saved_review'
        demand(row['file'] == refs[role], 'Normalized proof file differs')
        originals = [entry for entry in extra['receipts'] if entry['kind'] == row['kind'] and entry['file'] == row['file']]
        demand(len(originals) == 1, 'Original acceptance proof ambiguous')
        old = originals[0]
        demand(old['required_true_pointers'] == row['checked_true_pointers'] and old['common_file_bindings'] == row['checked_common_file_bindings'] and old['artifact_bindings'] == row['checked_artifact_bindings'] and row['checked_true_pointers'] and all(pointer(proof, ptr) is True for ptr in row['checked_true_pointers']), 'Exact checked acceptance contract differs')
        required = {'ui_receipt'} if is_visual else set(common)
        demand(required <= set(row['checked_common_file_bindings']) <= set(common), 'Proof common bindings incomplete')
        for name, contract in row['checked_common_file_bindings'].items():
            projection(proof, contract, common[name], is_visual)
        covered = set()
        for contract in row['checked_artifact_bindings']:
            path = contract['artifact_path']
            demand(path in artifacts and path not in covered, 'Proof artifact duplicated or unrelated')
            projection(proof, contract, artifacts[path]['file'], is_visual)
            covered.add(path)
        demand((png_paths if is_visual else set(artifacts)) <= covered, 'Proof artifact coverage incomplete')
        if is_visual:
            demand(pointer(proof, old['actual_view_image_pointer']) is True and row['actual_saved_review_primary_exit'] is None, 'Visual cannot replace actual image inspection or invent a saved execution')
        else:
            demand(old['execution_name'] == 'saved_review' and row['actual_saved_review_primary_exit'] == witness['executions']['saved_review'], 'Saved normalized primary witness differs')
    record('unchanged_exact_acceptance_projection', 'Original and normalized saved/visual contracts preserve exact true pointers, common guard/UI bindings, all artifact projections and the genuine eighth witness.')
    for declared, checked in zip(spec['sections'], final['completed_working_tree_chain']):
        demand(declared['number'] == checked['section'], 'Actual completed section chain differs')
        for name, role in (('receipt', declared['receipt_role']), ('closure', declared['closure_role']), ('source_guard', declared['source_role'])):
            demand(checked[name] == refs[role], 'Actual chain file binding differs')
        receipt, closure = raw_json[declared['receipt_role']], raw_json[declared['closure_role']]
        demand(receipt['passed'] is receipt['workflow_complete'] is receipt['actual_window_verified_by_root'] is True and receipt['completion_ref_is_Git_tag'] is False and receipt['commit_status'] == 'pending_next_fifth_section_full_PASS' and closure['status'] == 'VERIFIED_ARCHIVED_NOT_COMMITTED_OR_PUSHED' and closure['actual_HEAD_unchanged'] == HEAD and closure['all_archive_index_blobs_exact'] is True, 'Completed section receipt/closure differs')
    demand(final['completed_working_tree_chain'] == actual['completed_working_tree_chain'] and [row['section'] for row in final['completed_working_tree_chain']] == [93, 94, 95], 'Actual chain changed or section96 counted')
    authorization = raw_json['publication_authorization']
    demand(authorization['branch'] == BRANCH and authorization['user_explicit_destination'] == '提交并推送到 GitHub 当前开发分支', 'Existing user batch publication authorization differs')
    record('accepted_chain_and_existing_authorization', 'Spec preserves accepted archived93/94/95 receipt/closure refs, pending single batch commit and existing current-branch authorization; no section96 completion is counted.')
    sealed = set()
    packet_payload_count = 0
    for info in spec['public_packets']:
        demand(info['public'] is True and info['numbered_section_completed'] is False, 'SOURCE packet counted as a completed section')
        manifest_ref = physical_ref(info['manifest_path'])
        demand(manifest_ref['sha256'] == info['manifest_sha256'], 'Explicit public packet manifest differs')
        packet = document(manifest_ref)
        if info['style'] == 'source_archive_rows':
            rows = packet['files']
        elif info['style'] == 'local_artifact_dict':
            rows = [{'source_path': str(Path(info['manifest_path']).parent / name), 'archive_path': name, **metadata} for name, metadata in packet['artifacts'].items()]
        elif info['style'] == 'payload_file_rows':
            rows = [{'source_path': row['path'], 'archive_path': row['name'], 'bytes': row['bytes'], 'sha256': row['sha256']} for row in packet['payload_files']]
        elif info['style'] == 'payload_ref_rows':
            rows = [{'source_path': row['path'], 'archive_path': Path(row['path']).name, 'bytes': row['bytes'], 'sha256': row['sha256']} for row in packet['payload_files']]
        else:
            raise ValueError('Unqualified packet schema')
        demand(len(rows) == info['payload_count'], 'Explicit packet count differs')
        prefix = relative(info['archive_prefix'])
        for row in rows:
            reference = {'path': row['source_path'], 'bytes': row['bytes'], 'sha256': row['sha256']}
            demand(physical_ref(reference['path']) == reference, 'Public SOURCE packet payload differs')
            dest = prefix + '/' + relative(row['archive_path'])
            demand(dest not in archives or archives[dest] == reference, 'Public packet archive collision')
            archives[dest] = reference
            sealed.add((reference['path'], reference['sha256']))
        manifest_dest = prefix + '/' + Path(info['manifest_path']).name
        demand(manifest_dest not in archives or archives[manifest_dest] == manifest_ref, 'Public manifest archive collision')
        archives[manifest_dest] = manifest_ref
        packet_payload_count += len(rows)
    demand(spec['public_packets'] and all((refs[role]['path'], refs[role]['sha256']) in sealed for role in ('context_final_runner', 'context_source_binding', 'ui_final_runner')), 'Current final Source roles lack actual sealed public packets')
    record('physical_explicit_public_packets', 'All explicit packet styles/counts, manifests, payload hashes and safe destinations are physical; current context/binding/UI Sources are in sealed packets and count no completed sections.')
    demand(bound(refs['finish_primary_exit']) in (b'0\n', b'0\r\n') and refs['finish_console']['bytes'] > 0, 'Actual finish primary zero/console required')
    demand(spec['batch_product_and_metadata_files'] and type(spec['next_action']) is str and spec['next_action'].strip(), 'Explicit actual batch product metadata and next96 action required')
    product_paths = []
    for row in spec['batch_product_and_metadata_files']:
        product_paths.append(relative(row['path']))
        demand(type(row['bytes']) is int and row['bytes'] >= 0 and type(row['sha256']) is str and len(row['sha256']) == 64, 'Explicit batch product reference metadata differs')
    demand(len(product_paths) == len(set(product_paths)), 'Duplicate batch product path')
    record('actual_finish_and_late_live_boundary', 'Physical actual finish raw is zero and console is present. Explicit batch product refs are metadata; live maintained Source/Git/index/checkpoint checks remain unchanged in Root helper preflight.')
    for reference in tuple(SEEN.values()):
        demand(physical_ref(reference['path']) == reference, 'Physical input changed before review seal')
    record('final_physical_reread', 'Every actual metadata input hash was re-read before the independent report is written.')
    return {'actual_spec': spec_reference, 'bindings': len(bindings), 'actual_native_files': len(physical_native), 'actual_PNGs': len(png_paths), 'actual_UI_checks': len(ui['checks']), 'public_packets': len(spec['public_packets']), 'public_packet_payloads': packet_payload_count, 'unique_physical_inputs': len(SEEN)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--spec-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    demand(args.spec.is_relative_to(LOCAL) and args.output.is_relative_to(LOCAL) and str(args.output) == str(args.output.resolve()) and not args.output.exists(), 'Fresh external actual spec/review paths required')
    spec_reference = physical_ref(str(args.spec))
    demand(spec_reference['sha256'] == args.spec_sha256, 'Root supplied actual spec SHA differs')
    result = review(spec_reference)
    demand(str(args.output.resolve()) not in SEEN, 'Review output aliases an input')
    report = {'format_version': 1, 'section': 95, 'status': 'PASS_INDEPENDENT_ACTUAL_COMPLETED_ARCHIVE_SPEC_SOURCE_ONLY', 'passed': True, 'source_gate_passed': True, 'runtime_executed': False, 'runtime_pass': False, 'actual_completed_archive_spec_review_passed': True, 'actual_completed_archive_spec_sha256': spec_reference['sha256'], 'actual_spec_sha256': spec_reference['sha256'], 'archive_helper_sha256': HELPER['sha256'], 'archive_helper': HELPER, 'actual_source_binding': BINDING, 'early_source_basis': EARLY, 'actual_completed_archive_spec': spec_reference, 'reviewer_source': physical_ref(str(Path(__file__).resolve())), 'reviewed_at': datetime.now(timezone.utc).isoformat(), 'checks': CHECKS, 'passed_checks': len(CHECKS), 'failed_checks': 0, 'blockers': [], 'actual_metadata_counts': result, 'calls': {'target_helper_executions': 0, 'compiled_target_code_executions': 0, 'codecs': 0, 'project_imports': 0, 'project_calls': 0, 'tests': 0, 'Wine': 0, 'Git': 0, 'APIs': 0}, 'tracked_mutations': 0, 'actual_full095_runtime_executed_by_reviewer': False, 'archive_commit_push_executed': False, 'live_repository_guard_and_Git_checks_deferred_to_Root_preflight': True, 'STOPWRITE': True}
    raw = (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    with args.output.open('xb') as stream:
        stream.write(raw)
    demand(args.output.read_bytes() == raw, 'Independent review receipt changed during write')
    print(json.dumps({'source_review_only': True, 'review': physical_ref(str(args.output)), 'passed_checks': len(CHECKS), 'runtime_executed': False, 'archive_helper_sha256': HELPER['sha256'], 'actual_completed_archive_spec_sha256': spec_reference['sha256']}))


if __name__ == '__main__':
    main()
