from datetime import datetime, timezone
from hashlib import sha256
import ctypes
import json
from pathlib import Path
import subprocess
import time
import win32con
import win32gui
import win32process

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'verification/sections/288-main-window.json'
if RECEIPT.exists():
    raise FileExistsError(str(RECEIPT))
private = ['.local/operator-state.json', '.local/run-state.json',
           '.local/desktop-chat/conversations.json',
           '.local/desktop-chat/conversations.json.pending', 'local-settings.json']
def fingerprint():
    return {p: sha256((ROOT / p).read_bytes()).hexdigest() if (ROOT / p).is_file() else None for p in private}
before = fingerprint()
report = {'passed': False, 'private_contents_parsed_copied_or_restored': False,
          'started_utc': datetime.now(timezone.utc).isoformat()}
try:
    handle, expected_pid = 724352, 31352
    existing = []
    win32gui.EnumWindows(lambda h, _: existing.append(h)
        if '黑流树海助手' in win32gui.GetWindowText(h) else None, None)
    if existing:
        if existing != [handle] or win32process.GetWindowThreadProcessId(handle)[1] != expected_pid:
            raise RuntimeError('Original app identity changed; no close or overlapping launch performed.')
        win32gui.PostMessage(handle, win32con.WM_CLOSE, 0, 0)
        deadline = time.monotonic() + 12
        while win32gui.IsWindow(handle) and time.monotonic() < deadline:
            time.sleep(0.2)
        if win32gui.IsWindow(handle):
            raise RuntimeError('Original app did not close gracefully; no overlapping app launched.')
    report['existing_original_window_count_before_launch'] = len(existing)
    process = subprocess.Popen([str(ROOT / '.venv/Scripts/pythonw.exe'), '-B', '-m', 'rouge.app'],
                               cwd=ROOT, creationflags=subprocess.CREATE_NO_WINDOW)
    report['launcher_process_id'] = process.pid
    visible = []
    deadline = time.monotonic() + 18
    def collect(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and '黑流树海助手' in win32gui.GetWindowText(hwnd):
            visible.append({'hwnd': hwnd, 'pid': win32process.GetWindowThreadProcessId(hwnd)[1],
                'title': win32gui.GetWindowText(hwnd), 'visible': True,
                'minimized': bool(win32gui.IsIconic(hwnd)),
                'responding': not bool(ctypes.windll.user32.IsHungAppWindow(hwnd))})
    while not visible and time.monotonic() < deadline:
        win32gui.EnumWindows(collect, None)
        if not visible:
            time.sleep(0.4)
    if len(visible) != 1 or not visible[0]['responding']:
        raise RuntimeError('Expected one responsive original project window.')
    after = fingerprint()
    report.update(passed=True, previously_verified_original={'hwnd': handle, 'pid': expected_pid},
                  visible_windows=visible, private_file_hash_comparison_count=len(private),
                  private_hashes_equal=before == after,
                  changed_private_paths=[name for name in private if before[name] != after[name]],
                  launch='original .venv/Scripts/pythonw.exe -B -m rouge.app; original cwd; Windows-mcp PowerShell',
                  current_game_sampling_certified=False, no_private_restoration=True)
except BaseException as exc:
    report['error'] = type(exc).__name__ + ': ' + str(exc)
report['finished_utc'] = datetime.now(timezone.utc).isoformat()
RECEIPT.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
