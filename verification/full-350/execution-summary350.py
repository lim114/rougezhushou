"""Seal full350 from attempt2 plus the explicit same-source312 default-budget recheck.

Run only after attempt2 archive and root-visual-review.json exist.  Imports and
verification are read-only until all gates pass.  Preserve attempt2 root exit1
and its60s312 failure; only the complete, separately owned120s312 recheck fills
that available-scope gap.  Never claim one all-green full run or faster latency.
Creates summary.json and execution-summary350.py once.
"""
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.cache/full350-attempt2'
sys.path.insert(0, str(BASE))
from full350_common import bound, sha, FREEZE
from review_results350 import terminal, closure, source_stable

PARENT = '87b3f79683d0a406ae2d544502323e9239003a70'
FROZEN = '57d5b8b33a978ebbbc5af3f7331c9dc4f5045a4b1f306fd5cb62190c8101742e'
ACTIVATION = '9cc98f9c6df9036b9d26fdcb3fa3b683489345443c6a3cf8316148c8e7b93e28'
ARCHIVE = 'verification/full-350/execution-attempt2'
PREVIOUS_ARCHIVE = 'verification/full-350/execution-attempt1'
VISUAL = 'verification/full-350/root-visual-review.json'
RECHECK = 'verification/full-350/recheck-p3-312-default'
RECHECK_BASE = ROOT / '.cache/full350-312-recheck'


def require(value, message):
    if not value:
        raise ValueError(message)


def public(name):
    require(type(name) is str, 'A public relative path is required.')
    rel = PurePosixPath(name)
    require(not rel.is_absolute() and '..' not in rel.parts and '\\' not in name
            and ':' not in name and rel.as_posix() == name, 'Unsafe public path: ' + name)
    path = ROOT.joinpath(*rel.parts)
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT),
            'Missing or linked public file: ' + name)
    for parent in path.parents:
        if parent == ROOT:
            break
        require(not parent.is_symlink(), 'Linked public parent: ' + name)
    return path


def read(name):
    return json.loads(public(name).read_bytes())


def ref(name):
    return {'path': name, 'sha256': sha(public(name))}


def verify_archive(prefix, attempt):
    name = prefix + '/archive-manifest.json'
    manifest = read(name)
    require(manifest['section'] == 350 and manifest['actual_validation_attempt'] == attempt,
            'Wrong archive section or attempt.')
    require(manifest['required_component_positions'] == 70
            and manifest['all_original_ordered_components_retained'] is True
            and manifest['all_executed_retained_Popen_and_assigned_jobs_terminal'] is True
            and manifest['all_actual_root_identifiers_not_live_at_archive'] is True,
            'Incomplete or nonterminal archive.')
    require(type(manifest['files']) is dict and bool(manifest['files']), 'Archive has no files.')
    for relative, pin in manifest['files'].items():
        path = public(prefix + '/' + relative)
        require(sha(path) == pin['sha256'] and path.stat().st_size == pin['bytes'],
                'Archived bytes changed: ' + relative)
    return manifest


def verify_visual(archive, recheck_archive):
    """Root creates this receipt after direct review; hashes alone are not review."""
    visual = read(VISUAL)
    images = {ARCHIVE + '/' + name: pin['sha256']
              for name, pin in archive['files'].items()
              if name.endswith('.png') and len(PurePosixPath(name).parts) == 3
              and PurePosixPath(name).parts[1] == 'actual'}
    images.update({RECHECK + '/' + name: pin['sha256']
                   for name, pin in recheck_archive['files'].items()
                   if name.endswith('.png') and len(PurePosixPath(name).parts) == 3
                   and PurePosixPath(name).parts[:2] == ('p3_312', 'actual')})
    require(bool(images), 'No actual attempt2 native screenshots.')
    require(visual.get('section') == 350 and visual.get('all_reviewed') is True
            and visual.get('source_freeze_sha256') == FROZEN
            and visual.get('archive_manifest_sha256') == sha(public(ARCHIVE + '/archive-manifest.json'))
            and visual.get('recheck_archive_manifest_sha256') == sha(public(RECHECK + '/archive-manifest.json')),
            'Root visual review is not bound to attempt2 and the separate312 recheck.')
    rows = visual['images']
    require(type(rows) is list and len(rows) == len(images)
            and {r['file']: r['sha256'] for r in rows} == images,
            'Root review does not cover every attempt2 and separate312 PNG exactly once.')
    for row in rows:
        require(row.get('reviewed') is True and sha(public(row['file'])) == row['sha256'],
                'PNG review or current bytes missing.')
        method = row['method']
        if method == 'previous_root_same_bytes':
            require(sha(public(row['reviewed_file'])) == row['sha256']
                    and sha(public(row['review_receipt'])) == row['review_receipt_sha256'],
                    'Prior same-byte review binding differs.')
            previous = read(row['review_receipt'])
            require((previous.get('all_reviewed') is True
                     or (row['review_receipt'] == 'verification/full-350/repair/root-visual.json'
                         and previous.get('all_repair_images_reviewed') is True))
                    and any(r.get('file') == row['reviewed_file'] and r.get('sha256') == row['sha256']
                            and r.get('reviewed') is True for r in previous.get('images', [])),
                    'Prior receipt does not actually review that exact PNG.')
        elif method == 'same_byte_reuse':
            require(any(r['file'] == row['representative_file'] and r['sha256'] == row['sha256']
                        and r['method'] != 'same_byte_reuse' and r.get('reviewed') is True for r in rows),
                    'Same-byte review has no independently reviewed representative.')
        elif method == 'contact_sheet_review':
            sheet = read(row['contact_sheet_receipt'])
            require(sheet.get('root_viewed') is True and sha(public(sheet['file'])) == sheet['sha256']
                    and any(r['file'] == row['file'] and r['sha256'] == row['sha256']
                            for r in sheet['members']), 'Contact-sheet review binding differs.')
        else:
            require(method == 'direct_view', 'Unknown visual-review method.')
    return images


def verify_312_recheck(freeze, failed_raw):
    """Verify original120s canonical workflow without erasing the failed60s run."""
    receipt = read(RECHECK + '/receipt.json')
    require(receipt['section'] == 350 and receipt['passed'] is True
            and receipt['root_freeze_sha256'] == FROZEN and receipt['source_unchanged'] is True
            and receipt['original60s_pass_claimed'] is False
            and receipt['normal_latency_improvement_claimed'] is False,
            'Wrong or unsupported312 recheck receipt.')
    names = {'profile': '/profile.json', 'window': '/p3_312/actual/window.json',
             'closure': '/p3_312/actual/full350-source-closure.json', 'step': '/p3_312/step.json',
             'root_process': '/root-launch/controller-process.json',
             'archive_manifest': '/archive-manifest.json'}
    for key, suffix in names.items():
        require(receipt[key] == ref(RECHECK + suffix), 'Recheck receipt binding differs: ' + key)
    archive = read(RECHECK + '/archive-manifest.json')
    require(type(archive['files']) is dict and bool(archive['files']), 'No312 recheck archive files.')
    for name, pin in archive['files'].items():
        path = public(RECHECK + '/' + name)
        require(sha(path) == pin['sha256'] and path.stat().st_size == pin['bytes'],
                '312 archived bytes changed: ' + name)
    for name in ('profile.json', 'authority.json', 'result.json', 'root-launch/controller-process.json',
                 'root-launch/process.exit', 'p3_312/step.json', 'p3_312/controller-process.json',
                 'p3_312/supervisor.json', 'p3_312/process.exit', 'p3_312/process-exit-origin.json',
                 'p3_312/actual/window.json', 'p3_312/actual/full350-source-closure.json'):
        require(name in archive['files'], '312 archive omits original evidence: ' + name)
    profile = read(RECHECK + '/profile.json')
    target = ROOT / freeze['p3_scripts']['p3_312']
    require(profile['section'] == 350 and profile['component'] == 'p3_312'
            and profile['kind'] == 'complete_same_source_canonical_default_budget_recheck'
            and profile['parent_commit'] == PARENT and profile['root_freeze_sha256'] == FROZEN
            and profile['activation_sha256'] == ACTIVATION
            and profile['original_failed_visible_ms'] == 60000
            and profile['recheck_visible_ms'] == profile['canonical_default_ms'] == 120000
            and profile['product_source_changed'] is False and profile['canonical_fixture_changed'] is False
            and profile['full_suite_rerun'] is False and profile['original60s_pass_claimed'] is False
            and profile['normal_player_latency_improvement_claimed'] is False
            and profile['all_checks_and_three_subjects_retained'] is True
            and profile['first_failure'] == ARCHIVE + '/p3_312/actual/window.json'
            and profile['fixture_sha256'] == freeze['source_sha256'][freeze['p3_scripts']['p3_312']] == sha(target)
            and profile['child_sha256'] == sha(RECHECK_BASE / 'component_child350_recheck.py')
            and profile['original_child_sha256'] == sha(BASE / 'component_child350.py'),
            '312 recheck profile or unchanged executed sources differ.')
    actual_close = read(RECHECK + '/p3_312/actual/full350-source-closure.json')
    original_receipt = Path(actual_close['actual_argv'][2])
    original_container = original_receipt.parents[2]
    require(original_container.is_absolute() and not original_container.is_relative_to(ROOT)
            and original_container.name.startswith('rouge-full350-312-recheck-')
            and original_receipt == original_container / 'p3_312/actual/window.json',
            'Wrong isolated312 recheck namespace.')
    python = str(ROOT / '.venv/Scripts/python.exe')
    shared = ['--expected-parent-commit', PARENT, '--freeze-sha256', FROZEN, '--activation-sha256', ACTIVATION]
    child = [python, '-B', '-X', 'utf8', str(RECHECK_BASE / 'component_child350_recheck.py'),
             '--mode', 'p3_312', '--out', str(original_container / 'p3_312/actual'), *shared]
    folder = ROOT / RECHECK / 'p3_312'
    supervisor = terminal(folder, child, success=True)
    value, close = closure(folder, 'p3_312', FROZEN, ACTIVATION, target,
                           [str(target), '--receipt', str(original_receipt), '--visible-ms', '120000'], success=True)
    root = read(RECHECK + '/root-launch/controller-process.json')
    require(root['section'] == 350 and root['status'] == 'completed'
            and root['actual_observed_exit'] == 0 and root['owned_popen_retained'] is True
            and root['exit_observed_directly_from_retained_popen'] is True
            and root['argv'] == [python, '-B', '-X', 'utf8', str(RECHECK_BASE / 'run.py'), '--coordinator']
            and root['runner_sha256_at_launch'] == sha(RECHECK_BASE / 'run.py')
            and root['profile_sha256'] == receipt['profile']['sha256']
            and public(RECHECK + '/root-launch/process.exit').read_text('ascii').strip() == '0',
            'Independent312 retained root exit or launch binding differs.')
    authority = read(RECHECK + '/authority.json')
    require(authority['section'] == 350 and authority['root'] == str(ROOT)
            and authority['parent_commit'] == PARENT and authority['root_freeze_sha256'] == FROZEN
            and authority['activation_sha256'] == ACTIVATION
            and authority['profile_sha256'] == receipt['profile']['sha256']
            and authority['runner_sha256'] == root['runner_sha256_at_launch']
            and authority['child_sha256'] == profile['child_sha256']
            and datetime.fromisoformat(root['started_at']) <= datetime.fromisoformat(authority['created_at'])
            <= datetime.fromisoformat(root['finished_at']), 'Independent312 root authority differs.')
    result = read(RECHECK + '/result.json')
    step = read(RECHECK + '/p3_312/step.json')
    require(result['section'] == 350 and result['passed'] is True and result['row'] == step
            and step['name'] == 'p3_312' and step['status'] == 'terminal'
            and step['timed_out'] is False and step['owned_job_no_live_execution_verified'] is True
            and result['original60s_pass_claimed'] is False and result['normal_latency_improvement_claimed'] is False,
            'Independent312 actual step/result differs.')
    all_sources = {**freeze['source_sha256'], **freeze['supplemental_public_inputs_sha256']}
    selected = {name: all_sources[name] for name in freeze['p3_script_selected_paths']['p3_312']}
    source_stable(value, selected)
    first = read(PREVIOUS_ARCHIVE + '/p3_312/actual/window.json')
    require(value['passed'] is True and value['failure'] is None and value['qpa'] == 'windows'
            and value['qt_exit_code'] == 0 and type(value['process_id']) is int
            and value['verification_window_closed'] is True and value['temporary_state_root'] is True
            and value['private_state_read_copied_or_restored'] is False
            and value['state_paths_replaced_before_constructor'] == ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE']
            and value['game_captures'] == 0 and value['game_operated'] is False and value['chat_sent'] is False
            and value['checks'] == first['checks'] and value['unique_checks'] == len(first['checks']) == 31
            and value['source_sha256_before'] == failed_raw['source_sha256_before']
            and len(value['actual_entry_overviews']) == 3 and len(value['actual_topic_readings']) == 12
            and len(value['same_identity_refresh_observations']) == 6 and value['screenshot_count'] == 5
            and len(value['screenshots']) == 5 and value['source_negative_fixture']['restored_exact_bytes'] is True,
            'Complete original312 checks, source, subjects, readings or state boundary differ.')
    for key in ('actual_entry_overviews', 'actual_topic_readings'):
        def identities(rows):
            return [{k: row[k] for k in ('identity', 'topic_ids', 'topic_id') if k in row} for row in rows]
        require(identities(value[key]) == identities(first[key]), '312 subject/topic range differs: ' + key)
    for row in value['same_identity_refresh_observations']:
        require(row['before'] == row['after'] and row['before']['vertical'] > 0,
                '312 complete nonzero refresh preservation differs.')
    calls = value['external_operation_attempts']
    require(type(calls) is dict and len(calls) == 8 and all(type(v) is int and v == 0 for v in calls.values()),
            '312 external operations were attempted.')
    for image in value['screenshots']:
        require(sha(public(RECHECK + '/p3_312/actual/' + Path(image['path']).name)) == image['sha256'],
                '312 recheck actual image bytes differ.')
    proof = {'receipt': receipt['window'], 'source_closure': receipt['closure'], 'actual_fixture_exit': 0,
             'complete_independent_recheck': ref(RECHECK + '/receipt.json'),
             'original_failed60s_receipt': ref(ARCHIVE + '/p3_312/actual/window.json'),
             'source_identical_to_attempt2': True, 'recheck_visible_ms': 120000,
             'original60s_pass_claimed': False, 'normal_latency_improvement_claimed': False}
    details = {'receipt_sha256': receipt['window']['sha256'], 'actual_fixture_pid': value['process_id'],
               'owned_launcher_pid': supervisor['pid'], 'checks': value['unique_checks'],
               'screenshots': value['screenshots'], 'source_count': len(selected),
               'original287_single_map_and_no_PID_field_preserved_with_fresh_outer_postguard': False}
    return archive, proof, details


def main():
    final_path = ROOT / 'verification/full-350/summary.json'
    saved_script = ROOT / 'verification/full-350/execution-summary350.py'
    require(not final_path.exists() and not saved_script.exists(), 'Never overwrite an existing summary.')
    freeze, activation = bound(PARENT, FROZEN, ACTIVATION)
    require(FREEZE == ROOT / 'verification/full-350/source-freeze-attempt2.json'
            and freeze['actual_validation_attempt'] == 2, 'Wrong final freeze.')
    archive = verify_archive(ARCHIVE, 2)
    original_archive = verify_archive(PREVIOUS_ARCHIVE, 1)
    require(archive['source_freeze_sha256'] == FROZEN and archive['activation_sha256'] == ACTIVATION,
            'Archive freeze or activation differs.')
    require(sha(public(ARCHIVE + '/source-freeze.json')) == FROZEN
            and sha(public(ARCHIVE + '/activation350.json')) == ACTIVATION,
            'Archived authority bytes differ.')
    require(archive['actual_root_controller_exit'] == 1, 'Preserved attempt2 retained root exit must remain1.')
    authority = read(ARCHIVE + '/owned-execution.json')
    require(authority['section'] == 350 and authority['actual_validation_attempt'] == 2
            and authority['kind'] == 'FULL350_ROOT_OWNED_SERIAL_FULL_EXECUTION_ATTEMPT2'
            and authority['root'] == str(ROOT) and authority['parent_commit'] == PARENT
            and authority['root_freeze_sha256'] == FROZEN and authority['activation_sha256'] == ACTIVATION
            and authority['controller_sha256'] == sha(BASE / 'run_full350_controller.py'),
            'Actual root authority differs.')
    once = read(ARCHIVE + '/full350-once.json')
    require(once['section'] == 350 and once['root_freeze_sha256'] == FROZEN
            and once['explicit_root_execute'] is True and once['automatic_retry_allowed'] is False,
            'Wrong actual execution namespace declaration.')
    original_container = Path(once['container'])
    require(original_container.is_absolute() and not original_container.is_relative_to(ROOT)
            and original_container.name.startswith('rouge-full350-attempt2-')
            and archive['raw_namespace_preserved_in_original_bytes'] == str(original_container),
            'Wrong original attempt2 namespace.')
    shared = ['--expected-parent-commit', PARENT, '--freeze-sha256', FROZEN, '--activation-sha256', ACTIVATION]
    python = str(ROOT / '.venv/Scripts/python.exe')
    root_process = read(ARCHIVE + '/root-launch/controller-process.json')
    require(root_process['section'] == 350 and root_process['status'] == 'completed'
            and root_process['actual_observed_exit'] == 1 and root_process['owned_popen_retained'] is True
            and root_process['exit_observed_directly_from_retained_popen'] is True
            and root_process['exit_inferred_from_output_json'] is False
            and root_process['argv'] == [python, '-B', '-X', 'utf8', str(BASE / 'run_full350_controller.py'), '--execute', *shared]
            and public(ARCHIVE + '/root-launch/process.exit').read_text('ascii').strip() == '1',
            'Actual retained root Popen record differs.')
    require(datetime.fromisoformat(root_process['started_at']) <= datetime.fromisoformat(authority['created_at'])
            <= datetime.fromisoformat(root_process['finished_at']), 'Root authority is outside observed invocation.')

    previous = read('verification/full-335/source-freeze-binding-recheck2.json')
    require(len(freeze['selectors']) == 569 and len(set(freeze['selectors'])) == 569
            and len(freeze['p3_scripts']) == 65
            and freeze['selectors'][:len(previous['selectors'])] == previous['selectors']
            and list(freeze['p3_scripts'])[:len(previous['p3_scripts'])] == list(previous['p3_scripts']),
            'Complete maintained scope/order was reduced.')
    expected = ['offline', 'legacy', 'legacy_typed', 'current30', 'current29', *freeze['p3_scripts']]
    orchestration = read(ARCHIVE + '/orchestration.json')
    review = read(ARCHIVE + '/automated-scope-review.json')
    require(len(expected) == 70 and orchestration['status'] == 'all_required_components_terminal'
            and orchestration['required_components'] == expected == [r['name'] for r in orchestration['steps']],
            'Not all 70 required positions actually ran in order.')
    require(orchestration['automated_available_scope_passed'] is False
            and review['automated_available_scope_passed'] is False
            and len(review['review_failures']) == 1 and review['review_failures'][0]['component'] == 'p3_312'
            and orchestration['review_failures'] == review['review_failures']
            and review['root_freeze_sha256'] == FROZEN and review['scope_not_reduced'] is True,
            'Attempt2 must preserve its exact single312 available-scope failure.')
    raw, closures, supervisors, component_proofs = {}, {}, {}, {}
    for step in orchestration['steps']:
        mode = step['name']
        require(step['status'] == 'terminal' and step['terminal_supervisor_and_job_verified'] is True
                and step['owned_job_no_live_execution_verified'] is True and step['timed_out'] is False,
                'Missing actual terminal component: ' + mode)
        folder = ROOT / ARCHIVE / mode
        original_folder = original_container / mode
        if mode == 'legacy_typed':
            child = [python, '-B', '-X', 'utf8', str(BASE / 'readback_child350.py'),
                     '--legacy-container', str(original_container / 'legacy'), *shared]
        else:
            child = [python, '-B', '-X', 'utf8', str(BASE / 'component_child350.py'),
                     '--mode', mode, '--out', str(original_folder / 'actual'), *shared]
        supervisors[mode] = terminal(folder, child, success=mode not in ('current30', 'p3_312'))
        require(step == read(ARCHIVE + '/' + mode + '/step.json'), 'Root/step ledger mismatch: ' + mode)
        if mode == 'legacy_typed':
            continue
        if mode == 'offline':
            target = ROOT / 'scripts/verify_full_available.py'
            argv = [str(target), '--output', str(original_folder / 'actual/windows-offline.json'), '--verbosity', '2']
        elif mode in ('legacy', 'current30', 'current29'):
            target = BASE / ('bound-legacy' if mode == 'legacy' else 'bound-current') / 'launcher275.py'
            argv = [str(target), '--root', str(ROOT), '--out', str(original_folder / 'actual'), '--mode', mode]
        else:
            target = ROOT / freeze['p3_scripts'][mode]
            argv = [str(target), '--receipt', str(original_folder / 'actual/window.json')]
            options = freeze['p3_script_options'][mode]
            if options.get('explicit_current_source_freeze'):
                argv += ['--source-freeze', str(FREEZE)]
            if options['accepts_visible_ms']:
                argv += ['--visible-ms', str(options['visible_ms'])]
        value, close = closure(folder, mode, FROZEN, ACTIVATION, target, argv,
                               success=mode not in ('current30', 'p3_312'))
        raw[mode], closures[mode] = value, close
        receipt_name = ARCHIVE + '/' + mode + '/actual/' + close['actual_receipt_file']
        component_proofs[mode] = {'receipt': ref(receipt_name),
                                 'source_closure': ref(ARCHIVE + '/' + mode + '/actual/full350-source-closure.json'),
                                 'actual_fixture_exit': close['actual_fixture_exit']}
        if mode == 'offline':
            require(value['selectors'] == freeze['selectors'] and value['source_sha256'] == freeze['source_sha256']
                    and value['source_drift'] == [] and value['failed_cases'] == [] and value['verbosity'] == 2
                    and value['platform'] == 'Windows' and value['wine_compatibility'] is False
                    and value['failures'] == value['errors'] == 0 and value['available_checks_passed'] is True
                    and value['qt_shutdown_error'] is None, 'Complete offline scope/source/result differs.')
        elif mode in ('legacy', 'current30', 'current29'):
            launch = read(ARCHIVE + '/' + mode + '/actual/native275-launcher-closure.json')
            require(launch['root_freeze_sha256'] == FROZEN and launch['source_drift'] == []
                    and launch['executed_tool_drift'] == [] and launch['fixture_exception'] is None
                    and launch['qt_cleanup_error'] is None
                    and launch['actual_current_native_windows_window_verified'] is True
                    and value['source_drift'] == [], 'Actual native launcher/source closure differs: ' + mode)
            if mode != 'legacy':
                require(value['source_freeze_sha256'] == FROZEN and value['frozen_source_binding_matches'] is True
                        and value['qt_platform'] == 'windows', 'Current native binding differs.')
                source_stable(value, freeze['source_sha256'])
        else:
            all_sources = {**freeze['source_sha256'], **freeze['supplemental_public_inputs_sha256']}
            selected = {name: all_sources[name] for name in freeze['p3_script_selected_paths'][mode]}
            source_stable(value, selected, original287=mode == 'p3_287')
            if mode == 'p3_312':
                failure = value['failure']
                first312 = read(PREVIOUS_ARCHIVE + '/p3_312/actual/window.json')
                require(options['visible_ms'] == 60000 and value['passed'] is False
                        and failure['type'] == 'TimeoutError'
                        and failure['message'] == 'The documentary native fixture did not finish before its deadline.'
                        and supervisors[mode]['child_primary_exit'] == supervisors[mode]['supervisor_exit']
                        == close['actual_fixture_exit'] == 1
                        and close['actual_receipt_passed'] is False and close['component_automated_passed'] is False
                        and value['unique_checks'] == 29 and value['checks'] == first312['checks'][:-2]
                        and len(value['actual_entry_overviews']) == 3 and len(value['actual_topic_readings']) == 12
                        and len(value['same_identity_refresh_observations']) == 6
                        and value['screenshot_count'] == 5 and value['verification_window_closed'] is True
                        and value['temporary_state_root'] is True and value['private_state_read_copied_or_restored'] is False
                        and type(value['external_operation_attempts']) is dict
                        and len(value['external_operation_attempts']) == 8
                        and all(type(v) is int and v == 0 for v in value['external_operation_attempts'].values()),
                        '312 original failure differs from preserved full-workflow60s deadline failure.')
            if mode == 'p3_287':
                old = read('verification/full-290/p3-supplementary-attempt2/p3_287/actual/p3-window.json')
                require(value['checks'] == old['checks'] and value['game_captures'] == value['chat_sends'] == 0
                        and value['private_state_loaded'] is False and value['qt_exit_code'] == 0
                        and len(value['stages']) == 2 and all(type(s['hwnd']) is int and s['hwnd'] > 0 for s in value['stages']),
                        'Complete original287 native checks differ.')
            elif int(mode.split('_')[1]) <= 312:
                paths = value.get('state_paths_replaced_before_constructor')
                require(value['qpa'] == 'windows' and value['qt_exit_code'] == (1 if mode == 'p3_312' else 0)
                        and type(value['process_id']) is int
                        and value['game_captures'] == 0 and value['game_operated'] is False and value['chat_sent'] is False
                        and (paths is True or paths == ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE']),
                        'Native/state boundary differs: ' + mode)
            else:
                calls = value.get('external_operation_attempts')
                require(value['qpa'] == 'windows' and value['qt_exit_code'] == 0 and type(value['process_id']) is int
                        and value['game_operated'] is False and value['chat_sent'] is False
                        and value['verification_window_closed'] is True and value['temporary_state'] is True
                        and value['private_contents_read_copied_or_restored'] is False
                        and type(calls) is dict and len(calls) == 7
                        and all(type(v) is int and v == 0 for v in calls.values()),
                        'Current native/state/external boundary differs: ' + mode)

    typed_name = ARCHIVE + '/legacy/independent-saved-readback-audit.json'
    typed = read(typed_name)
    invocation = read(ARCHIVE + '/legacy/full350-typed-audit-invocation.json')
    require(invocation['actual_auditor_exit'] == 0 and invocation['passed'] is True
            and invocation['actual_audit_sha256'] == sha(public(typed_name))
            and invocation['original_source_sha256'] == freeze['original_typed_auditor_sha256'],
            'Complete typed auditor invocation differs.')
    require(typed['passed'] is True and typed['saved_rows'] == 52 and typed['complete_runtime_checks'] == 4283
            and typed['current_revised_assertions'] == 862 and typed['readonly_trace_empty_rows_not_invented'] == 26
            and typed['exact_ten_admission_indices'] == [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]
            and typed['original552_maintry_sha256'] == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922',
            'Complete legacy typed assertion range differs.')
    c30, c29 = raw['current30'], raw['current29']
    old29 = read('verification/full-290/execution-attempt2/current29/actual/window.json')
    require(c29['passed'] is True and c29['checks'] == old29['checks'] and len(c29['checks']) == 29,
            'Original current29 workflow range differs.')
    symlink_passed = c30['passed'] is True
    if symlink_passed:
        require(supervisors['current30']['child_primary_exit'] == supervisors['current30']['supervisor_exit']
                == closures['current30']['actual_fixture_exit'] == 0
                and closures['current30']['component_automated_passed'] is True,
                'Original30 PASS lacks actual successful exits.')
    else:
        failure = c30['failure']
        require(failure['type'] == 'OSError' and '[WinError 1314]' in failure['message']
                and 'public-261-never-create.txt' in failure['message']
                and 'diagnostic.symlink_to(public_target.name)' in failure['traceback']
                and 'pathlib.py' in failure['traceback'] and 'os.symlink(' in failure['traceback']
                and supervisors['current30']['child_primary_exit'] == supervisors['current30']['supervisor_exit']
                == closures['current30']['actual_fixture_exit'] == 1
                and closures['current30']['component_automated_passed'] is False
                and review['current30_original_actual_symlink_prerequisite_unavailable'] is True,
                'Original30 failed for a reason other than actual1314; do not substitute29.')

    first_review = read(PREVIOUS_ARCHIVE + '/automated-scope-review.json')
    require(original_archive['actual_root_controller_exit'] == 1
            and {r['component'] for r in first_review['review_failures']}
            == {'offline', 'p3_291', 'p3_304', 'p3_305', 'p3_338'}, 'Original failure evidence differs.')
    repair_name = 'verification/full-350/repair/repair-scope.json'
    repair = read(repair_name)
    old_freeze = read('verification/full-350/source-freeze-attempt1.json')
    require(freeze['selectors'] == old_freeze['selectors']
            and list(freeze['p3_scripts']) == list(old_freeze['p3_scripts']), 'Repair reduced selectors or native components.')
    require(set(repair['files']) == {'rouge/node_catalog_view.py', 'scripts/verify_peace_guardian_window_291.py',
                                    'scripts/verify_current_reward_origins_window_338.py',
                                    'tests/test_documented_event_flow_view_321.py'}, 'Unexpected repair scope.')
    for name, pins in repair['files'].items():
        require(old_freeze['source_sha256'][name] == pins['before_sha256']
                and freeze['source_sha256'][name] == pins['after_sha256'] == sha(public(name)),
                'Repair source mapping differs: ' + name)
    for mode in ('p3_304', 'p3_305'):
        first = read(PREVIOUS_ARCHIVE + '/' + mode + '/actual/full350-source-closure.json')
        require(first['actual_fixture_exit'] == 0 and first['component_automated_passed'] is True,
                'Do not relabel an originally passing304/305 fixture as a fixture failure.')
    recheck_archive, recheck_proof, recheck_details = verify_312_recheck(freeze, raw['p3_312'])
    component_proofs['p3_312']['passed'] = False
    component_proofs['p3_312']['original_visible_ms'] = 60000
    effective_component_proofs = {**component_proofs, 'p3_312': recheck_proof}
    effective_component_details = {**review['component_details'], 'p3_312': recheck_details}
    images = verify_visual(archive, recheck_archive)
    for name, pin in freeze['functional_validation'].items():
        require(sha(public(pin['path'])) == pin['sha256'], 'Declared functional evidence changed: ' + name)
    offline = raw['offline']
    summary = {
        'after_section': 350, 'kind': 'functional_section_full_validation',
        'checked_at_UTC': datetime.now(timezone.utc).isoformat(),
        'available_checks_passed': True, 'complete_repository_validation': False, 'scope_not_reduced': True,
        'P3_complete': False, 'P2_complete': False, 'P1_complete': False,
        'actual_validation_attempt': 2, 'actual_root_controller_exit': 1,
        'validation_composition': 'Complete attempt2 plus complete same-source312 canonical120s recheck.',
        'single_available_scope_execution_all_green': False, 'complete_original30_passed': symlink_passed,
        'all_final_component_source_maps_share_one_freeze': True, 'current_worktree_validation_authority': True,
        'source_files': len(freeze['source_sha256']), 'maintained_selectors': len(freeze['selectors']),
        'supplemental_public_input_files': len(freeze['supplemental_public_inputs_sha256']),
        'source_freeze': 'verification/full-350/source-freeze-attempt2.json', 'source_freeze_sha256': FROZEN,
        'activation_sha256': ACTIVATION, 'tested_worktree_parent_commit': PARENT, 'source_drift': [],
        'actual_required_components': 70, 'native_supplements': 65,
        'native_current_windows_gui_verified': True, 'native_windows_game_chat_verified': False,
        'historical_original_Windows_verified': False, 'all_tests_executed_on_original_local_Windows': True,
        'cloud_test_execution_started': False,
        'archive_manifests_sha256': {p + '/archive-manifest.json': sha(public(p + '/archive-manifest.json'))
                                    for p in (PREVIOUS_ARCHIVE, ARCHIVE, RECHECK)},
        'root_PNG_visual_review': {**ref(VISUAL), 'images': len(images), 'appearance_only_not_unpictured_semantics': True},
        'offline_windows': {k: offline[k] for k in ('tests_run', 'tests_passed', 'historical_or_declared_skips',
                            'failures', 'errors', 'unavailable_records', 'unavailable_parent_count', 'qt_shutdown', 'qt_shutdown_error')},
        'actual_offline_process_exit': 0,
        'legacy_window': {**review['component_details']['legacy'], 'actual_typed_receipt': ref(typed_name)},
        'current_window': {'maintained_scope': 30, 'actual_full30_attempt_preserved': True,
                           'full30_actual_exit': closures['current30']['actual_fixture_exit'], 'current29_actual_exit': 0,
                           'available_original_workflows_passed': 30 if symlink_passed else 29,
                           'original_symlink_operation_passed': symlink_passed,
                           'unavailable_reason': None if symlink_passed else 'Actual Path.symlink_to/os.symlink WinError1314; not passed.'},
        'p3_supplementary_windows': {k: {**effective_component_details[k], **effective_component_proofs[k]}
                                     for k in freeze['p3_scripts']},
        'actual_component_proofs': effective_component_proofs,
        'original_attempt2_component_proofs': component_proofs,
        'original_complete_scope_review': ref(ARCHIVE + '/automated-scope-review.json'),
        'original_attempt1': {'actual_root_exit': 1, 'review_failures': first_review['review_failures'],
                              'fixture_failures': ['offline', 'p3_291', 'p3_338'],
                              'reviewer_only_argument_mismatches': ['p3_304', 'p3_305'],
                              'passed304305_fixtures_not_mislabelled_as_failures': True,
                              'archive': ref(PREVIOUS_ARCHIVE + '/archive-manifest.json')},
        'original_attempt2': {'actual_root_exit': 1, 'automated_available_scope_passed': False,
                              'review_failures': review['review_failures'],
                              'failed_component': 'p3_312', 'failed_visible_ms': 60000,
                              'original_failure': ref(ARCHIVE + '/p3_312/actual/window.json'),
                              'archive': ref(ARCHIVE + '/archive-manifest.json'),
                              'not_relabelled_as_single_all_green_run': True},
        '312_complete_default_budget_recheck': {**ref(RECHECK + '/receipt.json'), **recheck_proof,
                                               'canonical_fixture_source_unchanged': True,
                                               'all_three_subjects_and_all31_checks_retained': True,
                                               'complete_suite_rerun_for_budget_change': False},
        'maintenance_reconciliation': {**ref(repair_name), 'complete_attempt2_reexecuted_after_repair': True,
                                       'mechanics_changed': False, 'new_functional_section_count_added': False},
        '311_current300s_complete_workflow_profile_only': True, '311_original120s_budget_PASS_claimed': False,
        '311_previous120s_failure_retained': 'verification/full-320/summary.json',
        '311_profile_is_not_normal_latency_benchmark': True, 'repeated_refresh_performance_issue_closed': False,
        '312_original60s_budget_PASS_claimed': False, '312_default120s_complete_workflow_only': True,
        '312_profile_is_not_normal_latency_benchmark': True, '312_latency_improvement_claimed': False,
        'functional350_necessary_and_native': freeze['functional_validation'],
        'unavailable_scopes': ([] if symlink_passed else ['Original actual symlink1314 is unavailable, not passed.'])
                              + ['Original Linux/WSL/Wine and historical private Windows samples remain unverified.',
                                 'No live game sampling, game operation or chat request.'],
        'root_wrapper_bytes_saved_at_archive_not_claimed_as_launch_time_hash': True,
        'assigned_owned_jobs_empty_not_global_descendant_enumeration': True,
        'current_wrap_up_threshold_percent': 15,
    }
    bound(PARENT, FROZEN, ACTIVATION)
    # Create-only outputs. No source/data/test/window/state mutation is performed.
    payload = (json.dumps(summary, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    with final_path.open('xb') as stream:
        stream.write(payload)
    with saved_script.open('xb') as stream:
        stream.write(Path(__file__).read_bytes())
    print(json.dumps({'available_scope_passed': True, 'actual_validation_attempt': 2,
                      'tests_run': offline['tests_run'], 'native_supplements': 65,
                      'PNG_scope': len(images), 'scope_not_reduced': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
