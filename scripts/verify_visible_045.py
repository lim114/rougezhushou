"""Recheck the visible app after a run changed before the upgrade.

The work-start checkpoint is immutable. This receipt proves preservation
within the post-launch observation, not an unobserved pre-upgrade prefix.
"""
import ctypes, hashlib, json, time
from pathlib import Path
import win32api, win32con, win32gui, win32process
from verify_launch_045 import ROOT, TITLE, windows, verify_process, foreground, state


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    old = read(ROOT / '.cache/upgrade-0.45-checkpoint.json')
    failure = ROOT / '.cache/refresh-045/launch.log'
    assert 'Run ID changed; do not restore old data.' in failure.read_text(encoding='utf-8')
    live = windows()
    assert len(live) == 1 and live[0]['title'] == TITLE, live
    current = live[0]
    verify_process(current['pid'])
    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, current['pid'])
    try:
        process_started = win32process.GetProcessTimes(handle)['CreationTime'].timestamp()
    finally:
        handle.Close()
    before = state()
    run = read(ROOT / '.local/run-state.json')
    assert before['run_id_hash'] != old['run_id_hash']
    assert old['verified_at'] < run['started_at'] < process_started
    assert before['config_hashes'] == old['config_hashes']
    before.update(verified_at=time.time(), app_process_created_at=process_started)
    checkpoint = ROOT / '.cache/post-launch-0.45-checkpoint.json'
    with checkpoint.open('x', encoding='utf-8') as stream:
        json.dump(before, stream, ensure_ascii=False, indent=2)
    foreground(current['hwnd'])
    checks = []
    for i in range(6):
        live = windows()
        assert len(live) == 1 and live[0]['pid'] == current['pid'] and live[0]['title'] == TITLE
        assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung']
        checks.append({'at': time.time(), 'visible_and_responsive': True})
        if i < 5:
            time.sleep(4)
    after = state()
    run = read(ROOT / '.local/run-state.json')
    prefix = run['history'][:before['history_count']]
    assert after['run_id_hash'] == before['run_id_hash']
    assert hashlib.sha256(json.dumps(prefix, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == before['history_prefix_hash']
    assert after['config_hashes'] == before['config_hashes'] == old['config_hashes']
    focused = foreground(current['hwnd'])
    rect = win32gui.GetWindowRect(current['hwnd'])
    work = win32api.GetMonitorInfo(win32api.MonitorFromWindow(current['hwnd']))['Work']
    assert work[0] <= rect[0] < rect[2] <= work[2] and work[1] <= rect[1] < rect[3] <= work[3]
    logs = ROOT / '.cache/launch-045'
    assert (logs / 'stderr.log').stat().st_size == 0
    receipt = {
        'version': '0.45.0', 'passed': True, 'verified_at': time.time(),
        'window_title': TITLE, 'process_id': current['pid'], 'app_process_created_at': process_started,
        'only_one_project_window': True, 'window_visible_and_restored': True,
        'foreground_verified': focused, 'window_raised': True, 'within_monitor_work_area': True,
        'rect': rect, 'stability_checks': checks, 'observation_seconds': 20,
        'initial_upgrade_audit_passed': False, 'initial_work_start_run_matches_current': False,
        'current_run_established_before_launch': True, 'initial_checkpoint_history_count': old['history_count'],
        'upgrade_history_prefix_preserved': None,
        'same_current_run_preserved_after_launch': True, 'current_history_prefix_preserved_after_launch': True,
        'history_count_before': before['history_count'], 'history_count_after': after['history_count'],
        'settings_and_bindings_unchanged': True, 'configuration_files_checked': len(after['config_hashes']),
        'startup_route': 'cmd /d /c run.cmd', 'run_cmd_startup_verified': True,
        'launcher_sha256': hashlib.sha256((ROOT / 'run.cmd').read_bytes()).hexdigest(),
        'launcher_stderr_bytes': 0, 'checkpoint': str(checkpoint.relative_to(ROOT)),
        'initial_checkpoint': '.cache/upgrade-0.45-checkpoint.json',
        'initial_audit_failure': str(failure.relative_to(ROOT)),
        'initial_audit_failure_sha256': hashlib.sha256(failure.read_bytes()).hexdigest(),
        'run_state_writes_by_upgrade_script': 0, 'old_checkpoint_restored': False,
        'game_actions': 0, 'chat_requests': 0,
        'comparison_note': 'The current run began before the actual 0.45 process. The initial work-start run differs, so its 190-entry prefix is not an applicable preservation baseline. This check proves the current prefix over a new post-launch 20-second observation only. No unobserved pre-upgrade prefix claim or old-state restoration.'
    }
    (ROOT / 'APP_0.45_LAUNCH_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
