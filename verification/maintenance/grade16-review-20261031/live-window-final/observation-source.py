from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,sys,time,ctypes
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
import psutil,win32gui,win32process
from player_ui_verification import source_hashes
out=R/'verification/maintenance/grade16-review-20261031/live-window-final';out.mkdir(exist_ok=True)
files=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json','.local/player-shortcut.json']
private={n:sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None for n in files}
assert private==json.loads((R/'.cache/grade16-review-before.json').read_bytes())
pids=[]
for p in psutil.process_iter(['pid','cmdline']):
 if any(str(a).replace('\\','/').endswith('/.cache/player_test_window_grade16_closure.py')for a in(p.info['cmdline']or[])):
  if Path(p.cwd()).resolve()==R:pids.append(p.pid)
assert pids
windows=[]
def visit(h,_):
 if win32process.GetWindowThreadProcessId(h)[1]in pids and win32gui.IsWindowVisible(h):
  windows.append({'hwnd':h,'pid':win32process.GetWindowThreadProcessId(h)[1],'visible':True,'responding':not bool(ctypes.windll.user32.IsHungAppWindow(h))})
win32gui.EnumWindows(visit,None);assert windows and all(r['responding']for r in windows)
s1=json.loads((R/'.cache/grade16-review-live-status.json').read_bytes());time.sleep(2.3);s2=json.loads((R/'.cache/grade16-review-live-status.json').read_bytes())
assert s2['toolbar_visible']and s2['elapsed_since_launch']>s1['elapsed_since_launch']
v={'passed':True,'owned_windows':windows,'actual_process_PIDs_observed_after_launcher_return':pids,'Popen_PID_not_separately_persisted':True,'private_six_paths_unchanged':True,'private_contents_or_hashes_published':False,'source_sha256_after':source_hashes(),'qt_timer_advanced':True,'game_operated':False,'chat_sent':False,'at_UTC':datetime.now(timezone.utc).isoformat(),'recovery':'Launcher performed normal exact-owned close and successful start, then failed saving receipt at reused archive path. Observed surviving exact child without relaunching or restoring state. Virtualenv redirect parent and runtime child share command arguments; visible window ownership is checked by actual PID.'}
(out/'window.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
(out/'launch-source.py').write_bytes((R/'.cache/player_test_window_grade16_closure.py').read_bytes())
(out/'failed-update-source.py').write_bytes((R/'.cache/update_grade16_window_final.py').read_bytes())
(out/'startup-record-failure.json').write_text(json.dumps({'observed_tool_exit':1,'error':'FileExistsError WinError183 at existing live-window artifact directory; application already running','product_startup_failed':False,'private_state_restored':False},indent=2)+'\n','utf8')
(out/'observation-source.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'passed':True,'visible_responding':windows,'private_six_paths_unchanged':True}))
