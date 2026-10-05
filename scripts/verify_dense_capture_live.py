"""Observe six seconds of actual background WGC; never changes the game."""
import json
import hashlib
import sys
import time
from pathlib import Path
import win32gui
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.capture import GameCapture,list_game_windows
from rouge.recognition import ScreenReader

capture=GameCapture()
receipt={'version':'0.23.0','game_input_actions':0,'chat_requests':0,'sampling_seconds':6,
         'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
             for p in ('rouge/capture.py','rouge/frame_buffer.py','rouge/recognition.py')}}
try:
    targets=list_game_windows()
    if len(targets)!=1 or targets[0]['minimized']:
        receipt.update(status='unavailable',reason='Window absent, ambiguous, or minimized; no game action performed.')
    else:
        foreground=win32gui.GetForegroundWindow()
        capture.connect(targets[0]);start=time.monotonic();stamp=time.time();samples=[]
        while time.monotonic()-start<6:
            samples.append(capture.stats());time.sleep(.1)
        stats=capture.stats();frame=capture.capture();elapsed=time.monotonic()-start
        capture.close()
        observed=ScreenReader().read(frame['image'],client_rect=frame.get('client_rect'))
        receipt.update(status='captured',elapsed_seconds=elapsed,received_frames=stats['received'],
            received_per_second=stats['received']/elapsed,buffer_stats=stats,
            peak_bytes=max(s['bytes'] for s in samples),frame_shape=list(frame['image'].shape),
            page=observed['page'],recognition_ms=observed.get('performance',{}).get('total_ms'),
            captured_after_connection=frame['captured_at']>=stamp,
            game_in_background=foreground!=targets[0]['hwnd'],
            foreground_unchanged=foreground==win32gui.GetForegroundWindow(),
            limits='One live page only; rapid switching validated separately using saved fixtures.')
finally:
    capture.close()
    (ROOT/'DENSE_CAPTURE_LIVE_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(receipt,ensure_ascii=False))
