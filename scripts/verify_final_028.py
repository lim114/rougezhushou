"""Observed 0.28 receipt assembly; private state is read-only and tasks stay ended."""
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


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    calc = read('RELIC_0.28_VERIFICATION.json')
    ui = read('UI_0.28_VERIFICATION.json')
    launch = read('APP_0.28_LAUNCH_VERIFICATION.json')
    audit = read('RELIC_VERIFICATION.json')
    assert calc['passed'] and calc['tests'] == 220 and calc['new_tests'] == 23
    assert calc['skill_matrix_skills'] == 87 and calc['skill_matrix_cases'] == 1740
    assert calc['independent_oracle_cases'] == 60 and calc['wine_oracle_phases'] == 46
    assert ui['passed'] and ui['skill_option_visibility_cases'] == 87 and ui['event_rule_visibility_cases'] == 174
    assert ui['event_preview_not_saved_to_run'] and ui['private_state_isolated']
    assert launch['only_one_project_window'] and launch['same_run_preserved'] and launch['history_preserved']
    assert launch['settings_and_bindings_unchanged'] and launch['run_cmd_startup_verified']
    assert audit['version'] == '0.28.0' and audit['public_entry_cases'] == 8704
    assert audit['bound_recipient_cases'] == 609 and audit['forbidden_skill_cases'] == 87
    assert read('TARGET_ICON_VERIFICATION.json')['count'] == 15
    for proof, field in ((calc, 'source_sha256_files'), (ui, 'source_sha256'), (audit, 'source_hashes')):
        for name, checksum in proof[field].items():
            assert digest(ROOT / name) == checksum, name
    old = read('.cache/batch-028-before/rouge/data/relic-mechanics.json')
    new = read('rouge/data/relic-mechanics.json')
    changed = [rid for rid, record in new['relics'].items() if record != old['relics'][rid]]
    assert set(changed) == {'rogue_6_relic_fight_5', 'rogue_6_relic_hand_5'}
    assert new['char_buffs'] == old['char_buffs']
    assert new['counts'] == {'numeric': 118, 'conditional': 27, 'partial': 12, 'pending': 63, 'non_output': 52}
    assert new['counts'] == audit['data_rule_counts'] == calc['data_rule_counts']
    checkpoint = read('.cache/upgrade-0.28-checkpoint.json')
    run = read('.local/run-state.json')
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest() == checkpoint['run_id_hash']
    prefix = run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == checkpoint['history_prefix_hash']
    for name, checksum in checkpoint['config_hashes'].items():
        assert digest(ROOT / name) == checksum, name
    live = []
    def visit(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if title.startswith('黑流树海助手'):
            live.append({'title': title, 'pid': win32process.GetWindowThreadProcessId(hwnd)[1]})
    win32gui.EnumWindows(visit, None)
    assert len(live) == 1 and '0.28' in live[0]['title']
    assert live[0]['pid'] == launch['process_id']
    version = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    assert version == '0.28.0'
    ended = read('.cache/automation-ended-028.json')
    assert ended['automation_id'] == '1-3' and ended['app_delete_result'] == 'deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    files = ('BATCH_0.28.md', 'PROJECT_PROGRESS.md', 'WORK_IN_PROGRESS.md', 'OUTPUT_FORMAT.md', 'README.md',
        'RELIC_MECHANICS.md', 'RELIC_COVERAGE.md', 'SP_EVENT_MODEL.md', '.cache/relic-028/evidence.json',
        '.cache/automation-ended-028.json', 'scripts/verify_event_sp_028.py', 'scripts/verify_event_sp_ui_028.py',
        'scripts/verify_final_028.py', '.cache/verify-launch-0.28.py')
    receipt = {'version': version, 'passed': True, 'verified_at': time.time(),
        'checks': ['220 relevant regressions, including 23 new public-boundary tests',
            '1740 skill/scenario cases across both timing modes and both relics',
            '60 independent frame cumulative cases and 46 wine-phase comparisons',
            '87 skills isolated UI options and 174 event-field visibility checks',
            '8704 relic public entries; 609 bindings; 87 forbidden skills',
            '15 bound icon hashes; compileall', 'Actual run.cmd launch and one 0.28 window',
            'Same run, nonempty history prefix and existing private config hashes preserved',
            'Recurring task deletion confirmed by app and absent manifest'],
        'changed_relic_ids': changed, 'changed_char_buff_ids': [], 'data_rule_counts': new['counts'],
        'history_count_before': checkpoint['history_count'], 'history_count_after': len(run['history']),
        'configuration_files_verified': list(checkpoint['config_hashes']), 'process_id': live[0]['pid'],
        'automation_id': '1-3', 'automation_status': 'DELETED', 'automatic_development_will_resume': False,
        'all_priorities_1_to_3_completed': False, 'new_game_actions': 0, 'chat_requests': 0,
        'new_live_combat_measurements': 0, 'evidence_sha256': {name: digest(ROOT / name) for name in files},
        'limits': ['Explicit offline callbacks, not automatically inferred from attack or damage totals.',
            'Wave and Book attack-stack refresh/ownership/per-hit snapshot remains unknown.',
            'Hidden blocking, simultaneous order and next-tick availability remain reference assumptions.',
            'Recognition unchanged; no new speed or whole-inventory reading claim.',
            'P1-3 still have documented remaining work.']}
    (ROOT / 'FINAL_0.28_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'version': version, 'passed': True, 'history_count': len(run['history']),
        'process_id': live[0]['pid'], 'automation_status': 'DELETED'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
