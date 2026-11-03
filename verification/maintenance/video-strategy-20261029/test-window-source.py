"""Open the unchanged test application only when none of its owned launchers runs."""
from pathlib import Path
from hashlib import sha256
import subprocess,json,time,sys,ctypes
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R),str(R/'.cache/305-window-tooldeps')]
import psutil,win32gui,win32process
files=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json','.local/player-shortcut.json']
def fingerprints():return {n:sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None for n in files}
before=fingerprints();launcher=R/'.cache/player_test_window410.py'
owned=[]
for process in psutil.process_iter(['pid','cmdline']):
    try:
        args=process.info['cmdline']or[]
        if any(str(launcher).lower()==str(arg).lower() or arg=='.cache/player_test_window410.py'for arg in args) and Path(process.cwd()).resolve()==R:owned.append(process.pid)
    except(psutil.Error,OSError):pass
child=None
if not owned:
    out=(R/'.cache/video-strategy-20261029-window.log').open('ab')
    child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(launcher)],cwd=R,stdout=out,stderr=out,creationflags=subprocess.CREATE_NO_WINDOW)
    owned=[child.pid];out.close()
def rows():
    candidates=set(owned)
    for pid in list(candidates):
        try:candidates.update(p.pid for p in psutil.Process(pid).children(recursive=True))
        except psutil.Error:pass
    found=[]
    def visit(hwnd,_):
        pid=win32process.GetWindowThreadProcessId(hwnd)[1]
        if pid in candidates and win32gui.IsWindowVisible(hwnd):
            found.append({'pid':pid,'hwnd':hwnd,'visible':True,'responding':not bool(ctypes.windll.user32.IsHungAppWindow(hwnd))})
    win32gui.EnumWindows(visit,None);return found
found=[]
for _ in range(60):
    found=rows()
    if found:break
    if child is not None and child.poll() is not None:raise RuntimeError('Test window exited; inspect local startup log.')
    time.sleep(.5)
result={'visible_owned_windows':found,'opened_if_absent':child is not None,'existing_windows_closed':False,
    'automatic_sampling_started_by_launcher':False,'chat_sent':False,'game_operated':False,
    'private_six_paths_unchanged':before==fingerprints(),'private_contents_or_hashes_published':False,
    'desktop_visual_review_claimed':False,'unchanged_410_application':True}
assert found and all(r['responding']for r in found)
assert result['private_six_paths_unchanged'], 'Private files changed; do not restore stale state.'
out=R/'verification/maintenance/video-strategy-20261029/test-window.json';assert not out.exists()
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(result,ensure_ascii=False))
