"""Fresh WGC only, no foreground operations, no game inputs or chats."""
import sys,json,time,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import win32gui
from rouge.capture import GameCapture,list_game_windows
from rouge.recognition import ScreenReader
from rouge.run_state import RunState
targets=list_game_windows();assert len(targets)==1 and not targets[0]['minimized']
capture=GameCapture();reader=ScreenReader();foreground=win32gui.GetForegroundWindow()
try:
    capture.connect(targets[0]);frame=capture.capture(timeout=8)
    observed=reader.read(frame['image'],client_rect=frame.get('client_rect'))
    state=RunState(root/'.local/run-state.json')
    configs=(observed.get('run') or {}).get('config',{})
    for key in ('zone','difficulty'):
        if key in configs:
            expected=configs[key];actual=state.state['config'].get(key,{})
            identity='value' if key=='difficulty' else 'name'
            assert actual.get(identity)==expected[identity],(key,actual,expected)
    before=json.loads((root/'.cache/upgrade-0.14-checkpoint.json').read_text(encoding='utf-8'))
    assert before['run_id_hash']==hashlib.sha256(state.state['id'].encode()).hexdigest()
    assert len(state.state['history'])>=before['history_count']
    receipt={'version':'0.14.0','verified_at':time.time(),'page':observed['page'],
        'fresh_capture':frame['captured_at'],'viewport':observed['viewport'],
        'confirmed_config':configs,'running_app_matches_visible_config':bool(configs),
        'same_run_preserved':True,'history_preserved':True,
        'foreground_unchanged':foreground==win32gui.GetForegroundWindow(),'game_in_background':targets[0]['hwnd']!=foreground,
        'chat_requests':0,'limits':['当前页面后台实测；不代表所有区域与敌人的实机准确率。']}
    (root/'ENVIRONMENT_0.14_LIVE_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
finally:capture.close()
