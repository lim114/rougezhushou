"""Read one fresh background frame, without touching stored run state."""
import json
import sys
import time
from pathlib import Path
import win32gui
import cv2

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge.capture import GameCapture,list_game_windows
from rouge.recognition import ScreenReader

targets=list_game_windows();assert len(targets)==1 and not targets[0]['minimized']
foreground=win32gui.GetForegroundWindow();capture=GameCapture()
try:
    capture.connect(targets[0]);frame=capture.capture(timeout=8)
    observed=ScreenReader().read(frame['image'],client_rect=frame.get('client_rect'))
    cv2.imencode('.png',frame['image'])[1].tofile(ROOT/'.cache/research/maps/live-frame.png')
    (ROOT/'.cache/research/maps/live-observation.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2),encoding='utf-8')
    graph=observed.get('map')
    receipt={'version':'0.17.0','verified_at':time.time(),'captured_at':frame['captured_at'],
        'page':observed['page'],'map':graph,'viewport':observed['viewport'],
        'foreground_unchanged':foreground==win32gui.GetForegroundWindow(),
        'game_in_background':targets[0]['hwnd']!=foreground,'chat_requests':0}
    (ROOT/'.cache/map-0.17-live-inspection.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'page':observed['page'],'map_status':(graph or {}).get('status'),
        'template':(graph or {}).get('template_id'),'reason':(graph or {}).get('reason'),
        'foreground_unchanged':receipt['foreground_unchanged'],'size':observed['size']},ensure_ascii=False))
finally:capture.close()
