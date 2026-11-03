"""Read only actual fresh305 outputs; this module never executes a component."""
import json
from pathlib import Path
from full305_common import BASE, ROOT, bound, public, sha, write_new


def load(path):
    if path.is_symlink() or not path.is_file(): raise ValueError('Actual regular receipt missing: ' + str(path))
    return json.loads(path.read_bytes())


def require(condition, message):
    if not condition: raise ValueError(message)


def hashes(value):
    require(type(value) is dict and bool(value), 'Nonempty actual selected source map required.')
    return {name: entry['sha256'] if type(entry) is dict else entry for name, entry in value.items()}


def terminal(folder, expected_child, success=True):
    step = load(folder / 'step.json'); process = load(folder / 'controller-process.json'); sup = load(folder / 'supervisor.json')
    observed = process.get('actual_observed_popen_exit')
    require(process.get('status') == 'completed' and type(observed) is int and process.get('owned_popen_retained') is True,
            'Supervisor not actually observed terminal by retained Popen: ' + folder.name)
    require(int((folder / 'process.exit').read_text('ascii').strip()) == observed == sup.get('supervisor_exit'), 'Actual process.exit mismatch.')
    origin = load(folder / 'process-exit-origin.json')
    require(origin.get('kind') == 'ACTUAL_RETAINED_POPEN_OBSERVED_SUPERVISOR_EXIT'
            and origin.get('derived_from_supervisor_json') is False and origin.get('actual_observed_popen_exit') == observed
            and origin.get('process_exit_sha256') == sha(folder / 'process.exit'), 'Original observed exit provenance absent.')
    require(sup.get('status') == 'completed' and sup.get('timed_out') is False and sup.get('owned_handle_retained') is True
            and sup.get('owned_job_assigned') is True and sup.get('owned_job_no_live_execution_verified') is True,
            'Assigned owned job not terminal, timed out, or not empty: ' + folder.name)
    require(sup.get('argv') == expected_child and sup.get('supervisor_sha256') == sha(BASE / 'supervisor305.py'), 'Actual child argv/supervisor source differs.')
    require(process.get('argv') == step.get('argv') and step.get('terminal_supervisor_and_job_verified') is True,
            'Actual controller step/argv mismatch.')
    for stream in ('stdout', 'stderr'):
        record = sup[stream]; path = folder / record['file']
        require(path.parent == folder and path.stat().st_size == record['bytes'] and sha(path) == record['sha256'], 'Actual supervisor stream hash differs.')
    if success: require(observed == sup.get('child_primary_exit') == 0, 'Actual child/supervisor not both0: ' + folder.name)
    return sup


def closure(folder, mode, freeze_sha, activation_sha, expected_target, expected_argv, success=True):
    path = folder / 'actual/full305-source-closure.json'; value = load(path)
    require(value.get('section') == 305 and value.get('mode') == mode and value.get('root_freeze_sha256') == freeze_sha
            and value.get('activation_sha256') == activation_sha, 'Wrong actual component freeze/mode.')
    require(Path(value['actual_target']).resolve() == expected_target.resolve() and value.get('actual_target_sha256') == sha(expected_target)
            and value.get('actual_argv') == expected_argv, 'Executed component target/argv changed.')
    for key in ('fixture_exception', 'source_guard_exception_after', 'qt_cleanup_error'):
        require(value.get(key) is None, 'Actual component error: ' + mode + ':' + key)
    require(value.get('actual_receipt_exists') is True, 'Actual component never produced final receipt.')
    receipt = folder / 'actual' / value['actual_receipt_file']
    require(receipt.parent == folder / 'actual' and sha(receipt) == value['actual_receipt_sha256'], 'Actual fixture receipt hash mismatch.')
    if success:
        require(value.get('actual_fixture_exit') == 0 and value.get('actual_receipt_passed') is True
                and value.get('component_automated_passed') is True, 'Actual component did not pass: ' + mode)
    return load(receipt), value


def source_stable(raw, expected, original287=False):
    key = next(key for key in ('source_sha256_before', 'loaded_source_sha256', 'source_sha256') if key in raw)
    before = hashes(raw[key])
    # Original287 records one map after two in-fixture equality assertions;
    # the new outer source closure independently fresh-checks after the call.
    # Do not invent a nonexistent original before/after field.
    after = hashes(raw['source_sha256_after']) if 'source_sha256_after' in raw else before if original287 else {}
    require(before == after == expected, 'Actual selected source names or before/after hashes differ.')
    require(all(sha(public(name)) == expected_sha for name, expected_sha in after.items()), 'Selected source bytes now differ.')


def review(container, data, activation, parent, freeze_sha):
    bound(parent, freeze_sha, sha(BASE / 'activation305.json'))
    authority = load(container / 'owned-execution.json'); activation_sha = authority['activation_sha256']
    require(authority.get('section') == 305 and authority.get('root_freeze_sha256') == freeze_sha
            and authority.get('parent_commit') == parent, 'Wrong owned actual305 namespace.')
    shared = ['--expected-parent-commit', parent, '--freeze-sha256', freeze_sha, '--activation-sha256', activation_sha]
    modes = ['offline', 'legacy', 'current30', 'current29', *data['p3_scripts']]
    actuals = {}; supers = {}; closures = {}; findings = []; details = {}
    for mode in modes:
        folder = container / mode
        try:
            child = [str(ROOT / '.venv/Scripts/python.exe'), '-B', '-X', 'utf8', str(BASE / 'component_child305.py'),
                     '--mode', mode, '--out', str(folder / 'actual'), *shared]
            supers[mode] = terminal(folder, child, success=mode != 'current30')
            if mode == 'offline':
                target = ROOT / 'scripts/verify_full_available.py'
                argv = [str(target), '--output', str(folder / 'actual/windows-offline.json'), '--verbosity', '2']
            elif mode in ('legacy', 'current30', 'current29'):
                target = BASE / ('bound-legacy' if mode == 'legacy' else 'bound-current') / 'launcher275.py'
                argv = [str(target), '--root', str(ROOT), '--out', str(folder / 'actual'), '--mode', mode]
            else:
                target = ROOT / data['p3_scripts'][mode]; argv = [str(target), '--receipt', str(folder / 'actual/window.json')]
                if data['p3_script_options'][mode]['accepts_visible_ms']:
                    argv += ['--visible-ms', str(data['p3_script_options'][mode]['visible_ms'])]
            raw, close = closure(folder, mode, freeze_sha, activation_sha, target, argv, success=mode != 'current30')
            actuals[mode] = raw; closures[mode] = close
            if mode == 'offline':
                require(raw.get('source_sha256') == data['source_sha256'] and raw.get('selectors') == data['selectors']
                        and raw.get('source_drift') == [] and raw.get('failed_cases') == [] and raw.get('verbosity') == 2
                        and raw.get('platform') == 'Windows' and raw.get('wine_compatibility') is False
                        and raw.get('failures') == raw.get('errors') == 0 and raw.get('available_checks_passed') is True
                        and raw.get('qt_shutdown_error') is None, 'Fresh complete offline result/source/platform differs.')
                details[mode] = {key: raw[key] for key in ('tests_run', 'tests_passed', 'historical_or_declared_skips',
                    'failures', 'errors', 'unavailable_records', 'unavailable_parent_count', 'native_symlink_prerequisite')}
            elif mode in ('legacy', 'current30', 'current29'):
                launch = load(folder / 'actual/native275-launcher-closure.json')
                require(launch.get('root_freeze_sha256') == freeze_sha and launch.get('source_drift') == []
                        and launch.get('executed_tool_drift') == [] and launch.get('fixture_exception') is None
                        and launch.get('qt_cleanup_error') is None and launch.get('actual_current_native_windows_window_verified') is True,
                        'Actual original launcher/window/source closure differs.')
                require(raw.get('source_drift') == [], 'Original actual fixture source drift.')
                if mode != 'legacy':
                    require(raw.get('source_freeze_sha256') == freeze_sha and raw.get('frozen_source_binding_matches') is True
                            and raw.get('qt_platform') == 'windows', 'Current actual freeze/native QPA differs.')
                    source_stable(raw, data['source_sha256'])
                    old = load(ROOT / 'verification/full-290/execution-attempt2/current29/actual/window.json')
                    require(raw.get('checks') == old['checks'] and len(raw['checks']) == 29, 'Original29 workflows not retained completely.')
            else:
                expected = {name: ({**data['source_sha256'], **data['supplemental_public_inputs_sha256']})[name]
                            for name in data['p3_script_selected_paths'][mode]}
                source_stable(raw, expected, original287=mode == 'p3_287')
                if mode == 'p3_287':
                    old287 = load(ROOT / 'verification/full-290/p3-supplementary-attempt2/p3_287/actual/p3-window.json')
                    require(raw.get('checks') == old287['checks'] and raw.get('game_captures') == raw.get('chat_sends') == 0
                            and raw.get('private_state_loaded') is False and raw.get('qt_exit_code') == 0
                            and all(type(row.get('hwnd')) is int and row['hwnd'] > 0 for row in raw.get('stages', []))
                            and len(raw.get('stages', [])) == 2, 'Complete original287 native checks not retained.')
                else:
                    paths = raw.get('state_paths_replaced_before_constructor')
                    require(raw.get('qpa') == 'windows' and raw.get('qt_exit_code') == 0 and type(raw.get('process_id')) is int
                            and raw.get('game_captures') == 0 and raw.get('game_operated') is False and raw.get('chat_sent') is False
                            and (paths is True or paths == ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE']),
                            'Actual native QPA/exit/state/external boundary failed: ' + mode)
                # Each unchanged canonical script itself verifies its exact HWND,
                # controls, identities, temporary paths, screenshots and scopes.
                details[mode] = {'receipt_sha256': close['actual_receipt_sha256'], 'actual_fixture_pid': raw.get('process_id'),
                    'owned_launcher_pid': supers[mode]['pid'], 'checks': raw.get('unique_checks', raw.get('completed_check_count', len(raw.get('checks', [])))),
                    'screenshots': raw.get('screenshots', raw.get('visible_stages', raw.get('stages', []))), 'source_count': len(expected),
                    'original287_single_map_and_no_PID_field_preserved_with_fresh_outer_postguard': mode == 'p3_287'}
        except (KeyError, ValueError, OSError, TypeError) as error:
            findings.append({'component': mode, 'error_type': type(error).__name__, 'message': str(error)})
    current30_unavailable = False
    if 'current30' in actuals and 'current29' in actuals:
        raw = actuals['current30']; sup = supers['current30']; close = closures['current30']
        if raw.get('passed') is True:
            if not (sup.get('supervisor_exit') == sup.get('child_primary_exit') == close.get('actual_fixture_exit') == 0
                    and close.get('component_automated_passed') is True):
                findings.append({'component': 'current30', 'message': 'Passed raw receipt without actual child/supervisor0.'})
        else:
            failure = raw.get('failure') or {}; trace = failure.get('traceback', ''); message = failure.get('message', '')
            current30_unavailable = (failure.get('type') == 'OSError' and '[WinError 1314]' in message
                and 'public-261-never-create.txt' in message and 'diagnostic.symlink_to(public_target.name)' in trace
                and 'pathlib.py' in trace and 'os.symlink(' in trace and sup.get('child_primary_exit') == sup.get('supervisor_exit') == 1
                and close.get('actual_fixture_exit') == 1 and actuals['current29'].get('passed') is True)
            if not current30_unavailable:
                findings.append({'component': 'current30', 'message': 'Actual30 failure is not the exact original symlink WinError1314 prerequisite; no substitution allowed.'})
    try:
        child = [str(ROOT / '.venv/Scripts/python.exe'), '-B', '-X', 'utf8', str(BASE / 'readback_child305.py'),
                 '--legacy-container', str(container / 'legacy'), *shared]
        terminal(container / 'legacy_typed', child)
        invocation = load(container / 'legacy/full305-typed-audit-invocation.json')
        raw_path = container / 'legacy/independent-saved-readback-audit.json'; audit = load(raw_path)
        require(invocation.get('actual_auditor_exit') == 0 and invocation.get('passed') is True
                and invocation.get('actual_audit_sha256') == sha(raw_path)
                and invocation.get('original_source_sha256') == data['original_typed_auditor_sha256'], 'Original complete typed auditor not actual0.')
        require(audit.get('passed') is True and audit.get('complete_runtime_checks') == 4283 and audit.get('saved_rows') == 52
                and audit.get('current_revised_assertions') == 862 and audit.get('readonly_trace_empty_rows_not_invented') == 26
                and audit.get('exact_ten_admission_indices') == [18,19,20,21,38,39,40,41,44,45]
                and audit.get('original552_maintry_sha256') == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922',
                'Original full typed/readback range differs.')
        details['legacy'] = {key: audit[key] for key in ('complete_runtime_checks', 'saved_rows', 'passed_flag_records', 'metadata_records',
            'current_revised_assertions', 'original552_maintry_sha256', 'readonly_trace_empty_rows_not_invented', 'exact_ten_admission_indices')}
        details['legacy'].update(actual_original_typed_exit=0, audit_sha256=sha(raw_path), explicit_three_text_requests=156,
                                 original_projection_scope=42, all_original552_body_preserved=True)
    except (KeyError, ValueError, OSError, TypeError) as error:
        findings.append({'component': 'legacy_typed', 'error_type': type(error).__name__, 'message': str(error)})
    bound(parent, freeze_sha, activation_sha)
    result = {'automated_available_scope_passed': not findings, 'available_checks_passed': None,
              'final_public_summary_requires_root_visual_review_and_seal': True, 'scope_not_reduced': True,
              'complete_repository_validation': False, 'P2_complete': False,
              'current30_original_actual_symlink_prerequisite_unavailable': current30_unavailable,
              'Linux_WSL_Wine_or_historical_private_Windows_verified': False,
              'all_component_sources_fresh305_not_reused290_PASS': True, 'root_freeze_sha256': freeze_sha,
              'component_details': details, 'review_failures': findings,
              'assigned_owned_jobs_empty_not_a_claim_about_unassigned_or_preexisting_processes': True,
              'PNG_visual_inspection_claimed': False}
    write_new(container / 'automated-scope-review.json', result)
    return result
