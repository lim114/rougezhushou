"""Verify current offline relic receipts and running app without state mutations."""

import compileall
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
from rouge.offline_scope import partition, scope_counts
from rouge.relics import mechanics


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))


def digest(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main():
    calculation = read('RELIC_0.31_VERIFICATION.json')
    ui = read('UI_0.31_VERIFICATION.json')
    launch = read('APP_0.31_LAUNCH_VERIFICATION.json')
    audit = read('RELIC_VERIFICATION.json')
    evidence = read('.cache/research/relics-031/evidence.json')
    data = mechanics()
    before = read('.cache/batch-031-before/rouge/data/relic-mechanics.json')
    assert all(p['version'] == '0.31.0' for p in (calculation, ui, launch, audit, evidence))
    assert calculation['passed'] and calculation['failures'] == calculation['errors'] == 0
    assert calculation['current_tests_passed'] == 178 and calculation['new_tests'] == 16
    assert calculation['historical_combat_tests_skipped'] == len(calculation['skipped_tests']) == 70
    assert calculation['tests_run'] == 178 + 70
    expected_cases = {'parts_stat_oracle_cases': 696, 'first_cost_cases': 174,
        'enemy_environment_cases': 1740, 'reference_non_interference_cases': 13050}
    for key, value in expected_cases.items():
        assert calculation[key] == value, key
    expected_scope = {'items': {'reference_only': 75, 'mixed': 4, 'offline': 193},
        'offline_mechanism_gaps': {'pending': 11, 'partial': 9}}
    assert calculation['offline_scope'] == scope_counts(data) == audit['offline_scope'] == expected_scope
    assert data['counts'] == calculation['data_rule_counts'] == audit['data_rule_counts'] == {
        'numeric': 118, 'conditional': 28, 'partial': 12, 'pending': 62, 'non_output': 52}
    active = [(rid, entry) for rid, entry in data['relics'].items() if partition(entry, rid)[0]]
    assert len(active) == 134 and sum(not partition(e, r)[2] for r, e in active) == 125
    changed = sorted(rid for rid in before['relics'] if before['relics'][rid] != data['relics'][rid])
    assert set(before['relics']) == set(data['relics'])
    assert changed == sorted(calculation['changed_relic_ids']) == sorted(evidence['changed_relic_ids']) == sorted([
        'rogue_6_relic_cargo_2', 'rogue_6_relic_book_3', 'rogue_6_start_4'])
    assert before['char_buffs'] == data['char_buffs']
    assert all(before['relics'][rid]['raw_buffs'] == data['relics'][rid]['raw_buffs'] for rid in data['relics'])
    for flag in ('char_buffs_unchanged', 'primary_source_unchanged', 'recognition_unchanged'):
        assert calculation[flag], flag
    assert digest('.cache/game-data/roguelike_topic_table.json') == data['source_sha256'] == evidence['source_sha256'] == audit['source_sha256']
    latest = read('.cache/research/relics-031/latest-commit.json')
    assert latest == evidence['latest_table_commit']
    assert latest['sha'] == latest['pinned_commit'] == data['commit'] == audit['source_commit']
    assert calculation['recognition_sha256'] == digest('rouge/relic_recognition.py') == '8edff23d07bd013063d6c0d2fe4993500f66a80026a5d44c83373b8d4e700eb6'
    assert digest('rouge/offline_scope.py') == read('SCOPE_0.30_VERIFICATION.json')['source_hashes']['rouge/offline_scope.py']
    assert ui['passed'] and ui['skills_checked'] == 87 and ui['tank_first_cost_skill_cases'] == 11
    for flag in ('non_tank_fee_panel_hidden', 'native_options_appropriate',
                 'parts_input_scoped_and_capped', 'combined_fee_unknown', 'event_input_absent',
                 'temporary_context_not_saved', 'private_data_isolated'):
        assert ui[flag], flag
    assert audit['audit_count'] == 272 and audit['public_entry_cases'] == 8704
    assert audit['bound_recipient_cases'] == 609 and audit['forbidden_skill_cases'] == 87
    icons = read('TARGET_ICON_VERIFICATION.json')
    assert icons['count'] == len(icons['icons']) == 15
    for icon in icons['icons']:
        assert digest('rouge/data/' + icon['file']) == icon['sha256'], icon['id']
    for p in (calculation, ui, audit):
        for name, checksum in p['source_hashes'].items():
            assert digest(name) == checksum, name
    for flag in ('only_one_project_window', 'same_run_preserved', 'history_preserved',
                 'settings_and_bindings_unchanged', 'run_cmd_startup_verified'):
        assert launch[flag], flag
    assert launch['launcher_sha256'] == digest('run.cmd')
    checkpoint = read('.cache/upgrade-0.31-checkpoint.json')
    run = read('.local/run-state.json')
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest() == checkpoint['run_id_hash']
    assert checkpoint['history_count'] > 0
    prefix = run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == checkpoint['history_prefix_hash']
    for name, checksum in checkpoint['config_hashes'].items():
        assert digest(name) == checksum, name
    live = []

    def visit(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if title.startswith('黑流树海助手'):
            live.append({'title': title, 'pid': win32process.GetWindowThreadProcessId(hwnd)[1]})

    win32gui.EnumWindows(visit, None)
    assert len(live) == 1 and '0.31' in live[0]['title'] and live[0]['pid'] == launch['process_id'], live
    assert tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version'] == '0.31.0'
    ended = read('.cache/automation-ended-028.json')
    assert ended['automation_id'] == '1-3' and ended['app_delete_result'] == 'deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert read('.cache/kill-recovery-030-superseded/STATUS.json')['status'] == 'superseded_by_user_scope_change'
    assert all(compileall.compile_dir(str(ROOT / folder), quiet=2) for folder in ('rouge', 'scripts', 'tests'))
    names = ('BATCH_0.31.md', 'PROJECT_PROGRESS.md', 'WORK_IN_PROGRESS.md', 'README.md',
        'OUTPUT_FORMAT.md', 'RELIC_MECHANICS.md', 'RELIC_COVERAGE.md', 'pyproject.toml',
        'scripts/verify_final_031.py', 'RELIC_0.31_VERIFICATION.json', 'UI_0.31_VERIFICATION.json',
        'APP_0.31_LAUNCH_VERIFICATION.json', 'RELIC_VERIFICATION.json', 'TARGET_ICON_VERIFICATION.json',
        '.cache/research/relics-031/evidence.json', '.cache/research/relics-031/latest-commit.json',
        '.cache/research/relics-031/verification.log', '.cache/automation-ended-028.json')
    receipt = {'version': '0.31.0', 'passed': True, 'verified_at': time.time(),
        'calculation_scope': 'offline_stable_effects', 'scope': expected_scope,
        'active_relic_rules': len(active), 'current_tests_passed': 178, 'new_tests': 16,
        'historical_combat_tests_skipped': 70, **expected_cases,
        'skill_ui_cases': 87, 'tank_first_cost_skill_cases': 11, 'public_entry_cases': 8704,
        'bound_recipient_cases': 609, 'forbidden_skill_cases': 87, 'bound_icon_hashes': 15,
        'changed_relic_ids': changed, 'char_buffs_unchanged': True,
        'primary_source_unchanged': True, 'latest_table_commit_verified': latest['sha'],
        'recognition_unchanged': True, 'process_id': live[0]['pid'],
        'run_cmd_startup_verified': True, 'same_run_and_history_preserved': True,
        'history_count_before': checkpoint['history_count'], 'history_count_after': len(run['history']),
        'private_configuration_files_verified': len(checkpoint['config_hashes']),
        'automation_id': '1-3', 'automation_status': 'DELETED',
        'all_priorities_1_to_3_completed': False, 'new_game_actions': 0,
        'chat_requests': 0, 'new_live_combat_measurements': 0,
        'checks': ['Pinned source and latest table commit agree; exactly 3 derived items change',
            'Parts cap, tank-only first fee, enemy environment and reference-only non-interference',
            '178 current regressions; 70 historical skips are not counted as passes',
            '87 isolated UI skills, 8704 entries, 609 bindings, 87 forbidden skills and 15 icon hashes',
            'Source hashes, unchanged product scope policy and recognition, compileall',
            'Unique 0.31 run.cmd window, same nonempty run history and private hashes',
            'Automation remains deleted; combat recovery archive remains superseded'],
        'evidence_sha256': {name: digest(name) for name in names},
        'source_sha256': calculation['source_hashes'],
        'limits': ['11 offline pending and 9 partial items; priorities 1-3 remain incomplete.',
            'Card cost rounding/order/lifecycle and hydra ally growth retention remain unknown.',
            'No new recognition benchmark, full-inventory accuracy or live-combat calibration.']}
    (ROOT / 'FINAL_0.31_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('passed', 'current_tests_passed',
        'active_relic_rules', 'process_id', 'history_count_before', 'history_count_after',
        'automation_status', 'all_priorities_1_to_3_completed')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
