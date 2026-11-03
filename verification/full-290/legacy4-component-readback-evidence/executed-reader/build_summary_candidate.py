"""Strict public-evidence readback into a CACHE candidate, never public summary.

No tests, GUI, source freeze, private state or network calls. Missing, failed or
unreviewed evidence raises before a candidate is written. Root owns both the
human screenshot review receipt and the final public publication decision.
"""
import argparse
import ast
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FULL = ROOT / 'verification/full-290'
MAIN = FULL / 'execution-attempt2'
P3 = FULL / 'p3-supplementary-attempt2'
FREEZE = FULL / 'source-freeze-repair.json'
STEPS = ('offline', 'legacy', 'current30', 'current29')
P3_STEPS = tuple('p3_' + str(number) for number in range(286, 291))
INDICES = [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]
MAP_ORIGINALS = {
    'rouge/data/battle-maps/ro6_t_1.png': 'research/p3-map-direct-road-288/ro6_t_1-original.png',
    'rouge/data/battle-maps/ro6_t_3.png': 'research/p3-map-direct-road-288/ro6_t_3-original.png',
    'rouge/data/battle-maps/ro6_e_t_3.png': 'research/p3-map-direct-road-288/ro6_t_3-original.png',
}
A1_PINS = {
    'source-freeze.json': '489a0d4707060e379c8b6c2c6b50db6eea3b597d5c4066989df0713254ce48da',
    'execution-attempt1/archive-manifest.json': 'eaa1191537539370e3ee8f4a24e8dc00ffd27f56dc0b5329f259e8722c2932ea',
    'p3-supplementary-attempt1/archive-manifest.json': '1bacc56454ed94af133e5b92719ff3b3f0eb46269a3cfd56dc559ea71edecb8e',
}
CHECKS = []


def require(condition, name):
    if condition is not True:
        raise ValueError('Summary prerequisite failed: ' + name)
    CHECKS.append(name)


def regular(path, boundary=ROOT):
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(boundary.resolve()),
            'regular public file: ' + str(path))
    for parent in path.parents:
        if parent == boundary.resolve():
            break
        require(not parent.is_symlink(), 'no linked parent: ' + str(path))
    return path


def sha(path):
    return hashlib.sha256(regular(path).read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def read(path):
    return json.loads(regular(path).read_bytes())


def safe_child(folder, name):
    part = Path(name)
    require(not part.is_absolute() and '..' not in part.parts and '\\' not in name and part.as_posix() == name,
            'safe public relative member: ' + name)
    return regular(folder / part, folder)


def verify_archive(folder, freeze_sha, parent):
    manifest = read(folder / 'archive-manifest.json')
    require(manifest['source_freeze_sha256'] == freeze_sha and manifest['parent_commit'] == parent,
            folder.name + ' exact repair freeze and parent')
    for name, entry in manifest['files'].items():
        path = safe_child(folder, name)
        require(path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256'],
                folder.name + ' exact archived bytes: ' + name)
    require(sha(folder / 'root-source-freeze.json') == freeze_sha, folder.name + ' copied root freeze')
    return manifest


def verify_terminal(folder, expected_exit, supervisor_sha):
    supervisor = read(folder / 'supervisor.json')
    observed = read(folder / 'controller-process.json')
    origin = read(folder / 'process-exit-origin.json')
    actual_exit = int(regular(folder / 'process.exit').read_text(encoding='ascii').strip())
    require(supervisor['status'] == 'completed' and observed['status'] == 'completed', relative(folder) + ' terminal')
    require(supervisor['child_primary_exit'] == supervisor['supervisor_exit'] == observed['actual_observed_popen_exit'] == actual_exit == expected_exit,
            relative(folder) + ' independently observed actual exit')
    require(supervisor['timed_out'] is False and supervisor['owned_handle_retained'] is True
            and supervisor['owned_job_assigned'] is True and supervisor['owned_job_no_live_execution_verified'] is True,
            relative(folder) + ' real handle/job closed without timeout')
    require(supervisor['deadline_seconds'] == 1800 and supervisor['supervisor_sha256'] == supervisor_sha,
            relative(folder) + ' actual1800 and exact new supervisor')
    require(origin['kind'] == 'ACTUAL_RETAINED_POPEN_OBSERVED_SUPERVISOR_EXIT'
            and origin['derived_from_supervisor_json'] is False
            and origin['actual_observed_popen_exit'] == actual_exit
            and origin['process_exit_sha256'] == sha(folder / 'process.exit'),
            relative(folder) + ' original observed exit not derived')
    require(observed['argv'][9:] == supervisor['argv'], relative(folder) + ' same actual child argv')
    return supervisor


def qt_clean(value, name):
    require(isinstance(value, dict) and value.get('application_destroyed') is True
            and value.get('valid_wrappers_after_shutdown') == 0, name + ' real Qt teardown')


def native_window(folder, expected_pass, freeze_sha):
    closure = read(folder / 'actual/native275-launcher-closure.json')
    constructor = read(folder / 'actual/native275-constructor-ledger.json')
    require(closure['root_freeze_sha256'] == freeze_sha and closure['source_drift'] == []
            and closure['executed_tool_drift'] == [] and closure['qt_cleanup_error'] is None
            and closure['actual_current_native_windows_window_verified'] is True
            and closure['passed'] is expected_pass, relative(folder) + ' source-bound native closure')
    require(constructor['host_platform'] == 'win32' and constructor['original_class_reference_restored'] is True
            and constructor['production_source_edited'] is False
            and constructor['game_api_mocked'] is False and constructor['assertions_modified'] is False
            and constructor['calculation_input_or_result_rewritten'] is False
            and any(row.get('kind') == 'normal_public_constructor' and row.get('qt_platform') == 'windows'
                    for row in constructor['records'])
            and any(row.get('kind') == 'normal_public_show' and row.get('real_win32_window_visible') is True
                    for row in constructor['records']), relative(folder) + ' actual HWND/QPA and original constructor')
    qt_clean(closure['qt_cleanup'], relative(folder))
    return closure


def run(args):
    output = args.output.resolve()
    require(output.is_relative_to(HERE) and output.parent.is_dir() and not output.exists()
            and output.suffix == '.json', 'new cache-only candidate output')
    frozen = read(FREEZE)
    freeze_sha = sha(FREEZE)
    require(frozen['section'] == 290 and frozen['root_declared'] is True
            and frozen['actual_validation_attempt'] == 2, 'root actual attempt2 freeze')
    parent = frozen['parent_commit']
    require(subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
            and subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == parent,
            'exact current branch and tested parent before publication')
    a1 = read(FULL / 'source-freeze.json')
    require(frozen['selectors'] == a1['selectors'] and set(frozen['source_sha256']) == set(a1['source_sha256'])
            and set(frozen['supplemental_public_inputs_sha256']) == set(a1['supplemental_public_inputs_sha256']),
            'no selector/source/supplemental scope reduction from full attempt1')
    original275 = read(ROOT / 'verification/full-275/source-freeze-reset-repair.json')
    require(set(original275['selectors']) <= set(frozen['selectors']), 'all original408 selectors still included')
    all_sources = {**frozen['source_sha256'], **frozen['supplemental_public_inputs_sha256']}
    for name, expected in {**all_sources, **frozen['preparation_tools_sha256']}.items():
        require(sha(safe_child(ROOT, name)) == expected, 'fresh frozen source/control: ' + name)
    for name, expected in A1_PINS.items():
        require(sha(FULL / name) == expected, 'first actual failure evidence unchanged: ' + name)
    verify_archive(FULL / 'execution-attempt1', sha(FULL / 'source-freeze.json'), a1['parent_commit'])
    verify_archive(FULL / 'p3-supplementary-attempt1', sha(FULL / 'source-freeze.json'), a1['parent_commit'])
    first_timeout = read(FULL / 'execution-attempt1/offline/supervisor.json')
    require(first_timeout['child_primary_exit'] == first_timeout['supervisor_exit'] == 124
            and first_timeout['timed_out'] is True
            and first_timeout['owned_job_no_live_execution_verified'] is True
            and not (FULL / 'execution-attempt1/offline/actual/windows-offline.json').exists(),
            'preserved actual attempt1 timeout with no final offline JSON')
    main_manifest = verify_archive(MAIN, freeze_sha, parent)
    p3_manifest = verify_archive(P3, freeze_sha, parent)
    require(main_manifest['actual_started_steps'] == list(STEPS) and main_manifest['all_four_started'] is True
            and main_manifest['status'] == 'sealed_exact_outputs_no_pass_claim', 'all four actual main jobs archived')
    require(read(MAIN / 'orchestration.json')['status'] == 'all_four_terminal'
            and [row['name'] for row in read(MAIN / 'orchestration.json')['steps']] == list(STEPS), 'four main job terminal ledger')
    require(read(P3 / 'orchestration.json')['status'] == 'all_five_terminal'
            and [row['name'] for row in read(P3 / 'orchestration.json')['steps']] == list(P3_STEPS), 'five supplementary terminal ledger')
    supervisor_sha = sha(MAIN / 'executed-tools/legacy/supervisor275.py')
    for label in ('legacy', 'current'):
        folder = MAIN / 'executed-tools' / label
        binding = read(folder / 'activation275.json')
        require(binding['binding_ready'] is True and binding['actual_validation_attempt'] == 2
                and binding['root_freeze_sha256'] == freeze_sha
                and binding['tested_worktree_parent_commit'] == parent
                and binding['scope_not_reduced'] is True, label + ' actual attempt2 bound tool map')
        for name, expected in binding['execution_tools_sha256'].items():
            require(sha(safe_child(folder, name)) == expected, label + ' bound tool bytes: ' + name)
    for name, expected in frozen['preparation_tools_sha256'].items():
        require(sha(MAIN / 'controller-tools' / Path(name).name) == expected, 'archived actual controller: ' + name)
    with tarfile.open(regular(MAIN / 'frozen-public-source.tar.gz'), 'r:gz') as archive:
        members = archive.getmembers()
        require(len(members) == len(all_sources) and {member.name for member in members} == set(all_sources), 'exact full source plus supplemental archive members')
        for member in members:
            require(member.isfile() and not member.issym() and not member.islnk(), 'regular frozen source tar member')
            with archive.extractfile(member) as file:
                require(hashlib.sha256(file.read()).hexdigest() == all_sources[member.name], 'exact frozen tar member SHA: ' + member.name)

    # Require a ROOT-AUTHORED manual review covering exactly all actual A2 PNGs.
    authority_path = regular(args.root_visual_review.resolve())
    authority = read(authority_path)
    require(authority['kind'] == 'ROOT_FULL290_ATTEMPT2_PNG_REVIEW' and authority['reviewer'] == 'root'
            and authority['actual_validation_attempt'] == 2
            and authority['source_freeze_sha256'] == freeze_sha
            and authority['all_actual_images_individually_reviewed'] is True,
            'root manual visual review authority, not generated by builder')
    pngs = {}
    for folder, manifest in ((MAIN, main_manifest), (P3, p3_manifest)):
        for name, entry in manifest['files'].items():
            if '/actual/' in '/' + name and name.endswith('.png'):
                pngs[relative(folder / name)] = entry['sha256']
    legacy_pngs = {name for name in pngs if '/legacy/actual/' in name}
    require(len(legacy_pngs) == 4, 'all four actual legacy screenshots')
    reviews = authority['images']
    require(len(reviews) == len(pngs) and len({row['file'] for row in reviews}) == len(reviews)
            and {row['file'] for row in reviews} == set(pngs), 'every actual new PNG and no A1 substitutions')
    for review in reviews:
        require(review['sha256'] == pngs[review['file']] and review['reviewed'] is True
                and review['acceptable'] is True and isinstance(review['observation'], str)
                and bool(review['observation'].strip()), 'root individual actual PNG review: ' + review['file'])

    # Actual offline counters only; a timeout without final JSON cannot enter.
    offline_supervisor = verify_terminal(MAIN / 'offline', 0, supervisor_sha)
    offline = read(MAIN / 'offline/actual/windows-offline.json')
    offline_closure = read(MAIN / 'offline/actual/offline290-source-closure.json')
    require(offline['available_checks_passed'] is True and offline['failures'] == 0 and offline['errors'] == 0
            and offline['source_drift'] == [] and offline['source_sha256'] == frozen['source_sha256']
            and offline['selectors'] == frozen['selectors'] and offline['verbosity'] == 2
            and offline['platform'] == 'Windows' and offline['wine_compatibility'] is False,
            'actual complete maintained offline receipt with verbosity2')
    require(offline['tests_run'] == offline['tests_passed'] + offline['historical_or_declared_skips'] + offline['unavailable_parent_count'],
            'parent accounting does not add unavailable subcases as passed parents')
    require(offline_closure['actual_suite_exit'] == 0 and offline_closure['exception'] is None
            and offline_closure['actual_validation_attempt'] == 2 and offline_closure['runner_verbosity'] == 2
            and offline_closure['root_freeze_sha256'] == freeze_sha and offline_closure['source_drift'] == []
            and offline_closure['suite_source_map_matches_root_freeze'] is True
            and offline_closure['actual_selector_list_matches_root_freeze'] is True
            and offline_closure['available_checks_passed'] is True, 'offline native closure')
    qt_clean(offline['qt_shutdown'], 'offline')
    require(offline['qt_shutdown_error'] is None, 'offline Qt shutdown no error')

    legacy_supervisor = verify_terminal(MAIN / 'legacy', 0, supervisor_sha)
    native_window(MAIN / 'legacy', True, freeze_sha)
    legacy = read(MAIN / 'legacy/actual/wine-ui-100.json')
    typed = read(MAIN / 'legacy/independent-saved-readback-audit.json')
    readback_process = read(MAIN / 'legacy/readback-process.json')
    require(int(regular(MAIN / 'legacy/readback.exit').read_text().strip()) == 0
            and readback_process['actual_observed_subprocess_returncode'] == 0
            and readback_process['derived_from_json_or_timeout'] is False,
            'actual original typed auditor process exit0')
    argv = readback_process['argv']
    require(argv[argv.index('--freeze') + 1] == str(FREEZE)
            and Path(argv[argv.index('--container') + 1]).resolve() == Path(main_manifest['source_container']).resolve() / 'legacy'
            and Path(argv[argv.index('--bundle') + 1]).resolve() == ROOT / '.cache/p3-full290-repair-prep/legacy',
            'typed auditor actually read this new A2 namespace')
    require(sha(MAIN / 'executed-tools/legacy/audit_full261_saved_readback.py') ==
            sha(ROOT / 'verification/full-275/legacy-window-attempt3/executed-tools/audit_full261_saved_readback.py'),
            'original complete typed auditor bytes unchanged')
    require(typed['passed'] is True and typed['process_exit'] == typed['child_primary_exit'] == typed['supervisor_exit'] == 0
            and typed['timeout'] is False and typed['source_and_additional_drift'] == [], 'full typed readback actual success')
    expected_typed = {'complete_runtime_checks': 4283, 'passed_flag_records': 4281, 'metadata_records': 2,
                      'saved_rows': 52, 'current_revised_assertions': 862, 'readonly_trace_empty_rows_not_invented': 26}
    require(all(typed[key] == value for key, value in expected_typed.items())
            and typed['exact_ten_admission_indices'] == INDICES
            and typed['codec_exact_typed_roundtrip'] is True and typed['codec_plain_JSON_order_and_values_match'] is True,
            'all original complete typed/state/check/bridge/empty trace scope')
    require(legacy['new_explicit_three_text_requests090'] == 156
            and legacy['source_drift'] == legacy['source_additional_drift'] == []
            and legacy['passed'] is True, 'legacy actual156 requests and zero drift')

    current30_supervisor = verify_terminal(MAIN / 'current30', 1, supervisor_sha)
    native_window(MAIN / 'current30', False, freeze_sha)
    current30 = read(MAIN / 'current30/actual/window.json')
    failure = current30['failure']
    require(current30['passed'] is False and failure['type'] == 'OSError'
            and '[WinError 1314]' in failure['message'] and 'diagnostic.symlink_to(public_target.name)' in failure['traceback']
            and 'os.symlink(target, self, target_is_directory)' in failure['traceback']
            and 'public-261-never-create.txt' in failure['message'], 'current30 exact real original symlink prerequisite unavailable, not passed')
    current29_supervisor = verify_terminal(MAIN / 'current29', 0, supervisor_sha)
    native_window(MAIN / 'current29', True, freeze_sha)
    current29 = read(MAIN / 'current29/actual/window.json')
    require(current29['passed'] is True and len(current29['checks']) == 29
            and current29['maintenance261_safe_save_check'] is False
            and 'WinError1314' in current29['maintenance261_symlink_specialization'], 'all29 available workflows and explicit unavailable specialization')
    for name, raw in (('current30', current30), ('current29', current29)):
        require(raw['source_sha256_before'] == raw['source_sha256_after'] == frozen['source_sha256']
                and raw['source_drift'] == [] and raw['source_freeze_sha256'] == freeze_sha
                and raw['game_captures'] == raw['chat_requests'] == 0 and raw['private_state_isolated'] is True,
                name + ' exact current source and isolated state')

    supplementary = {}
    for section, mode in zip(range(286, 291), P3_STEPS):
        folder = P3 / mode
        supervisor = verify_terminal(folder, 0, supervisor_sha)
        raw = read(folder / 'actual/p3-window.json')
        closure = read(folder / 'actual/supplementary290-source-closure.json')
        require(raw['passed'] is True and raw['qt_exit_code'] == 0
                and closure['actual_fixture_exit'] == 0 and closure['actual_validation_attempt'] == 2
                and closure['fixture_exception'] is None and closure['source_validation_error_after'] is None
                and closure['qt_cleanup_error'] is None and closure['root_freeze_sha256'] == freeze_sha
                and closure['actual_receipt_sha256'] == sha(folder / 'actual/p3-window.json')
                and closure['passed'] is True, mode + ' own actual receipt/closure success')
        qt_clean(closure['qt_cleanup'], mode)
        before = raw.get('source_sha256_before', raw.get('loaded_source_sha256', raw.get('source_sha256')))
        after = raw.get('source_sha256_after', before)
        require(isinstance(before, dict) and before == after, mode + ' unchanged actual bound source map')
        for name, value in before.items():
            if name in all_sources:
                require(all_sources[name] == value, mode + ' actual bound source subset: ' + name)
            else:
                # Maintained source_hashes intentionally omits PNGs.288's
                # three production aliases are independently fingerprinted by
                # its canonical actual window and the two frozen originals.
                require(section == 288 and name in MAP_ORIGINALS
                        and all_sources[MAP_ORIGINALS[name]] == value
                        and sha(safe_child(ROOT, name)) == value,
                        '288 actual bitmap alias matches canonical raw plus frozen original: ' + name)
        if section == 287:
            require('native_windows_qpa' in raw['checks'] and len(raw['stages']) == 2
                    and all(isinstance(stage['hwnd'], int) and stage['hwnd'] > 0 for stage in raw['stages']),
                    '287 actual canonical HWND stages, no invented qpa field')
            executed = len(raw['checks'])
            unique = raw['unique_checks']
        elif section == 286:
            require(raw['qpa'] == 'windows' and raw['window_closed'] is True, '286 actual native and closed')
            executed = raw['successful_assertion_executions_including_repeated_safety_guards']
            unique = raw['completed_check_count']
        else:
            require(raw['qpa'] == 'windows' and raw['verification_window_closed'] is True, mode + ' native and closed')
            executed = raw['successful_assertion_executions_including_repeated_guards']
            unique = raw['unique_checks']
        supplementary[str(section)] = {'passed': True, 'actual_child_and_supervisor_exit': supervisor['child_primary_exit'],
            'owned_job_no_live_execution_verified': supervisor['owned_job_no_live_execution_verified'],
            'actual_assertion_executions': executed, 'unique_check_labels': unique,
            'runtime_seconds': supervisor['elapsed_seconds'], 'receipt': relative(folder / 'actual/p3-window.json'),
            'closure': relative(folder / 'actual/supplementary290-source-closure.json'),
            'root_individually_reviewed_PNGs': [entry for entry in reviews if entry['file'].startswith(relative(folder) + '/')],
            'historical_or_game_chat_verified': False}

    # All required actual prerequisites have succeeded. Completeness remains
    # false: unavailable original scopes are preserved rather than fabricated.
    offline_keys = ('tests_run', 'tests_passed', 'historical_or_declared_skips', 'failures', 'errors',
                    'unavailable_records', 'unavailable_parent_count', 'qt_shutdown', 'qt_shutdown_error')
    summary = {
        'after_section': 290, 'kind': 'functional_section_full_validation',
        'checked_at_Beijing': datetime.now(timezone(timedelta(hours=8))).isoformat(),
        'available_checks_passed': True, 'complete_repository_validation': False, 'scope_not_reduced': True,
        'P2_complete': False, 'single_execution_all_green': False, 'actual_validation_attempt': 2,
        'validation_composition': {step: relative(MAIN / step) for step in STEPS},
        'native_current_windows_gui_verified': True, 'native_windows_game_chat_verified': False,
        'historical_original_Windows_verified': False,
        'actual_platform': 'Current native Windows offline and isolated visible public-state MainWindow. Linux/Wine/private original history and game/chat remain unverified.',
        'source_files': len(frozen['source_sha256']), 'maintained_selectors': len(frozen['selectors']),
        'supplemental_public_input_files': len(frozen['supplemental_public_inputs_sha256']),
        'all_original408_selectors_retained': True, 'all_attempt1_430_selectors_retained': True,
        'source_drift': [], 'tested_worktree_parent_commit': parent, 'source_freeze': relative(FREEZE),
        'source_freeze_sha256': freeze_sha,
        'archive_manifests_sha256': {relative(folder / 'archive-manifest.json'): sha(folder / 'archive-manifest.json')
            for folder in (FULL / 'execution-attempt1', FULL / 'p3-supplementary-attempt1', MAIN, P3)},
        'offline_windows': {key: offline[key] for key in offline_keys},
        'actual_offline_process_exit': offline_supervisor['child_primary_exit'],
        'offline_receipt': relative(MAIN / 'offline/actual/windows-offline.json'),
        'offline_count_accounting': f"{offline['tests_run']} parents = {offline['tests_passed']} passed + {offline['historical_or_declared_skips']} skipped + {offline['unavailable_parent_count']} unavailable parents; {offline['unavailable_records']} unavailable subcase records are not added as passed tests.",
        'legacy_window': {'passed': True, 'actual_child_and_supervisor_exit': legacy_supervisor['child_primary_exit'],
            'owned_job_no_live_execution_verified': True, 'runtime_seconds': legacy_supervisor['elapsed_seconds'],
            'runtime_check_records': typed['complete_runtime_checks'], 'passed_flag_records': typed['passed_flag_records'],
            'metadata_records': typed['metadata_records'], 'saved_states': typed['saved_rows'],
            'explicit_text_requests': legacy['new_explicit_three_text_requests090'],
            'current_assertion_AST_and_order': typed['current_revised_assertions'], 'original_maintry_checks': 552,
            'original_maintry_bytes_unchanged': True, 'original_maintry_sha256': typed['original552_maintry_sha256'],
            'historical_projection_records': 42, 'exact_bridge_indices': typed['exact_ten_admission_indices'],
            'real_empty_trace_rows': typed['readonly_trace_empty_rows_not_invented'], 'typed_readback_verified': True,
            'formal_typed_readback_actual_exit': 0, 'typed_archive_sha256': typed['compressed_archive_sha256'],
            'receipt': relative(MAIN / 'legacy/actual/wine-ui-100.json'),
            'closure': relative(MAIN / 'legacy/actual/native275-launcher-closure.json'),
            'independent_saved_readback': relative(MAIN / 'legacy/independent-saved-readback-audit.json'),
            'readback_exit_file': relative(MAIN / 'legacy/readback.exit'),
            'inherited_wine_261_275_names_and_false_history_flags_preserved': True,
            'PNG_visual_inspection_confirmed_by_root': True, 'PNG_visual_inspection_count': len(legacy_pngs),
            'screenshots': [entry for entry in reviews if entry['file'] in legacy_pngs]},
        'current_window': {'maintained_scope': 30, 'available_original_workflows_passed': len(current29['checks']),
            'actual_full30_attempt_preserved': True, 'full30_actual_child_and_supervisor_exit': current30_supervisor['child_primary_exit'],
            'current29_actual_child_and_supervisor_exit': current29_supervisor['child_primary_exit'],
            'symlink_specialization': 'Unavailable: original Path.symlink_to -> os.symlink actual WinError1314. Not passed.',
            'current29_receipt': relative(MAIN / 'current29/actual/window.json'),
            'full30_failure_receipt': relative(MAIN / 'current30/actual/window.json'),
            'raw_native_windows_verified_flags_preserved_false': True},
        'p3_supplementary_windows': supplementary,
        'original_failures_preserved': {
            'attempt1_offline_timeout_supervisor': 'verification/full-290/execution-attempt1/offline/supervisor.json',
            'attempt1_offline_exit': 'verification/full-290/execution-attempt1/offline/process.exit',
            'attempt1_had_no_final_offline_json': True,
            'attempt1_current30_failure': 'verification/full-290/execution-attempt1/current30/actual/window.json',
            'independent_diagnostic_failures_not_reconstructed_original_timeout_failures': True},
        'unavailable_scopes': ['Actual Windows symlink prerequisite subcases and current30 specialization, attempted but not passed.',
            'Current Linux/WSL/Wine unavailable; old compatibility receipts remain historical.',
            'Original Windows/private samples, deferred095/109, real game capture/actions and chat remain unverified.'],
        'root_visual_review': relative(authority_path), 'root_visual_review_sha256': sha(authority_path),
        'current_worktree_validation_authority': True,
        'candidate_only_not_publicly_published': True,
        'builder_review': {'script': relative(Path(__file__)), 'script_sha256': sha(Path(__file__)),
            'check_count': len(CHECKS), 'author_readback_not_additional_independent_mechanics_review': True},
    }
    with output.open('xb') as file:
        file.write((json.dumps(summary, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps({'candidate': relative(output), 'sha256': sha(output), 'checks': len(CHECKS),
                      'public_summary_written': False}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root-visual-review', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args())
