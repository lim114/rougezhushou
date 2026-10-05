"""Read only the game's window for an authorized operator-page verification."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cv2
import win32gui
from rouge.capture import GameCapture,list_game_windows
from rouge.recognition import ScreenReader
root=Path(__file__).resolve().parents[1]
targets=list_game_windows()
if len(targets)!=1:raise RuntimeError('需要唯一、可渲染的游戏窗口。')
before=win32gui.GetForegroundWindow()
capture=GameCapture()
try:
    capture.connect(targets[0]);sample=capture.capture()
    observed=ScreenReader().read(sample['image'])
    folder=root/'.cache';folder.mkdir(exist_ok=True)
    (folder/'operator-page.png').write_bytes(cv2.imencode('.png',sample['image'])[1].tobytes())
    (folder/'operator-page.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'foreground_unchanged':before==win32gui.GetForegroundWindow(),
        'size':observed['size'],'texts':[{'text':r['text'],'confidence':round(r['confidence'],3),'box':r['box']} for r in observed['texts']]},ensure_ascii=False))
finally:capture.close()
