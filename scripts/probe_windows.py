"""Read-only desktop compatibility report. Does not print chat contents."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rouge.capture import list_game_windows
import win32gui
import win32process
import win32api
import win32con

result = {'game_windows': list_game_windows(), 'chat_windows': []}
def visit(hwnd, _):
    title = win32gui.GetWindowText(hwnd)
    if win32gui.IsWindowVisible(hwnd) and title == 'ChatGPT':
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
        try:
            exe = win32process.GetModuleFileNameEx(handle, 0)
        finally:
            handle.Close()
        result['chat_windows'].append({'hwnd': hwnd, 'pid': pid, 'executable': exe})
win32gui.EnumWindows(visit, None)
print(json.dumps(result, ensure_ascii=False, indent=2))
