"""Root-only full380 complete available-scope summary seal, bound to one actual attempt. Never runs a test/window/reviewer.

Preparation is not execution. Requires the terminal original archive, retained
root-Popen exit, every declared actual job, original automatic review and real visual
proof. A refusal never writes a PASS summary or changes any original evidence.
"""
from pathlib import Path, PurePosixPath
from hashlib import sha256
from datetime import datetime, timezone
from collections import Counter
import argparse
import ast
import gzip
import json
import re
import sys
import tempfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
BASE = None
ARCHIVE = None
VISUAL = None
FREEZE = None
OUT = ROOT / 'verification/full-380/summary.json'
PARENT = None
ATTEMPT = None
FREEZE_SHA = None
ACTIVATION_SHA = None
REVIEW_SHA = None
VISUAL_SCHEMA = 'full380_actual_png_visual_inventory_v1'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def regular(path, base=ROOT):
    path = Path(path)
    require(path.is_absolute() and path.is_file() and not path.is_symlink()
            and path.resolve().is_relative_to(base.resolve()), 'Exact regular recorded file required: ' + str(path))
    for parent in path.parents:
        if parent == base:
            break
        require(not parent.is_symlink(), 'Linked parent refused: ' + str(path))
    return path


def relative(path):
    return Path(path).relative_to(ROOT).as_posix()


def safe_member(name):
    require(type(name) is str, 'Relative member must be text.')
    p = PurePosixPath(name)
    require(bool(p.parts) and not p.is_absolute() and '..' not in p.parts and '\\' not in name
            and ':' not in name and p.as_posix() == name, 'Unsafe relative member: ' + name)
    return name


def read(path, base=ROOT):
    return json.loads(regular(path, base).read_bytes())


def public_file(name):
    safe_member(name)
    require(name.startswith('verification/'), 'Visual proof must be public verification evidence.')
    return regular(ROOT / name)


def proof(path):
    path = regular(path)
    return {'path': relative(path), 'sha256': sha(path), 'bytes': path.stat().st_size}


def equal_original(path, original, original_base):
    require(regular(path).read_bytes() == regular(original, original_base).read_bytes(),
            'Archive bytes differ from original: ' + str(path))


def verify_archive(manifest_sha, *, archive=None, base=None, freeze=None, attempt=None, freeze_sha=None, activation_sha=None):
    archive = ARCHIVE if archive is None else archive
    base = BASE if base is None else base
    freeze = FREEZE if freeze is None else freeze
    attempt = ATTEMPT if attempt is None else attempt
    freeze_sha = FREEZE_SHA if freeze_sha is None else freeze_sha
    activation_sha = ACTIVATION_SHA if activation_sha is None else activation_sha
    manifest_path = regular(archive / 'archive-manifest.json')
    require(sha(manifest_path) == manifest_sha, 'Explicit actual archive manifest SHA differs.')
    m = read(manifest_path)
    require(m.get('section') == 380 and m.get('actual_validation_attempt') == attempt
            and m.get('kind') == 'EXACT_FULL380_ORIGINAL_EXECUTION_ARCHIVE'
            and m.get('source_freeze_sha256') == freeze_sha and m.get('activation_sha256') == activation_sha,
            'Wrong actual380 archive identity.')
    require(m.get('required_component_positions') == 5 + len(read(freeze)['p3_scripts'])
            and m.get('all_original_ordered_components_retained') is True
            and m.get('all_executed_retained_Popen_and_assigned_jobs_terminal') is True
            and m.get('root_exit_observed_from_retained_popen') is True,
            'Complete original terminal archive required.')
    require(m.get('final_available_checks_passed_not_claimed_by_archive') is True
            and m.get('PNG_visual_inspection_claimed') is False
            and m.get('private_or_dependency_directories_traversed_or_copied') is False,
            'Archive preservation scope differs.')
    files = m['files']
    require(type(files) is dict and files, 'Nonempty complete archive required.')
    physical = set()
    for path in archive.rglob('*'):
        require(not path.is_symlink(), 'Linked archive item refused.')
        if path.is_file():
            physical.add(path.relative_to(archive).as_posix())
    require(physical == set(files) | {'archive-manifest.json'}, 'Archive file set differs from complete manifest.')
    for name, pin in files.items():
        safe_member(name)
        raw = regular(archive / name, archive).read_bytes()
        require(digest(raw) == pin['sha256'] and len(raw) == pin['bytes'], 'Archive file bytes differ: ' + name)
    once = read(base / 'full380-once.json')
    container = Path(once['container'])
    require(container.is_absolute() and container.parent == Path(tempfile.gettempdir()).resolve()
            and re.fullmatch('rouge-full380-attempt' + str(attempt) + r'-[0-9a-f]{32}', container.name)
            and not container.is_symlink() and m['raw_namespace_preserved_in_original_bytes'] == str(container)
            and once.get('section') == 380 and once.get('root_freeze_sha256') == freeze_sha
            and once.get('automatic_retry_allowed') is False and once.get('explicit_root_execute') is True,
            'Only original current380 owned namespace accepted.')
    # Every archived original is checked against its exact still-retained file.
    for name in files:
        if name == 'source-freeze.json':
            original, origin_base = freeze, ROOT
        elif name in ('activation380.json', 'full380-once.json'):
            original, origin_base = base / name, ROOT
        elif name.startswith('execution-tools/'):
            original, origin_base = base / name.removeprefix('execution-tools/'), ROOT
        elif name.startswith('executed-legacy/'):
            original, origin_base = base / 'bound-legacy' / name.removeprefix('executed-legacy/'), ROOT
        elif name.startswith('executed-current/'):
            original, origin_base = base / 'bound-current' / name.removeprefix('executed-current/'), ROOT
        elif name.startswith('root-launch/'):
            original, origin_base = base / name, ROOT
        else:
            original, origin_base = container / name, container
        equal_original(archive / name, original, origin_base)
    return m, files, container


def load_readonly_helpers():
    # The imported modules contain definitions only; do not call review(), which writes.
    require(sha(BASE / 'review_results380.py') == REVIEW_SHA, 'Original reviewer helper bytes changed.')
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(BASE))
    from full380_common import bound
    from review_results380 import terminal, closure, source_stable
    return bound, terminal, closure, source_stable




def component_argv(mode, data, container):
    shared = ['--expected-parent-commit', PARENT, '--freeze-sha256', FREEZE_SHA,
              '--activation-sha256', ACTIVATION_SHA]
    prefix = [str(ROOT / '.venv/Scripts/python.exe'), '-B', '-X', 'utf8']
    if mode == 'legacy_typed':
        return prefix + [str(BASE / 'readback_child380.py'), '--legacy-container', str(container / 'legacy'), *shared]
    return prefix + [str(BASE / 'component_child380.py'), '--mode', mode,
                     '--out', str(container / mode / 'actual'), *shared]


def target_argv(mode, data, container):
    actual = container / mode / 'actual'
    if mode == 'offline':
        target = ROOT / 'scripts/verify_full_available.py'
        return target, [str(target), '--output', str(actual / 'windows-offline.json'), '--verbosity', '2']
    if mode in ('legacy', 'current30', 'current29'):
        target = BASE / ('bound-legacy' if mode == 'legacy' else 'bound-current') / 'launcher275.py'
        return target, [str(target), '--root', str(ROOT), '--out', str(actual), '--mode', mode]
    target = ROOT / data['p3_scripts'][mode]
    argv = [str(target), '--receipt', str(actual / 'window.json')]
    options = data['p3_script_options'][mode]
    if options.get('explicit_current_source_freeze'):
        argv += ['--source-freeze', str(FREEZE)]
    if options['accepts_visible_ms'] and not options.get('use_canonical_visible_default'):
        argv += ['--visible-ms', str(options['visible_ms'])]
    return target, argv


def verify_root_and_ledger(manifest, data, container):
    process = read(ARCHIVE / 'root-launch/controller-process.json')
    require(process.get('section') == 380 and process.get('actual_validation_attempt') == ATTEMPT
            and process.get('status') == 'completed' and type(process.get('actual_observed_exit')) is int
            and process.get('owned_popen_retained') is True
            and process.get('exit_observed_directly_from_retained_popen') is True
            and process.get('exit_inferred_from_output_json') is False,
            'Original retained root Popen was not actually observed complete.')
    actual_exit = int((ARCHIVE / 'root-launch/process.exit').read_text('ascii').strip())
    require(actual_exit == process['actual_observed_exit'] == manifest['actual_root_controller_exit'] == 0
            and sha(ARCHIVE / 'root-launch/process.exit') == process['actual_process_exit_sha256'],
            'Root exit is not actual0; this builder must not seal a repaired/composite or failed attempt.')
    argv = [str(ROOT / '.venv/Scripts/python.exe'), '-B', '-X', 'utf8', str(BASE / 'run_full380_controller.py'),
            '--execute', '--expected-parent-commit', PARENT, '--freeze-sha256', FREEZE_SHA,
            '--activation-sha256', ACTIVATION_SHA]
    require(process.get('argv') == argv and process.get('wrapper_sha256') == sha(BASE / 'run_owned_full380.py')
            and process.get('automatic_retry_allowed') is False and process.get('global_process_termination') is False,
            'Retained root launch/source/no-retry provenance differs.')
    authority = read(ARCHIVE / 'owned-execution.json')
    require(authority.get('section') == 380 and authority.get('actual_validation_attempt') == ATTEMPT
            and type(process.get('controller_pid')) is int and process['controller_pid'] > 0
            and type(authority.get('controller_fixture_pid')) is int and authority['controller_fixture_pid'] > 0
            and authority.get('parent_commit') == PARENT and authority.get('root_freeze_sha256') == FREEZE_SHA
            and authority.get('activation_sha256') == ACTIVATION_SHA
            and authority.get('controller_sha256') == sha(BASE / 'run_full380_controller.py')
            and Path(authority['root']).resolve() == ROOT.resolve()
            and authority.get('game_actions') == authority.get('chat_requests') == 0
            and authority.get('private_state_copied') is False, 'Owned root/controller binding differs.')
    required = ['offline', 'legacy', 'legacy_typed', 'current30', 'current29', *data['p3_scripts']]
    require(len(required) == len(set(required)) == 5 + len(data['p3_scripts']), 'Required ordered380 positions differ.')
    ledger = read(ARCHIVE / 'orchestration.json')
    require(ledger.get('status') == 'all_required_components_terminal' and ledger.get('required_components') == required
            and [row.get('name') for row in ledger.get('steps', [])] == required
            and all(row.get('status') == 'terminal' for row in ledger['steps']),
            'Every declared original and new component must actually execute and terminate; skipped typed is not accepted.')
    review = read(ARCHIVE / 'automated-scope-review.json')
    require(review.get('automated_available_scope_passed') is True and review.get('review_failures') == []
            and review.get('available_checks_passed') is None
            and review.get('final_public_summary_requires_root_visual_review_and_seal') is True
            and review.get('scope_not_reduced') is True and review.get('root_freeze_sha256') == FREEZE_SHA
            and review.get('PNG_visual_inspection_claimed') is False
            and review.get('all_component_sources_fresh380_not_reused290_PASS') is True,
            'Original automatic review is missing, failed, altered or not fresh380.')
    require(all(ledger.get(k) == v for k, v in review.items()), 'Original ledger/review values differ.')
    require(manifest.get('automated_available_scope_passed') is True, 'Archive preserves a nonpassing automated review.')
    return process, ledger, review


def verify_components(data, container, ledger, review, terminal, closure, source_stable):
    raws, supers, proofs = {}, {}, {}
    from full380_common import canonical_frozen_inputs
    expected_sources = {**data['source_sha256'], **data['supplemental_public_inputs_sha256'], **canonical_frozen_inputs(data)}
    for row in ledger['steps']:
        mode = row['name']; folder = ARCHIVE / mode
        step = read(folder / 'step.json'); observed = read(folder / 'controller-process.json')
        require(step == row and step.get('observed') == observed, 'Original ledger/step/Popen observation differ: ' + mode)
        child = component_argv(mode, data, container)
        supervisor = terminal(folder, child, success=mode != 'current30')
        supers[mode] = supervisor
        origin = read(folder / 'process-exit-origin.json')
        require(origin.get('original_controller_pid') == read(ARCHIVE / 'owned-execution.json')['controller_fixture_pid']
                and step.get('supervisor_sha256') == sha(folder / 'supervisor.json')
                and step.get('supervisor_exit') == supervisor['supervisor_exit']
                and step.get('child_primary_exit') == supervisor['child_primary_exit']
                and step.get('timed_out') is False and type(observed.get('pid')) is int,
                'Actual step/supervisor/PID lineage differs: ' + mode)
        deadline = 5400 if mode == 'offline' else 3690 if mode == 'legacy' else 120 if mode == 'legacy_typed' else 1200
        expected_supervisor = [str(ROOT / '.venv/Scripts/python.exe'), '-B', '-X', 'utf8', str(BASE / 'supervisor380.py'),
                               '--status', str(container / mode / 'supervisor.json'), '--timeout', str(deadline), '--', *child]
        require(step['argv'] == expected_supervisor, 'Original supervisor deadline/argv differs: ' + mode)
        details = {'step': proof(folder / 'step.json'), 'controller_process': proof(folder / 'controller-process.json'),
                   'actual_exit': proof(folder / 'process.exit'), 'exit_origin': proof(folder / 'process-exit-origin.json'),
                   'supervisor': proof(folder / 'supervisor.json'), 'actual_supervisor_exit': supervisor['supervisor_exit'],
                   'actual_child_exit': supervisor['child_primary_exit'], 'owned_launcher_pid': supervisor['pid'],
                   'assigned_owned_job_empty': True, 'timed_out': False}
        if mode != 'legacy_typed':
            target, argv = target_argv(mode, data, container)
            raw, close = closure(folder, mode, FREEZE_SHA, ACTIVATION_SHA, target, argv, success=mode != 'current30')
            raws[mode] = raw
            details.update(closure=proof(folder / 'actual/full380-source-closure.json'),
                           receipt=proof(folder / 'actual' / close['actual_receipt_file']),
                           actual_fixture_exit=close['actual_fixture_exit'], actual_fixture_pid=raw.get('process_id'),
                           source_map_before_after_not_fabricated=True)
            if mode == 'offline':
                require(raw.get('source_sha256') == data['source_sha256'] and raw.get('selectors') == data['selectors']
                        and raw.get('source_drift') == [] and raw.get('failed_cases') == [] and raw.get('verbosity') == 2
                        and raw.get('platform') == 'Windows' and raw.get('wine_compatibility') is False
                        and raw.get('failures') == raw.get('errors') == 0 and raw.get('available_checks_passed') is True
                        and raw.get('qt_shutdown_error') is None, 'Actual fresh offline source/result/platform differs.')
                for key in ('tests_run', 'tests_passed', 'historical_or_declared_skips', 'unavailable_records', 'unavailable_parent_count'):
                    require(type(raw.get(key)) is int and raw[key] >= 0, 'Offline real statistic missing: ' + key)
                require(raw['tests_passed'] <= raw['tests_run'] and raw['historical_or_declared_skips'] == len(raw['skips'])
                        and raw['unavailable_records'] == len(raw['unavailable']), 'Offline raw statistics differ; do not infer tests from unavailable record count.')
                require(review['component_details']['offline'] == {k: raw[k] for k in review['component_details']['offline']},
                        'Original offline review summary differs from raw.')
            elif mode in ('legacy', 'current30', 'current29'):
                launch = read(folder / 'actual/native275-launcher-closure.json')
                require(launch.get('root_freeze_sha256') == FREEZE_SHA and launch.get('source_drift') == []
                        and launch.get('executed_tool_drift') == [] and launch.get('fixture_exception') is None
                        and launch.get('qt_cleanup_error') is None and launch.get('actual_current_native_windows_window_verified') is True
                        and raw.get('source_drift') == [], 'Actual original native launcher guard differs: ' + mode)
                details['original_launcher_closure'] = proof(folder / 'actual/native275-launcher-closure.json')
                if mode != 'legacy':
                    require(raw.get('source_freeze_sha256') == FREEZE_SHA and raw.get('frozen_source_binding_matches') is True
                            and raw.get('qt_platform') == 'windows', 'Actual current window freeze/QPA differs.')
                    source_stable(raw, data['source_sha256'])
                    old = read(ROOT / 'verification/full-290/execution-attempt2/current29/actual/window.json')
                    require(type(old.get('checks')) is list and len(old['checks']) == len(set(old['checks'])) == 29,
                            'Complete independent original29 authority changed.')
                    if mode == 'current29':
                        require(raw.get('checks') == old['checks'] and len(raw['checks']) == 29
                                and raw.get('added_section_checks') == old['added_section_checks'],
                                'Independent current29 must retain every exact original workflow in order.')
                    elif raw.get('passed') is True:
                        expected30 = old['checks'] + ['261 real MainWindow safe save and health refresh retain original dangling diagnostic entry and never create target']
                        require(raw.get('checks') == expected30 and len(raw['checks']) == 30
                                and raw.get('added_section_checks') == old['added_section_checks'] + [{'section': '261', 'name': 'real MainWindow safe save and health refresh retain original dangling diagnostic entry and never create target'}]
                                and raw.get('maintenance261_safe_save_check') is True,
                                'Successful original30 must also execute its exact final maintenance261 safe-save workflow.')
                    else:
                        require(raw.get('checks') == old['checks'] and len(raw['checks']) == 29
                                and raw.get('added_section_checks') == old['added_section_checks']
                                and raw.get('maintenance261_safe_save_check') is not True,
                                'Failed original30 must retain the exact29 prefix; only the separate exact1314 classifier may call it unavailable.')
            else:
                expected = {name: expected_sources[name] for name in data['p3_script_selected_paths'][mode]}
                source_stable(raw, expected, original287=mode == 'p3_287', canonical_mode=mode)
                details['selected_source_count'] = len(expected)
                details['checks'] = raw.get('unique_checks', raw.get('completed_check_count', len(raw.get('checks', []))))
                original_detail = review['component_details'][mode]
                require(original_detail['receipt_sha256'] == close['actual_receipt_sha256']
                        and original_detail['actual_fixture_pid'] == raw.get('process_id')
                        and original_detail['owned_launcher_pid'] == supervisor['pid']
                        and original_detail['source_count'] == len(expected)
                        and original_detail['checks'] == details['checks'], 'P3 review/raw identity differs: ' + mode)
                if mode == 'p3_287':
                    old = read(ROOT / 'verification/full-290/p3-supplementary-attempt2/p3_287/actual/p3-window.json')
                    require(raw.get('checks') == old['checks'] and raw.get('game_captures') == raw.get('chat_sends') == 0
                            and raw.get('private_state_loaded') is False and raw.get('qt_exit_code') == 0
                            and len(raw.get('stages', [])) == 2
                            and all(type(x.get('hwnd')) is int and x['hwnd'] > 0 for x in raw['stages']), 'Original287 actual scope differs.')
                    details['original287_single_source_map_and_absent_PID_preserved'] = 'process_id' not in raw
                elif int(mode.split('_')[1]) <= 312:
                    require(raw.get('qpa') == 'windows' and raw.get('qt_exit_code') == 0 and type(raw.get('process_id')) is int
                            and raw.get('game_captures') == 0 and raw.get('game_operated') is False and raw.get('chat_sent') is False
                            and (raw.get('state_paths_replaced_before_constructor') is True
                                 or raw.get('state_paths_replaced_before_constructor') == ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE']),
                            'Native supplement state/exit/external scope differs: ' + mode)
                else:
                    calls = raw.get('external_operation_attempts')
                    require(raw.get('qpa') == 'windows' and raw.get('qt_exit_code') == 0 and type(raw.get('process_id')) is int
                            and raw.get('game_operated') is False and raw.get('chat_sent') is False
                            and raw.get('verification_window_closed') is True and raw.get('temporary_state') is True
                            and raw.get('private_contents_read_copied_or_restored') is False
                            and type(calls) is dict and len(calls) == 7 and all(type(x) is int and x == 0 for x in calls.values()),
                            'Current supplement native/private/external scope differs: ' + mode)
        proofs[mode] = details
    return raws, supers, proofs


def verify_typed(data, review, container):
    folder = ARCHIVE / 'legacy'
    invocation = read(folder / 'full380-typed-audit-invocation.json')
    audit_path = folder / 'independent-saved-readback-audit.json'; audit = read(audit_path)
    script = BASE / 'bound-legacy/audit_full261_saved_readback.py'
    require(invocation.get('section') == 380 and invocation.get('kind') == 'ORIGINAL_COMPLETE_TYPED_AUDITOR_ACTUAL_INVOCATION'
            and invocation.get('actual_auditor_exit') == 0 and invocation.get('passed') is True
            and invocation.get('root_freeze_sha256') == FREEZE_SHA and invocation.get('original_raw_labels_preserved') is True
            and invocation.get('actual_audit_sha256') == sha(audit_path)
            and invocation.get('original_source_sha256') == data['original_typed_auditor_sha256'] == sha(script)
            and invocation.get('argv') == [str(script), '--root', str(ROOT), '--container', str(container / 'legacy'),
                                          '--bundle', str(BASE / 'bound-legacy'), '--freeze', str(FREEZE)], 'Original complete typed invocation differs.')
    require(audit.get('passed') is True and audit.get('process_exit') == audit.get('child_primary_exit') == audit.get('supervisor_exit') == 0
            and audit.get('timeout') is False and audit.get('complete_runtime_checks') == 4283 and audit.get('saved_rows') == 52
            and audit.get('passed_flag_records') == 4281 and audit.get('metadata_records') == 2
            and audit.get('current_revised_assertions') == 862 and audit.get('original_assertions_outside_two_helpers') == 807
            and audit.get('readonly_trace_empty_rows_not_invented') == 26
            and audit.get('exact_ten_admission_indices') == [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]
            and audit.get('original552_maintry_sha256') == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'
            and audit.get('source_and_additional_drift') == [] and audit.get('codec_exact_typed_roundtrip') is True
            and audit.get('codec_plain_JSON_order_and_values_match') is True
            and audit.get('exact_ten_identity_types_input_and_full_row_hash_match') is True,
            'Complete original typed audit scope differs; no reduced audit allowed.')
    raw = (folder / 'actual/wine-ui-new-states-100.json.gz').read_bytes(); decoded = gzip.decompress(raw)
    state = json.loads(decoded); rows = state['actual_new_window_states']
    require(digest(raw) == audit['compressed_archive_sha256'] and digest(decoded) == audit['decoded_archive_sha256']
            and state.get('passed') is True and state.get('actual_main_window_execution_only') is True
            and state.get('expected_UI_state_rows') == len(rows) == len(audit['rows']) == 52
            and Counter(row['section'] for row in rows) == {86: 44, 88: 8}
            and len({(r['section'], r['pair_id'], r['widget_checked']) for r in rows}) == 52
            and all(row.get('passed') is True and row.get('explicit_three_text_requests') == 3 for row in rows),
            'Actual52 saved states/typed archive binding differs.')
    details = review['component_details']['legacy']
    require(details.get('audit_sha256') == sha(audit_path) and details.get('explicit_three_text_requests') == 156
            and details.get('original_projection_scope') == 42 and details.get('all_original552_body_preserved') is True
            and details.get('actual_original_typed_exit') == 0, 'Original typed review scope differs.')
    return {'audit': proof(audit_path), 'invocation': proof(folder / 'full380-typed-audit-invocation.json'),
            'actual_complete_scope': details, 'archive': proof(folder / 'actual/wine-ui-new-states-100.json.gz'),
            'original_raw_historical_labels_preserved': True, 'auditor_reexecuted_by_sealer': False}


def verify_current30(raws, supers, proofs, review):
    raw = raws['current30']; sup = supers['current30']; fixture_exit = proofs['current30']['actual_fixture_exit']
    require(raws['current29'].get('passed') is True and supers['current29']['child_primary_exit'] == 0,
            'Independent original29 did not actually pass.')
    passed = raw.get('passed') is True
    unavailable = False
    if passed:
        require(sup['supervisor_exit'] == sup['child_primary_exit'] == fixture_exit == 0,
                'Passed30 raw flag without actual0 exits.')
    else:
        failure = raw.get('failure') or {}; message = failure.get('message', ''); trace = failure.get('traceback', '')
        unavailable = (failure.get('type') == 'OSError' and '[WinError 1314]' in message
                       and 'public-261-never-create.txt' in message and 'diagnostic.symlink_to(public_target.name)' in trace
                       and 'pathlib.py' in trace and 'os.symlink(' in trace
                       and sup['child_primary_exit'] == sup['supervisor_exit'] == fixture_exit == 1)
        require(unavailable, 'Fresh original30 has a real failure other than exact1314; do not seal PASS.')
    require(review.get('current30_original_actual_symlink_prerequisite_unavailable') is unavailable,
            'Original current30 review classification differs.')
    return {'maintained_scope': 'Original30 execution and separate complete original29 execution, both retained.',
            'actual_full30_attempt_preserved': True, 'full30_raw_passed': passed,
            'full30_actual_exit': sup['child_primary_exit'], 'current29_actual_exit': supers['current29']['child_primary_exit'],
            'available_original_workflows_passed': True,
            'available_original_workflow_count': 30 if passed else 29,
            'workflow_count_does_not_add_independent29_to_original30': True,
            'original_symlink_operation_passed': passed,
            'original_symlink_prerequisite_unavailable': unavailable,
            'unavailable_reason': raw.get('failure') if unavailable else None,
            'current30': proofs['current30'], 'current29': proofs['current29']}


def verify_functional(data, source_stable):
    require(set(data['functional_validation']) == {'necessary', 'native', 'native_process'}, 'Exactly3 original functional380 receipts required.')
    docs = {}
    union = {**data['source_sha256'], **data['supplemental_public_inputs_sha256']}
    for name, ref in data['functional_validation'].items():
        path = public_file(ref['path']); require(sha(path) == ref['sha256'], 'Functional380 original changed.')
        doc = read(path); docs[name] = doc
        require(doc.get('section') == 380 and doc.get('passed') is True, 'Functional380 did not pass: ' + name)
        before = doc.get('source_sha256_before'); after = doc.get('source_sha256_after')
        require(type(before) is dict and before == after and before, 'Functional selected source map differs.')
        source_stable(doc, {key: union[key] for key in before})
    necessary, native, process = docs['necessary'], docs['native'], docs['native_process']
    require(necessary.get('actual_observed_exit') == necessary.get('exit_code') == 0
            and necessary.get('source_unchanged') is True and type(necessary.get('methods_ran')) is int and necessary.get('methods_ran') > 0
            and type(necessary.get('retained_popen_pid')) is int, 'Functional380 necessary observation differs.')
    require(process.get('actual_observed_exit') == process.get('exit_code') == 0
            and process.get('source_unchanged') is True and process.get('window_passed') is True
            and process.get('window_receipt') == data['functional_validation']['native']['path']
            and process.get('window_receipt_sha256') == data['functional_validation']['native']['sha256']
            and process.get('actual_fixture_pid') == native.get('process_id')
            and process.get('PID_equality_assumed') is False and type(process.get('retained_popen_pid')) is int,
            'Functional380 native retained observation differs.')
    calls = native.get('external_operation_attempts')
    require(native.get('failure') is None and native.get('qpa') == 'windows' and native.get('qt_exit_code') == 0
            and native.get('verification_window_closed') is True and type(native.get('unique_checks')) is int and native.get('unique_checks') > 0
            and len(native['screenshots']) > 0 and native.get('temporary_state') is True
            and native.get('private_contents_read_copied_or_restored') is False
            and native.get('game_operated') is False and native.get('chat_sent') is False
            and type(calls) is dict and len(calls) == 7 and all(type(x) is int and x == 0 for x in calls.values()),
            'Functional380 actual native scope differs.')
    require(type(native.get('checks')) is list and native['unique_checks'] == len(set(native['checks']))
            and len({image['path'] for image in native['screenshots']}) == len(native['screenshots']),
            'Actual functional checks and screenshot path count differ.')
    for image in native['screenshots']:
        path = regular(Path(image['path']))
        require(path.parent == (ROOT / data['functional_validation']['native']['path']).parent
                and path.suffix == '.png' and sha(path) == image['sha256'], 'Original functional380 screenshot bytes differ.')
    return {'references': data['functional_validation'], 'necessary_tests_run': necessary['methods_ran'],
            'native_unique_checks': native['unique_checks'], 'native_images': len(native['screenshots']),
            'separate_functional_scope_not_added_to_full_counts': True}


def pin_public(name, expected):
    path = public_file(name); require(sha(path) == expected, 'Public proof bytes differ: ' + name)
    return path


def leaf_rows(document):
    """Only explicit final direct-review rows; never infer review from a PNG path."""
    require(type(document) is dict and type(document.get('images')) is list, 'Actual direct proof must have images rows.')
    return document['images']


# BEGIN EXACT FULL380 HISTORICAL SCHEMA COMPATIBILITY
"""Exact historical full380 schema compatibility only; no execution, views or evidence rewrite.
This source is embedded verbatim into a NEW revision2 sealer by the guarded generator.
It is not imported by or applied to the original frozen sealer.
"""
import json as _full380_history_json
from hashlib import sha256 as _full380_history_sha256

_FULL380_HISTORICAL_LEAF_SPECS = [{'proof': 'verification/sections/323-root-visual.json', 'proof_sha256': '91dc9131c1f6f1e1f772fedc4a7393a5f4d869e0b3d8c5ea7b5619d43853ecc1', 'row_pointer': ['final_screenshot_reviews', 5], 'item': {'proof': 'verification/sections/323-root-visual.json', 'proof_sha256': '91dc9131c1f6f1e1f772fedc4a7393a5f4d869e0b3d8c5ea7b5619d43853ecc1', 'row': ['final_screenshot_reviews', 5], 'png': 'verification/sections/323-native-attempt2/actual/window-source-loss-cleared.png', 'png_sha256': '4e5dc970a5335257ed00bb335b36d8a99546ac571ec55ffad5882ce588646352', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/323-native-attempt1/actual/window-source-loss-cleared.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'root row byte_equal_to_directly_viewed_initial=True; initial exact native screenshot receipt verification/sections/323-native-attempt1/actual/window.json', 'initial_native_receipt': {'path': 'verification/sections/323-native-attempt1/actual/window.json', 'sha256': 'e3b4cd776affaa593f021ab9439b7a0f5bf074149ca6e7be0b33ab1bf2c384ab'}}, 'item_sha256': '623488c2b6be6a51aded3a00190f0950b86a01c63c81dbf1d00ccf577d29c344', 'row': {'file': 'verification/sections/323-native-attempt2/actual/window-source-loss-cleared.png', 'sha256': '4e5dc970a5335257ed00bb335b36d8a99546ac571ec55ffad5882ce588646352', 'final_directly_viewed': False, 'byte_equal_to_directly_viewed_initial': True, 'initial_receipt': 'verification/sections/323-native-attempt1/actual/window.json'}, 'row_sha256': '432325367a55b7955049c6ad2404a3d48154bbe57d56d4294190f153c7c9efdb', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/323-native-attempt1/actual/window-source-loss-cleared.png', 'leaf_proof': 'verification/sections/323-root-visual.json', 'leaf_proof_sha256': '91dc9131c1f6f1e1f772fedc4a7393a5f4d869e0b3d8c5ea7b5619d43853ecc1'}, 'png_sha256': '4e5dc970a5335257ed00bb335b36d8a99546ac571ec55ffad5882ce588646352', 'png_bytes': 59895, 'section': 323, 'scope_original': {'section': 323, 'passed': True, 'scope': 'Five changed final widget PNGs individually viewed, one byte-identical final PNG linked to directly viewed initial pixels; visual presentation only.', 'native_receipt': 'verification/sections/323-native-attempt2/actual/window.json'}, 'extra_native_receipt': {'file': 'verification/sections/323-native-attempt1/actual/window.json', 'sha256': 'e3b4cd776affaa593f021ab9439b7a0f5bf074149ca6e7be0b33ab1bf2c384ab', 'row_pointer': ['screenshots', 5], 'row_sha256': '03623adf1c818c9651cf5f89acfbf03d7e08b25897735bc8edc3acdb98676c41'}}, {'proof': 'verification/sections/325-root-visual.json', 'proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3', 'row_pointer': ['final_screenshot_reviews', 1], 'item': {'proof': 'verification/sections/325-root-visual.json', 'proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3', 'row': ['final_screenshot_reviews', 1], 'png': 'verification/sections/325-native-attempt3/actual/window-49-gold-unmet.png', 'png_sha256': 'fcb04c32e1bb8de816d33c34f4a7ef3799d4ea66de88efd83559e984dc38b0a8', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/325-native-attempt2/actual/window-49-gold-unmet.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'root row explicitly earlier directly viewed attempt2; same exact basename/path of attempt2'}, 'item_sha256': '9791d7382f6b949c9fe9cb4792ad847d1206edffa2f8fd1ffa37ec2ece0ceada', 'row': {'name': '49-gold-unmet', 'path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\325-native-attempt3\\actual\\window-49-gold-unmet.png', 'sha256': 'fcb04c32e1bb8de816d33c34f4a7ef3799d4ea66de88efd83559e984dc38b0a8', 'native': {'hwnd': 1838882, 'pid': 39400, 'size': [1220, 850]}, 'pixel_file_byte_equal_previous_attempt2': True, 'viewed_directly_this_turn': False, 'earlier_directly_viewed_attempt2': True}, 'row_sha256': 'd83fa2172aa8015da4f40791ba0e52d2cabecce097eeb799f823ef14e279906f', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/325-native-attempt2/actual/window-49-gold-unmet.png', 'leaf_proof': 'verification/sections/325-root-visual.json', 'leaf_proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3'}, 'png_sha256': 'fcb04c32e1bb8de816d33c34f4a7ef3799d4ea66de88efd83559e984dc38b0a8', 'png_bytes': 151731, 'section': 325, 'scope_original': {'section': 325, 'passed': True, 'review': 'Chinese optional reference controls, clear cost/reward/status grouping, historical context separate, related map exact, unavailable content cleared. No raw identifiers in default event reading.'}}, {'proof': 'verification/sections/325-root-visual.json', 'proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3', 'row_pointer': ['final_screenshot_reviews', 3], 'item': {'proof': 'verification/sections/325-root-visual.json', 'proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3', 'row': ['final_screenshot_reviews', 3], 'png': 'verification/sections/325-native-attempt3/actual/window-history-reference.png', 'png_sha256': '2f5e29f89a588b188293f98fe1b195f44f510d55b4168583582195a9678000f7', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/325-native-attempt2/actual/window-history-reference.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'root row explicitly earlier directly viewed attempt2; same exact basename/path of attempt2'}, 'item_sha256': 'dc5162bd3185ef58f9180e65cfaed947c6308f46291181c5e2e9c7b84d11af03', 'row': {'name': 'history-reference', 'path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\325-native-attempt3\\actual\\window-history-reference.png', 'sha256': '2f5e29f89a588b188293f98fe1b195f44f510d55b4168583582195a9678000f7', 'native': {'hwnd': 1838882, 'pid': 39400, 'size': [1220, 850]}, 'pixel_file_byte_equal_previous_attempt2': True, 'viewed_directly_this_turn': False, 'earlier_directly_viewed_attempt2': True}, 'row_sha256': '1710cd8ce49254fcbebda483dc174d554cdccfabbef33703ce9b519af0ecfbac', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/325-native-attempt2/actual/window-history-reference.png', 'leaf_proof': 'verification/sections/325-root-visual.json', 'leaf_proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3'}, 'png_sha256': '2f5e29f89a588b188293f98fe1b195f44f510d55b4168583582195a9678000f7', 'png_bytes': 152078, 'section': 325, 'scope_original': {'section': 325, 'passed': True, 'review': 'Chinese optional reference controls, clear cost/reward/status grouping, historical context separate, related map exact, unavailable content cleared. No raw identifiers in default event reading.'}}, {'proof': 'verification/sections/325-root-visual.json', 'proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3', 'row_pointer': ['final_screenshot_reviews', 0], 'item': {'proof': 'verification/sections/325-root-visual.json', 'proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3', 'row': ['final_screenshot_reviews', 0], 'png': 'verification/sections/325-native-attempt3/actual/window-informer-alpha.png', 'png_sha256': '75518e969240102505594fe379876f7d6ed0e7d5259135e8dadd9b1173bf6155', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/325-native-attempt2/actual/window-informer-alpha.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'root row explicitly earlier directly viewed attempt2; same exact basename/path of attempt2'}, 'item_sha256': '8f35e796146aa692a2ced86137dd921f6e50a368900aff18d6c856c601fcd4f9', 'row': {'name': 'informer-alpha', 'path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\325-native-attempt3\\actual\\window-informer-alpha.png', 'sha256': '75518e969240102505594fe379876f7d6ed0e7d5259135e8dadd9b1173bf6155', 'native': {'hwnd': 1838882, 'pid': 39400, 'size': [1220, 850]}, 'pixel_file_byte_equal_previous_attempt2': True, 'viewed_directly_this_turn': False, 'earlier_directly_viewed_attempt2': True}, 'row_sha256': 'c8ce986c9b387e6146f04d9d8c57d43c94536fe00cf088ef174f85bf087b04c6', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/325-native-attempt2/actual/window-informer-alpha.png', 'leaf_proof': 'verification/sections/325-root-visual.json', 'leaf_proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3'}, 'png_sha256': '75518e969240102505594fe379876f7d6ed0e7d5259135e8dadd9b1173bf6155', 'png_bytes': 158778, 'section': 325, 'scope_original': {'section': 325, 'passed': True, 'review': 'Chinese optional reference controls, clear cost/reward/status grouping, historical context separate, related map exact, unavailable content cleared. No raw identifiers in default event reading.'}}, {'proof': 'verification/sections/325-root-visual.json', 'proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3', 'row_pointer': ['final_screenshot_reviews', 2], 'item': {'proof': 'verification/sections/325-root-visual.json', 'proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3', 'row': ['final_screenshot_reviews', 2], 'png': 'verification/sections/325-native-attempt3/actual/window-random-relic.png', 'png_sha256': 'acf66747bf4712ab4cb0f4bc3d2ae0617ef743e2b0789a06780f38080b712da1', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/325-native-attempt2/actual/window-random-relic.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'root row explicitly earlier directly viewed attempt2; same exact basename/path of attempt2'}, 'item_sha256': 'f43663a71abed03a3b0c5e5fad29a78911e4fac55b27a8ea0f27db2bf4f975ae', 'row': {'name': 'random-relic', 'path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\325-native-attempt3\\actual\\window-random-relic.png', 'sha256': 'acf66747bf4712ab4cb0f4bc3d2ae0617ef743e2b0789a06780f38080b712da1', 'native': {'hwnd': 1838882, 'pid': 39400, 'size': [1220, 850]}, 'pixel_file_byte_equal_previous_attempt2': True, 'viewed_directly_this_turn': False, 'earlier_directly_viewed_attempt2': True}, 'row_sha256': 'ca53d9b3a21a091130f1629f01276e231278fcb8b2094644bb259605f16736e0', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/325-native-attempt2/actual/window-random-relic.png', 'leaf_proof': 'verification/sections/325-root-visual.json', 'leaf_proof_sha256': 'f0da18421da1bbaff2d995aaace8511a32bf26964ada89539ad727d9db32aee3'}, 'png_sha256': 'acf66747bf4712ab4cb0f4bc3d2ae0617ef743e2b0789a06780f38080b712da1', 'png_bytes': 160593, 'section': 325, 'scope_original': {'section': 325, 'passed': True, 'review': 'Chinese optional reference controls, clear cost/reward/status grouping, historical context separate, related map exact, unavailable content cleared. No raw identifiers in default event reading.'}}, {'proof': 'verification/sections/327-root-visual.json', 'proof_sha256': '2b177969e321b8969ec15c402858a7b1737d7beaa52830cc2d02ea9548a261ab', 'row_pointer': ['final_screenshot_reviews', 3], 'item': {'proof': 'verification/sections/327-root-visual.json', 'proof_sha256': '2b177969e321b8969ec15c402858a7b1737d7beaa52830cc2d02ea9548a261ab', 'row': ['final_screenshot_reviews', 3], 'png': 'verification/sections/327-native-attempt2/actual/window-source-loss.png', 'png_sha256': '86549c9208d13bcc09b6436f95b40b75dd5201af86a0527a03514361df01b3d8', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/327-native-attempt1/actual/window-source-loss.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'root row explicitly identifies already directly viewed first-attempt source-loss PNG'}, 'item_sha256': 'ee25dea2266cd72161d18904f8304353038e9a2548c5ea7492b2897d3bc5f54f', 'row': {'name': 'source-loss', 'path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\327-native-attempt2\\actual\\window-source-loss.png', 'sha256': '86549c9208d13bcc09b6436f95b40b75dd5201af86a0527a03514361df01b3d8', 'native': {'hwnd': 2425260, 'pid': 17780, 'size': [1220, 850]}, 'review': 'Byte equal to already directly viewed first-attempt source-loss PNG'}, 'row_sha256': '56fa87ea9d298565780694838cb0a8d63c787e580af69183c3f60c5b7b7c25a3', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/327-native-attempt1/actual/window-source-loss.png', 'leaf_proof': 'verification/sections/327-root-visual.json', 'leaf_proof_sha256': '2b177969e321b8969ec15c402858a7b1737d7beaa52830cc2d02ea9548a261ab'}, 'png_sha256': '86549c9208d13bcc09b6436f95b40b75dd5201af86a0527a03514361df01b3d8', 'png_bytes': 33688, 'section': 327, 'scope_original': {'section': 327, 'passed': True, 'review': 'Five unique changed final PNGs directly viewed. Two others byte-equal to already directly viewed PNGs. Ordinary-player wording, relevant-only tool control, variants not duplicate deductions, half-gold unknown and linked dialogue are legible.'}}, {'proof': 'verification/sections/331-root-visual.json', 'proof_sha256': '33b5e41c0a3b0fcc6fd07f929404e5e2107fae561790d15bda647139754fa2b9', 'row_pointer': ['final_screenshot_reviews', 7], 'item': {'proof': 'verification/sections/331-root-visual.json', 'proof_sha256': '33b5e41c0a3b0fcc6fd07f929404e5e2107fae561790d15bda647139754fa2b9', 'row': ['final_screenshot_reviews', 7], 'png': 'verification/sections/331-native-attempt2/actual/window-source-loss.png', 'png_sha256': '50897bdccf780adad2e87687b03dd9797ba36120b0779eee24368bcb08fe62cf', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/331-native-attempt1/actual/window-source-loss.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'explicit directly viewed initial path in root row'}, 'item_sha256': '46a96a2052fe82521f97a7d8958fdccd638566f6e95d4a7035da7cf9df3739dd', 'row': {'name': 'source-loss', 'path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\331-native-attempt2\\actual\\window-source-loss.png', 'sha256': '50897bdccf780adad2e87687b03dd9797ba36120b0779eee24368bcb08fe62cf', 'native': {'hwnd': 18681668, 'pid': 43060, 'size': [1220, 850]}, 'review': 'Byte identical to already directly viewed initial actual PNG', 'directly_viewed_initial_path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\331-native-attempt1\\actual\\window-source-loss.png', 'identical_sha256': '50897bdccf780adad2e87687b03dd9797ba36120b0779eee24368bcb08fe62cf'}, 'row_sha256': '1e0469e635984e72a8e0d5a09e89b809cee6671e6e6bc2da9900f6a6db7dcafe', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/331-native-attempt1/actual/window-source-loss.png', 'leaf_proof': 'verification/sections/331-root-visual.json', 'leaf_proof_sha256': '33b5e41c0a3b0fcc6fd07f929404e5e2107fae561790d15bda647139754fa2b9'}, 'png_sha256': '50897bdccf780adad2e87687b03dd9797ba36120b0779eee24368bcb08fe62cf', 'png_bytes': 30522, 'section': 331, 'scope_original': {'section': 331, 'passed': True, 'six_final_PNGs_directly_viewed_two_identical_to_viewed_initial': True, 'ordinary_player_text_reviewed': True, 'internal_parent_relation_wording_removed': True, 'screenshots_do_not_prove_current_game_eligibility': True}}, {'proof': 'verification/sections/331-root-visual.json', 'proof_sha256': '33b5e41c0a3b0fcc6fd07f929404e5e2107fae561790d15bda647139754fa2b9', 'row_pointer': ['final_screenshot_reviews', 6], 'item': {'proof': 'verification/sections/331-root-visual.json', 'proof_sha256': '33b5e41c0a3b0fcc6fd07f929404e5e2107fae561790d15bda647139754fa2b9', 'row': ['final_screenshot_reviews', 6], 'png': 'verification/sections/331-native-attempt2/actual/window-travel-decline-confirmation.png', 'png_sha256': '23f310759f2fadfad31cee78ac9752a2d720a5ecc4d6d4d4e5ea11647fb115b5', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/331-native-attempt1/actual/window-travel-decline-confirmation.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'explicit directly viewed initial path in root row'}, 'item_sha256': 'c5c7296ec3e1e69ccb99ed0b97f1be0b5b14ccfc9b932e730fb41b80b82de743', 'row': {'name': 'travel-decline-confirmation', 'path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\331-native-attempt2\\actual\\window-travel-decline-confirmation.png', 'sha256': '23f310759f2fadfad31cee78ac9752a2d720a5ecc4d6d4d4e5ea11647fb115b5', 'native': {'hwnd': 18681668, 'pid': 43060, 'size': [1220, 850]}, 'review': 'Byte identical to already directly viewed initial actual PNG', 'directly_viewed_initial_path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\331-native-attempt1\\actual\\window-travel-decline-confirmation.png', 'identical_sha256': '23f310759f2fadfad31cee78ac9752a2d720a5ecc4d6d4d4e5ea11647fb115b5'}, 'row_sha256': 'b39d796a460c0b78fb50ba26ec15dbaf9c76c8e49c6ef7f2b69d29cb2744465a', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/331-native-attempt1/actual/window-travel-decline-confirmation.png', 'leaf_proof': 'verification/sections/331-root-visual.json', 'leaf_proof_sha256': '33b5e41c0a3b0fcc6fd07f929404e5e2107fae561790d15bda647139754fa2b9'}, 'png_sha256': '23f310759f2fadfad31cee78ac9752a2d720a5ecc4d6d4d4e5ea11647fb115b5', 'png_bytes': 51989, 'section': 331, 'scope_original': {'section': 331, 'passed': True, 'six_final_PNGs_directly_viewed_two_identical_to_viewed_initial': True, 'ordinary_player_text_reviewed': True, 'internal_parent_relation_wording_removed': True, 'screenshots_do_not_prove_current_game_eligibility': True}}, {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row_pointer': ['final_screenshot_reviews', 4], 'item': {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row': ['final_screenshot_reviews', 4], 'png': 'verification/sections/341-native-attempt3/actual/window-fog-橙雾.png', 'png_sha256': '6e877dd9150f500a7a09748a64e4dd1e941dc3ce3258f26f4163bbc44dae782d', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/341-native-attempt2/actual/window-fog-橙雾.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': '916341adcf32f3eec3f6c9a52ae15a2dd4f9dae27cf8d7478c41b26772a5098d', 'row': {'name': 'fog-橙雾', 'receipt_image': 'verification/sections/341-native-attempt3/actual/window-fog-橙雾.png', 'sha256': '6e877dd9150f500a7a09748a64e4dd1e941dc3ce3258f26f4163bbc44dae782d', 'directly_viewed_by_root': False, 'review_reused_from': 'verification/sections/341-native-attempt2/actual/window-fog-橙雾.png', 'whole_PNG_byte_identical': True, 'previous_direct_review': True}, 'row_sha256': 'ffb41dd2c8ca8cc8a34bf268057b3728027e37bbd98bd1c1e07c59a9a040cbe5', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/341-native-attempt2/actual/window-fog-橙雾.png', 'leaf_proof': 'verification/sections/341-root-visual.json', 'leaf_proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9'}, 'png_sha256': '6e877dd9150f500a7a09748a64e4dd1e941dc3ce3258f26f4163bbc44dae782d', 'png_bytes': 107162, 'section': 341, 'scope_original': {'section': 341, 'passed': True, 'review_scope': 'Final confirmation directly viewed by root; other eight full PNG bytes identical to all directly reviewed attempt2 images. No current game/server/teleport claim.', 'at_utc': '2026-10-22T02:47:10.876582+00:00'}}, {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row_pointer': ['final_screenshot_reviews', 5], 'item': {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row': ['final_screenshot_reviews', 5], 'png': 'verification/sections/341-native-attempt3/actual/window-fog-紫雾.png', 'png_sha256': 'bd6633249a6835193148b2f808e7db1ba780c648401a581fdddb7665f7cd34fa', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/341-native-attempt2/actual/window-fog-紫雾.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': 'be4dd9637601bf730b2293b11834432c9836854cb8ebb28e306df2b997e450b9', 'row': {'name': 'fog-紫雾', 'receipt_image': 'verification/sections/341-native-attempt3/actual/window-fog-紫雾.png', 'sha256': 'bd6633249a6835193148b2f808e7db1ba780c648401a581fdddb7665f7cd34fa', 'directly_viewed_by_root': False, 'review_reused_from': 'verification/sections/341-native-attempt2/actual/window-fog-紫雾.png', 'whole_PNG_byte_identical': True, 'previous_direct_review': True}, 'row_sha256': '7e57fcbe181014919c7d4a97aaefadd97c533fc56f76afa65474b3261915ec07', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/341-native-attempt2/actual/window-fog-紫雾.png', 'leaf_proof': 'verification/sections/341-root-visual.json', 'leaf_proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9'}, 'png_sha256': 'bd6633249a6835193148b2f808e7db1ba780c648401a581fdddb7665f7cd34fa', 'png_bytes': 106847, 'section': 341, 'scope_original': {'section': 341, 'passed': True, 'review_scope': 'Final confirmation directly viewed by root; other eight full PNG bytes identical to all directly reviewed attempt2 images. No current game/server/teleport claim.', 'at_utc': '2026-10-22T02:47:10.876582+00:00'}}, {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row_pointer': ['final_screenshot_reviews', 0], 'item': {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row': ['final_screenshot_reviews', 0], 'png': 'verification/sections/341-native-attempt3/actual/window-fog-红雾.png', 'png_sha256': '94a86696a805492eefce5cb42fa57c23c2682c34bc56841c73f758069ea5c300', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/341-native-attempt2/actual/window-fog-红雾.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': '5ad508f2f417b6c18abe0957c6e10d3fd8f4d33fb79ff6dd42863b56386fe6e3', 'row': {'name': 'fog-红雾', 'receipt_image': 'verification/sections/341-native-attempt3/actual/window-fog-红雾.png', 'sha256': '94a86696a805492eefce5cb42fa57c23c2682c34bc56841c73f758069ea5c300', 'directly_viewed_by_root': False, 'review_reused_from': 'verification/sections/341-native-attempt2/actual/window-fog-红雾.png', 'whole_PNG_byte_identical': True, 'previous_direct_review': True}, 'row_sha256': '2b9d327d05c8302eb7c283159fd750fcc6cbba9ab81063ffdf1b086b9a86687b', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/341-native-attempt2/actual/window-fog-红雾.png', 'leaf_proof': 'verification/sections/341-root-visual.json', 'leaf_proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9'}, 'png_sha256': '94a86696a805492eefce5cb42fa57c23c2682c34bc56841c73f758069ea5c300', 'png_bytes': 106196, 'section': 341, 'scope_original': {'section': 341, 'passed': True, 'review_scope': 'Final confirmation directly viewed by root; other eight full PNG bytes identical to all directly reviewed attempt2 images. No current game/server/teleport claim.', 'at_utc': '2026-10-22T02:47:10.876582+00:00'}}, {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row_pointer': ['final_screenshot_reviews', 2], 'item': {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row': ['final_screenshot_reviews', 2], 'png': 'verification/sections/341-native-attempt3/actual/window-fog-绿雾.png', 'png_sha256': '0f4b76537927847631718f9cf6082bb9e897ef89bbad300d982d3e2cd44f5bc0', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/341-native-attempt2/actual/window-fog-绿雾.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': 'c203b94ce0e77b8fc32fe32cc2f20675714ccdb8b112ed74454086e857946090', 'row': {'name': 'fog-绿雾', 'receipt_image': 'verification/sections/341-native-attempt3/actual/window-fog-绿雾.png', 'sha256': '0f4b76537927847631718f9cf6082bb9e897ef89bbad300d982d3e2cd44f5bc0', 'directly_viewed_by_root': False, 'review_reused_from': 'verification/sections/341-native-attempt2/actual/window-fog-绿雾.png', 'whole_PNG_byte_identical': True, 'previous_direct_review': True}, 'row_sha256': '871457afd3e1bc07d689c5894e0e89c581f11a7370b2dd54cc3c805801206d00', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/341-native-attempt2/actual/window-fog-绿雾.png', 'leaf_proof': 'verification/sections/341-root-visual.json', 'leaf_proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9'}, 'png_sha256': '0f4b76537927847631718f9cf6082bb9e897ef89bbad300d982d3e2cd44f5bc0', 'png_bytes': 116236, 'section': 341, 'scope_original': {'section': 341, 'passed': True, 'review_scope': 'Final confirmation directly viewed by root; other eight full PNG bytes identical to all directly reviewed attempt2 images. No current game/server/teleport claim.', 'at_utc': '2026-10-22T02:47:10.876582+00:00'}}, {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row_pointer': ['final_screenshot_reviews', 1], 'item': {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row': ['final_screenshot_reviews', 1], 'png': 'verification/sections/341-native-attempt3/actual/window-fog-蓝雾.png', 'png_sha256': '4ddff92890ca9bae018ed39fd0f3fd08d15abfc509e1528aa60eb0032724da00', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/341-native-attempt2/actual/window-fog-蓝雾.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': '5b5e08a88e73d90fde6dbce3d61f1355669d910e24e0190fabb8e829fd25f325', 'row': {'name': 'fog-蓝雾', 'receipt_image': 'verification/sections/341-native-attempt3/actual/window-fog-蓝雾.png', 'sha256': '4ddff92890ca9bae018ed39fd0f3fd08d15abfc509e1528aa60eb0032724da00', 'directly_viewed_by_root': False, 'review_reused_from': 'verification/sections/341-native-attempt2/actual/window-fog-蓝雾.png', 'whole_PNG_byte_identical': True, 'previous_direct_review': True}, 'row_sha256': 'd5daef54e4693782143b33de95377c1c4a2e51467b5b4822f2a2c2e8f928083f', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/341-native-attempt2/actual/window-fog-蓝雾.png', 'leaf_proof': 'verification/sections/341-root-visual.json', 'leaf_proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9'}, 'png_sha256': '4ddff92890ca9bae018ed39fd0f3fd08d15abfc509e1528aa60eb0032724da00', 'png_bytes': 106736, 'section': 341, 'scope_original': {'section': 341, 'passed': True, 'review_scope': 'Final confirmation directly viewed by root; other eight full PNG bytes identical to all directly reviewed attempt2 images. No current game/server/teleport claim.', 'at_utc': '2026-10-22T02:47:10.876582+00:00'}}, {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row_pointer': ['final_screenshot_reviews', 3], 'item': {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row': ['final_screenshot_reviews', 3], 'png': 'verification/sections/341-native-attempt3/actual/window-fog-金雾.png', 'png_sha256': '5284d4ef5b1d8db4a623654f445495e6b272694aebec9ff0d8c05c53ff3bbb0d', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/341-native-attempt2/actual/window-fog-金雾.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': '2ec553d230ac33776bd579d123d6114b26de108753bae2e14b61835d62139115', 'row': {'name': 'fog-金雾', 'receipt_image': 'verification/sections/341-native-attempt3/actual/window-fog-金雾.png', 'sha256': '5284d4ef5b1d8db4a623654f445495e6b272694aebec9ff0d8c05c53ff3bbb0d', 'directly_viewed_by_root': False, 'review_reused_from': 'verification/sections/341-native-attempt2/actual/window-fog-金雾.png', 'whole_PNG_byte_identical': True, 'previous_direct_review': True}, 'row_sha256': '34f5af259c2c9ba62f058969f43c2a32be71b828c27e4ed3805a42eb5252a4ea', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/341-native-attempt2/actual/window-fog-金雾.png', 'leaf_proof': 'verification/sections/341-root-visual.json', 'leaf_proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9'}, 'png_sha256': '5284d4ef5b1d8db4a623654f445495e6b272694aebec9ff0d8c05c53ff3bbb0d', 'png_bytes': 107058, 'section': 341, 'scope_original': {'section': 341, 'passed': True, 'review_scope': 'Final confirmation directly viewed by root; other eight full PNG bytes identical to all directly reviewed attempt2 images. No current game/server/teleport claim.', 'at_utc': '2026-10-22T02:47:10.876582+00:00'}}, {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row_pointer': ['final_screenshot_reviews', 8], 'item': {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row': ['final_screenshot_reviews', 8], 'png': 'verification/sections/341-native-attempt3/actual/window-node-banner.png', 'png_sha256': '3d61f78c9f3ae14271ad754e9eea25e00c65bc3256af1489853bc78d6d623800', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/341-native-attempt2/actual/window-node-banner.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': 'df896b9e3a01f75e9b1873779025f0379f33095b8c3b95da024b96c09c1d1dbd', 'row': {'name': 'node-banner', 'receipt_image': 'verification/sections/341-native-attempt3/actual/window-node-banner.png', 'sha256': '3d61f78c9f3ae14271ad754e9eea25e00c65bc3256af1489853bc78d6d623800', 'directly_viewed_by_root': False, 'review_reused_from': 'verification/sections/341-native-attempt2/actual/window-node-banner.png', 'whole_PNG_byte_identical': True, 'previous_direct_review': True}, 'row_sha256': 'e02e9544338ec24415dbc00baac9004584adedc93e2aa480cec7a4f8a7af2a59', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/341-native-attempt2/actual/window-node-banner.png', 'leaf_proof': 'verification/sections/341-root-visual.json', 'leaf_proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9'}, 'png_sha256': '3d61f78c9f3ae14271ad754e9eea25e00c65bc3256af1489853bc78d6d623800', 'png_bytes': 64831, 'section': 341, 'scope_original': {'section': 341, 'passed': True, 'review_scope': 'Final confirmation directly viewed by root; other eight full PNG bytes identical to all directly reviewed attempt2 images. No current game/server/teleport claim.', 'at_utc': '2026-10-22T02:47:10.876582+00:00'}}, {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row_pointer': ['final_screenshot_reviews', 7], 'item': {'proof': 'verification/sections/341-root-visual.json', 'proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9', 'row': ['final_screenshot_reviews', 7], 'png': 'verification/sections/341-native-attempt3/actual/window-source-loss.png', 'png_sha256': '1d530388db09e3bba5c36f367eb7dfa5f5a03530b04039fadce73f8f457ee5a3', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/341-native-attempt2/actual/window-source-loss.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': '86b06aec669cb3ae42f0caaadd8d42264628620040c542c507e75e3790ed0cac', 'row': {'name': 'source-loss', 'receipt_image': 'verification/sections/341-native-attempt3/actual/window-source-loss.png', 'sha256': '1d530388db09e3bba5c36f367eb7dfa5f5a03530b04039fadce73f8f457ee5a3', 'directly_viewed_by_root': False, 'review_reused_from': 'verification/sections/341-native-attempt2/actual/window-source-loss.png', 'whole_PNG_byte_identical': True, 'previous_direct_review': True}, 'row_sha256': '1400941e7ff3b158ac34731c21a6e4c9d583de86ef208444f2ecb2837493534f', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/341-native-attempt2/actual/window-source-loss.png', 'leaf_proof': 'verification/sections/341-root-visual.json', 'leaf_proof_sha256': '4681a3e7939a9dc3a777f59328e1b694842dd4cbcff5a8af800124aca18434e9'}, 'png_sha256': '1d530388db09e3bba5c36f367eb7dfa5f5a03530b04039fadce73f8f457ee5a3', 'png_bytes': 30430, 'section': 341, 'scope_original': {'section': 341, 'passed': True, 'review_scope': 'Final confirmation directly viewed by root; other eight full PNG bytes identical to all directly reviewed attempt2 images. No current game/server/teleport claim.', 'at_utc': '2026-10-22T02:47:10.876582+00:00'}}, {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row_pointer': ['final_screenshot_reviews', 5], 'item': {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row': ['final_screenshot_reviews', 5], 'png': 'verification/sections/344-native-attempt3/actual/window-named-receipt.png', 'png_sha256': 'a3b902b486e013340c14c1b29ed405fd30c1f31b7a052a1762fbb172b00e675a', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/344-native-attempt2/actual/window-named-receipt.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': '0c787e55f0acfe714ab88b8da2632947479cfa66c580205c87b83bc2bcb9dd6c', 'row': {'name': 'named-receipt', 'receipt_image': 'verification/sections/344-native-attempt3/actual/window-named-receipt.png', 'sha256': 'a3b902b486e013340c14c1b29ed405fd30c1f31b7a052a1762fbb172b00e675a', 'whole_PNG_byte_identical': True, 'review_reused_from': 'verification/sections/344-native-attempt2/actual/window-named-receipt.png', 'previous_direct_review': True, 'directly_viewed_final3': False}, 'row_sha256': 'ed48d35ee0992ac16d08f59c04664ec2ac551dcc8637b048277cc334e0082521', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/344-native-attempt2/actual/window-named-receipt.png', 'leaf_proof': 'verification/sections/344-root-visual.json', 'leaf_proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2'}, 'png_sha256': 'a3b902b486e013340c14c1b29ed405fd30c1f31b7a052a1762fbb172b00e675a', 'png_bytes': 180382, 'section': 344, 'scope_original': {'section': 344, 'passed': True, 'review_scope': 'All eight final attempt3 complete PNGs byte-identical to eight directly root-reviewed attempt2 PNGs. Reuse actual visual evidence; no false claim of another direct view. EOL-only fixture formatting did not change product/UI.', 'at_utc': '2026-10-22T04:07:36.880926+00:00'}}, {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row_pointer': ['final_screenshot_reviews', 4], 'item': {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row': ['final_screenshot_reviews', 4], 'png': 'verification/sections/344-native-attempt3/actual/window-natural-blocked.png', 'png_sha256': 'e141512c90187455e677938edcbf2b7ca94e7822092429bd4c90a7ca9179b650', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/344-native-attempt2/actual/window-natural-blocked.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': 'babb12339a2bd4f79d2ddb868b148d591803d93c25ee0079dc4b320865eda259', 'row': {'name': 'natural-blocked', 'receipt_image': 'verification/sections/344-native-attempt3/actual/window-natural-blocked.png', 'sha256': 'e141512c90187455e677938edcbf2b7ca94e7822092429bd4c90a7ca9179b650', 'whole_PNG_byte_identical': True, 'review_reused_from': 'verification/sections/344-native-attempt2/actual/window-natural-blocked.png', 'previous_direct_review': True, 'directly_viewed_final3': False}, 'row_sha256': 'bd811803a2a1e72b8d611dff450b89e63b5bb9d3d5ba5975fc7408dd84fa1627', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/344-native-attempt2/actual/window-natural-blocked.png', 'leaf_proof': 'verification/sections/344-root-visual.json', 'leaf_proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2'}, 'png_sha256': 'e141512c90187455e677938edcbf2b7ca94e7822092429bd4c90a7ca9179b650', 'png_bytes': 161066, 'section': 344, 'scope_original': {'section': 344, 'passed': True, 'review_scope': 'All eight final attempt3 complete PNGs byte-identical to eight directly root-reviewed attempt2 PNGs. Reuse actual visual evidence; no false claim of another direct view. EOL-only fixture formatting did not change product/UI.', 'at_utc': '2026-10-22T04:07:36.880926+00:00'}}, {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row_pointer': ['final_screenshot_reviews', 7], 'item': {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row': ['final_screenshot_reviews', 7], 'png': 'verification/sections/344-native-attempt3/actual/window-node-banner.png', 'png_sha256': '7b460121d76641a06529989440345cbd32d2d9ce3e91ac96712a934c4d9d2fee', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/344-native-attempt2/actual/window-node-banner.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': '37dddcd6a66760d6abd8c6cf8affc920b8bcde73e19845e4e8980a74c6709f82', 'row': {'name': 'node-banner', 'receipt_image': 'verification/sections/344-native-attempt3/actual/window-node-banner.png', 'sha256': '7b460121d76641a06529989440345cbd32d2d9ce3e91ac96712a934c4d9d2fee', 'whole_PNG_byte_identical': True, 'review_reused_from': 'verification/sections/344-native-attempt2/actual/window-node-banner.png', 'previous_direct_review': True, 'directly_viewed_final3': False}, 'row_sha256': '9158d7033d2dbbde0c61059bfc77636ce3f7be9a18e62af9ccf23aff9d9a3625', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/344-native-attempt2/actual/window-node-banner.png', 'leaf_proof': 'verification/sections/344-root-visual.json', 'leaf_proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2'}, 'png_sha256': '7b460121d76641a06529989440345cbd32d2d9ce3e91ac96712a934c4d9d2fee', 'png_bytes': 110681, 'section': 344, 'scope_original': {'section': 344, 'passed': True, 'review_scope': 'All eight final attempt3 complete PNGs byte-identical to eight directly root-reviewed attempt2 PNGs. Reuse actual visual evidence; no false claim of another direct view. EOL-only fixture formatting did not change product/UI.', 'at_utc': '2026-10-22T04:07:36.880926+00:00'}}, {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row_pointer': ['final_screenshot_reviews', 2], 'item': {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row': ['final_screenshot_reviews', 2], 'png': 'verification/sections/344-native-attempt3/actual/window-offering-directory.png', 'png_sha256': '2a7e51d77ef2160b3fe16193b2b5a3a5746835243ae14854f1cf607f3064b46d', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/344-native-attempt2/actual/window-offering-directory.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': '5d4b4d0192e06a654d0c0748eedfdfcd166954ebb36e2b5d4f3a6652f3b03214', 'row': {'name': 'offering-directory', 'receipt_image': 'verification/sections/344-native-attempt3/actual/window-offering-directory.png', 'sha256': '2a7e51d77ef2160b3fe16193b2b5a3a5746835243ae14854f1cf607f3064b46d', 'whole_PNG_byte_identical': True, 'review_reused_from': 'verification/sections/344-native-attempt2/actual/window-offering-directory.png', 'previous_direct_review': True, 'directly_viewed_final3': False}, 'row_sha256': 'fa9bfc1544eebf8ec6c73dcb80e244440abf91509cbc86856741ea3ef99bc8cf', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/344-native-attempt2/actual/window-offering-directory.png', 'leaf_proof': 'verification/sections/344-root-visual.json', 'leaf_proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2'}, 'png_sha256': '2a7e51d77ef2160b3fe16193b2b5a3a5746835243ae14854f1cf607f3064b46d', 'png_bytes': 106615, 'section': 344, 'scope_original': {'section': 344, 'passed': True, 'review_scope': 'All eight final attempt3 complete PNGs byte-identical to eight directly root-reviewed attempt2 PNGs. Reuse actual visual evidence; no false claim of another direct view. EOL-only fixture formatting did not change product/UI.', 'at_utc': '2026-10-22T04:07:36.880926+00:00'}}, {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row_pointer': ['final_screenshot_reviews', 3], 'item': {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row': ['final_screenshot_reviews', 3], 'png': 'verification/sections/344-native-attempt3/actual/window-parts-again.png', 'png_sha256': 'e9fd70d36b10665b3ec507e18baeeaff4c59fa0f4148f1f503c5cb6b780f903c', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/344-native-attempt2/actual/window-parts-again.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': 'd48c70d93983abd7362505e081de4c233f7dc5de741ddb0924d1da01dec32c9c', 'row': {'name': 'parts-again', 'receipt_image': 'verification/sections/344-native-attempt3/actual/window-parts-again.png', 'sha256': 'e9fd70d36b10665b3ec507e18baeeaff4c59fa0f4148f1f503c5cb6b780f903c', 'whole_PNG_byte_identical': True, 'review_reused_from': 'verification/sections/344-native-attempt2/actual/window-parts-again.png', 'previous_direct_review': True, 'directly_viewed_final3': False}, 'row_sha256': '59f22e402193cbb740e99269fa79b261717b99c26ded906deeabf60a23ffdd9c', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/344-native-attempt2/actual/window-parts-again.png', 'leaf_proof': 'verification/sections/344-root-visual.json', 'leaf_proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2'}, 'png_sha256': 'e9fd70d36b10665b3ec507e18baeeaff4c59fa0f4148f1f503c5cb6b780f903c', 'png_bytes': 175581, 'section': 344, 'scope_original': {'section': 344, 'passed': True, 'review_scope': 'All eight final attempt3 complete PNGs byte-identical to eight directly root-reviewed attempt2 PNGs. Reuse actual visual evidence; no false claim of another direct view. EOL-only fixture formatting did not change product/UI.', 'at_utc': '2026-10-22T04:07:36.880926+00:00'}}, {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row_pointer': ['final_screenshot_reviews', 1], 'item': {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row': ['final_screenshot_reviews', 1], 'png': 'verification/sections/344-native-attempt3/actual/window-relic-offering.png', 'png_sha256': '507abfe6f3d3bb4c14aadcee152295fa0cf731d31efaa34db1757550c025f4d7', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/344-native-attempt2/actual/window-relic-offering.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': 'd6340448172256ea46842d4651bc112b76f1b6b215d6a3106c811acd67d24510', 'row': {'name': 'relic-offering', 'receipt_image': 'verification/sections/344-native-attempt3/actual/window-relic-offering.png', 'sha256': '507abfe6f3d3bb4c14aadcee152295fa0cf731d31efaa34db1757550c025f4d7', 'whole_PNG_byte_identical': True, 'review_reused_from': 'verification/sections/344-native-attempt2/actual/window-relic-offering.png', 'previous_direct_review': True, 'directly_viewed_final3': False}, 'row_sha256': '52368d67870fde2011aaa120ada8df824a0eea88a6ef3a13f6ed88c0f329fb54', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/344-native-attempt2/actual/window-relic-offering.png', 'leaf_proof': 'verification/sections/344-root-visual.json', 'leaf_proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2'}, 'png_sha256': '507abfe6f3d3bb4c14aadcee152295fa0cf731d31efaa34db1757550c025f4d7', 'png_bytes': 166781, 'section': 344, 'scope_original': {'section': 344, 'passed': True, 'review_scope': 'All eight final attempt3 complete PNGs byte-identical to eight directly root-reviewed attempt2 PNGs. Reuse actual visual evidence; no false claim of another direct view. EOL-only fixture formatting did not change product/UI.', 'at_utc': '2026-10-22T04:07:36.880926+00:00'}}, {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row_pointer': ['final_screenshot_reviews', 0], 'item': {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row': ['final_screenshot_reviews', 0], 'png': 'verification/sections/344-native-attempt3/actual/window-source-exchange.png', 'png_sha256': 'b9670dba7b04894c61c7e42a403087c09e121c8439dd57a99f7aac5257bbdef0', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/344-native-attempt2/actual/window-source-exchange.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': '0e3431db5a674987d96badac8aaa89a4953a292882fbe54a890662ea9b0896e1', 'row': {'name': 'source-exchange', 'receipt_image': 'verification/sections/344-native-attempt3/actual/window-source-exchange.png', 'sha256': 'b9670dba7b04894c61c7e42a403087c09e121c8439dd57a99f7aac5257bbdef0', 'whole_PNG_byte_identical': True, 'review_reused_from': 'verification/sections/344-native-attempt2/actual/window-source-exchange.png', 'previous_direct_review': True, 'directly_viewed_final3': False}, 'row_sha256': '96c473f4d3c761421854b52976da2e688e90a96057e90421d6d7d98ac8d91aeb', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/344-native-attempt2/actual/window-source-exchange.png', 'leaf_proof': 'verification/sections/344-root-visual.json', 'leaf_proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2'}, 'png_sha256': 'b9670dba7b04894c61c7e42a403087c09e121c8439dd57a99f7aac5257bbdef0', 'png_bytes': 147607, 'section': 344, 'scope_original': {'section': 344, 'passed': True, 'review_scope': 'All eight final attempt3 complete PNGs byte-identical to eight directly root-reviewed attempt2 PNGs. Reuse actual visual evidence; no false claim of another direct view. EOL-only fixture formatting did not change product/UI.', 'at_utc': '2026-10-22T04:07:36.880926+00:00'}}, {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row_pointer': ['final_screenshot_reviews', 6], 'item': {'proof': 'verification/sections/344-root-visual.json', 'proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2', 'row': ['final_screenshot_reviews', 6], 'png': 'verification/sections/344-native-attempt3/actual/window-source-loss.png', 'png_sha256': '63331cb8558720b28c01369e7f0560c06514560a150aa05c641bdb8e70a3130a', 'method': 'documented_prior_direct_view_full_byte_equality', 'reviewed_png': 'verification/sections/344-native-attempt2/actual/window-source-loss.png', 'whole_png_bytes_compared_equal': True, 'explicit_prior_direct_basis': 'row previous_direct_review=True and whole_PNG_byte_identical=True'}, 'item_sha256': '1d6fad70f6d460dc3f7d552a949320e44b7296fe3faf040d040a54361815572a', 'row': {'name': 'source-loss', 'receipt_image': 'verification/sections/344-native-attempt3/actual/window-source-loss.png', 'sha256': '63331cb8558720b28c01369e7f0560c06514560a150aa05c641bdb8e70a3130a', 'whole_PNG_byte_identical': True, 'review_reused_from': 'verification/sections/344-native-attempt2/actual/window-source-loss.png', 'previous_direct_review': True, 'directly_viewed_final3': False}, 'row_sha256': 'c97fac7623600ce5e3ff13089d736c493057081ea5ea8d189109e2da6a8cf2e9', 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/344-native-attempt2/actual/window-source-loss.png', 'leaf_proof': 'verification/sections/344-root-visual.json', 'leaf_proof_sha256': '1c47927b6c4ee6541c467a5427b0df87e46daa67edf37189c7560f5a1ff023b2'}, 'png_sha256': '63331cb8558720b28c01369e7f0560c06514560a150aa05c641bdb8e70a3130a', 'png_bytes': 31660, 'section': 344, 'scope_original': {'section': 344, 'passed': True, 'review_scope': 'All eight final attempt3 complete PNGs byte-identical to eight directly root-reviewed attempt2 PNGs. Reuse actual visual evidence; no false claim of another direct view. EOL-only fixture formatting did not change product/UI.', 'at_utc': '2026-10-22T04:07:36.880926+00:00'}}]

_FULL380_SAME_PROOF_EDGE_SPEC = {'proof': 'verification/sections/327-root-visual.json', 'proof_sha256': '2b177969e321b8969ec15c402858a7b1737d7beaa52830cc2d02ea9548a261ab', 'item': {'proof': 'verification/sections/327-root-visual.json', 'proof_sha256': '2b177969e321b8969ec15c402858a7b1737d7beaa52830cc2d02ea9548a261ab', 'row': ['final_screenshot_reviews', 6], 'png': 'verification/sections/327-native-attempt2/actual/window-reverse-full-dialogue.png', 'png_sha256': 'fb0408fba7a55893cde35af14b69c71d0dc9e123379967f7c83249fdb48051de', 'method': 'explicit_same_proof_emergency_confirm_full_byte_equality', 'reviewed_png': 'verification/sections/327-native-attempt2/actual/window-emergency-confirm.png', 'whole_png_bytes_compared_equal': True}, 'item_sha256': '9e84ab7ee95e98254f920afd40e407eff632f8b73aa3a76346fff44f27716b75', 'row': {'name': 'reverse-full-dialogue', 'path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\327-native-attempt2\\actual\\window-reverse-full-dialogue.png', 'sha256': 'fb0408fba7a55893cde35af14b69c71d0dc9e123379967f7c83249fdb48051de', 'native': {'hwnd': 2425260, 'pid': 17780, 'size': [1220, 850]}, 'review': 'Byte equal to directly viewed final emergency-confirm PNG'}, 'row_sha256': 'e42041b54ed39ec410689f8f8fe298036e9c2e548f3bcaa86a7266fdf4f81b7e', 'next_item': {'proof': 'verification/sections/327-root-visual.json', 'proof_sha256': '2b177969e321b8969ec15c402858a7b1737d7beaa52830cc2d02ea9548a261ab', 'row': ['final_screenshot_reviews', 5], 'png': 'verification/sections/327-native-attempt2/actual/window-emergency-confirm.png', 'png_sha256': 'fb0408fba7a55893cde35af14b69c71d0dc9e123379967f7c83249fdb48051de', 'method': 'root_direct_visual_review'}, 'next_item_sha256': 'ecd4b31953c3217dbba4621d44ef17e71784f37dd507b93a8304d66cea5155c4', 'next_row': {'name': 'emergency-confirm', 'path': 'C:\\Users\\李娜\\Desktop\\lcn\\rouge\\verification\\sections\\327-native-attempt2\\actual\\window-emergency-confirm.png', 'sha256': 'fb0408fba7a55893cde35af14b69c71d0dc9e123379967f7c83249fdb48051de', 'native': {'hwnd': 2425260, 'pid': 17780, 'size': [1220, 850]}, 'review': 'Direct final PNG viewed'}, 'origin': {'actor': '/root', 'review_method': 'root_direct_visual_review', 'original_png': 'verification/sections/327-native-attempt2/actual/window-emergency-confirm.png', 'leaf_proof': 'verification/sections/327-root-visual.json', 'leaf_proof_sha256': '2b177969e321b8969ec15c402858a7b1737d7beaa52830cc2d02ea9548a261ab'}, 'png_sha256': 'fb0408fba7a55893cde35af14b69c71d0dc9e123379967f7c83249fdb48051de', 'png_bytes': 100221, 'scope_original': 'Five unique changed final PNGs directly viewed. Two others byte-equal to already directly viewed PNGs. Ordinary-player wording, relevant-only tool control, variants not duplicate deductions, half-gold unknown and linked dialogue are legible.', 'next_row_sha256': 'c8f55124b2df5f5881905db9fa3b749833d4e7f4761ed688a60b2f9109326ecd'}

def _full380_history_fingerprint(value):
    return _full380_history_sha256(_full380_history_json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def _full380_historical_leaf_schema_compatible(item, row, origin, entry, current, leaf_document, pin_public, read):
    """Only these24 original leaf rows. Not a new review or a general schema bypass."""
    if type(item) is not dict or type(row) is not dict or type(item.get('row')) is not list:
        return False
    matches = [s for s in _FULL380_HISTORICAL_LEAF_SPECS
               if item.get('proof') == s['proof'] and item.get('proof_sha256') == s['proof_sha256']
               and item['row'] == s['row_pointer']]
    if len(matches) != 1:
        return False
    spec = matches[0]
    if (origin != spec['origin'] or origin.get('actor') != '/root'
            or origin.get('review_method') != 'root_direct_visual_review'
            or entry.get('sha256') != spec['png_sha256'] or entry.get('bytes') != spec['png_bytes']
            or len(current) != spec['png_bytes'] or _full380_history_sha256(current).hexdigest() != spec['png_sha256']
            or _full380_history_fingerprint(item) != spec['item_sha256']
            or _full380_history_fingerprint(row) != spec['row_sha256']
            or leaf_document.get('section') != spec['section'] or leaf_document.get('passed') is not True):
        return False
    section = spec['section']
    if section == 323:
        claim = (row.get('byte_equal_to_directly_viewed_initial') is True
                 and row.get('final_directly_viewed') is False
                 and row.get('initial_receipt') == spec['extra_native_receipt']['file'])
    elif section == 325:
        claim = (row.get('pixel_file_byte_equal_previous_attempt2') is True
                 and row.get('earlier_directly_viewed_attempt2') is True
                 and row.get('viewed_directly_this_turn') is False)
    elif section == 327:
        claim = row.get('review') == 'Byte equal to already directly viewed first-attempt source-loss PNG'
    elif section == 331:
        claim = (row.get('review') == 'Byte identical to already directly viewed initial actual PNG'
                 and row.get('directly_viewed_initial_path') == spec['row']['directly_viewed_initial_path']
                 and row.get('identical_sha256') == spec['png_sha256'])
    elif section in (341, 344):
        claim = (row.get('review_reused_from') == origin['original_png']
                 and row.get('whole_PNG_byte_identical') is True
                 and row.get('previous_direct_review') is True)
    else:
        return False
    if not claim:
        return False
    extra = spec.get('extra_native_receipt')
    if extra:
        native = read(pin_public(extra['file'], extra['sha256']))
        native_row = native
        for key in extra['row_pointer']:
            native_row = native_row[key]
        if (native.get('section') != section or native.get('passed') is not True
                or native.get('failure') is not None
                or _full380_history_fingerprint(native_row) != extra['row_sha256']):
            return False
    return True


def _full380_explicit_same_proof_edge_compatible(item, next_item, row, origin, entry, current, leaf_document):
    """Only the recorded327 row6->row5 same-document edge, reached by two PNG rows."""
    spec = _FULL380_SAME_PROOF_EDGE_SPEC
    if (type(item) is not dict or type(next_item) is not dict or type(row) is not dict
            or item.get('proof') != spec['proof'] or item.get('proof_sha256') != spec['proof_sha256']
            or next_item.get('proof') != spec['proof'] or next_item.get('proof_sha256') != spec['proof_sha256']
            or item.get('row') != ['final_screenshot_reviews', 6]
            or next_item.get('row') != ['final_screenshot_reviews', 5]
            or _full380_history_fingerprint(item) != spec['item_sha256']
            or _full380_history_fingerprint(next_item) != spec['next_item_sha256']
            or _full380_history_fingerprint(row) != spec['row_sha256']
            or origin != spec['origin'] or origin.get('actor') != '/root'
            or origin.get('review_method') != 'root_direct_visual_review'
            or entry.get('sha256') != spec['png_sha256'] or entry.get('bytes') != spec['png_bytes']
            or len(current) != spec['png_bytes'] or _full380_history_sha256(current).hexdigest() != spec['png_sha256']
            or leaf_document.get('section') != 327 or leaf_document.get('passed') is not True
            or leaf_document.get('review') != spec['scope_original']):
        return False
    next_row = leaf_document['final_screenshot_reviews'][5]
    return (item.get('method') == 'explicit_same_proof_emergency_confirm_full_byte_equality'
            and item.get('whole_png_bytes_compared_equal') is True
            and item.get('reviewed_png') == next_item.get('png') == origin['original_png']
            and next_item.get('method') == 'root_direct_visual_review'
            and row.get('review') == 'Byte equal to directly viewed final emergency-confirm PNG'
            and next_row.get('review') == 'Direct final PNG viewed'
            and _full380_history_fingerprint(next_row) == spec['next_row_sha256'])

# END EXACT FULL380 HISTORICAL SCHEMA COMPATIBILITY


def verify_registry_chain(entry, origin, current, document_cache):
    """Verify one complete already-recorded public derivation, without new discovery.

    Public copies preserve leaf JSON bytes, including old internal path strings;
    the byte-bound registry carries their explicit public alias mapping. Do not
    rewrite those originals or reinterpret an old source path as a new viewing.
    """
    aliases = [a for a in entry.get('verified_public_png_aliases', [])
               if a.get('actual_original_reviewer') == origin['actor']
               and a.get('actual_original_review_method') == origin['review_method']
               and a.get('evidence_chain')
               and a['evidence_chain'][-1].get('proof') == origin['leaf_proof']
               and a['evidence_chain'][-1].get('proof_sha256') == origin['leaf_proof_sha256']
               and (a['evidence_chain'][-1].get('png') == origin['original_png']
                    or (a['evidence_chain'][-1].get('method') == 'documented_prior_direct_view_full_byte_equality'
                        and a['evidence_chain'][-1].get('reviewed_png') == origin['original_png']))]
    require(bool(aliases), 'Public registry lacks the complete chain to its declared origin.')
    alias = aliases[0]; chain = alias['evidence_chain']; seen = set()
    require(chain[0]['proof'] == alias['proof'] and chain[0]['proof_sha256'] == alias['proof_sha256']
            and chain[0]['png'] == alias['png'], 'Public alias does not start at its recorded proof.')
    for index, item in enumerate(chain):
        identity = (item['proof'], tuple(item['row']))
        require(identity not in seen, 'Historical public registry chain is cyclic.'); seen.add(identity)
        key = (item['proof'], item['proof_sha256'])
        if key not in document_cache:
            document_cache[key] = read(pin_public(*key))
        row = document_cache[key]
        for part in item['row']:
            row = row[part]
        require(type(row) is dict and item['png_sha256'] == entry['sha256']
                and pin_public(item['png'], entry['sha256']).read_bytes() == current,
                'Historical chain row or actual whole PNG bytes differ.')
        if index + 1 < len(chain):
            next_item = chain[index + 1]
            if not _full380_explicit_same_proof_edge_compatible(item, next_item, row, origin, entry, current, document_cache[key]):
                require(item.get('whole_png_bytes_compared_equal') is True
                        and item.get('referenced_proof') == next_item['proof']
                        and item.get('referenced_proof_sha256') == next_item['proof_sha256']
                        and item.get('reviewed_png') == next_item['png'], 'Historical chain edge differs.')
        else:
            require(item['proof'] == origin['leaf_proof'], 'Historical chain does not terminate at the original leaf proof.')
            if item['png'] != origin['original_png']:
                if _full380_historical_leaf_schema_compatible(item, row, origin, entry, current, document_cache[key], pin_public, read):
                    require(item.get('method') == 'documented_prior_direct_view_full_byte_equality'
                            and item.get('reviewed_png') == origin['original_png']
                            and item.get('whole_png_bytes_compared_equal') is True
                            and pin_public(origin['original_png'], entry['sha256']).read_bytes() == current,
                            'Exact historical leaf compatibility must retain original full-PNG-byte guards.')
                else:
                    require(item.get('method') == 'documented_prior_direct_view_full_byte_equality'
                            and item.get('reviewed_png') == origin['original_png']
                            and item.get('whole_png_bytes_compared_equal') is True
                            and row.get('direct_review_reused_only_because_entire_PNG_bytes_identical') is True
                            and row.get('original_direct_review') == origin['original_png']
                            and pin_public(origin['original_png'], entry['sha256']).read_bytes() == current,
                            'Documented prior direct origin/full-byte basis differs.')


def verify_visual(visual_sha, files, manifest_sha):
    require(sha(regular(VISUAL)) == visual_sha, 'Explicit final visual SHA differs.')
    visual = read(VISUAL)
    require(visual.get('schema') == VISUAL_SCHEMA and visual.get('section') == 380
            and visual.get('actual_validation_attempt') == ATTEMPT and visual.get('source_freeze_sha256') == FREEZE_SHA
            and visual.get('archive_manifest_sha256') == manifest_sha and visual.get('all_reviewed') is True
            and visual.get('pending_actual_view_rows') == 0,
            'Final root visual schema/complete status/binding is missing; pending inventory cannot seal.')
    require(visual.get('blocking_visual_issues') == [], 'A final visual proof must explicitly contain no unresolved blocking issue.')
    names = {n for n in files if len(PurePosixPath(n).parts) == 3 and PurePosixPath(n).parts[1] == 'actual' and n.lower().endswith('.png')}
    expected = {relative(ARCHIVE / n): files[n]['sha256'] for n in names}
    rows = visual['images']
    require(type(rows) is list and len(rows) == len(expected) > 0
            and len({row['file'] for row in rows}) == len(rows)
            and {row['file']: row['sha256'] for row in rows} == expected
            and visual.get('image_count') == len(rows), 'Final visual exact actual PNG path/hash set differs.')
    by_file = {row['file']: row for row in rows}; checked = set(); active = set(); registries = {}; documents = {}

    def verify(row):
        file = row['file']
        if file in checked:
            return
        require(file not in active, 'Cyclic same-byte visual review chain.')
        active.add(file)
        for key in ('file', 'sha256', 'reviewed', 'method', 'reviewed_file', 'review_receipt', 'review_receipt_sha256', 'review_actor', 'registry_proof'):
            require(key in row, 'Final visual row schema missing ' + key)
        require(row.get('reviewed') is True and type(row.get('review_actor')) is str and bool(row['review_actor'])
                and row.get('status') != 'needs_actual_view', 'Actual PNG still unreviewed: ' + file)
        current = public_file(file).read_bytes(); require(digest(current) == row['sha256'], 'Actual PNG drift.')
        method = row['method']
        reviewed_path = pin_public(row['reviewed_file'], row['sha256'])
        require(reviewed_path.read_bytes() == current, 'Visual full PNG bytes are not identical.')
        leaf_path = pin_public(row['review_receipt'], row['review_receipt_sha256'])
        require(leaf_path != VISUAL, 'Final visual receipt cannot self-attest via circular hash.')
        if method in ('previous_exact_bytes', 'contact_sheet'):
            rp = row['registry_proof']; require(type(rp) is dict, 'Prior exact review requires public registry.')
            require(rp.get('entry_sha256') == row['sha256'], 'Registry entry PNG SHA differs.')
            key = (rp['file'], rp['sha256'])
            if key not in registries:
                registry = read(pin_public(*key))
                require(registry.get('schema') in ('full365_prior_actual_visual_png_registry_v1', 'full380_prior_actual_visual_png_registry_v1')
                        and type(registry.get('public_derivation')) is dict, 'Public derived registry schema absent.')
                registries[key] = registry
            entry = registries[key]['entries'][rp['entry_sha256']]
            require(entry.get('sha256') == row['sha256'] and entry.get('bytes') == len(current)
                    and type(rp.get('origin_index')) is int and 0 <= rp['origin_index'] < len(entry['review_origins']), 'Registry origin index/bytes differ.')
            origin = entry['review_origins'][rp['origin_index']]
            require(origin['actor'] == row['review_actor'] and origin['original_png'] == row['reviewed_file']
                    and origin['leaf_proof'] == row['review_receipt'] and origin['leaf_proof_sha256'] == row['review_receipt_sha256'],
                    'Final visual actor/original/leaf differs from actual public registry origin.')
            verify_registry_chain(entry, origin, current, documents)
            if method == 'contact_sheet':
                require(origin['review_method'] == row.get('inherited_review_method') == 'inherited_contact_sheet_visual_review',
                        'Historical sheet must retain true scale/method, not claim direct new PNG view.')
                contact = origin['contact_sheet']; mapping = read(pin_public(contact['proof'], contact['proof_sha256']))
                require(mapping.get('root_viewed') is True, 'Historical sheet not actually viewed.')
                pin_public(contact['sheet'], contact['sheet_sha256'])
                require(any(m.get('file') == row['reviewed_file'] and m.get('sha256') == row['sha256'] for m in mapping.get('members', [])),
                        'Historical sheet does not contain the exact original PNG.')
            else:
                require(origin['review_method'] in ('root_direct_visual_review', 'subagent_direct_visual_review'),
                        'Prior exact method must retain real root/agent direct origin.')
        elif method == 'direct_view':
            require(row['registry_proof'] is None and row['reviewed_file'] == file
                    and row.get('actual_new_view_image_called') is True
                    and row.get('actual_pixels_visually_reviewed') is True
                    and row.get('visual_blocking_issue') is False, 'New direct view requires actual pixels and no blocking issue, not inventory request.')
            doc = read(leaf_path)
            matches = [x for x in leaf_rows(doc) if x.get('file') == file and x.get('sha256') == row['sha256']]
            require(len(matches) == 1 and matches[0].get('reviewed') is True and matches[0].get('method') == 'direct_view'
                    and matches[0].get('review_actor') == row['review_actor']
                    and matches[0].get('actual_new_view_image_called') is True
                    and matches[0].get('actual_pixels_visually_reviewed') is True
                    and matches[0].get('visual_blocking_issue') is False
                    and not doc.get('blocking_visual_issues'), 'Independent actual direct pixels/proof/actor differs or blocking issue remains.')
        elif method == 'same_byte_reuse':
            require(row['registry_proof'] is None and row['reviewed_file'] in by_file and row['reviewed_file'] != file,
                    'New same-byte reuse must resolve to a different actual current image.')
            source = by_file[row['reviewed_file']]; verify(source)
            require(source['method'] == 'direct_view' and source['review_actor'] == row['review_actor']
                    and source['review_receipt'] == row['review_receipt']
                    and source['review_receipt_sha256'] == row['review_receipt_sha256'],
                    'Same-byte row must preserve a real current direct reviewer and proof.')
        else:
            raise ValueError('Unknown final visual method: ' + str(method))
        active.remove(file); checked.add(file)

    for row in rows:
        verify(row)
    return {'file': relative(VISUAL), 'sha256': visual_sha, 'image_count': len(rows), 'all_reviewed': True,
            'method_counts': dict(Counter(r['method'] for r in rows)),
            'review_actors': sorted({r['review_actor'] for r in rows}),
            'actual_path_set_complete': True, 'exact_full_png_bytes_compared_for_reuse': True,
            'historical_sheet_scale_and_actual_actor_preserved': True,
            'visual_reuse_is_not_new_semantic_validation': True,
            'all_images_directly_viewed_by_root_claimed': False}


def verify_scope_floor(data):
    prior_path = ROOT / 'verification/full-365/summary.json'
    prior = read(prior_path)
    old_path = ROOT / prior['source_freeze']
    require(sha(old_path) == prior['source_freeze_sha256'] and prior.get('available_checks_passed') is True
            and prior.get('scope_not_reduced') is True, 'Actual complete365 historical floor required.')
    old = read(old_path)
    require(len(old['selectors']) == 598 and len(old['p3_scripts']) == 80, 'Actual365 floor changed.')
    require(data['selectors'][:len(old['selectors'])] == old['selectors']
            and len(set(data['selectors'])) == len(data['selectors'])
            and all(data['p3_scripts'].get(k) == v for k,v in old['p3_scripts'].items())
            and list(data['p3_scripts'])[:len(old['p3_scripts'])] == list(old['p3_scripts']),
            'Original365 selectors/native ordered scope reduced or replaced.')
    require(data['template_bundle_sha256'] == old['template_bundle_sha256']
            and data['local_public_input_bindings'] == old['local_public_input_bindings']
            and data['historical_manifest_bindings'] == old['historical_manifest_bindings'],
            'Original52/typed/30/29 and explicit original inputs must remain complete.')
    require(set(old['source_sha256']) <= set(data['source_sha256'])
            and set(old['supplemental_public_inputs_sha256']) <= set(data['supplemental_public_inputs_sha256']),
            'Complete source and supplemental path scope reduced.')
    from full380_common import canonical_binding_plan, canonical_frozen_inputs
    require(data.get('canonical_local_public_input_bindings') == canonical_binding_plan(),
            'Exactly the five original canonical369 local/public/provenance bindings must be retained separately.')
    canonical = canonical_frozen_inputs(data)
    require(len(canonical) == 5, 'Original canonical369 five local sources are not complete.')
    for section in range(366,381):
        require(any(int(k.split('_')[1]) == section for k in data['p3_scripts']),
                'Missing actually installed new native workflow: '+str(section))
    for mode in ('p3_304','p3_305'):
        require(data['p3_script_options'][mode].get('explicit_current_source_freeze') is True,
                '304/305 must receive current380 freeze explicitly.')
    require(data['p3_script_options']['p3_312'].get('canonical_visible_default_ms') == 120000
            and data['p3_script_options']['p3_312'].get('visible_ms') == 120000
            and data['p3_script_options']['p3_312'].get('use_canonical_visible_default') is True,
            'Original312 actual default120s must remain.')
    return {'summary':proof(prior_path),'source_freeze':proof(old_path),
            'old_selectors':len(old['selectors']),'old_native_supplements':len(old['p3_scripts']),
            'current_selectors':len(data['selectors']),'current_native_supplements':len(data['p3_scripts']),
            'current_required_components':5+len(data['p3_scripts']),
            'canonical369_explicit_original_local_public_bindings':data['canonical_local_public_input_bindings'],
            'canonical369_exact5_sources_preserved_only_in_mode369':True,
            'prior_results_reused_as_current_PASS':False}


def main():
    global FREEZE_SHA, ACTIVATION_SHA, BASE, ARCHIVE, FREEZE, VISUAL, PARENT, ATTEMPT, REVIEW_SHA
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seal',action='store_true')
    parser.add_argument('--attempt',type=int,required=True)
    parser.add_argument('--expected-parent-commit',required=True)
    for key in ('freeze-sha256','activation-sha256','archive-manifest-sha256','visual-sha256','review-helper-sha256'):
        parser.add_argument('--'+key,required=True)
    args=parser.parse_args()
    require(args.seal and args.attempt >= 1,'Explicit root seal and positive actual attempt required.')
    require(re.fullmatch(r'[0-9a-f]{40}',args.expected_parent_commit)is not None,'Actual parent commit required.')
    for key in ('freeze_sha256','activation_sha256','archive_manifest_sha256','visual_sha256','review_helper_sha256'):
        require(re.fullmatch(r'[0-9a-f]{64}',getattr(args,key))is not None,'Explicit actual lower-case SHA256 required.')
    ATTEMPT=args.attempt;PARENT=args.expected_parent_commit
    BASE=ROOT/'.cache/full380-prepared'/('attempt-'+str(ATTEMPT))
    ARCHIVE=ROOT/'verification/full-380'/('execution-attempt'+str(ATTEMPT))
    FREEZE=ROOT/'verification/full-380'/('source-freeze-attempt'+str(ATTEMPT)+'.json')
    VISUAL=ROOT/'verification/full-380/root-visual-review.json'
    FREEZE_SHA=args.freeze_sha256;ACTIVATION_SHA=args.activation_sha256;REVIEW_SHA=args.review_helper_sha256
    require(not OUT.exists(),'Never overwrite an original summary.')
    manifest,files,container=verify_archive(args.archive_manifest_sha256)
    require(sha(FREEZE)==FREEZE_SHA and sha(BASE/'activation380.json')==ACTIVATION_SHA,'Actual current authority changed.')
    bound,terminal,closure,source_stable=load_readonly_helpers()
    data,activation=bound(PARENT,FREEZE_SHA,ACTIVATION_SHA)
    require(data['actual_validation_attempt']==ATTEMPT,'Wrong actual attempt.')
    scope_floor=verify_scope_floor(data)
    prior_attempts=[]
    for attempt in range(1,ATTEMPT):
        prior_archive=ROOT/'verification/full-380'/('execution-attempt'+str(attempt))
        prior_manifest=read(prior_archive/'archive-manifest.json')
        pm,pf,pc=verify_archive(sha(prior_archive/'archive-manifest.json'),archive=prior_archive,
            base=ROOT/'.cache/full380-prepared'/('attempt-'+str(attempt)),
            freeze=ROOT/'verification/full-380'/('source-freeze-attempt'+str(attempt)+'.json'),
            attempt=attempt,freeze_sha=prior_manifest['source_freeze_sha256'],activation_sha=prior_manifest['activation_sha256'])
        prior_attempts.append({'manifest':proof(prior_archive/'archive-manifest.json'),
            'actual_root_exit':pm['actual_root_controller_exit'],'not_relabelled_PASS':True})
    process,ledger,review=verify_root_and_ledger(manifest,data,container)
    raws,supers,component_proofs=verify_components(data,container,ledger,review,terminal,closure,source_stable)
    typed=verify_typed(data,review,container)
    current=verify_current30(raws,supers,component_proofs,review)
    functional=verify_functional(data,source_stable)
    visual=verify_visual(args.visual_sha256,files,args.archive_manifest_sha256)
    bound(PARENT,FREEZE_SHA,ACTIVATION_SHA)
    require(sha(ARCHIVE/'archive-manifest.json')==args.archive_manifest_sha256
            and sha(VISUAL)==args.visual_sha256,'Actual archive or visual changed during seal.')
    offline=raws['offline']
    result = {
        'after_section': 380, 'kind': 'FRESH380_COMPLETE_AVAILABLE_SCOPE_ONE_ACTUAL_ATTEMPT_SEALED',
        'checked_at_UTC': datetime.now(timezone.utc).isoformat(), 'available_checks_passed': True,
        'complete_repository_validation': False, 'scope_not_reduced': True,
        'P3_complete': False, 'P2_complete': False, 'P1_complete': False,
        'actual_validation_attempt': ATTEMPT, 'actual_root_controller_exit': process['actual_observed_exit'],
        'validation_composition': 'One declared current380 complete available scope executed and was observed terminal. Original30 exact1314, if observed, remains unavailable and independent29 remains separate.',
        'single_available_scope_execution_all_green': True,
        'all_executed_component_exit_codes_zero': all(p['actual_child_exit'] == p['actual_supervisor_exit'] == 0 for p in component_proofs.values()),
        'complete_original30_passed': current['original_symlink_operation_passed'],
        'all_final_component_source_maps_share_one_freeze': True, 'current_worktree_validation_authority': True,
        'source_files': len(data['source_sha256']), 'maintained_selectors': len(data['selectors']),
        'supplemental_public_input_files': len(data['supplemental_public_inputs_sha256']),
        'source_counts_are_not_summed_unique_files': True,
        'source_freeze': relative(FREEZE), 'source_freeze_sha256': FREEZE_SHA, 'activation_sha256': ACTIVATION_SHA,
        'tested_worktree_parent_commit': PARENT, 'source_drift': [], 'actual_required_components': len(ledger['steps']),
        'native_supplements': len(data['p3_scripts']), 'native_current_windows_gui_verified': True,
        'native_windows_game_chat_verified': False, 'historical_original_Windows_verified': False,
        'all_tests_executed_on_original_local_Windows': True, 'cloud_test_execution_started': False,
        'archive_manifests_sha256': {relative(ARCHIVE / 'archive-manifest.json'): args.archive_manifest_sha256},
        'earlier_actual_attempt_archives_preserved': prior_attempts,
        'previous_full_scope_retained_as_floor_not_current_PASS': scope_floor,
        'archive_all_files_sha256_and_bytes_checked': len(files),
        'root_retained_Popen': proof(ARCHIVE / 'root-launch/controller-process.json'),
        'root_retained_launcher_pid': process['controller_pid'],
        'root_runtime_controller_fixture_pid': read(ARCHIVE / 'owned-execution.json')['controller_fixture_pid'],
        'root_launcher_and_runtime_PID_equality_assumed': False,
        'root_actual_process_exit': proof(ARCHIVE / 'root-launch/process.exit'),
        'original_complete_scope_review': proof(ARCHIVE / 'automated-scope-review.json'),
        'original_orchestration': proof(ARCHIVE / 'orchestration.json'),
        'root_PNG_visual_review': visual,
        'offline_windows': {key: offline[key] for key in ('tests_run', 'tests_passed', 'historical_or_declared_skips',
            'failures', 'errors', 'unavailable_records', 'unavailable_parent_count', 'native_symlink_prerequisite',
            'unavailable', 'skips', 'qt_shutdown', 'qt_shutdown_error')},
        'actual_offline_process_exit': supers['offline']['child_primary_exit'],
        'legacy_window': typed, 'current_window': current,
        'p3_supplementary_windows': {name: review['component_details'][name] for name in data['p3_scripts']},
        'actual_component_proofs': component_proofs, 'functional380_necessary_and_native': functional,
        'unavailable_scopes': (["Original actual symlink WinError1314 remains unavailable, not passed."] if current['original_symlink_prerequisite_unavailable'] else []) + [
            'Actual offline unavailable records and historical skips remain separately listed above, not counted as passes.',
            'Original Linux/WSL/Wine and historical private Windows samples remain unverified.',
            'No live game sampling, game operation, chat request or current-server validation.'],
        'wrapper_launch_time_sha256_checked_against_retained_original': True,
        'assigned_owned_jobs_empty_not_global_descendant_enumeration': True,
        'canonical_budgets_are_workflow_profiles_not_latency_improvement': data['p3_script_options'],
        'normal_latency_improvement_claimed': False,
        'prior365_result_reused_as_current_PASS': False,
        'summary_sealer_reexecuted_review_or_auditor_or_tests_or_windows': False,
        'summary_sealer': {'path': relative(Path(__file__).resolve()), 'sha256': sha(Path(__file__))},
        'current_wrap_up_threshold_percent': 15,
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('xb')as stream:stream.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'summary':relative(OUT),'sha256':sha(OUT),'available_checks_passed':True,
        'complete_repository_validation':False,'actual_terminal_positions':len(ledger['steps']),
        'actual_root_exit':process['actual_observed_exit'],'visual_paths':visual['image_count']},ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Original failed/missing evidence is preserved. Never manufacture a PASS
        # or mutate automatic review, archive, freeze, state, HEAD or source files.
        print(json.dumps({'summary_NOT_sealed': True, 'available_checks_passed': None,
                          'error': type(error).__name__, 'message': str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
