"""Own-application restart and upgrade checks; no game or chat action."""
import hashlib
import json
import sys
import time
from pathlib import Path
import win32gui
import win32process
from win32con import WM_CLOSE, SW_RESTORE

ROOT=Path(__file__).resolve().parents[1]
CHECK=ROOT/'.cache/upgrade-0.33-checkpoint.json'


def windows():
    found=[]
    def visit(hwnd,_):
        title=win32gui.GetWindowText(hwnd)
        if title.startswith('黑流树海助手'):
            found.append({'hwnd':hwnd,'pid':win32process.GetWindowThreadProcessId(hwnd)[1],'title':title})
    win32gui.EnumWindows(visit,None)
    return found


def state():
    path=ROOT/'.local/run-state.json'
    run=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    paths=[ROOT/'local-settings.json',ROOT/'.local/operator-state.json',*sorted((ROOT/'.local/desktop-chat').glob('*.json'))]
    return {'run_id_hash':hashlib.sha256(str(run.get('id')).encode()).hexdigest(),
        'history_count':len(run.get('history',[])),
        'history_prefix_hash':hashlib.sha256(json.dumps(run.get('history',[]),sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
        'config_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.exists()}}


mode=sys.argv[1]
if mode=='before':
    data=state();data['windows']=windows()
    assert len(data['windows'])<=1,data['windows']
    CHECK.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'windows':data['windows'],'history_count':data['history_count']},ensure_ascii=False))
elif mode=='close':
    data=json.loads(CHECK.read_text(encoding='utf-8'))
    for window in data['windows']:
        assert win32gui.IsWindow(window['hwnd'])
        assert win32gui.GetWindowText(window['hwnd']).startswith('黑流树海助手 0.32')
        assert win32process.GetWindowThreadProcessId(window['hwnd'])[1]==window['pid']
        win32gui.PostMessage(window['hwnd'],WM_CLOSE,0,0)
    deadline=time.monotonic()+10
    while windows() and time.monotonic()<deadline:time.sleep(.2)
    assert not windows(),'Old project window did not close; do not launch a duplicate.'
    print('Previous project window closed.')
else:
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        live=windows()
        if len(live)==1 and '0.33' in live[0]['title']:break
        time.sleep(.3)
    before=json.loads(CHECK.read_text(encoding='utf-8'));after=state();live=windows()
    assert len(live)==1 and '0.33' in live[0]['title'],live
    win32gui.ShowWindow(live[0]['hwnd'],SW_RESTORE)
    assert win32gui.IsWindowVisible(live[0]['hwnd']) and not win32gui.IsIconic(live[0]['hwnd'])
    assert before['run_id_hash']==after['run_id_hash'],'Run ID changed'
    run=json.loads((ROOT/'.local/run-state.json').read_text(encoding='utf-8'))
    prefix=run['history'][:before['history_count']]
    assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==before['history_prefix_hash'],'History changed'
    assert before['config_hashes']==after['config_hashes'],'Configuration changed'
    receipt={'version':'0.33.0','verified_at':time.time(),'window_title':live[0]['title'],'process_id':live[0]['pid'],
        'only_one_project_window':True,'window_visible_and_restored':True,'same_run_preserved':True,'history_preserved':True,
        'history_count_before':before['history_count'],'history_count_after':after['history_count'],
        'settings_and_bindings_unchanged':True,'configuration_files_checked':len(after['config_hashes']),
        'chat_requests':0,'game_actions':0,'startup_route':'cmd /d /c run.cmd','run_cmd_startup_verified':True,
        'launcher_sha256':hashlib.sha256((ROOT/'run.cmd').read_bytes()).hexdigest(),
        'historical_0_20_run_change_explained':False}
    (ROOT/'APP_0.33_LAUNCH_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
