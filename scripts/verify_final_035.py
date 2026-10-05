"""Verify 0.35 evidence, actual app and preservation of the fresh current run."""
import compileall
import ctypes
import hashlib
import json
import sys
import time
import tomllib
from pathlib import Path

import win32gui
import win32process

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts, partition
from verify_launch_035 import foreground


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))


def digest(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main():
    calculation = read('NEURAL_0.35_VERIFICATION.json')
    ui = read('UI_0.35_VERIFICATION.json')
    launch = read('APP_0.35_LAUNCH_VERIFICATION.json')
    audit = read('RELIC_VERIFICATION.json')
    evidence = read('.cache/research/neural-035/evidence.json')
    previous = read('FINAL_0.34_VERIFICATION.json')
    before_audit = read('.cache/batch-035-before/RELIC_VERIFICATION.json')
    data = mechanics()
    assert all(p['version'] == '0.35.0' for p in (calculation, ui, launch, audit, evidence))
    assert calculation['passed'] and calculation['failures'] == calculation['errors'] == 0
    assert calculation['current_tests_passed'] == 268 and calculation['new_tests'] == 20
    assert calculation['tests_run'] == 338
    assert calculation['historical_combat_tests_skipped'] == len(calculation['skipped_tests']) == 70
    assert calculation['public_before_after_cases'] == 348
    assert calculation['unchanged_cases'] == 344 and calculation['changed_s3_cases'] == 4
    assert digest(calculation['test_log']) == calculation['test_log_sha256']
    assert digest('.cache/neural-035/before-public-results.json') == calculation['baseline_sha256']

    expected_scope = {
        'items': {'reference_only': 75, 'mixed': 4, 'offline': 193},
        'offline_mechanism_gaps': {'pending': 10, 'partial': 9},
    }
    assert scope_counts(data) == calculation['offline_scope'] == audit['offline_scope'] == expected_scope
    assert data['counts'] == calculation['data_rule_counts'] == audit['data_rule_counts'] == {
        'numeric': 119, 'conditional': 28, 'partial': 12, 'pending': 61, 'non_output': 52,
    }
    active = [(r, p) for r, p in data['relics'].items() if partition(p, r)[0]]
    assert len(active) == 135 and sum(not partition(p, r)[2] for r, p in active) == 126
    assert calculation['raw_relic_data_unchanged']
    assert digest('rouge/data/relic-mechanics.json') == previous['source_sha256']['rouge/data/relic-mechanics.json']
    assert digest('.cache/game-data/roguelike_topic_table.json') == data['source_sha256'] == audit['source_sha256']
    assert data['commit'] == evidence['source_commit'] == audit['source_commit']
    for name, primary in evidence['primary_sources'].items():
        assert digest('.cache/game-data/' + name + '.json') == primary['sha256'], name
        assert evidence['source_commit'] in primary['url']
    assert evidence['skill_id'] == 'skchr_phatm2_3'
    skill = evidence['raw_skill_level_10']
    blackboard = {p['key']: p['value'] for p in skill['blackboard']}
    assert skill['name'] == '空剧场' and skill['duration'] == 30
    assert '技能期间酒神造成过' in skill['description'] and '直至爆发' in skill['description']
    assert blackboard['atk'] == 1.25 and blackboard['ep_damage_ratio'] == .1 and blackboard['interval'] == 1
    assert skill['spData']['spCost'] == 40 and skill['spData']['initSp'] == 30
    assert evidence['standing_instruction_file'] == 'AGENTS.md' and evidence['unknowns']
    assert '未知项不耗费精力猜测机制' in evidence['user_rule']
    instructions = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
    assert 'every later operation' in instructions and 'retain an explicit unknown' in instructions

    recognition_names = (
        'rouge/relic_recognition.py', 'rouge/run_state.py', 'rouge/run_config.py',
        'rouge/run_recognition.py', 'rouge/resource_recognition.py', 'rouge/recognition.py',
        'rouge/visual_recognition.py', 'rouge/data/run-config.json',
        'rouge/data/relic-reference-equivalence.json',
    )
    for name in recognition_names:
        assert digest(name) == previous['source_sha256'][name], name
    clock_names = (
        'rouge/timing.py', 'rouge/sp_events.py', 'rouge/damage.py',
        'rouge/estimate.py', 'rouge/deployment.py', 'rouge/offline_scope.py', 'rouge/catalog.py',
    )
    for name in clock_names:
        assert digest(name) == before_audit['source_hashes'][name], name
    app_before = (ROOT / '.cache/batch-035-before/rouge/app.py').read_text(encoding='utf-8')
    assert (ROOT / 'rouge/app.py').read_text(encoding='utf-8') == app_before.replace(
        '黑流树海助手 0.34 · 识别与计算测试版', '黑流树海助手 0.35 · 识别与计算测试版')
    manifest = read('.cache/batch-035-before/manifest.json')
    public_backups = {
        'rouge/operator_engine.py', 'rouge/elemental_relics.py', 'rouge/reporting.py',
        'rouge/app.py', 'pyproject.toml', 'PROJECT_PROGRESS.md', 'WORK_IN_PROGRESS.md',
        'README.md', 'RELIC_VERIFICATION.json', 'RELIC_COVERAGE.md',
    }
    assert set(manifest['source_sha256']) == public_backups
    for name, checksum in manifest['source_sha256'].items():
        assert digest('.cache/batch-035-before/' + name) == checksum, name

    assert ui['passed'] and ui['skills_checked'] == 87 and ui['panel_scenarios'] == 174
    assert ui['secondary_section_scenarios'] == 2
    assert ui['base_partial_sections'] == 1 and ui['river_partial_sections'] == 3
    assert ui['river_reference_sections'] == 6
    for flag in ('unrelated_sections_hidden', 'native_options_appropriate',
                 'event_input_absent', 'private_data_isolated'):
        assert ui[flag], flag
    assert audit['audit_count'] == 272 and audit['public_entry_cases'] == 8704
    assert audit['bound_recipient_cases'] == 609 and audit['forbidden_skill_cases'] == 87
    icons = read('TARGET_ICON_VERIFICATION.json')
    assert icons['count'] == len(icons['icons']) == 15
    for icon in icons['icons']:
        assert digest('rouge/data/' + icon['file']) == icon['sha256']
    source_hashes = {}
    for receipt in (calculation, ui, audit):
        for name, checksum in receipt['source_hashes'].items():
            assert digest(name) == checksum, name
            source_hashes[name] = checksum
    for name in recognition_names + clock_names:
        source_hashes[name] = digest(name)
    for name in ('scripts/verify_relic_mechanics.py', 'scripts/verify_final_035.py',
                 'scripts/verify_launch_035.py', 'pyproject.toml', 'AGENTS.md'):
        source_hashes[name] = digest(name)

    for receipt in (calculation, ui, launch):
        assert receipt['game_actions'] == receipt['chat_requests'] == 0
    for flag in ('only_one_project_window', 'window_visible_and_restored', 'same_run_preserved',
                 'history_preserved', 'settings_and_bindings_unchanged', 'run_cmd_startup_verified',
                 'within_monitor_work_area', 'window_raised', 'previous_app_process_stopped_before_launch'):
        assert launch[flag], flag
    assert launch['run_state_writes_by_upgrade_script'] == 0
    assert launch['launcher_sha256'] == digest('run.cmd')
    assert len(launch['stability_checks']) == 6 and launch['observation_seconds'] == 20
    assert all(c['visible_and_responsive'] for c in launch['stability_checks'])
    assert launch['launcher_stderr_bytes'] == 0
    checkpoint = read('.cache/upgrade-0.35-checkpoint.json')
    run = read('.local/run-state.json')
    assert checkpoint['history_count'] == launch['history_count_before'] == 8
    assert len(run['history']) >= checkpoint['history_count']
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest() == checkpoint['run_id_hash']
    prefix = run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == checkpoint['history_prefix_hash']
    for name, checksum in checkpoint['config_hashes'].items():
        assert digest(name) == checksum, name
    assert len(checkpoint['config_hashes']) == launch['configuration_files_checked'] == 2

    live = []
    def visit(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if title.startswith('黑流树海助手'):
            live.append({'hwnd': hwnd, 'title': title,
                         'pid': win32process.GetWindowThreadProcessId(hwnd)[1],
                         'visible': bool(win32gui.IsWindowVisible(hwnd)),
                         'minimized': bool(win32gui.IsIconic(hwnd)),
                         'hung': bool(ctypes.windll.user32.IsHungAppWindow(hwnd))})
    win32gui.EnumWindows(visit, None)
    assert len(live) == 1 and '0.35' in live[0]['title'] and live[0]['pid'] == launch['process_id'], live
    assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung'], live
    assert tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version'] == '0.35.0'
    ended = read('.cache/automation-ended-028.json')
    assert ended['automation_id'] == '1-3' and ended['app_delete_result'] == 'deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert read('.cache/kill-recovery-030-superseded/STATUS.json')['status'] == 'superseded_by_user_scope_change'
    assert all(compileall.compile_dir(str(ROOT / f), quiet=2) for f in ('rouge', 'scripts', 'tests'))

    names = (
        'BATCH_0.35.md', 'PROJECT_PROGRESS.md', 'WORK_IN_PROGRESS.md', 'README.md', 'AGENTS.md',
        'RELIC_COVERAGE.md', 'NEURAL_0.35_VERIFICATION.json', 'UI_0.35_VERIFICATION.json',
        'APP_0.35_LAUNCH_VERIFICATION.json', 'RELIC_VERIFICATION.json', 'TARGET_ICON_VERIFICATION.json',
        '.cache/research/neural-035/evidence.json', calculation['test_log'],
        '.cache/neural-035/before-public-results.json', '.cache/upgrade-0.35-checkpoint.json',
        '.cache/batch-035-before/manifest.json', '.cache/automation-ended-028.json',
    )
    focused = foreground(live[0]['hwnd'])
    receipt = {
        'version': '0.35.0', 'passed': True, 'verified_at': time.time(),
        'calculation_scope': 'offline_stable_effects', 'scope': expected_scope,
        'active_relic_rules': 135, 'current_tests_passed': 268, 'new_tests': 20,
        'historical_combat_tests_skipped': 70, 'public_before_after_cases': 348,
        'unchanged_cases': 344, 'changed_s3_cases': 4, 'skill_ui_cases': 87, 'ui_panel_scenarios': 174,
        'public_entry_cases': 8704, 'bound_recipient_cases': 609,
        'forbidden_skill_cases': 87, 'bound_icon_hashes': 15,
        'standing_evidence_rule': 'AGENTS.md', 'raw_and_derived_relic_data_unchanged': True,
        'recognition_unchanged_from_034': True, 'attack_and_sp_timing_modules_unchanged': True,
        'process_id': live[0]['pid'], 'test_window_open': True, 'window_raised': True,
        'foreground_on_final_check': focused, 'run_cmd_startup_verified': True,
        'previous_app_process_stopped_before_launch': True,
        'same_current_run_and_history_preserved': True,
        'history_count_before': checkpoint['history_count'], 'history_count_after': len(run['history']),
        'private_configuration_files_verified': len(checkpoint['config_hashes']),
        'automation_id': '1-3', 'automation_status': 'DELETED', 'all_priorities_1_to_3_completed': False,
        'new_game_actions': 0, 'chat_requests': 0, 'run_state_writes_by_upgrade_script': 0,
        'new_live_combat_measurements': 0,
        'checks': [
            'Standing evidence-first rule persisted; pinned skill/character source hashes verified',
            'S1 attack-attached sources require emitted attacks; no fabricated global S3 ticks',
            'Unknown secondary sequence excludes direct-only burst prediction from known arts subtotal',
            '268 current regressions, 348 old public cases, 87 skills and 174 isolated UI scenarios',
            '8704 entries, 609 bindings, 87 forbidden skills, 15 icon hashes and compileall',
            'Relic data/recognition/timing modules unchanged; fresh 8-record prefix/configuration preserved',
            'Old app stopped before unique visible responsive 0.35 window; automation remains deleted',
        ],
        'source_sha256': source_hashes, 'evidence_sha256': {n: digest(n) for n in names},
        'limits': calculation['limits'] + [
            '10 offline pending and 9 data-partial items; priorities 1-3 remain incomplete.',
            'Bilibili episode and boss drop sheet are unread leads, not verified mechanism evidence.',
            'Window visible/raised does not imply Windows granted keyboard foreground focus.',
        ],
    }
    (ROOT / 'FINAL_0.35_VERIFICATION.json').write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in (
        'passed', 'current_tests_passed', 'skill_ui_cases', 'ui_panel_scenarios', 'process_id',
        'test_window_open', 'foreground_on_final_check', 'history_count_before', 'history_count_after',
        'automation_status', 'all_priorities_1_to_3_completed')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
