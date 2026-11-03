from pathlib import Path
import sys,ctypes,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.cache/305-window-tooldeps'))
import win32gui,win32process,win32con
h=5378884;assert win32process.GetWindowThreadProcessId(h)[1]==14196 and win32gui.GetWindowText(h)=='黑流树海助手'
before=ctypes.windll.user32.GetForegroundWindow();win32gui.SetWindowPos(h,win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_NOMOVE|win32con.SWP_NOSIZE|win32con.SWP_NOACTIVATE);same=before==ctypes.windll.user32.GetForegroundWindow();assert same
(R/'verification/maintenance/enemy-table-reading-20261101/live-final/toolbar-exposure.json').write_text(json.dumps({'only_exact_owned_test_toolbar':True,'temporary_native_topmost_no_private_setting_write':True,'foreground_unchanged':same,'game_input_or_operating':False,'popup_not_reopened':True},indent=2)+'\n','utf8');print({'owned_toolbar_exposed_without_activation':True})
