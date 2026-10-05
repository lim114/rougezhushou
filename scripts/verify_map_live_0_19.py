"""Actual background map sampling, upgraded app sync and preservation proof."""
import hashlib
import json
import sys
import time
from pathlib import Path
import win32gui
import cv2

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge.capture import GameCapture,list_game_windows
from rouge.recognition import ScreenReader
from rouge.run_state import RunState

targets=list_game_windows();assert len(targets)==1 and not targets[0]['minimized']
foreground=win32gui.GetForegroundWindow();capture=GameCapture()
try:
    capture.connect(targets[0]);reader=ScreenReader();attempts=[]
    for attempt in range(3):
        frame=capture.capture(timeout=8)
        observed=reader.read(frame['image'],client_rect=frame.get('client_rect'))
        graph=observed.get('map');attempts.append((graph or {}).get('status'))
        if graph and graph['status']=='matched':break
        print('Current frame insufficient; retaining same-run historical map; trying a fresh frame',flush=True)
    assert graph and graph['status']=='matched',graph
    state=RunState(ROOT/'.local/run-state.json')
    stored=state.state['maps'].get(graph['zone_id'])
    assert stored and stored['template_id']==graph['template_id']
    assert len(stored['nodes'])==len(graph['nodes']) and stored['edges']==graph['edges']
    before=json.loads((ROOT/'.cache/upgrade-0.19-checkpoint.json').read_text(encoding='utf-8'))
    assert before['run_id_hash']==hashlib.sha256(state.state['id'].encode()).hexdigest()
    assert len(state.state['history'])>=before['history_count']
    sample=ROOT/'samples/native-client'/f"map-live-0.19-{graph['template_id']}.png"
    cv2.imencode('.png',frame['image'])[1].tofile(sample)
    receipt={'version':'0.19.0','verified_at':time.time(),'page':observed['page'],
        'fresh_capture':frame['captured_at'],'viewport':observed['viewport'],
        'zone_id':graph['zone_id'],'template_id':graph['template_id'],
        'nodes':len(graph['nodes']),'edges':len(graph['edges']),'current_node':graph.get('current_node'),
        'last_confirmed_current_node':stored.get('last_confirmed_current_node'),
        'frame_attempt_statuses':attempts,
        'reader_performance':observed.get('performance'),
        'game_sample':str(sample.relative_to(ROOT)),'sample_sha256':hashlib.sha256(sample.read_bytes()).hexdigest(),
        'running_app_matches_map':True,'same_run_preserved':True,'history_preserved':True,
        'foreground_unchanged':foreground==win32gui.GetForegroundWindow(),
        'game_in_background':targets[0]['hwnd']!=foreground,'chat_requests':0,
        'limits':['本次当前区域布局后台实测；未测布局视觉与真实隐藏节点仍需扩充验证，当前位置不强行补值。']}
    (ROOT/'MAP_0.19_LIVE_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
finally:capture.close()
