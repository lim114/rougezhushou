"""Unexecuted291 closeout strict revision3. Root must review real receipt schemas first.

Default: validate actual public evidence and preview; no writes. --apply writes
only allowlisted section/docs. Never runs tests/Qt/game/chat, reads private state,
publishes Git, repeats full290, or equates Qt exit with process exit.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import struct

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / '.cache/p3-291-closeout/revision3'
SECTION = 291
TITLE = '和平守卫者单向结果说明、居民据点资料位置与两关独立预览'
PACKET = 'research/p3-peace-guardian-results-291'
MANIFEST = PACKET + '/source-manifest.json'
CANONICAL = 'scripts/verify_peace_guardian_window_291.py'
PROMOTION = '.cache/p3-291-promotion-readiness/PROMOTION_FILES.json'
FULL = 'verification/full-290/summary.json'
FULL_SHA = '2c6e93534e443089bc0f8ffbbd686e3c37610ccf3c4aafd43fbf44d16188b823'
SOURCE_MANIFEST_SHA = '0d601704bff78b79089ce56c49ecce4874f37e134546081d3801575a06d5f5f6'
MODULES = ['tests.test_peace_guardian_results_291', 'tests.test_resident_location_references_291',
    'tests.test_peace_guardian_integration_291', 'tests.test_resident_reference_signals_291',
    'tests.test_choice_recruitment_integration_290', 'tests.test_event_planning',
    'tests.test_node_map_navigation', 'tests.test_readable_map_047', 'tests.test_node_catalog_view']
FIXED_SOURCE = {
    'prts-events-427904.html': 'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9',
    'prts-events-440271.html': 'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8',
    'bwiki-investigation.html': '26b7768bf3556cf73c24529659c2c92f4095059476f782130bf3fa768422b908',
    'original-records.json': 'c7baa3810b029676bb3e37cd60e5b810a62c35fa21c21edc18d5ee402e54441a',
    'README.md': '4960b5459985a1c248b209f27ffea579f5ff2a552e39216be8545887a40243f2',
    'extract_original_records.py': '3cb3be5b57d22a35fa2309c09cd4401817b06ff1fd4f960e4c36db3771402e13',
    'extraction.json': '6e4e3ac49f084a73e09dbd2aa3ad5b7faeea336bf6ca9a80c231c713e0e9286e',
}
BUILDER = 'scripts/build_peace_guardian_results_291.py'
DATA = 'rouge/data/peace-guardian-results.json'
SOURCE_EXTRA = {
    BUILDER: 'a145c1f6ffe0e2b5168944f298550b138dfe9a2aa6dd1d66ab9104a44a040f7b',
    DATA: '509a021ec214791a42de91534d695a42cb35494eb1044057d3a67e99e9863ecb',
    'rouge/data/node-catalog.json': '7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d',
}
SIZES = [[1050, 720], [1280, 800], [1440, 930]]

def require(value, message):
    if value is not True:
        raise ValueError('291 closeout prerequisite: ' + message)

def relpath(value):
    path = Path(value)
    path = path if path.is_absolute() else ROOT / path
    resolved = path.resolve()
    require(resolved.is_relative_to(ROOT.resolve()) and not path.is_symlink(), 'canonical public path under repository')
    return path

def regular(value):
    path = relpath(value)
    require(path.is_file(), 'regular public file: ' + str(value))
    return path

def relative(value):
    return relpath(value).resolve().relative_to(ROOT.resolve()).as_posix()

def digest(value):
    return sha256(regular(value).read_bytes()).hexdigest()

def read(value):
    return json.loads(regular(value).read_bytes())

def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

def map_current(mapping, label):
    require(isinstance(mapping, dict) and bool(mapping), label + ' nonempty source map')
    for path, expected in mapping.items():
        require(isinstance(path, str) and not Path(path).is_absolute() and '..' not in Path(path).parts
                and '\\' not in path and isinstance(expected, str) and re.fullmatch('[0-9a-f]{64}', expected) is not None,
                label + ' safe public relative SHA source')
        require(digest(path) == expected, label + ' current exact source: ' + path)

def source_packet():
    require(digest(MANIFEST) == SOURCE_MANIFEST_SHA, 'unchanged reviewed source-manifest bytes')
    expected = {PACKET + '/' + name: value for name, value in FIXED_SOURCE.items()}
    expected.update(SOURCE_EXTRA)
    manifest = read(MANIFEST)
    require(set(manifest['files']) == set(expected) and len(expected) == 10, 'all ten exact source members')
    actual_packet = {p.relative_to(ROOT).as_posix() for p in (ROOT / PACKET).rglob('*') if p.is_file()}
    require(actual_packet == {MANIFEST, *[PACKET + '/' + name for name in FIXED_SOURCE]}, 'complete original eight-file packet')
    for path, expected_sha in expected.items():
        row = manifest['files'][path]
        require(row['sha256'] == digest(path) == expected_sha and regular(path).stat().st_size == row['bytes'],
                'fixed full source original: ' + path)
    return {MANIFEST: digest(MANIFEST), **expected}

def expected_necessary_sources():
    # Same public scope construction as the actual necessary producer, without
    # importing or executing it. Never follow caller map paths into private data.
    paths = set(ROOT.glob('rouge/**/*.py')) | set(ROOT.glob('rouge/data/*.json'))
    paths |= {ROOT / ('tests/' + name.split('.')[-1] + '.py') for name in MODULES}
    paths |= set((ROOT / PACKET).glob('*'))
    paths |= set((ROOT / 'verification/sections/291-preparation/location-fixtures').rglob('*'))
    paths |= {ROOT / 'verification/sections/291-preparation/before-integration/rouge/event_planning.py',
              ROOT / CANONICAL, ROOT / BUILDER}
    return {path.relative_to(ROOT).as_posix() for path in paths if path.is_file()}

def necessary(value, parent):
    data = read(value)
    require(data['section'] == 291 and data['kind'] == 'necessary_change_related_tests_not_full_suite'
            and type(data['exit_code']) is int and data['exit_code'] == 0
            and data['source_unchanged'] is True and data['source_sha256_before'] == data['source_sha256_after'],
            'actual successful necessary run on stable declared sources')
    require(data['modules'] == MODULES and data['argv'][-len(MODULES):] == MODULES
            and data['argv'][1:7] == ['-B', '-X', 'utf8', '-m', 'unittest', '-v'], 'complete nine necessary modules actual argv')
    require(data['source_commit_before'] == parent, 'actual necessary run based on current worktree parent')
    require(data['game_sampling_verified'] is False and data['chat_verified'] is False
            and data['full_scope_reduced'] is False and data['full_suite_rerun'] is False, 'necessary-only scope, no invented full or integrations')
    require(set(data['source_sha256_after']) == expected_necessary_sources(), 'complete actual public necessary producer scope; no private map paths')
    map_current(data['source_sha256_after'], 'final necessary')
    promotion = read(PROMOTION)
    promoted_paths = {row['destination'] for row in promotion['files']}
    require(len(promoted_paths) == 32 and promoted_paths <= set(data['source_sha256_after']),
            'all initial32 destination paths covered using final actual hashes, never obsolete candidate hashes')
    log_path = regular(value).with_name('stderr.txt')
    raw = regular(log_path).read_text(encoding='utf-8')
    runs = re.findall(r'Ran (\d+) tests in ([0-9.]+)s', raw)
    require(len(runs) == 1 and int(runs[0][0]) > 0 and raw.rstrip().endswith('OK')
            and not re.search(r'^(FAIL|ERROR):', raw, re.M), 'actual complete necessary Ran/OK, no unknown or prefilled N')
    return data, {'receipt': relative(value), 'receipt_sha256': digest(value), 'stderr': relative(log_path),
        'stderr_sha256': digest(log_path), 'methods_run': int(runs[0][0]), 'seconds': float(runs[0][1]),
        'actual_exit': 0, 'source_unchanged': True, 'modules': MODULES, 'source_count': len(data['source_sha256_after'])}

def expected_window_sources():
    names = {'rouge/app.py', 'rouge/map_view.py', 'rouge/map_reporting.py', 'rouge/node_catalog.py',
        'rouge/node_catalog_view.py', 'rouge/ui_state.py', 'rouge/player_node_information.py',
        'rouge/event_planning.py', 'rouge/peace_guardian_results.py', 'rouge/resident_location_references.py',
        'rouge/choice_recruitment_results.py', 'rouge/data/node-catalog.json', 'rouge/data/battle-node-pools.json',
        DATA, BUILDER, CANONICAL, 'tests/test_readable_map_047.py'}
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / PACKET).rglob('*') if p.is_file())
    names.update(read(MANIFEST)['files'])
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'tests').glob('test_*291*.py'))
    require(len(names) == 29, 'exact current canonical29 selected source coverage, not entire App dependency graph')
    return names

def local_launcher_probe_reference():
    prefix = 'verification/sections/291-preparation/local-launcher-probe/'
    expected = {'process.json': 'd4920aff4d3658a9c603080ddba033c77f938cf9ea76513d70bdf6e0e4e45f47', 'runner.py': '5d157eba67ddc996f8c9ca28b623c455f3715997c2eea42196767a21d62d5048', 'stdout.txt': '49c192bf4795564f22ea88aaa4f62a728c855d5d506a63add983167fa2f4159f', 'stderr.txt': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}
    for name, expected_sha in expected.items():
        require(digest(prefix + name) == expected_sha, 'actual independent local launcher probe original ' + name)
    probe = read(prefix + 'process.json')
    stdout = json.loads(regular(prefix + 'stdout.txt').read_bytes())
    require(probe['kind'] == 'actual_local_venv_launcher_pid_probe_not_historical_window_replay'
            and type(probe['exit_code']) is int and probe['exit_code'] == 0
            and probe['actual_python'] == stdout and regular(prefix + 'stderr.txt').read_bytes() == b'',
            'actual standalone local probe exit0 and original stdout/stderr')
    launcher, interpreter = probe['popen_launcher_pid'], stdout['pid']
    require(type(launcher) is int and launcher > 0 and type(interpreter) is int and interpreter > 0
            and launcher != interpreter and stdout['parent_pid'] == launcher
            and probe['observed_distinct_launcher_and_interpreter_PIDs'] is True
            and probe['interpreter_parent_matches_owned_probe_popen_pid'] is True,
            'only this independent local probe has the observed launcher/interpreter parent relation')
    require(probe['historical_window_ancestry_reconstructed'] is False
            and probe['new_GUI_or_game_chat_execution'] is False,
            'new standalone probe is not retrospective ancestry or a GUI replay')
    return {'receipt': prefix + 'process.json', 'sha256': expected['process.json'],
        'source_files_sha256': {prefix + key: value for key, value in expected.items()},
        'scope': 'Current local launcher mechanism observation only; not historical window process ancestry.',
        'observed_probe_launcher_pid': launcher, 'observed_probe_interpreter_pid': interpreter,
        'historical_window_ancestry_reconstructed': False, 'new_probe_run_by_closeout': False}


def window(value, process_value, necessary_data):
    data = read(value)
    process = read(process_value)
    launcher_probe = local_launcher_probe_reference()
    require(type(data['process_id']) is int and data['process_id'] > 0, 'actual fixture-reported interpreter PID separately valid')
    child = process['child_argv']
    require(isinstance(child, list) and len(child) == 9 and child[1:4] == ['-B', '-X', 'utf8']
            and Path(child[0]).resolve() == (ROOT / '.venv/Scripts/python.exe').resolve()
            and Path(child[4]).resolve() == (ROOT / CANONICAL).resolve()
            and child[5] == '--receipt' and child[7:] == ['--visible-ms', '120000'],
            'actual canonical child argv with explicit raw receipt path')
    raw_destination = Path(child[6])
    require(raw_destination.is_absolute() and raw_destination.name == regular(value).name,
            'raw actual receipt basename preserved by exact public archival copy')
    require(data['section'] == 291 and data['kind'] == 'isolated_native_windows_resident_position_and_fixed_battle_references'
            and data['passed'] is True and data['failure'] is None and data['qpa'] == 'windows'
            and type(data['qt_exit_code']) is int and data['qt_exit_code'] == 0 and data['verification_window_closed'] is True,
            'actual canonical native Windows fixture normal Qt completion and window closure')
    checks = data['checks']
    require(isinstance(checks, list) and all(isinstance(item, str) for item in checks)
            and len(set(checks)) == len(checks) == data['unique_checks']
            and data['successful_assertion_executions_including_repeated_guards'] >= len(checks), 'actual unique checks and executions, no preset count')
    required = {'native_windows_QPA', 'actual_HWND_exists', 'actual_HWND_visible',
        'actual_HWND_owned_by_fixture_process', 'actual_window_not_minimized',
        'real_nonzero_scroll_and_text_selection', 'real_search_selection_nonempty',
        'bound_event_refresh_keeps_dossier_key_search_tab_scroll_and_selection',
        'return_to_event_preserves_bound_key_search_tab_nonzero_scroll_and_selection',
        'explicit_view_selected_map_node_uses_latest_selection_not_old_event_context',
        'ordinary_MapView_selection_still_follows_original_bound_dossier_flow',
        'exact_two_resident_fixed_battle_choices', 'position_and_fixed_stage_default_unselected',
        'all_actual_MOVE_outcomes_unknown', 'all_bound_public_sources_unchanged',
        'all_reference_interactions_leave_temporary_run_memory_unchanged',
        'all_external_operation_attempt_counts_zero_at_actual_closure',
        'two_manual_fixed_previews_never_become_event_outcomes',
        'invalid_source_retains_raw_condition_and_explicit_unknown',
        'actual_window_client_size_matches_requested_layout_size',
        'initial_public_directory_has_no_node_context_or_bound_dossier',
        'initial_view_selected_map_node_button_disabled_without_selection',
        'first_unbound_reference_click_reaches_latest_MapView_selection',
        'first_unbound_reference_click_enables_explicit_view_selected_node_button',
        'first_unbound_reference_click_does_not_create_or_replace_reading_binding',
        'first_unbound_reference_click_preserves_selected_event_reading',
        'first_unbound_probe_clears_only_UI_reference_selection',
        'first_unbound_probe_reset_disables_explicit_view_without_selection',
        'first_unbound_probe_restores_original_directory_reading_and_placeholders',
        *[s + '_manual_button_opens_actual_fixed_battle_preview' for s in ('ro6_t_10', 'ro6_t_11')]}
    require(required <= set(checks), 'all meaningful291 native behaviors, not merely passed label')
    require(data['source_sha256_before'] == data['source_sha256_after']
            and set(data['source_sha256_after']) == expected_window_sources(), 'exact29 stable window selected sources')
    map_current(data['source_sha256_after'], 'actual canonical window')
    require(all(necessary_data['source_sha256_after'][path] == value for path, value in data['source_sha256_after'].items()),
            'window and final necessary checks same actual selected bytes')
    require(data['state_paths_replaced_before_constructor'] == ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE']
            and data['temporary_state_root'] is True and data['private_state_read_copied_or_restored'] is False
            and data['external_entrypoints_blocked_before_original_call'] is True,
            'all four paths isolated before constructor; original outside entrypoints blocked')
    attempts = data['external_operation_attempts']
    require(set(attempts) == {'game_enumeration', 'game_connect', 'game_capture', 'game_next_frame',
            'desktop_start', 'desktop_request', 'provider_chat', 'credential_read'}
            and all(type(value) is int and value == 0 for value in attempts.values()), 'all eight actual external attempts zero')
    require(data['game_capture_attempts'] == data['game_captures'] == 0 and data['game_operated'] is False
            and data['chat_sent'] is False and data['chat_attempted'] is False
            and data['original_project_window_operated_or_restarted'] is False, 'no game/chat/private/original-window operations in fixture')
    geometry = data['geometry_observations']
    require(data['geometry_stages_observed'] == len(geometry) == 3
            and [row['requested_size'] for row in geometry] == SIZES, 'actual three requested sizes, no synthetic fourth size')
    fixture_hwnd = None
    for row in geometry:
        require(row['actual_size'] == row['requested_size'], 'actual client size exactly equals requested; no minhint-clamped substitute')
        native = row['native_window']
        require(type(native['hwnd']) is int and native['hwnd'] > 0 and native['process_id'] == data['process_id']
                and native['qpa'] == 'windows', 'actual owned native HWND for each recorded geometry')
        require(all(type(n) is int and n > 0 for n in row['actual_size']), 'actual positive native size')
        if fixture_hwnd is None:
            fixture_hwnd = native['hwnd']
        require(native['hwnd'] == fixture_hwnd, 'all three actual geometry observations share the same fixture-owned HWND')
    images = data['screenshots']
    require(data['screenshot_count'] == len(images) and len({row['name'] for row in images}) == len(images)
            and {'layout-1', 'layout-2', 'layout-3', 'bound-current', 'bound-history', 'fixed-ro6_t_10', 'fixed-ro6_t_11'} <= {row['name'] for row in images},
            'all actual native three-size/current/history/two-stage images retained')
    for image in images:
        require(Path(image['path']).resolve() == raw_destination.with_name(raw_destination.stem + '-' + image['name'] + '.png').resolve(),
                'raw actual own-window screenshot sibling provenance remains unchanged')
        # Read the exact public archived sibling, not the private/Temp raw path.
        archived_image = regular(value).with_name(raw_destination.stem + '-' + image['name'] + '.png')
        raw = regular(archived_image).read_bytes()
        require(sha256(raw).hexdigest() == image['sha256'] and raw[:8] == b'\x89PNG\r\n\x1a\n'
                and len(raw) > 24 and all(n > 0 for n in struct.unpack('>II', raw[16:24])), 'exact nonempty actual own-window PNG')
        require(image['native_window']['process_id'] == data['process_id'] and image['native_window']['hwnd'] > 0,
                'image own process HWND provenance')
        require(image['native_window']['hwnd'] == fixture_hwnd, 'every actual screenshot has the same geometry-owned HWND and fixture PID')
    observations = data['public_observations']
    require(len(observations) == 1 and observations[0]['event_id'] == 'community_group_019'
            and observations[0]['reference_positions_are_not_route_or_destination_choices'] is True,
            'single actual event reference observation')
    require(all(observations[0][key] is None for key in ('actual_current_floor_completion', 'actual_target', 'actual_movement', 'actual_battle'))
            and {'ro6_t_10', 'ro6_t_11'} <= set(observations[0]['manual_fixed_stage_requests']),
            'both manually opened fixed references, all actual MOVE outcomes still unknown')
    # Independent owned supervisor/Popen terminal evidence, never Qt-only exit.
    require(process['section'] == 291 and process['kind'] == 'actual_native_window_owned_process_execution'
            and process['status'] == 'completed' and type(process['exit_code']) is int and process['exit_code'] == 0
            and type(process['child_primary_exit']) is int and process['child_primary_exit'] == 0
            and process['timed_out'] is False and process['owned_job_no_live_execution_verified'] is True
            and process['source_before_after_unchanged'] is True and process['window_receipt_sha256'] == digest(value),
            'separately observed actual supervisor/child exit0 and no live owned execution')
    argv = process['argv']
    require(isinstance(argv, list) and argv.count('--') == 1 and argv[argv.index('--') + 1:] == child
            and argv.count('--status') == 1 and argv.count('--timeout') == 1,
            'actual supervisor argv contains exact child and bounded owned status')
    status_raw = Path(argv[argv.index('--status') + 1])
    require(status_raw.is_absolute() and status_raw.name == process['supervisor_receipt'] == 'supervisor.json'
            and 0 < float(argv[argv.index('--timeout') + 1]) <= 3690, 'actual bounded supervisor status path')
    supervisor_path = regular(process_value).with_name(process['supervisor_receipt'])
    supervisor = read(supervisor_path)
    require(supervisor['status'] == 'completed' and supervisor['argv'] == child
            and type(supervisor['pid']) is int and supervisor['pid'] > 0
            and supervisor['supervisor_exit'] == process['exit_code'] == 0
            and supervisor['child_primary_exit'] == process['child_primary_exit'] == 0
            and supervisor['timed_out'] is False and supervisor['owned_job_assigned'] is True
            and supervisor['owned_handle_retained'] is True and supervisor['owned_job_no_live_execution_verified'] is True
            and supervisor['global_process_termination'] is False
            and supervisor['game_operations'] == supervisor['chat_requests'] == 0
            and not supervisor.get('launch_or_supervision_error'), 'unaltered raw owned Popen/job terminal record')
    require(supervisor['supervisor_sha256'] == process['supervisor_sha256'], 'same actual supervisor source hash')
    supervisor_sources = [Path(arg) for arg in argv[1:argv.index('--')] if isinstance(arg, str) and arg.endswith('.py')]
    require(len(supervisor_sources) == 1 and digest(supervisor_sources[0]) == process['supervisor_sha256'],
            'actual supervisor argv code bytes remain exact')
    for channel in ('stdout', 'stderr'):
        row = supervisor[channel]
        require(Path(row['file']).name == row['file'], 'raw supervisor log basename')
        path = supervisor_path.with_name(row['file'])
        require(digest(path) == row['sha256'] and regular(path).stat().st_size == row['bytes'], 'actual supervisor raw ' + channel)
    return data, {'receipt': relative(value), 'receipt_sha256': digest(value), 'process_receipt': relative(process_value),
        'process_receipt_sha256': digest(process_value), 'actual_process_exit': 0, 'actual_Qt_exit': 0,
        'owned_supervisor_receipt': relative(supervisor_path), 'owned_supervisor_receipt_sha256': digest(supervisor_path),
        'actual_child_exit': 0, 'owned_job_no_live_execution_verified': True,
        'supervisor_child_launch_pid': supervisor['pid'], 'fixture_reported_pid': data['process_id'], 'fixture_hwnd': fixture_hwnd,
        'same_pid_required': False, 'historical_window_ancestry_verified': False,
        'actual_process_exit_field_role': 'owned supervisor Popen process; actual_child_exit is its primary launched child',
        'owned_job_cleanup': {'no_live_execution_verified_after_supervision': True,
            'active_processes_after_primary_child_exit': supervisor.get('owned_job_active_processes_after_child_exit'),
            'owned_descendants_still_live_before_cleanup': supervisor.get('owned_descendants_still_live'),
            'termination_scope_recorded': supervisor.get('termination_scope'),
            'all_descendants_natural_exit_claimed': False, 'fixture_historical_job_membership_claimed': False},
        'local_launcher_probe': launcher_probe,
        'source_selected_files': len(data['source_sha256_after']), 'source_unchanged': True,
        'unique_checks': len(checks), 'actual_assertion_executions': data['successful_assertion_executions_including_repeated_guards'],
        'geometry_stages': len(geometry), 'screenshots': len(images), 'actual_window_closed': True,
        'actual_client_sizes': [row['actual_size'] for row in geometry], 'requested_sizes_are_actual_client_sizes': True,
        'images_visually_reviewed_by_this_helper': False, 'game_or_chat_verified': False}

def original_window(main_value, focus_value, fixture):
    main, focus = read(main_value), read(focus_value)
    require(main['passed'] is True and main['private_file_hash_comparison_count'] == 5
            and main['private_hashes_equal'] is True and main['changed_private_paths'] == []
            and main['private_contents_parsed_copied_or_restored'] is False and main['no_private_restoration'] is True,
            'actual original window update, private5 only-hash unchanged/no restore')
    require(len(main['visible_windows']) == 1, 'single visible original project window')
    own = main['visible_windows'][0]
    require(own['visible'] is True and own['responding'] is True and own['minimized'] is False
            and own['pid'] != fixture['process_id'] and own['hwnd'] > 0, 'original responsive visible window differs from fixture')
    require(focus['visible'] is True and focus['hwnd'] == focus['actual_foreground'] == own['hwnd']
            and focus['pid'] == own['pid'], 'actual foreground original project HWND, not intended focus')
    return {'receipt': relative(main_value), 'sha256': digest(main_value), 'focus_receipt': relative(focus_value),
        'focus_sha256': digest(focus_value), 'private_file_hash_comparison_count': 5, 'private_paths_changed': 0,
        'visible_responsive': True, 'actual_foreground': True, 'private_contents_read_by_closeout': False}

def main(args):
    require(Path(__file__).resolve() == (HERE / 'close_section_291.py').resolve(), 'root-reviewed canonical cache helper')
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    parent = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    require(branch == 'codex/p2-development', 'authorized branch')
    require(not (ROOT / 'verification/sections/291.json').exists(), 'exclusive new section291 receipt')
    originals = source_packet()
    tests, test_ref = necessary(args.necessary_receipt, parent)
    fixture, window_ref = window(args.window_receipt, args.window_process_receipt, tests)
    main_ref = original_window(args.main_window_receipt, args.focus_receipt, fixture)
    full = read(FULL)
    require(digest(FULL) == FULL_SHA and full['after_section'] == 290 and full['available_checks_passed'] is True
            and full['scope_not_reduced'] is True and full['complete_repository_validation'] is False
            and full['P2_complete'] is False and full['source_files'] == 1221 and full['maintained_selectors'] == 430
            and full['supplemental_public_input_files'] == 42 and full['source_drift'] == [], 'preserved actual290 full available scope, not rerun/current291 full')
    checkpoint = read('DEVELOPMENT_CHECKPOINT.json')
    require(checkpoint['completed_sections'] == checkpoint['latest_functional_section'] == 290
            and checkpoint['next_section'] == 291 and checkpoint['active_section']['section'] == 291,
            'only actual290→291 active continuation')
    require(checkpoint['policy']['priority_order'] == ['P3', 'P2', 'P1']
            and checkpoint['policy']['stop_after_section'] is None
            and checkpoint['policy']['current_user_batch_target_section'] is None
            and checkpoint['policy']['full_validation_interval'] == 15
            and checkpoint['policy']['full_validation_anchor_section'] == 125
            and checkpoint['last_full_validation']['after_section'] == 290
            and checkpoint['current_available_full_validation']['section'] == 290, 'current priorities/no target/original full cadence')
    next_full = 125 + ((SECTION - 125) // 15 + 1) * 15
    require(next_full == 305, 'next periodic full305, no new full291')
    prior_save = checkpoint['last_verified_cloud_save']
    prior_proof = read(prior_save['proof'])
    require(prior_save['section'] == 290 and digest(prior_save['proof']) == prior_save['proof_sha256']
            and prior_proof['passed'] is True and prior_proof['section'] == 290
            and prior_proof['commit'] == prior_proof['remote_HEAD'] == prior_save['commit']
            and prior_proof['push_primary_exit'] == 0, 'preserve actual previous290 ordinary publication proof')
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    scope = ('和平守卫者只对守卫和平选项说明“已完成本层居民据点作战时不会移动”的单向资料例外；'
        '独立列出本图已读或记忆中的居民据点资料位置，默认不选，不计算最近或实际目的地；'
        '手动位置映射保留事件阅读并拒绝过期上下文，显式查看才切换节点内容；提供枯枝、败叶两个独立固定作战预览。')
    limits = ['25个原场景与57个原选项入口缺口不减少，原入口/资格/费用及原始目录未借此补全。',
        '例外是单向资料；未完成不推出一定移动，未移动不反推完成，visited/空地/记忆类型均不是作战完成。',
        '本层完成、实际目的地/移动、触发关卡、实际战斗与后态仍未知；两个预览不是实际触发结果。',
        '第290节完整可用范围沿用其原冻结和组合来源，不声称对291新源码重跑全量；下次305。',
        'P3/P2/P1仍未完成，识别最后；不推荐、排序、比较或自动选择探索路线。',
        '真实符号链接1314、Linux/Wine/原Windows私样本及游戏聊天仍不计通过。']
    paths = {row['destination'] for row in read(PROMOTION)['files']}
    receipt = {'section': SECTION, 'kind': 'functional_section', 'title': TITLE, 'at_Beijing': now,
        'branch': branch, 'prior_commit': parent, 'remaining_item': 'P3节点事件条件与地图资料对应',
        'new_capability': scope, 'files': sorted(paths), 'source_sha256': {name: digest(name) for name in sorted(paths)},
        'source_evidence': {'packet': PACKET, 'original_files_sha256': originals,
            'exact_choice': 'community_group_019:scene:1:choice:0', 'remaining_original_scenes': 25,
            'remaining_original_choices': 57, 'one_way_exception_only': True,
            'actual_completed': None, 'actual_target': None, 'actual_moved': None, 'actual_battle': None,
            'fixed_previews': ['ro6_t_10', 'ro6_t_11'], 'fixed_previews_are_actual_outcomes': False},
        'necessary_validation': test_ref, 'native_windows_validation': {**window_ref, 'original_project_window': main_ref},
        'full_validation': {'receipt': FULL, 'sha256': FULL_SHA, 'after_section': 290, 'full_suite_rerun': False,
            'scope_not_reduced': True, 'available_checks_passed_on_its_original_frozen_sources': True,
            'new291_sources_have_full_validation_claim': False, 'complete_repository_validation': False,
            'next_periodic_section': 305, 'cadence_anchor': 125, 'interval': 15},
        'limits': limits, 'next_section': 292, 'P2_complete': False, 'P3_complete': False,
        'cloud_publication_binding': 'enclosing_commit', 'cloud_published': False}
    history_key = 'historical_before291_current_pointers'
    require(history_key not in checkpoint, 'exclusive old-current history')
    history_keys = ['current_section_save', 'current_section_validation', 'latest_section_environment',
        'current_batch', 'active_section', 'cloud_publication_closeout', 'current_available_full_validation']
    checkpoint[history_key] = {key: deepcopy(checkpoint[key]) for key in history_keys if key in checkpoint}
    checkpoint.pop('active_section', None)
    checkpoint.pop('cloud_publication_closeout', None)
    checkpoint.update(completed_sections=291, latest_functional_section=291, next_section=292,
        batch_status='P3_SECTION291_VALIDATED_AWAITING_PUBLICATION', next_full_validation_after=305,
        next_action='从292继续有证P3剩余事项；无连续数字终点。下一定期完整可用全量305。')
    checkpoint['policy']['next_full_validation_after'] = 305
    checkpoint['current_batch_commit_policy']['next_full_validation_after'] = 305
    checkpoint['current_batch'].update(status=checkpoint['batch_status'], next_section=292, next_section_started=False,
        receipt='verification/sections/291.json', next_full_validation_after=305, batch_closed=False)
    checkpoint['confirmed_next_stage_direction'].update(last_completed_functional_section=291, next_functional_section_started=False)
    checkpoint['sections'].append({'number': 291, 'completion_ref': 'p3-section-291', 'topic': TITLE, 'verification': 'verification/sections/291.json'})
    checkpoint['current_section_save'] = {'section': 291, 'verification': 'verification/sections/291.json',
        'scope': 'current_functional_section', 'binding': 'enclosing_commit',
        'commit_reference': 'commit containing291 source, necessary/native receipts, requirements and cloud index'}
    checkpoint['last_verified_cloud_save']['scope'] = 'previous_functional_section'
    checkpoint['current_section_validation'] = {'section': 291, 'receipt': 'verification/sections/291.json',
        'necessary_methods_passed': test_ref['methods_run'], 'native_isolated_window_checks': fixture['unique_checks'],
        'full_suite_rerun': False, 'last_full_receipt': FULL, 'full_source_is_historical290': True}
    checkpoint['latest_section_environment'] = {'section': 291, 'receipt': 'verification/sections/291.json',
        'native_windows': f"{test_ref['methods_run']} necessary checks; canonical291 actual {fixture['unique_checks']} unique native checks, three sizes/two previews; original visible responsive window private5 unchanged",
        'native_game_or_chat_verified': False, 'new_Linux_Wine_full_run': False,
        'current_section_full_rerun': False, 'last_full_receipt': FULL}
    checkpoint['functional_sections_since_latest_requirement'] = list(dict.fromkeys([*checkpoint['functional_sections_since_latest_requirement'], 291]))
    require(checkpoint['last_full_validation']['after_section'] == 290
            and checkpoint['current_available_full_validation']['section'] == 290, 'full pointers remain historically290')
    completed = (f'## 功能第291节 · {TITLE}\n\n{now}。{scope}\n\n'
        f"最终实际{test_ref['methods_run']}项必要检查及原生隔离窗口{fixture['unique_checks']}个唯一检查通过，三尺寸和两关预览、非零滚动/选区与刷新留存已验；"
        '原项目窗口更新且可见响应/置前，5私人路径hash不变。25/57原入口不减，实际完成、移动、目的地和战斗仍未知。'
        f'证据见verification/sections/291.json；沿用{FULL}的完整可用历史范围，不重复全量或称291新源全量通过。'
        'P3→P2→P1、识别最后；后续292，下一定期全量305，无连续数字终点。本节尚待普通推送核对。\n\n')
    docs = {name: regular(name).read_bytes() for name in ['DEVELOPMENT_CHECKPOINT.json', 'WORK_IN_PROGRESS.md',
        'PROJECT_COMPLETED.md', 'PROJECT_PROGRESS.md', 'PROJECT_REQUIREMENTS.md', 'AGENTS.md']}
    mutations = {'verification/sections/291.json': encode(receipt), 'DEVELOPMENT_CHECKPOINT.json': encode(checkpoint),
        'PROJECT_COMPLETED.md': completed.encode('utf-8') + docs['PROJECT_COMPLETED.md']}
    wip = docs['WORK_IN_PROGRESS.md'].decode('utf-8')
    require('## 功能第290节' in wip, 'preserve290 onward work log')
    mutations['WORK_IN_PROGRESS.md'] = (completed + wip[wip.index('## 功能第290节'):]).encode('utf-8')
    progress = docs['PROJECT_PROGRESS.md'].decode('utf-8')
    anchor = '已绑定来源关系及原件明确目的地的实际可达、展示、跳转后状态与完整脚本；'
    require(progress.count(anchor) == 1, 'exact remaining-only todo scope anchor')
    mutations['PROJECT_PROGRESS.md'] = progress.replace(anchor,
        '和平守卫者本层实际完成、真实目的地、实际移动/作战与当前服务器适用性；其余' + anchor, 1).encode('utf-8')
    requirements = docs['PROJECT_REQUIREMENTS.md'].decode('utf-8')
    start, end = requirements.index('<!-- current-delivery:start -->'), requirements.index('<!-- current-delivery:end -->')
    block = ('<!-- current-delivery:start -->\n## 当前交付与续接 · 第291节\n\n2026-10-16继续P3，无数字终点。' + scope
        + f"最终实际{test_ref['methods_run']}必要检查与Windows三尺寸/两关{fixture['unique_checks']}个唯一检查通过；原窗口更新、私人5路径不变。"
        + '25/57原入口不减，实际完成/移动/目的地/战斗未知；第290节完整可用验收保留原来源，不称291新源码全量通过。'
        + '后续292，下一定期全量305。P3→P2→P1，识别最后，不提供路线建议；本节待普通推送核对，源码/要求/回执/索引同提交。\n')
    mutations['PROJECT_REQUIREMENTS.md'] = (requirements[:start] + block + requirements[end:]).encode('utf-8')
    agents = docs['AGENTS.md'].decode('utf-8')
    start, end = agents.index('## 当前续接 · 第290节'), agents.index('## 当前优先顺序与输出可读性')
    mutations['AGENTS.md'] = (agents[:start] + '## 当前续接 · 第291节已完成功能与必要/原生验收\n\n'
        + scope + '本机来源与验收见verification/sections/291.json；原测试窗口更新打开，私人5路径hash不变。'
        + '25/57原入口和本局实际完成/移动/目标/战斗仍待证。沿用290完整可用原回执，不称291新源全量复验；'
        + '下一节292，下次305。P3→P2→P1，识别最后，无数字终点；不推荐/排序/自动选路。'
        + '本节待普通推送并核对真实远端，源码/要求/验收/索引同提交。\n\n' + agents[end:]).encode('utf-8')
    require('初次招募时即处于已进阶状态' in mutations['PROJECT_REQUIREMENTS.md'].decode('utf-8')
            and '初次招募即处于已进阶状态' in mutations['AGENTS.md'].decode('utf-8'), 'preserve verified terminology outside current block')
    require(all(str(index) + '.' in mutations['AGENTS.md'].decode('utf-8').split('## 当前续接')[0] for index in range(1, 6)), 'preserve highest-priority five requirements')
    archive = ROOT / 'verification/sections/291-preparation/closeout-tools'
    require(not archive.exists(), 'exclusive public closeout tools archive')
    copies = {'close_section_291.py': regular(HERE / 'close_section_291.py').read_bytes(),
        'CLOSEOUT_CONTRACT.md': regular(HERE / 'CLOSEOUT_CONTRACT.md').read_bytes()}
    copies.update({'before-' + name: raw for name, raw in docs.items()})
    tool_manifest = {'kind': 'SECTION291_PUBLIC_CLOSEOUT_TOOLS_ONLY',
        'files': {name: {'bytes': len(raw), 'sha256': sha256(raw).hexdigest()} for name, raw in copies.items()},
        'private_contents_or_hash_lists_copied': False, 'tests_GUI_game_chat_or_git_write_executed_by_helper': False}
    print(json.dumps({'gates_passed': True, 'apply_requested': args.apply, 'necessary_actual_methods': test_ref['methods_run'],
        'window_actual_unique_checks': fixture['unique_checks'], 'planned_public_files': list(mutations),
        'full_suite_rerun': False, 'last_full_section': 290, 'next_full_validation_after': 305,
        'continuous_numeric_target': None, 'cloud_publication_claimed': False}, ensure_ascii=False))
    if not args.apply:
        return
    # Recheck originals immediately before allowlisted writes; no stale proposal.
    for name, raw in docs.items():
        require(regular(name).read_bytes() == raw, 'public document unchanged during proposal: ' + name)
    map_current(tests['source_sha256_after'], 'final pre-write necessary sources')
    archive.mkdir(parents=True)
    for name, raw in copies.items():
        with (archive / name).open('xb') as stream: stream.write(raw)
    with (archive / 'archive-manifest.json').open('xb') as stream: stream.write(encode(tool_manifest))
    for name, raw in mutations.items():
        path = relpath(name); path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb' if name == 'verification/sections/291.json' else 'wb') as stream: stream.write(raw)
    print(json.dumps({'section': 291, 'local_closeout_written': True, 'cloud_published': False,
        'next_section': 292, 'next_full_validation_after': 305}, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--necessary-receipt', required=True)
    parser.add_argument('--window-receipt', required=True)
    parser.add_argument('--window-process-receipt', required=True)
    parser.add_argument('--main-window-receipt', default='verification/sections/291-main-window.json')
    parser.add_argument('--focus-receipt', default='verification/sections/291-main-window-focus.json')
    parser.add_argument('--apply', action='store_true')
    main(parser.parse_args())
