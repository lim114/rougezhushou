"""Fresh background native frames and running app state, no game/chat input."""
import sys,json,time,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import win32gui
from rouge.capture import GameCapture,list_game_windows
from rouge.recognition import ScreenReader
from rouge.run_state import RunState
targets=list_game_windows();assert len(targets)==1 and not targets[0]['minimized'],targets
capture=GameCapture();reader=ScreenReader();foreground=win32gui.GetForegroundWindow()
try:
    capture.connect(targets[0]);frames=[]
    for _ in range(2):
        frame=capture.capture(timeout=8);observed=reader.read(frame['image'],client_rect=frame.get('client_rect'))
        run=observed['run'];assert run['relics']['count']==0 and not run['relics']['ids'] and not run['relics']['icons'],run['relics']
        assert run['config']['difficulty']['value']==10
        frames.append({'captured_at':frame['captured_at'],'page':observed['page'],'count':0,'viewport':observed['viewport']})
    assert frames[1]['captured_at']>frames[0]['captured_at']
    state=RunState(root/'.local/run-state.json');status=state.inventory_status()
    assert status['complete'] and status['expected_count']==0 and status['recognized']==status['recognized_tools']==0
    assert time.time()-state.state['last_read']<45
    before=json.loads((root/'.cache/upgrade-0.13-checkpoint.json').read_text(encoding='utf-8'))
    assert before['run_id_hash']==hashlib.sha256(state.state['id'].encode()).hexdigest()
    assert len(state.state['history'])>=before['history_count']
    receipt={'version':'0.13.0','verified_at':time.time(),'fresh_background_frames':frames,
        'running_app_empty_inventory_complete':True,'same_run_preserved':True,'history_preserved':True,
        'foreground_unchanged':foreground==win32gui.GetForegroundWindow(),'game_in_background':targets[0]['hwnd']!=foreground,
        'chat_requests':0,'limits':['当前空持有栏实测；不是所有UI比例、字形或强化藏品识别率的证明。']}
    (root/'INVENTORY_0.13_LIVE_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
finally:capture.close()
