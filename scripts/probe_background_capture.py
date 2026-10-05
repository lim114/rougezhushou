"""Live verification with game behind another window; no game input is sent."""
import hashlib
import json
import sys
import time
from pathlib import Path
import win32gui
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rouge.capture import list_game_windows, GameCapture

targets=list_game_windows()
if not targets:
    raise SystemExit('没有游戏窗口。')
target=targets[0]
capture=GameCapture()
try:
    foreground=win32gui.GetForegroundWindow()
    if foreground==target['hwnd']:
        raise SystemExit('验证需在助手或其他窗口处于前台时运行。')
    capture.connect(target)
    first=capture.capture(timeout=8)
    time.sleep(2)
    second=capture.capture(timeout=8)
    result={'game_in_foreground':False,'foreground_unchanged':foreground==win32gui.GetForegroundWindow(),
            'game_minimized':bool(win32gui.IsIconic(target['hwnd'])),
            'size':list(second['image'].shape),'fresh_callback':second['captured_at']>first['captured_at'],
            'pixels_changed':hashlib.sha256(first['image'].tobytes()).hexdigest()!=hashlib.sha256(second['image'].tobytes()).hexdigest()}
    print(json.dumps(result,ensure_ascii=False))
    (Path(__file__).resolve().parents[1]/'BACKGROUND_CAPTURE_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
finally:
    capture.close()
