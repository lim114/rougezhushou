"""Root explicitly run only after complete343 change-specific acceptance; full320 retained, not rerun; normal app restart."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'305-window-tooldeps'))
import ctypes,json,subprocess,time,psutil
import win32gui,win32process,win32con
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/sections/343-main-window.json'
assert not OUT.exists()
def load(n):return json.loads((ROOT/n).read_bytes())
def digest(p):return sha256(p.read_bytes()).hexdigest()
full=load('verification/full-335/summary.json');assert full['after_section']==335 and full['available_checks_passed']is True
native_path=ROOT/'verification/sections/343-native-attempt2/actual/window.json'
native=json.loads(native_path.read_bytes());process=load('verification/sections/343-native-attempt2/process.json')
necessary=load('verification/sections/343-necessary-attempt2/process.json')
assert native['passed'] and native['qt_exit_code']==0
assert process['passed'] and process['exit_code']==0
assert necessary['passed'] and necessary['methods_ran']==36
for name,value in native['source_sha256_after'].items():assert digest(ROOT/name)==value,name
private=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json']
def fingerprint():return{n:digest(ROOT/n)if(ROOT/n).is_file()else None for n in private}
before_close=fingerprint()
old=load('verification/sections/342-main-window.json');closed=[]
for row in old['visible_windows']:
 h=row['hwnd']
 if not win32gui.IsWindow(h):continue
 pid=win32process.GetWindowThreadProcessId(h)[1]
 assert pid==row['pid'] and '黑流树海助手' in win32gui.GetWindowText(h),'Unexpected reused HWND; never close unrelated window.'
 proc=psutil.Process(pid)
 assert Path(proc.cwd()).resolve()==ROOT.resolve() and any('rouge.app' in arg for arg in proc.cmdline()),'Exact original app identity required.'
 win32gui.PostMessage(h,win32con.WM_CLOSE,0,0)
 deadline=time.monotonic()+15
 while win32gui.IsWindow(h) and time.monotonic()<deadline:time.sleep(0.1)
 assert not win32gui.IsWindow(h),'Old app did not close normally; no forced termination.'
 closed.append({'hwnd':h,'pid':pid,'normal_WM_CLOSE':True})
existing=[]
win32gui.EnumWindows(lambda h,_:existing.append(h)if '黑流树海助手' in win32gui.GetWindowText(h)else None,None)
assert not existing,'Existing app requires identity review; do not duplicate.'
before=fingerprint()
p=subprocess.Popen([str(ROOT/'.venv/Scripts/pythonw.exe'),'-B','-m','rouge.app'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
visible=[]
def collect(h,_):
 if win32gui.IsWindowVisible(h)and '黑流树海助手' in win32gui.GetWindowText(h):
  visible.append({'hwnd':h,'pid':win32process.GetWindowThreadProcessId(h)[1],'title':win32gui.GetWindowText(h),'visible':True,'responding':not bool(ctypes.windll.user32.IsHungAppWindow(h)),'minimized':bool(win32gui.IsIconic(h))})
deadline=time.monotonic()+20
while not visible and time.monotonic()<deadline:
 win32gui.EnumWindows(collect,None)
 if not visible:time.sleep(0.25)
assert len(visible)==1 and visible[0]['responding'],'Expected exactly one responsive original app.'
actual_app=psutil.Process(visible[0]['pid'])
assert Path(actual_app.cwd()).resolve()==ROOT.resolve()and any('rouge.app'in arg for arg in actual_app.cmdline()),'New actual Qt process must be the original project app; never equate it with the launcher PID.'
h=visible[0]['hwnd'];win32gui.ShowWindow(h,win32con.SW_RESTORE)
try:win32gui.SetForegroundWindow(h)
except Exception:pass
after=fingerprint()
report={'section':343,'passed':before==after,'actual_exit':0,'window_visible_and_responsive':True,'main_app_still_running':True,'launcher_pid':p.pid,'visible_windows':visible,'new_Qt_process_project_cwd_and_cmdline_verified':True,'closed_previous_exact_project_windows':closed,'foreground_hwnd':win32gui.GetForegroundWindow(),'own_window_is_foreground':win32gui.GetForegroundWindow()==h,'private_state_five_paths_unchanged':before==after,'private_entire_normal_close_and_start_interval_unchanged':before_close==before==after,'private_paths_changed_during_normal_old_app_close':[n for n in private if before_close[n]!=before[n]],'private_path_comparison_count':5,'private_contents_parsed_copied_or_restored':False,'private_hashes_published':False,'private_comparison_scope':'after normal old-app close through new-app startup; separate full-interval comparison retained; no previous run restored','native_receipt':native_path.relative_to(ROOT).as_posix(),'native_receipt_sha256':digest(native_path),'full_receipt':'verification/full-335/summary.json','full_receipt_sha256':digest(ROOT/'verification/full-335/summary.json'),'last_full335_historical_not_rerun_this_section':True,'source_sha256':native['source_sha256_after'],'native_game_or_chat_validation_claimed':False,'at_utc':datetime.now(timezone.utc).isoformat(),'launch':'Windows-mcp PowerShell; original .venv/Scripts/pythonw.exe -B -m rouge.app; original project cwd'}
OUT.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
review={k:report[k]for k in('section','passed','actual_exit','window_visible_and_responsive','private_state_five_paths_unchanged')}
review.update(original_receipt=OUT.relative_to(ROOT).as_posix(),original_receipt_sha256=digest(OUT))
(ROOT/'verification/sections/343-main-window-review.json').write_bytes((json.dumps(review,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:v for k,v in report.items()if k!='source_sha256'},ensure_ascii=False))
raise SystemExit(0 if report['passed']else 1)
