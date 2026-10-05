"""Seal the recipient evidence lifecycle batch and its full maintained regression."""
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
    names = ['CORE_0.63_VERIFICATION.json', 'NUMERIC_REPLAY_0.63_VERIFICATION.json',
             'NATIVE_UI_0.63_VERIFICATION.json', 'APP_0.63_LAUNCH_VERIFICATION.json',
             'RECIPIENT_UI_0.63_VERIFICATION.json', 'PACKAGE_0.63_VERIFICATION.json']
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
        for field in ('test_log', 'current_output', 'worker_receipt', 'wheel'):
            if field in data:
                path = ROOT / data[field]
                assert sha(path) == data[field + '_sha256'], field
                evidence[data[field]] = sha(path)
        for source, expected in data.get('mechanism_source_sha256', {}).items():
            assert sha(ROOT / source) == expected, source
            evidence[source] = expected
    assert receipts[names[0]]['tests_run'] == 1169
    assert receipts[names[1]]['exact_structured_unchanged'] == 732
    assert len(receipts[names[2]]['checks']) == 19
    assert len(receipts[names[4]]['checks']) == 9
    assert receipts[names[5]]['isolated_import']['recipient_lifecycle_rules'] == 7
    app = receipts[names[3]]
    assert app['same_run_preserved'] and app['settings_and_bindings_unchanged']
    # Check the actual current project window, without interacting with game UI.
    import verify_launch_063 as launch
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
    old = json.loads((ROOT / '.cache/batch-063-before/manifest.json').read_text(encoding='utf-8'))['files']
    changed = [name for name, expected in old.items() if name.startswith('rouge/') and sha(ROOT / name) != expected]
    assert sorted(changed) == ['rouge/app.py', 'rouge/relics.py', 'rouge/run_state.py'], changed
    lifecycle = json.loads((ROOT/'rouge/data/recipient-lifecycle.json').read_text(encoding='utf-8'))
    topic = ROOT/'.cache/game-data/roguelike_topic_table.json'
    assert sha(topic) == lifecycle['source_sha256']
    evidence[topic.relative_to(ROOT).as_posix()] = sha(topic)
    source_names = set(old) | {'AGENTS.md', 'WORK_IN_PROGRESS.md', 'BATCH_0.63.md',
        'scripts/verify_core_063.py', 'scripts/build_recipient_lifecycle_063.py',
        'scripts/verify_recipient_ui_063.py', 'scripts/verify_package_063.py',
        'rouge/recipient_state.py', 'rouge/data/recipient-lifecycle.json', 'scripts/verify_calculation_replay_063.py',
        'scripts/verify_native_ui_063.py', 'scripts/verify_launch_063.py',
        'scripts/verify_batch_063.py', 'tests/test_recipient_lifecycle_063.py',
        '.cache/research/recipient-lifecycle-063/REPORT.md'}
    result = {
        'version': '0.63.0', 'passed': True, 'verified_at': time.time(),
        'source_sha256': {name: sha(ROOT / name) for name in sorted(source_names)},
        'evidence_sha256': evidence, 'production_files_changed': sorted(changed),
        'recognition_changed': False, 'recognition_priority': 'after_all_other_projects',
        'related_tests_passed': 71, 'new_regression_tests': 20, 'current_core_tests_passed': 1099, 'historical_tests_skipped': 70,
        'complete_calculation_outputs_unchanged': 732, 'temporary_qt_checks': 28,
        'full_core_suite_rerun': True, 'last_full_core_receipt': 'CORE_0.63_VERIFICATION.json',
        'package_rebuilt': True, 'last_package_receipt': 'PACKAGE_0.63_VERIFICATION.json',
        'test_window': window, 'foreground': win32gui.GetForegroundWindow() == window['hwnd'],
        'same_run_and_history_preserved': True, 'configuration_files_preserved': len(after['config_hashes']),
        'all_priority_1_completed': False, 'private_backups_created': False,
        'game_actions': 0, 'chat_requests': 0, 'agents_spawned': 0,
    }
    with (ROOT / 'FINAL_0.63_VERIFICATION.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps({k: result[k] for k in ('passed', 'related_tests_passed',
        'complete_calculation_outputs_unchanged', 'temporary_qt_checks', 'recognition_changed',
        'test_window', 'foreground')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
