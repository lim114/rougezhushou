"""Seal the ammunition event batch and current own test window."""
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    names = ['CORE_0.67_VERIFICATION.json', 'NUMERIC_REPLAY_0.67_VERIFICATION.json',
        'NATIVE_UI_0.67_VERIFICATION.json', 'PACKAGE_0.67_VERIFICATION.json',
        'APP_0.67_LAUNCH_VERIFICATION.json', '.cache/research/ammo-events-067/native-proof.json']
    receipts = {}; evidence = {}
    for name in names:
        data = json.loads((ROOT / name).read_text(encoding='utf-8'))
        receipts[name] = data; evidence[name] = sha(ROOT / name)
        if 'source_sha256' in data:
            assert data['passed'], name
            for source, digest in data['source_sha256'].items():
                assert sha(ROOT / source) == digest, source
        for field in ('test_log', 'current_output', 'worker_receipt', 'wheel'):
            if field in data:
                assert sha(ROOT / data[field]) == data[field + '_sha256'], field
                evidence[data[field]] = sha(ROOT / data[field])
    assert receipts[names[0]]['tests_run'] == 1223
    assert receipts[names[0]]['current_tests_passed'] == 1153
    assert receipts[names[1]]['exact_structured_unchanged'] == 732
    assert len(receipts[names[2]]['checks']) == 27
    assert receipts[names[3]]['assets_checked'] == 34
    app = receipts[names[4]]
    assert app['same_run_preserved'] and app['settings_and_bindings_unchanged']
    import verify_launch_067 as launch
    import win32gui
    windows = launch.windows(); assert len(windows) == 1, windows
    window = windows[0]
    assert window['pid'] == app['process_id'] and window['title'] == launch.TITLE
    assert window['visible'] and not window['minimized'] and not window['hung']
    launch.verify_process(window['pid']); focused = launch.foreground(window['hwnd'])
    before = json.loads(launch.CHECK.read_text(encoding='utf-8')); after = launch.state()
    assert before['config_hashes'] == after['config_hashes']
    assert before['run_id_hash'] == after['run_id_hash']
    run = json.loads((ROOT / '.local/run-state.json').read_text(encoding='utf-8'))
    prefix = run['history'][:before['history_count']]
    assert hashlib.sha256(json.dumps(prefix, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == before['history_prefix_hash']
    old = json.loads((ROOT / '.cache/batch-067-before/manifest.json').read_text(encoding='utf-8'))['files']
    changed = sorted(name for name, digest in old.items() if name.startswith('rouge/') and sha(ROOT / name) != digest)
    assert changed == ['rouge/ammo_counter.py', 'rouge/app.py', 'rouge/relic_events.py'], changed
    expected = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').rglob('*.py')} - set(old)
    assert not expected, expected
    new = {'tests/test_ammo_events_067.py', 'BATCH_0.67.md',
        'scripts/build_relic_mechanics.py', '.cache/research/ammo-events-067/REPORT.md',
        *[p.relative_to(ROOT).as_posix() for p in (ROOT / 'scripts').glob('verify_*_067.py')]}
    for p in (ROOT / '.cache/research/ammo-events-067').iterdir():
        if p.is_file(): evidence[p.relative_to(ROOT).as_posix()] = sha(p)
    result = {'version': '0.67.0', 'passed': True, 'verified_at': time.time(),
        'source_sha256': {name: sha(ROOT / name) for name in sorted(set(old) | new)},
        'evidence_sha256': evidence, 'existing_production_files_changed': changed,
        'new_production_files': sorted(expected), 'recognition_changed': False, 'mechanism_data_changed': False,
        'recognition_priority': 'after_all_other_projects', 'related_tests_passed': 60,
        'new_regression_tests': 15, 'current_core_tests_passed': 1153, 'historical_tests_skipped': 70,
        'full_core_suite_rerun': True, 'complete_calculation_outputs_unchanged': 732,
        'temporary_qt_checks': 27, 'ui_scope': 'existing_27_temporary_checks_only',
        'new_live_recognition_acceptance': False, 'new_live_panel_acceptance': False,
        'package_rebuilt': True, 'windows_installer_verified': False,
        'test_window': window, 'foreground': focused and win32gui.GetForegroundWindow() == window['hwnd'],
        'same_run_and_history_preserved': True, 'configuration_files_preserved': len(after['config_hashes']),
        'all_priority_1_completed': False, 'current_hotfix_equivalence_proven': False,
        'special_refill_paths_enabled': False, 'full_ability_event_producer_timeline_proven': False, 'bound_consumption_skills': 6, 'private_backups_created': False,
        'game_actions': 0, 'chat_requests': 0, 'agents_spawned': 0}
    with (ROOT / 'FINAL_0.67_VERIFICATION.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps({k:result[k] for k in ('passed','current_core_tests_passed',
        'complete_calculation_outputs_unchanged','temporary_qt_checks','test_window','foreground')}, ensure_ascii=False))


if __name__ == '__main__': main()
