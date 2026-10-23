from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'305-window-tooldeps'))
import ctypes,json,subprocess,time,psutil
import win32gui,win32process,win32con
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/sections/354-main-window.json'
assert not OUT.exists()
def read(n):return json.loads((ROOT/n).read_bytes())
def digest(p):return sha256(p.read_bytes()).hexdigest()
n=read('verification/sections/354-necessary-attempt1/process.json');w=read('verification/sections/354-native-attempt1/actual/window.json')
assert n['passed']and w['passed']and w['qt_exit_code']==0
for name,h in w['source_sha256_after'].items():assert digest(ROOT/name)==h,name
private=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json']
def fingerprint():return{n:digest(ROOT/n)if(ROOT/n).is_file()else None for n in private}
def windows():
 rows=[]
 def visit(h,_):
  if '黑流树海助手'in win32gui.GetWindowText(h):
   rows.append({'hwnd':h,'pid':win32process.GetWindowThreadProcessId(h)[1],'title':win32gui.GetWindowText(h),'visible':bool(win32gui.IsWindowVisible(h)),'responding':not bool(ctypes.windll.user32.IsHungAppWindow(h)),'minimized':bool(win32gui.IsIconic(h))})
 win32gui.EnumWindows(visit,None);return rows
def owned(row):
 p=psutil.Process(row['pid']);return Path(p.cwd()).resolve()==ROOT.resolve()and any('rouge.app'in arg for arg in p.cmdline())
before=fingerprint();old=windows();assert len(old)<=1 and all(owned(r)for r in old),'Review existing exact app; do not duplicate or close unrelated windows.'
for row in old:
 win32gui.PostMessage(row['hwnd'],win32con.WM_CLOSE,0,0);deadline=time.monotonic()+15
 while win32gui.IsWindow(row['hwnd'])and time.monotonic()<deadline:time.sleep(.1)
 assert not win32gui.IsWindow(row['hwnd']),'App did not close normally; no forced termination.'
assert not windows()
p=subprocess.Popen([str(ROOT/'.venv/Scripts/pythonw.exe'),'-B','-m','rouge.app'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
deadline=time.monotonic()+35
while time.monotonic()<deadline:
 rows=windows()
 if len(rows)==1 and rows[0]['visible']and rows[0]['responding']:break
 time.sleep(.25)
assert len(rows)==1 and rows[0]['visible']and rows[0]['responding']and owned(rows[0])
h=rows[0]['hwnd'];win32gui.ShowWindow(h,win32con.SW_RESTORE)
try:win32gui.SetForegroundWindow(h)
except Exception:pass
after=fingerprint();result={'section':354,'passed':before==after,'window_visible_and_responsive':True,'launcher_pid':p.pid,'visible_windows':rows,'closed_previous_exact_project_windows':old,'private_state_five_paths_unchanged':before==after,'private_entire_normal_close_and_start_interval_unchanged':before==after,'private_path_comparison_count':5,'private_contents_parsed_copied_or_restored':False,'private_hashes_published':False,'source_sha256':w['source_sha256_after'],'full_validation_this_changed_source_rerun':False,'historical_full_receipt':'verification/full-350/summary.json','at_utc':datetime.now(timezone.utc).isoformat()}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items()if k!='source_sha256'},ensure_ascii=False));raise SystemExit(0 if result['passed']else 1)
