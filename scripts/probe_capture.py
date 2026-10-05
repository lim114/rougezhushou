import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rouge.capture import list_game_windows, GameCapture
from rouge.recognition import ScreenReader

windows = list_game_windows()
if not windows:
    raise SystemExit('没有检测到原生游戏窗口。')
capture = GameCapture()
try:
    capture.connect(windows[0])
    frame = capture.capture(timeout=8)
    observed = ScreenReader().read(frame['image'])
    print(json.dumps({'capture_size': list(frame['image'].shape), 'page': observed['page'],
                      'stage': (observed['stage'] or {}).get('name'), 'node_count': len(observed['nodes']),
                      'text_count': len(observed['texts'])},ensure_ascii=False))
finally:
    capture.close()
