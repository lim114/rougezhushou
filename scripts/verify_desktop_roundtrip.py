"""Send one check to the project's existing test chat; never retry a write."""
import json
import sys
import threading
import time
import uuid
from pathlib import Path
import win32gui
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rouge.desktop_backend import DesktopBackend

ROOT=Path(__file__).resolve().parents[1]
latest={}
lock=threading.Lock()
def state(snapshot):
    with lock:
        latest.clear();latest.update(snapshot)
backend=DesktopBackend(ROOT/'.local/desktop-chat',state)
proof={'transport':'Windows named pipe, native codex_app tools',
       'ui_automation':False,'api_key_used':False,'subscription_sharing_api':False,'send_count':0}
try:
    foreground=win32gui.GetForegroundWindow()
    threads=backend.request('refresh')
    matches=[t for t in threads if t['kind']=='chatgpt' and t['title']=='核对伤害计算']
    if len(matches)!=1:raise RuntimeError('未找到唯一的项目测试聊天；未发送。')
    backend.request('bind',threadId=matches[0]['id'])
    marker='ROUGE_PIPE_'+uuid.uuid4().hex[:12]
    prompt=f'{marker}: This is a background pipe verification. Reply with exactly: {marker} 100700'
    sent=backend.request('send',text=prompt)
    proof['send_count']=1
    proof['delivery_uncertain']=sent['deliveryUncertain']
    deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        with lock:
            chat=dict(latest.get('states',{}).get('chat',{}))
        if not chat.get('running',True) and not chat.get('pending',True):
            proof['matched_reply']=marker in chat.get('output','') and '100700' in chat.get('output','')
            proof['status']=chat.get('progress')
            proof['foreground_unchanged']=win32gui.GetForegroundWindow()==foreground
            break
        time.sleep(.2)
    else:proof['status']='reply_pending_no_resend'
except Exception as error:
    proof['error']=str(error)
finally:
    backend.close()
    (ROOT/'DESKTOP_PIPE_VERIFICATION.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(proof,ensure_ascii=True))
