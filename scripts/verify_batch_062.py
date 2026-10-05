"""Seal this calculation batch without re-running unrelated recognition work."""
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    names = ['AMMO_0.62_VERIFICATION.json', 'NUMERIC_REPLAY_0.62_VERIFICATION.json',
             'NATIVE_UI_0.62_VERIFICATION.json', 'APP_0.62_LAUNCH_VERIFICATION.json']
    evidence = {}
    receipts = {}
    for name in names:
        path = ROOT / name
        data = json.loads(path.read_text(encoding='utf-8'))
        receipts[name] = data
        evidence[name] = sha(path)
        if 'source_sha256' in data:
            assert data['passed'], name
            for source, expected in data['source_sha256'].items():
                assert sha(ROOT / source) == expected, source
        for field in ('test_log', 'current_output', 'worker_receipt'):
            if field in data:
                path = ROOT / data[field]
                assert sha(path) == data[field + '_sha256'], field
                evidence[data[field]] = sha(path)
        for source, expected in data.get('mechanism_source_sha256', {}).items():
            assert sha(ROOT / source) == expected, source
            evidence[source] = expected
    assert receipts[names[0]]['tests_run'] == 45
    assert receipts[names[1]]['exact_structured_unchanged'] == 732
    assert len(receipts[names[2]]['checks']) == 19
    app = receipts[names[3]]
    assert app['same_run_preserved'] and app['settings_and_bindings_unchanged']
    # Check the actual current project window, without interacting with game UI.
    import verify_launch_062 as launch
    import win32gui
    windows = launch.windows()
    assert len(windows) == 1, windows
    window = windows[0]
    assert window['pid'] == app['process_id'] and window['title'] == launch.TITLE, window
    assert window['visible'] and not window['minimized'] and not window['hung'], window
    launch.verify_process(window['pid'])
    before = json.loads(launch.CHECK.read_text(encoding='utf-8'))
    after = launch.state()
    assert before['config_hashes'] == after['config_hashes']
    assert before['run_id_hash'] == after['run_id_hash']
    run = json.loads((ROOT / '.local/run-state.json').read_text(encoding='utf-8'))
    prefix = run['history'][:before['history_count']]
    assert hashlib.sha256(json.dumps(prefix, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == before['history_prefix_hash']
    old = json.loads((ROOT / '.cache/batch-062-before/manifest.json').read_text(encoding='utf-8'))['files']
    changed = [name for name, expected in old.items() if name.startswith('rouge/') and sha(ROOT / name) != expected]
    assert sorted(changed) == ['rouge/ammo_counter.py', 'rouge/app.py'], changed
    source_names = set(old) | {'AGENTS.md', 'WORK_IN_PROGRESS.md', 'BATCH_0.62.md',
        'scripts/verify_ammo_capacity_062.py', 'scripts/verify_calculation_replay_062.py',
        'scripts/verify_native_ui_062.py', 'scripts/verify_launch_062.py',
        'scripts/verify_batch_062.py', 'tests/test_ammo_capacity_062.py',
        '.cache/research/ammo-capacity-062/REPORT.md'}
    result = {
        'version': '0.62.0', 'passed': True, 'verified_at': time.time(),
        'source_sha256': {name: sha(ROOT / name) for name in sorted(source_names)},
        'evidence_sha256': evidence, 'production_files_changed': sorted(changed),
        'recognition_changed': False, 'recognition_priority': 'after_all_other_projects',
        'related_tests_passed': 45, 'new_regression_tests': 8,
        'complete_calculation_outputs_unchanged': 732, 'temporary_qt_checks': 19,
        'full_core_suite_rerun': False, 'last_full_core_receipt': 'CORE_0.61_VERIFICATION.json',
        'package_rebuilt': False, 'last_package_receipt': 'PACKAGE_0.61_VERIFICATION.json',
        'test_window': window, 'foreground': win32gui.GetForegroundWindow() == window['hwnd'],
        'same_run_and_history_preserved': True, 'configuration_files_preserved': len(after['config_hashes']),
        'all_priority_1_completed': False, 'private_backups_created': False,
        'game_actions': 0, 'chat_requests': 0, 'agents_spawned': 0,
    }
    with (ROOT / 'FINAL_0.62_VERIFICATION.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps({k: result[k] for k in ('passed', 'related_tests_passed',
        'complete_calculation_outputs_unchanged', 'temporary_qt_checks', 'recognition_changed',
        'test_window', 'foreground')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
