"""Upgrade the user's own visible test window, preserving a fresh checkpoint."""
import ctypes,hashlib,json,subprocess,sys,time
from pathlib import Path
import win32api,win32con,win32event,win32gui,win32process

ROOT=Path(__file__).resolve().parents[1]
CHECK=ROOT/'.cache/upgrade-0.40-checkpoint.json'
TITLE='黑流树海助手 0.40 · 识别与计算测试版'


def windows():
    found=[]
    def visit(hwnd,_):
        title=win32gui.GetWindowText(hwnd)
        if title.startswith('黑流树海助手'):
            found.append({'hwnd':hwnd,'pid':win32process.GetWindowThreadProcessId(hwnd)[1],
                'title':title,'visible':bool(win32gui.IsWindowVisible(hwnd)),
                'minimized':bool(win32gui.IsIconic(hwnd)),
                'hung':bool(ctypes.windll.user32.IsHungAppWindow(hwnd))})
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


def verify_process(pid):
    handle=win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION|win32con.PROCESS_VM_READ,False,pid)
    try:exe=Path(win32process.GetModuleFileNameEx(handle,0)).resolve()
    finally:handle.Close()
    expected={(ROOT/'.venv/Scripts/pythonw.exe').resolve(),(Path(sys.base_prefix)/'pythonw.exe').resolve()}
    assert exe in expected,(pid,str(exe))
    return str(exe)


def foreground(hwnd):
    win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)
    current=win32api.GetCurrentThreadId()
    for attempt in range(4):
        if win32gui.GetForegroundWindow()==hwnd:return True
        active=win32gui.GetForegroundWindow()
        threads={win32process.GetWindowThreadProcessId(hwnd)[0]}
        if active:threads.add(win32process.GetWindowThreadProcessId(active)[0])
        attached=[]
        try:
            for thread in threads-{current}:
                if ctypes.windll.user32.AttachThreadInput(current,thread,True):attached.append(thread)
            win32gui.BringWindowToTop(hwnd)
            ctypes.windll.user32.SetActiveWindow(hwnd)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            # Foreground activation is asynchronous across GUI thread queues.
            deadline=time.monotonic()+.3
            while win32gui.GetForegroundWindow()!=hwnd and time.monotonic()<deadline:time.sleep(.03)
        finally:
            for thread in attached:ctypes.windll.user32.AttachThreadInput(current,thread,False)
        if win32gui.GetForegroundWindow()==hwnd:return True
    # Elevated foreground applications can reject AttachThreadInput (error 5).
    # Raise only our own window without sending keys or changing global focus
    # settings. Keep the distinction between visibility and keyboard focus.
    flags=win32con.SWP_NOMOVE|win32con.SWP_NOSIZE|win32con.SWP_SHOWWINDOW
    win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,0,0,0,0,flags)
    win32gui.SetWindowPos(hwnd,win32con.HWND_NOTOPMOST,0,0,0,0,flags)
    return win32gui.GetForegroundWindow()==hwnd


def main():
    mode=sys.argv[1]
    if mode=='before':
        assert not CHECK.exists(),'Do not overwrite this upgrade checkpoint.'
        data=state();data['windows']=windows();data['verified_at']=time.time()
        assert len(data['windows'])<=1,data['windows']
        for w in data['windows']:
            assert w['title']=='黑流树海助手 0.39 · 识别与计算测试版',w
            w['executable']=verify_process(w['pid'])
            h=win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION,False,w['pid'])
            try:w['process_created_at']=win32process.GetProcessTimes(h)['CreationTime'].timestamp()
            finally:h.Close()
        CHECK.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'windows':data['windows'],'history_count':data['history_count'],
                          'private_configuration_count':len(data['config_hashes'])},ensure_ascii=False))
        return
    before=json.loads(CHECK.read_text(encoding='utf-8'))
    if mode in ('launch','verify'):
        logs=ROOT/'.cache/launch-040';logs.mkdir(parents=True,exist_ok=True)
        if mode=='launch':
            old_handles=[]
            for w in before['windows']:
                assert win32gui.IsWindow(w['hwnd']) and win32gui.GetWindowText(w['hwnd'])==w['title']
                assert win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']
                assert verify_process(w['pid'])==w['executable']
                h=win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION|win32con.PROCESS_VM_READ|
                    win32con.PROCESS_TERMINATE|win32con.SYNCHRONIZE,False,w['pid'])
                assert win32process.GetProcessTimes(h)['CreationTime'].timestamp()==w['process_created_at']
                old_handles.append((h,w))
                win32gui.PostMessage(w['hwnd'],win32con.WM_CLOSE,0,0)
            deadline=time.monotonic()+10
            while windows() and time.monotonic()<deadline:time.sleep(.2)
            assert not windows(),'Old project window did not close; do not launch a duplicate.'
            for h,w in old_handles:
                try:
                    if win32event.WaitForSingleObject(h,5000)!=win32event.WAIT_OBJECT_0:
                        # This handle is pinned to the exact process whose
                        # window, executable and creation time were checked.
                        assert Path(win32process.GetModuleFileNameEx(h,0)).resolve()==Path(w['executable']).resolve()
                        win32api.TerminateProcess(h,0)
                    assert win32event.WaitForSingleObject(h,5000)==win32event.WAIT_OBJECT_0
                finally:h.Close()
            # The detached child is the requested visible app; the launcher
            # shell remains hidden. No game inputs or filesystem shell strings.
            with (logs/'stdout.log').open('xb') as out,(logs/'stderr.log').open('xb') as err:
                subprocess.run(['cmd.exe','/d','/c','run.cmd'],cwd=ROOT,check=True,
                    stdout=out,stderr=err,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            live=windows()
            if len(live)==1 and live[0]['title']==TITLE:break
            time.sleep(.3)
        live=windows();assert len(live)==1 and live[0]['title']==TITLE,live
        verify_process(live[0]['pid']);foreground(live[0]['hwnd'])
        checks=[]
        for i in range(6):
            live=windows()
            assert len(live)==1 and live[0]['title']==TITLE,live
            assert live[0]['visible'] and not live[0]['minimized'] and not live[0]['hung'],live
            checks.append({'at':time.time(),'visible_and_responsive':True})
            if i<5:time.sleep(4)
        focused=foreground(live[0]['hwnd'])
        rect=win32gui.GetWindowRect(live[0]['hwnd'])
        work=win32api.GetMonitorInfo(win32api.MonitorFromWindow(live[0]['hwnd']))['Work']
        assert work[0]<=rect[0]<rect[2]<=work[2] and work[1]<=rect[1]<rect[3]<=work[3],(rect,work)
        after=state();run=json.loads((ROOT/'.local/run-state.json').read_text(encoding='utf-8'))
        prefix=run['history'][:before['history_count']]
        assert before['run_id_hash']==after['run_id_hash'],'Run ID changed; do not restore old data.'
        assert hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==before['history_prefix_hash'],'History changed'
        assert before['config_hashes']==after['config_hashes'],'Configuration changed'
        receipt={'version':'0.40.0','verified_at':time.time(),'window_title':TITLE,'process_id':live[0]['pid'],
            'only_one_project_window':True,'window_visible_and_restored':True,'foreground_verified':focused,
            'previous_app_process_stopped_before_launch':True,
            'window_raised':True,
            'within_monitor_work_area':True,'rect':rect,'stability_checks':checks,'observation_seconds':20,
            'same_run_preserved':True,'history_preserved':True,
            'history_count_before':before['history_count'],'history_count_after':after['history_count'],
            'settings_and_bindings_unchanged':True,'configuration_files_checked':len(after['config_hashes']),
            'chat_requests':0,'game_actions':0,'run_state_writes_by_upgrade_script':0,
            'startup_route':'cmd /d /c run.cmd','run_cmd_startup_verified':True,
            'launcher_sha256':hashlib.sha256((ROOT/'run.cmd').read_bytes()).hexdigest(),
            'launcher_stderr_bytes':(logs/'stderr.log').stat().st_size,
            'checkpoint':str(CHECK.relative_to(ROOT)),
            'comparison_note':'Fresh current-run checkpoint; an empty history is valid. Historical 0.39 upgrade history is not restored.'}
        (ROOT/'APP_0.40_LAUNCH_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(receipt,ensure_ascii=False))
        return
    raise ValueError('Expected before, launch or verify.')


if __name__=='__main__':main()
