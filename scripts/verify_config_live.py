"""Background frame + actual running app persistence, no input or chats."""
import sys,time,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import win32gui
from rouge.capture import GameCapture,list_game_windows
from rouge.recognition import ScreenReader
targets=list_game_windows();assert len(targets)==1 and not targets[0]['minimized']
capture=GameCapture();reader=ScreenReader();foreground=win32gui.GetForegroundWindow()
try:
    capture.connect(targets[0]);frames=[]
    for _ in range(2):
        frame=capture.capture(timeout=8)
        observed=reader.read(frame['image'],client_rect=frame.get('client_rect'))
        config=(observed.get('run') or {}).get('config',{})
        assert config['difficulty']['value']==10,config
        assert frame['client_rect'] is not None
        frames.append({'captured_at':frame['captured_at'],'page':observed['page'],
                       'difficulty':10,'viewport':observed['viewport']})
    assert frames[1]['captured_at']>frames[0]['captured_at']
    state=json.loads((root/'.local/run-state.json').read_text(encoding='utf-8'))
    assert time.time()-state['last_read']<45,'App sampling did not update'
    assert state['config']['difficulty']['value']==10
    squad=state['config'].get('squad')
    receipt={'version':'0.12.0','verified_at':time.time(),'background_frames':frames,
             'running_app_auto_updated':True,'currently_retained_squad':squad,
             'run_id_hash':hashlib.sha256(state['id'].encode()).hexdigest(),
             'history_count':len(state['history']),'foreground_unchanged':foreground==win32gui.GetForegroundWindow(),
             'game_in_background':targets[0]['hwnd']!=foreground,'chat_requests':0,
             'limits':['分队实机信息面板已采集且回放确认；当前新局未读到分队时保持未知。']}
    (root/'CONFIG_0.12_LIVE_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
finally:capture.close()
