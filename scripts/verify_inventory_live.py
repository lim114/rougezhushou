"""Read two fresh background game frames; verify the running app's saved state."""
import json,time,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import win32gui
from rouge.capture import GameCapture,list_game_windows
from rouge.recognition import ScreenReader
targets=list_game_windows();assert len(targets)==1 and not targets[0]['minimized'],targets
capture=GameCapture();reader=ScreenReader();foreground=win32gui.GetForegroundWindow()
try:
    capture.connect(targets[0]);frames=[]
    for index in range(2):
        frame=capture.capture(timeout=8)
        observed=reader.read(frame['image']);run=observed['run']
        assert set(run['relics']['ids'])=={'rogue_6_relic_cargo_1','rogue_6_relic_fight_26'},run
        assert run['tactical_tools']['ids']==['rogue_6_active_tool_5'],run
        assert run['relics']['count']==3,run
        frames.append({'captured_at':frame['captured_at'],'page':observed['page'],
            'relics':run['relics']['ids'],'tools':run['tactical_tools']['ids'],
            'count':run['relics']['count'],'shape':list(frame['image'].shape)})
    assert frames[1]['captured_at']>frames[0]['captured_at']
    state=json.loads((ROOT/'.local/run-state.json').read_text(encoding='utf-8'))
    assert state['inventory_verified'] and state['relic_count']==3
    assert {k for k,v in state['relics'].items() if v.get('held',True)}==set(frames[0]['relics'])
    assert [k for k,v in state['tactical_tools'].items() if v.get('held',True)]==frames[0]['tools']
    assert time.time()-state['last_read']<45,'Running app did not update recently'
    receipt={'verified_at':time.time(),'version':'0.11.0','fresh_background_frames':frames,
        'running_app_inventory_complete':True,'relics':2,'tactical_tools':1,'total_badge_count':3,
        'run_id_hash':hashlib.sha256(state['id'].encode()).hexdigest(),
        'history_count':len(state['history']),'foreground_unchanged':foreground==win32gui.GetForegroundWindow(),
        'game_in_background':targets[0]['hwnd']!=foreground,'chat_requests':0,
        'limits':['当前三件物品样本实测，不代表全部藏品/变体识别率。','酒类未进行实战相位校准。']}
    (ROOT/'INVENTORY_0.11_LIVE_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
finally:capture.close()
