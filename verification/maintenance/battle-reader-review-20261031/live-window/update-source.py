"""Replace only the exact unchanged test launcher; preserve private state by hash."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,sys,subprocess,time,ctypes
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
import psutil,win32gui,win32process,win32con
from player_ui_verification import source_hashes as python_source_hashes
def source_hashes():
    return {**python_source_hashes(),**{p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in (R/'rouge/bridge').glob('*.cjs')}}
files=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json','.local/player-shortcut.json']
def private():return {n:sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None for n in files}
before=private();source=source_hashes()
(R/'.cache/runtime-battle-before.json').write_text(json.dumps(before),'utf8')
def owned(leaf):
    found=set()
    for p in psutil.process_iter(['pid','cmdline']):
        try:
            if any(str(arg).replace('\\','/').endswith('/.cache/'+leaf)or arg=='.cache/'+leaf for arg in(p.info['cmdline']or[]))and Path(p.cwd()).resolve()==R:found.add(p.pid)
        except(psutil.Error,OSError):pass
    return found
def windows(pids,visible_only=False):
    rows=[]
    def visit(h,_):
        pid=win32process.GetWindowThreadProcessId(h)[1]
        if pid in pids and(not visible_only or win32gui.IsWindowVisible(h)):
            rows.append({'hwnd':h,'pid':pid,'title':win32gui.GetWindowText(h),'visible':bool(win32gui.IsWindowVisible(h)),
                'responding':not bool(ctypes.windll.user32.IsHungAppWindow(h))})
    win32gui.EnumWindows(visit,None);return rows
old=owned('player_test_window_resources.py');closed=[]
for row in windows(old):
    if row['title']=='黑流树海助手 · 局外计算与节点测试':
        win32gui.PostMessage(row['hwnd'],win32con.WM_CLOSE,0,0);closed.append(row['pid'])
if old:
    for _ in range(20):
        if not(owned('player_test_window_resources.py')):break
        time.sleep(.25)
    assert not(owned('player_test_window_resources.py')),'Old exact test launcher still runs; no duplicate launch or forced termination.'
launcher=R/'.cache/player_test_window_battle.py'
assert not owned(launcher.name),'Current test window already runs; do not overlap.'
assert launcher.is_file(),'Reviewed live-test launcher required.'
with(R/'.cache/runtime-battle-startup.log').open('ab')as log:
    child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(launcher)],cwd=R,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
rows=[]
for _ in range(120):
    rows=windows(owned(launcher.name),True)
    if rows and all(row['responding']for row in rows):break
    assert child.poll()is None,'New test application exited; inspect local log.'
    time.sleep(.5)
assert rows and all(row['responding']for row in rows)
same=before==private();assert same,'Private state changed; never restore stale state.'
assert source==source_hashes()
out=R/'verification/maintenance/battle-reader-review-20261031/live-window';out.mkdir(exist_ok=False)
result={'kind':'review_maintenance_no_new_section','section':440,'passed':True,'owned_windows':[{k:v for k,v in row.items()if k!='title'}for row in rows],
    'actual_retained_launcher_pid':child.pid,'previous_exact_test_launchers_found':sorted(old),'normal_close_requested_only_for_exact_owned_test_pids':closed,
    'forced_termination':False,'private_six_paths_unchanged':same,'private_contents_or_hashes_published':False,
    'source_sha256_before':source,'source_sha256_after':source_hashes(),'explicit_automatic_sampling_start_called_by_launcher':False,'game_hover_read_only_authorized_in_this_task':True,
    'game_operated':False,'chat_sent':False,'desktop_visual_review_pending':True,'at_UTC':datetime.now(timezone.utc).isoformat()}
(out/'window.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
(out/'update-source.py').write_bytes(Path(__file__).read_bytes());(out/'launch-source.py').write_bytes(launcher.read_bytes())
print(json.dumps({'current_actual_test_window':result['owned_windows'],'private_six_unchanged':same,'no_game_chat_actions':True},ensure_ascii=False))
