"""Finalize refresh/pictures/predicted-only views with scoped state evidence."""
import compileall, hashlib, json, sys, time, tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_launch_045 import windows, verify_process, foreground, state
from rouge.battle_preview import battle_data
from rouge.offline_scope import scope_counts, partition
from rouge.relics import mechanics


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))


def digest(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def text(name):
    return (ROOT / name).read_text(encoding='utf-8')


def main():
    core = read('REFRESH_0.45_VERIFICATION.json')
    ui = read('UI_0.45_VERIFICATION.json')
    skill = read('SKILL_UI_0.45_VERIFICATION.json')
    launch = read('APP_0.45_LAUNCH_VERIFICATION.json')
    assert all(r['version'] == '0.45.0' and r['passed'] for r in (core, ui, skill, launch))
    assert core['current_tests_passed'] == 454 and core['tests_run'] == 524
    assert core['historical_combat_tests_skipped'] == 70 and core['new_unit_tests'] == 33
    assert core['failures'] == core['errors'] == 0
    assert digest(core['test_log']) == core['test_log_sha256']
    assert core['calibrated_bitmaps'] == 4 and len(core['bound_stages']) == 8
    assert core['remaining_stages'] == 97 and core['remaining_bitmap_identities'] == 67
    assert len(core['independent_landmarks']) == 20 and core['max_error_px'] <= core['tolerance_px'] == 4
    assert core['prior_calibration_records_unchanged'] and core['acute_independent_checks_unchanged_from_rejected_044']
    assert core['not_a_whole_map_precision_guarantee'] and core['all_105_map_bytes_unchanged']
    assert core['calibrated_spawn_rows'] == 166 and core['calibrated_route_point_references'] == 1556
    assert core['visible_tile_center_inverse_checks'] == 540
    assert core['calculation_functions_unchanged'] and core['recognition_and_run_state_sources_unchanged']
    assert core['estimate_and_report_only_heading_changed'] and core['enemy_preview_numerical_reference_unchanged']
    assert not core['actual_absolute_timeline_claimed'] and not core['actual_pathfinding_claimed']
    assert not core['numeric_public_replay_rerun'] and core['inherited_numeric_cases'] == 732
    assert not core['new_recognition_speed_claim'] and core['synthetic_refresh_tests_only']
    assert ui['private_data_isolated'] and ui['battle_data_readonly'] and ui['run_state_unchanged']
    assert ui['battle_stages_checked'] == 105 and ui['battle_enemy_panels_checked'] == 1087
    assert ui['battle_occurrence_selections'] == 4764 and ui['battle_resize_clicks'] == 3
    assert ui['calibrated_stage_clicks'] == 24 and ui['projected_row_selection_checks'] == 182
    assert ui['letterbox_sizes_checked'] == 4 and ui['battle_predicted_only_attribute_display_checked']
    for key in ('original_and_grid_selection_synced', 'occurrence_synced_on_original',
                'non_spawn_selection_clears_both_maps', 'letterbox_clicks_rejected',
                'same_size_wrong_bitmap_rejected', 'missing_bitmap_rejected',
                'uncalibrated_map_has_no_markers_or_click_mapping', 'broken_route_continuous_line_not_drawn',
                'continuous_checkpoint_reference_drawn', 'unknown_stage_cleared'):
        assert ui[key], key
    for key in ('battle_screenshot', 'enemy_skill_screenshot', 'fixed_map_screenshot', 'fixed_map_detail_screenshot'):
        assert digest(ui[key]) == ui[key + '_sha256']
    assert skill['private_data_isolated'] and skill['skills_checked'] == 87
    assert skill['panel_scenarios'] == 348 and skill['book_panels'] == 174 and skill['synthetic_module_panels'] == 18
    assert skill['wine_phase_panels'] == 22 and skill['book_combination_panels'] == 9
    assert skill['unrelated_sections_hidden'] and skill['event_input_absent']
    assert digest(skill['refill_screenshot']) == skill['refill_screenshot_sha256']
    hashes = {}
    for receipt, key in ((core, 'source_sha256'), (ui, 'source_hashes'), (skill, 'source_hashes')):
        for name, sha in receipt[key].items():
            assert digest(name) == sha, name
            hashes[name] = sha
    previous = read('FINAL_0.44_VERIFICATION.json')
    changed = {n for n, sha in previous['source_sha256'].items() if digest(n) != sha}
    assert changed == set(core['changed_existing_tracked_files'])
    backup = '.cache/batch-045-before/'
    manifest = read(backup + 'manifest.json')
    assert len(manifest) == 15
    assert all(digest(backup + name) == sha for name, sha in manifest.items())
    catalog = read('rouge/data/view-catalog.json')
    portraits = catalog['images']
    assert len(portraits) == 735 and len(catalog['operators']) == 431 and len(catalog['enemies']) == 334
    source = battle_data()['source']
    assert catalog['source']['game_commit'] == source['game_commit']
    assert catalog['source']['resource_commit'] == source['resource_commit']
    assert digest('.cache/research/visual-catalog-045/stage-floor-input.json') == catalog['source']['floor_input_sha256']
    files = set()
    total = 0
    for record in portraits.values():
        name = 'rouge/data/' + record['file']
        raw = (ROOT / name).read_bytes()
        assert digest(name) == record['sha256'] and len(raw) == record['bytes']
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == record['blob_sha1']
        assert raw.startswith(b'\x89PNG\r\n\x1a\n')
        total += len(raw)
        files.add((ROOT / name).resolve())
    assert files == {p.resolve() for p in (ROOT / 'rouge/data/portraits').glob('*.png')}
    assert total == 37603409
    missing = sorted(k for k, v in catalog['enemies'].items() if v['portrait'] is None)
    assert missing == sorted(['enemy_2156_shsmok', 'enemy_2154_shdfb', 'enemy_1177_dufrbl_2', 'enemy_2121_dyspl2'])
    floors = dict(Counter(v['group'] for v in catalog['stages'].values()))
    assert floors == {'floor_1': 11, 'floor_2': 13, 'floor_3': 18, 'floor_4': 20, 'floor_5': 17, 'hidden': 5, 'unconfirmed': 21}
    rank_unknown = read('.cache/research/visual-catalog-045/portrait-download-receipt.json')['rank_unknown']
    assert len(rank_unknown) == 8 and len({v['enemy_id'] for v in rank_unknown}) == 4
    progress = text('PROJECT_PROGRESS.md')
    for token in ('已接入', '已完成', '验收：', 'FINAL_0.', '## 上批', '## 证据入口'):
        assert token not in progress, token
    assert '97个关卡、67张独立原图' in progress and '急不可耐' not in progress
    assert '4个辅助实体' in progress and '21个事件/特殊关卡' in progress
    for line in text(backup + 'PROJECT_PROGRESS.md').splitlines():
        if '固定战斗地图映射' not in line:
            assert line in progress, line
    completed = text('PROJECT_COMPLETED.md')
    header = '## 0.44 · 六个关卡的固定原图映射'
    assert completed.count('## 0.45 · 刷新保留、图片分类与预测面板') == 1
    assert completed.split(header, 1)[1] == text(backup + 'PROJECT_COMPLETED.md').split(header, 1)[1]
    assert text('WORK_IN_PROGRESS.md').endswith(text(backup + 'WORK_IN_PROGRESS.md'))
    assert '# 黑流树海助手 · 0.45' in text('README.md')
    assert tomllib.loads(text('pyproject.toml'))['project']['version'] == '0.45.0'
    assert launch['only_one_project_window'] and launch['window_visible_and_restored'] and launch['window_raised']
    assert launch['run_cmd_startup_verified'] and launch['launcher_stderr_bytes'] == 0
    assert launch['launcher_sha256'] == digest('run.cmd')
    assert len(launch['stability_checks']) == 6 and launch['observation_seconds'] == 20
    assert launch['initial_upgrade_audit_passed'] is False and launch['upgrade_history_prefix_preserved'] is None
    assert launch['current_run_established_before_launch'] and not launch['old_checkpoint_restored']
    assert digest(launch['initial_audit_failure']) == launch['initial_audit_failure_sha256']
    checkpoint = read(launch['checkpoint'])
    initial = read(launch['initial_checkpoint'])
    assert initial['history_count'] == 190 and initial['run_id_hash'] != checkpoint['run_id_hash']
    after = state()
    run = read('.local/run-state.json')
    prefix = run['history'][:checkpoint['history_count']]
    assert checkpoint['run_id_hash'] == after['run_id_hash']
    assert hashlib.sha256(json.dumps(prefix, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == checkpoint['history_prefix_hash']
    assert initial['config_hashes'] == checkpoint['config_hashes'] == after['config_hashes']
    assert initial['verified_at'] < run['started_at'] < launch['app_process_created_at']
    assert launch['same_current_run_preserved_after_launch'] and launch['current_history_prefix_preserved_after_launch']
    for receipt in (core, ui, skill, launch):
        assert receipt['game_actions'] == receipt['chat_requests'] == 0
    live = windows()
    assert len(live) == 1 and live[0]['pid'] == launch['process_id'] and live[0]['title'] == launch['window_title']
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
    verify_process(live[0]['pid'])
    focused = foreground(live[0]['hwnd'])
    scope = scope_counts(mechanics())
    assert scope['offline_mechanism_gaps'] == {'pending': 10, 'partial': 9}
    assert sum(bool(partition(p, rid)[0]) for rid, p in mechanics()['relics'].items()) == 135
    assert read('.cache/automation-ended-028.json')['app_delete_result'] == 'deleted'
    assert not (Path.home() / '.codex/automations/1-3/automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT / f), quiet=2) for f in ('rouge', 'scripts', 'tests'))
    for name in ('scripts/verify_final_045.py', 'scripts/verify_launch_045.py', 'scripts/verify_visible_045.py'):
        hashes[name] = digest(name)
    artifacts = ['REFRESH_0.45_VERIFICATION.json', 'UI_0.45_VERIFICATION.json', 'SKILL_UI_0.45_VERIFICATION.json',
                 'APP_0.45_LAUNCH_VERIFICATION.json', 'RECOGNITION_0.43_VERIFICATION.json',
                 '.cache/research/visual-catalog-045/portrait-download-receipt.json',
                 '.cache/research/visual-catalog-045/portrait-download-first-failure.json',
                 '.cache/research/visual-catalog-045/stage-floor-input.json',
                 '.cache/research/map-projection-045/calibration-input.json',
                 '.cache/research/map-projection-045/acute-six-anchor-fit.json',
                 '.cache/research/map-projection-045/insect-fit.json',
                 '.cache/batch-045-before/manifest.json', launch['checkpoint'], launch['initial_checkpoint'],
                 'PROJECT_PROGRESS.md', 'PROJECT_COMPLETED.md', 'WORK_IN_PROGRESS.md', 'BATCH_0.45.md', 'README.md']
    # A redirected current stdout log is still growing while this receipt is
    # written; never seal it with an intermediate hash. Keep the first failed
    # document audit separately, as an already closed historical log.
    artifacts += [str(p.relative_to(ROOT)) for p in sorted((ROOT / '.cache/refresh-045').glob('*.log'))
                  if not p.name.startswith('final')]
    artifacts.append('.cache/refresh-045/final.log')
    result = {
        'version': '0.45.0', 'passed': True, 'verified_at': time.time(), 'current_tests_passed': 454,
        'new_unit_tests': 33, 'historical_combat_tests_skipped': 70,
        'refresh_preservation_synthetic_tests_passed': True, 'predicted_only_normal_display_verified': True,
        'portrait_images': 735, 'portrait_bytes': total, 'operator_profiles_with_picture': 431,
        'enemy_ids_with_picture': 330, 'missing_enemy_picture_ids': missing,
        'stage_floor_groups': floors, 'unknown_enemy_tier_references': rank_unknown,
        'calibrated_original_bitmaps': 4, 'bound_stages': core['bound_stages'],
        'uncalibrated_stages': 97, 'uncalibrated_bitmap_identities': 67,
        'independent_landmarks': 20, 'max_independent_error_px': core['max_error_px'], 'source_pixel_check_tolerance': 4,
        'tolerance_is_not_whole_map_precision_proof': True,
        'battle_ui_stages': 105, 'battle_ui_enemy_panels': 1087, 'battle_occurrence_selections': 4764,
        'calibrated_original_clicks': 24, 'original_letterbox_sizes': 4,
        'skill_ui_rerun': True, 'skills_checked': 87, 'skill_panel_scenarios': 348,
        'book_panels': 174, 'synthetic_module_panels': 18,
        'numeric_public_cases_inherited_from': 'RECOGNITION_0.43_VERIFICATION.json', 'inherited_numeric_cases': 732,
        'numeric_public_replay_rerun': False, 'recognition_and_run_state_core_unchanged': True,
        'new_recognition_speed_claim': False, 'source_sha256': hashes,
        'changed_existing_source_files': sorted(changed), 'evidence_sha256': {n: digest(n) for n in artifacts},
        'scope': scope, 'active_relic_rules': 135, 'completed_scope_removed_from_todo': True,
        'historical_completed_records_preserved': True, 'public_backup_files': 15,
        'initial_work_start_run_matches_current': False, 'upgrade_history_prefix_preserved': None,
        'current_run_established_before_launch': True, 'current_run_and_prefix_preserved_after_launch': True,
        'post_launch_history_count_before': checkpoint['history_count'], 'history_count_after': len(run['history']),
        'state_audit_scope': launch['comparison_note'], 'private_configuration_files_verified': len(after['config_hashes']),
        'process_id': live[0]['pid'], 'test_window_open': True, 'window_raised': True,
        'foreground_on_final_check': focused, 'run_cmd_startup_verified': True,
        'run_state_writes_by_upgrade_script': 0, 'old_checkpoint_restored': False,
        'new_live_battle_captures': 0, 'game_actions': 0, 'chat_requests': 0,
        'automation_status': 'DELETED', 'all_priorities_1_to_3_completed': False,
        'limits': ['Missing four auxiliary entity images, eight derived-enemy tier references and 21 special-stage floor scopes.',
                   '97 stages / 67 bitmaps remain uncalibrated; independent landmarks do not prove whole-map accuracy.',
                   'Enemy full phase/skill/relic corrections, actual paths, absolute spawn clock and branch selection remain incomplete.',
                   'Refresh scenarios and skill panels use isolated synthetic state, not complete live-page recognition accuracy.',
                   'No pre-upgrade current-new-run prefix was observed; only the scoped post-launch prefix is verified.']
    }
    (ROOT / 'FINAL_0.45_VERIFICATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('passed', 'current_tests_passed', 'portrait_images',
        'operator_profiles_with_picture', 'enemy_ids_with_picture', 'calibrated_original_bitmaps',
        'skills_checked', 'test_window_open', 'process_id', 'post_launch_history_count_before',
        'history_count_after', 'upgrade_history_prefix_preserved', 'all_priorities_1_to_3_completed')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
