"""Read-only pipe discovery and conversation identity verification."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rouge.desktop_backend import DesktopBackend

backend=DesktopBackend(Path(__file__).resolve().parents[1]/'.local/desktop-chat',lambda _:None)
try:
    threads=backend.request('refresh')
    ordinary=[t for t in threads if t['kind']=='chatgpt']
    print(json.dumps({'connected':True,'ordinary_chats':len(ordinary),
                      'test_candidates':[t for t in ordinary if t['title']=='核对伤害计算']},ensure_ascii=True))
finally:
    backend.close()
