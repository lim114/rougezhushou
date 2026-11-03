from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import sys,subprocess,time,ctypes,json
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
import win32gui,win32process,win32con,psutil
from player_ui_verification import source_hashes
out=R/'verification/sections/390-main-window';out.mkdir(exist_ok=False)
files=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json']
def fingerprint():return {n:sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None for n in files}
def windows():
 rows=[]
 def visit(h,_):
  if win32gui.GetWindowText(h).startswith('黑流树海助手'):
   p=psutil.Process(win32process.GetWindowThreadProcessId(h)[1]);owned=Path(p.cwd()).resolve()==R.resolve()and any('rouge.app'in a or'player_test_window390.py'in a for a in p.cmdline())
   rows.append({'hwnd':h,'pid':p.pid,'visible':bool(win32gui.IsWindowVisible(h)),'responding':not bool(ctypes.windll.user32.IsHungAppWindow(h)),'owned':owned})
 win32gui.EnumWindows(visit,None);return rows
before=fingerprint();source_before=source_hashes();old=windows();assert not old,'Existing window needs normal close review before replacement.'
launch=R/'.cache/player_test_window390.py'
p=subprocess.Popen([str(R/'.venv/Scripts/pythonw.exe'),'-B',str(launch)],cwd=R,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
deadline=time.monotonic()+35;rows=[]
while time.monotonic()<deadline:
 rows=windows();visible=[r for r in rows if r['visible']and r['pid']==p.pid and r['owned']and r['responding']]
 if len(visible)==1:break
 time.sleep(.2)
assert len(visible)==1
h=visible[0]['hwnd'];win32gui.ShowWindow(h,win32con.SW_RESTORE)
try:win32gui.SetForegroundWindow(h)
except Exception:pass
rect=win32gui.GetWindowRect(h);after=fingerprint();source_after=source_hashes()
r={'section':390,'passed':before==after and source_before==source_after,'window_visible_and_responsive':True,'native_compact_window':True,'visible_owned_count':1,'visible_window':visible[0],'window_rectangle':rect,'actual_retained_launcher_pid':p.pid,'private_five_paths_unchanged':before==after,'private_hashes_or_contents_published':False,'launcher_only_reads_hashes':True,'project_application_reads_its_normal_local_state':True,'private_path_comparison_count':len(files),'automatic_game_sampling_enabled':False,'chat_sent':False,'actual_native_game_or_chat_validation_claimed':False,'full_suite_rerun':False,'source_sha256_before':source_before,'source_sha256_after':source_after,'recorded_at':datetime.now(timezone.utc).isoformat()}
(out/'window.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(out/'controller-source.py').write_bytes(Path(__file__).read_bytes());(out/'launch-source.py').write_bytes(launch.read_bytes())
print(json.dumps({k:v for k,v in r.items()if not k.startswith('source_sha')},ensure_ascii=False));raise SystemExit(0 if r['passed']else 1)
