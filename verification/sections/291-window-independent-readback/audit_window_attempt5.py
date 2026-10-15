"""Pure readback of already executed291 native attempt5; no Qt/product imports."""
from hashlib import sha256
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'verification/sections/291-window-attempt5'
OUT = Path(__file__).resolve().parent / 'readback.json'
MANIFEST_SHA = 'd693d64ad0d47579e8eef5c3308deb08fb59632efe2450f667864a686c6c16ce'
PRIOR = {
    1: '127604adf333f6c038535cf6e3cbd4e8af496bf52b350a9491b8c86d1157dacc',
    2: '57f15e6508ad5213e0d2b53322e045409947539f99092788788d4befda39e43d',
    3: 'fa081c2a614679b943ca68ccd3f89710ddf948fd2be6081cb7aaec23496c9da6',
    4: '0ef50df6c0225fa842994969a9f01afeb4a60a364b61af18826649f78219c630',
}
SIZES = [[1050, 720], [1280, 800], [1440, 930]]
IMAGE_NAMES = ['layout-1', 'layout-2', 'layout-3', 'bound-current', 'bound-history', 'fixed-ro6_t_10', 'fixed-ro6_t_11']
EXTERNAL_KEYS = {'game_enumeration', 'game_connect', 'game_capture', 'game_next_frame', 'desktop_start', 'desktop_request', 'provider_chat', 'credential_read'}


def require(value, reason):
    if value is not True:
        raise ValueError(reason)


def raw(path, boundary=ROOT):
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(boundary.resolve()), 'unsafe/nonregular: ' + str(path))
    return path.read_bytes()


def digest(value):
    return sha256(value).hexdigest()


def read(name):
    return json.loads(raw(ARCHIVE / name, ARCHIVE))


def audit_manifest(folder, expected):
    value = raw(folder / 'archive-manifest.json')
    require(digest(value) == expected, 'exact sealed manifest: ' + folder.name)
    manifest = json.loads(value)
    require(manifest['kind'] == '291_EXACT_PUBLIC_NATIVE_ATTEMPT_OUTPUTS' and manifest['original_actual_paths_preserved'] is True and manifest['private_state_copied'] is False, 'public actual archive scope')
    for name, record in manifest['files'].items():
        value = raw(folder / name, folder)
        require(digest(value) == record['sha256'] and len(value) == record['bytes'], 'exact member: ' + folder.name + '/' + name)
    return manifest


def main():
    require(not OUT.exists(), 'fresh audit destination required')
    manifest = audit_manifest(ARCHIVE, MANIFEST_SHA)
    require(manifest['attempt'] == 5 and len(manifest['files']) == 17, 'actual attempt5 member scope')
    receipt_raw = raw(ARCHIVE / 'actual/window.json')
    receipt = json.loads(receipt_raw)
    process, supervisor = read('process.json'), read('supervisor.json')
    require(process['kind'] == 'actual_native_window_owned_process_execution' and process['attempt'] == 5 and process['section'] == 291 and process['status'] == 'completed', 'actual process ownership and attempt')
    require(process['exit_code'] == process['child_primary_exit'] == 0 and process['timed_out'] is False and process['owned_popen_retained'] is True and process['owned_job_no_live_execution_verified'] is True, 'actual retained process terminal0')
    require(process['window_receipt_sha256'] == digest(receipt_raw) and process['window_receipt_passed'] is True and process['source_before_after_unchanged'] is True, 'process binds this receipt')
    require(supervisor['kind'] == 'SECTION291_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION' and supervisor['status'] == 'completed' and supervisor['child_primary_exit'] == supervisor['supervisor_exit'] == 0 and supervisor['timed_out'] is False and supervisor['deadline_seconds'] == 180.0, 'actual child/supervisor/deadline')
    require(supervisor['argv'] == process['child_argv'] and process['argv'][process['argv'].index('--') + 1:] == process['child_argv'] and process['argv'][process['argv'].index('--timeout') + 1] == '180', 'actual supervisor and child argv')
    require(process['child_argv'][4] == str(ROOT / 'scripts/verify_peace_guardian_window_291.py') and process['child_argv'][-2:] == ['--visible-ms', '120000'], 'canonical native child and visible duration')
    supervisor_source = raw(ARCHIVE / 'execution-tools/supervisor.py')
    window_source = raw(ARCHIVE / 'execution-tools/window.py')
    require(supervisor['supervisor_sha256'] == process['supervisor_sha256'] == digest(supervisor_source), 'exact executed supervisor')
    require(digest(window_source) == digest(raw(ROOT / 'scripts/verify_peace_guardian_window_291.py')), 'exact executed canonical window tool')
    require(supervisor['owned_job_assigned'] is True and supervisor['owned_handle_retained'] is True and supervisor['global_process_termination'] is False and supervisor['owned_job_no_live_execution_verified'] is True, 'owned job cleanup boundary')
    require(supervisor['owned_job_active_processes_after_child_exit'] == 1 and supervisor['owned_descendants_still_live'] is True and b'win32job.TerminateJobObject(job,125)' in supervisor_source, 'one residual owned process was cleaned rather than presumed naturally exited')
    require(receipt['section'] == 291 and receipt['passed'] is True and receipt['failure'] is None and receipt['qpa'] == 'windows' and receipt['qt_exit_code'] == 0 and receipt['verification_window_closed'] is True, 'actual native result and Qt closure')
    checks = receipt['checks']
    require(len(checks) == len(set(checks)) == receipt['unique_checks'] == 140 and receipt['successful_assertion_executions_including_repeated_guards'] == 367, 'distinct assertions separate from repeated guards')
    required = {
        'fresh_MOVE_source_packet_valid', 'native_windows_QPA', 'automatic_sampling_disabled', 'sampling_timer_inactive',
        'no_capture_target', 'desktop_backend_not_started', 'all_external_operation_attempt_counts_zero',
        'two_explicit_positions_and_two_fixed_stages_with_placeholders', 'position_and_fixed_stage_default_unselected',
        'reference_buttons_disabled_without_manual_selection', 'exact_two_resident_fixed_battle_choices',
        'exact_MOVE_documented_result_role', 'one_way_documentation_not_sourceScene_or_converse_proof',
        'all_actual_MOVE_outcomes_unknown', 'VISION_does_not_inherit_MOVE_exception',
        'exact_raw_MOVE_annotation_and_original_IDs_preserved', 'player_keeps_completion_target_and_movement_unknown',
        'fixed_battle_references_not_added_as_MOVE_outcomes',
        'initial_public_directory_has_no_node_context_or_bound_dossier',
        'first_unbound_reference_click_enables_explicit_view_selected_node_button',
        'first_unbound_reference_click_does_not_create_or_replace_reading_binding',
        'first_unbound_reference_click_preserves_selected_event_reading',
        'first_unbound_probe_reset_disables_explicit_view_without_selection',
        'actual_window_client_size_matches_requested_layout_size',
        'sampling_page_has_real_scroll_range_at_720_height',
        'sampling_page_bottom_information_fully_reachable_without_clipping',
        'sampling_page_scroll_test_preserves_node_reading',
        'bound_event_refresh_keeps_dossier_key_search_tab_scroll_and_selection',
        'real_signal_chain_preserves_bound_event_reading_after_reference_navigation',
        'set_map_refresh_preserves_reference_origin_and_bound_event_reading',
        'reference_origin_retains_full_typed_binding_after_map_refresh',
        'reference_map_technical_toggle_keeps_bound_event_reading',
        'explicit_view_selected_map_node_uses_latest_selection_not_old_event_context',
        'explicit_selected_node_view_replaces_reading_only_after_user_intent',
        'ordinary_MapView_selection_still_follows_original_bound_dossier_flow',
        'history_labels_separate_recorded_and_past_type_evidence',
        'unknown_map_floor_not_taken_from_directory_filter',
        'historical_set_map_refresh_preserves_bound_event_and_reference_position',
        'latest_panel_context_rejects_stale_position_before_signal',
        'latest_App_graph_duplicate_rejects_before_MapView_navigation',
        'new_run_same_map_IDs_cannot_reuse_reference_origin',
        'new_run_reference_expiry_does_not_auto_rebind_old_reading',
        'two_manual_fixed_previews_never_become_event_outcomes',
        'cloned_public_source_initially_valid', 'invalid_source_clears_all_old_reference_data',
        'invalid_source_disables_both_reference_buttons', 'invalid_source_retains_raw_condition_and_explicit_unknown',
        'public_seed_graph_not_mutated_by_reference_UI', 'all_reference_interactions_leave_temporary_run_memory_unchanged',
        'all_bound_public_sources_unchanged', 'all_external_operation_attempt_counts_zero_at_actual_closure',
    }
    for label in ('same_ID_changed_position', 'same_ID_changed_type_evidence', 'changed_template', 'changed_history_context'):
        for suffix in ('clears_expired_reference_origin_without_rebinding', 'expired_reference_does_not_replace_event_reading', 'expired_reference_disables_explicit_button', 'explicit_button_does_not_fallback_to_old_node_context', 'direct_explicit_handler_also_rejects_missing_latest_selection'):
            required.add(label + '_' + suffix)
    for stage in ('ro6_t_10', 'ro6_t_11'):
        for suffix in ('manual_button_opens_actual_fixed_battle_preview', 'actual_fixed_battle_grid_loaded', 'fixed_preview_does_not_change_map_position_or_event_reading'):
            required.add(stage + '_' + suffix)
    for widget in ('resident_reference_label', 'resident_location', 'resident_map_button', 'resident_stage', 'resident_stage_button'):
        required.add('invalid_source_' + widget + '_hidden')
        required.add('layout_' + widget + '_visible')
        required.add('layout_' + widget + '_fully_inside_window_and_parent')
    require(required.issubset(checks), 'all required initial/bound/history/expiry/source/preview/layout state guards')
    sources = receipt['source_sha256_before']
    require(len(sources) == 29 and sources == receipt['source_sha256_after'], 'actual29 bound sources before/after identical')
    for name, expected in sources.items():
        require(digest(raw(ROOT / name)) == expected, 'current exact accepted source: ' + name)
    require(sources['scripts/verify_peace_guardian_window_291.py'] == digest(window_source), 'native tool included in before/after source map')
    geometry = receipt['geometry_observations']
    require(len(geometry) == receipt['geometry_stages_observed'] == 3 and [row['requested_size'] for row in geometry] == SIZES and [row['actual_size'] for row in geometry] == SIZES, 'three exact logical QWidget dimensions')
    for row in geometry:
        require(row['player_size'][0] >= 260 and row['player_size'][1] >= 120 and row['native_window']['qpa'] == 'windows' and row['native_window']['process_id'] == receipt['process_id'] and row['native_window']['hwnd'] > 0, 'actual process-owned native geometry and operational player area')
        require(set(row['controls']) == {'resident_reference_label', 'resident_location', 'resident_map_button', 'resident_stage', 'resident_stage_button'}, 'all five reference controls measured')
    images = receipt['screenshots']
    require(len(images) == receipt['screenshot_count'] == 7 and [row['name'] for row in images] == IMAGE_NAMES, 'exact seven screenshot states')
    image_rows = {}
    for row in images:
        path = ARCHIVE / 'actual' / Path(row['path']).name
        value = raw(path, ARCHIVE)
        require(digest(value) == row['sha256'] and value[:8] == b'\x89PNG\r\n\x1a\n' and row['native_window']['process_id'] == receipt['process_id'], 'actual screenshot binding/native owner: ' + row['name'])
        image_rows[row['name']] = {'relative': path.relative_to(ROOT).as_posix(), 'sha256': digest(value), 'PNG_physical_size': list(struct.unpack('>II', value[16:24]))}
    for index in range(3):
        image = image_rows['layout-' + str(index + 1)]
        require(image['PNG_physical_size'] == [size * 3 // 2 for size in SIZES[index]], 'actual 150-percent DPI screenshot dimensions, distinct from logical widget size')
    for name, node_id, historical in (('bound-current', '0,2', False), ('bound-history', '1,1', True)):
        snapshot = next(row['reading_state'] for row in images if row['name'] == name)
        require(snapshot['selected_key'] == snapshot['detail_key'] == 'event:community_group_019' and snapshot['node_context'][1] == '2,3' and snapshot['player']['vertical'] > 0 and bool(snapshot['player']['selected_text']) and bool(snapshot['search_selected_text']), 'bound event reading retains nonzero scroll/selection separately from reference position')
        require(snapshot['position']['node_id'] == node_id and snapshot['position']['map_historical'] is historical, 'current/historical typed reference evidence')
    observations = receipt['public_observations']
    require(len(observations) == 1 and observations[0]['manual_fixed_stage_requests'] == ['ro6_t_10', 'ro6_t_11'], 'both and only two manual fixed battle requests')
    observation = observations[0]
    require(all(observation[key] is None for key in ('actual_current_floor_completion', 'actual_target', 'actual_movement', 'actual_battle')) and observation['reference_positions_are_not_route_or_destination_choices'] is True, 'actual movement/completion/target remain unknown')
    require(set(receipt['external_operation_attempts']) == EXTERNAL_KEYS and all(type(value) is int and value == 0 for value in receipt['external_operation_attempts'].values()), 'all eight external attempts actually0')
    require(receipt['state_paths_replaced_before_constructor'] == ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'] and receipt['temporary_state_root'] is True and receipt['private_state_read_copied_or_restored'] is False and receipt['external_entrypoints_blocked_before_original_call'] is True and receipt['game_captures'] == 0 and receipt['game_operated'] is False and receipt['chat_sent'] is False and receipt['chat_attempted'] is False and receipt['original_project_window_operated_or_restarted'] is False, 'isolated public state and game/chat/original-window boundary')
    prior_rows = []
    for attempt, expected in PRIOR.items():
        folder = ARCHIVE.parent / ('291-window-attempt' + str(attempt))
        previous = audit_manifest(folder, expected)
        old_process = json.loads(raw(folder / 'process.json'))
        old_receipt = json.loads(raw(folder / 'actual/window.json'))
        require(old_process['exit_code'] == 1 and old_receipt['passed'] is False and old_receipt['failure'] is not None, 'original failed attempt remains failed: ' + str(attempt))
        prior_rows.append({'attempt': attempt, 'manifest_sha256': expected, 'sealed_members_verified': len(previous['files']), 'actual_process_exit': 1, 'raw_passed': False, 'failure_message': old_receipt['failure']['message'], 'counted_as_current_PASS': False})
    require(digest(raw(ARCHIVE / 'archive-manifest.json')) == MANIFEST_SHA, 'sealed final archive unchanged')
    report = {
        'kind': 'INDEPENDENT_PURE_291_NATIVE_ATTEMPT5_READBACK_NOT_TEST_EXECUTION',
        'auditor_sha256': digest(raw(Path(__file__))), 'section': 291, 'attempt': 5,
        'archive_manifest_sha256': MANIFEST_SHA, 'sealed_members_sha256_and_size_verified': 17,
        'actual_receipt_sha256': digest(receipt_raw), 'bound_sources_fresh_before_after_match': 29,
        'actual_unique_checks': 140, 'actual_successful_executions_including_repeated_guards': 367,
        'actual_logical_window_sizes': SIZES, 'physical_PNG_sizes_and_sha256': image_rows,
        'actual_manual_fixed_preview_requests': observation['manual_fixed_stage_requests'],
        'actual_process_exit': 0, 'actual_child_primary_exit': 0, 'actual_supervisor_exit': 0,
        'actual_timed_out': False, 'actual_qpa': 'windows', 'actual_qt_exit': 0,
        'actual_verification_window_closed': True,
        'owned_job_active_processes_after_child_exit': 1, 'owned_descendants_still_live_at_that_observation': True,
        'subsequent_owned_job_no_live_execution_verified': True, 'all_descendants_naturally_exited_claimed': False,
        'all_eight_external_attempts_zero': True, 'all_actual_MOVE_outcomes_still_unknown': True,
        'required_initial_bound_history_technical_expiry_source_and_preview_states_present': True,
        'original_failed_attempts_preserved_not_counted_as_PASS': prior_rows,
        'current_component_readback_passed': True, 'full_suite_or_all_P3_complete_claimed': False,
        'PNG_manual_visual_review_performed_by_this_auditor': False,
        'runtime_tests_or_GUI_reexecuted_by_this_auditor': False, 'additional_test_count': 0,
        'private_state_or_other_projects_read': False,
    }
    encoded = (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with OUT.open('xb') as stream:
        stream.write(encoded)
    require(raw(OUT) == encoded, 'audit report byte readback')
    print(json.dumps({'cache_report': OUT.relative_to(ROOT).as_posix(), 'report_sha256': digest(encoded), 'actual_component_readback_passed': True, 'additional_test_count': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
