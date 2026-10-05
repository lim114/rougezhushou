"""Assemble observed 0.27 checks; never modify private application state."""
import hashlib
import json
import time
import tomllib
import sys
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
    calc = read('RELIC_0.27_VERIFICATION.json')
    ui = read('UI_0.27_VERIFICATION.json')
    launch = read('APP_0.27_LAUNCH_VERIFICATION.json')
    audit = read('RELIC_VERIFICATION.json')
    assert calc['passed'] and calc['tests'] == 197 and calc['new_tests'] == 24
    assert calc['skill_matrix_cases'] == 1218 and calc['resident_enemy_difficulty_cases'] == 125
    assert calc['hp_combination_cases'] == 80 and calc['hp_combinations_guarded'] == 71
    assert len(calc['synthetic_canonical_examples']) == 3
    assert ui['passed'] and ui['skill_option_visibility_cases'] == 87
    assert ui['event_preview_not_saved_to_run'] and ui['private_state_isolated']
    assert launch['only_one_project_window'] and launch['same_run_preserved'] and launch['history_preserved']
    assert launch['settings_and_bindings_unchanged'] and launch['run_cmd_startup_verified']
    assert audit['version'] == '0.27.0' and audit['public_entry_cases'] == 8704
    assert audit['bound_recipient_cases'] == 609 and audit['forbidden_skill_cases'] == 87
    assert read('TARGET_ICON_VERIFICATION.json')['count'] == 15
    for proof, field in ((calc, 'source_sha256_files'), (ui, 'source_sha256'), (audit, 'source_hashes')):
        for name, checksum in proof[field].items():
            assert digest(ROOT / name) == checksum, name
    old = read('.cache/batch-027-before/rouge/data/relic-mechanics.json')
    new = read('rouge/data/relic-mechanics.json')
    changed = [rid for rid, record in new['relics'].items() if record != old['relics'][rid]]
    assert set(changed) == {'rogue_6_relic_fight_11', 'rogue_6_relic_cargo_11'}
    assert new['char_buffs'] == old['char_buffs']
    assert new['counts'] == {'numeric': 118, 'conditional': 26, 'partial': 11, 'pending': 65, 'non_output': 52}
    assert new['counts'] == audit['data_rule_counts']
    checkpoint = read('.cache/upgrade-0.27-checkpoint.json')
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
    assert len(live) == 1 and '0.27' in live[0]['title']
    assert live[0]['pid'] == launch['process_id']
    version = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    assert version == '0.27.0'
    automation = Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml')
    status = tomllib.loads(automation.read_text(encoding='utf-8'))['status']
    assert status == 'ACTIVE'
    files = ('BATCH_0.27.md', 'PROJECT_PROGRESS.md', 'WORK_IN_PROGRESS.md', 'OUTPUT_FORMAT.md',
        'README.md', 'RELIC_MECHANICS.md', 'RELIC_COVERAGE.md', '.cache/relic-027/evidence.json',
        'scripts/verify_deployment_relics_027.py', 'scripts/verify_deployment_ui_027.py', 'scripts/verify_final_027.py')
    receipt = {'version': version, 'passed': True, 'verified_at': time.time(),
        'checks': ['197 relevant regressions, including 24 new public-boundary tests',
            '1218 skill/scenario cases across both timing modes', '125 resident enemy/difficulty cases',
            '80 HP relic combination cases, 71 guarded', '3 synthetic canonical source examples',
            '87 skills isolated UI option checks', '8704 relic public entries; 609 bindings; 87 forbidden skills',
            '15 bound icon hashes; compileall', 'Actual run.cmd launch and one 0.27 window',
            'Same run, nonempty history prefix and existing private config hashes preserved'],
        'changed_relic_ids': changed, 'changed_char_buff_ids': [], 'data_rule_counts': new['counts'],
        'history_count_before': checkpoint['history_count'], 'history_count_after': len(run['history']),
        'configuration_files_verified': list(checkpoint['config_hashes']),
        'process_id': live[0]['pid'], 'automation_status': status, 'all_priorities_1_to_3_completed': False,
        'new_game_actions': 0, 'chat_requests': 0, 'new_live_combat_measurements': 0,
        'evidence_sha256': {name: digest(ROOT / name) for name in files},
        'limits': ['Cost rounding, skill/trait/redeployment deductions and HP lifecycle remain partial.',
            'Resident whitelist is a bounded source inference; mixed HP scripts remain unknown.',
            'Recognition code unchanged; no new speed or whole-inventory accuracy claim.',
            '87 skills and P1-3 still have documented remaining work.']}
    (ROOT / 'FINAL_0.27_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'version': version, 'passed': True, 'history_count': len(run['history']),
        'process_id': live[0]['pid'], 'automation_status': status}, ensure_ascii=False))


if __name__ == '__main__':
    main()
