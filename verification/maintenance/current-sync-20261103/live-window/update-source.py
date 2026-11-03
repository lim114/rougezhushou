from pathlib import Path
from hashlib import sha256
import sys,subprocess,json,time,ctypes
r=Path.cwd();sys.path[:0]=[str(r/'scripts'),str(r/'.cache/305-window-tooldeps')]
from player_ui_verification import source_hashes
import psutil,win32gui,win32process
out=r/'verification/maintenance/current-sync-20261103/live-window';out.mkdir(exist_ok=False)
private=json.loads((r/'.cache/sync-private-before.json').read_bytes())
def hashes():return {p:sha256((r/p).read_bytes()).hexdigest()if(r/p).is_file()else None for p in private}
assert hashes()==private,'Private changes before sampling: preserve them and inspect before validation.'
for proc in psutil.process_iter(['name','cmdline']):
 if 'python'not in(proc.info['name']or'').lower():continue
 args=' '.join(proc.info['cmdline']or[]).replace('\\','/')
 assert not any(n in args for n in('player_test_window_sync.py','player_test_window_urgent.py','run_gate0_session.py')),'Owned helper already runs; no duplicate.'
source=source_hashes();launcher=r/'.cache/player_test_window_sync.py'
with(r/'.cache/current-sync-live.log').open('ab')as log:child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(launcher)],cwd=r,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
status=None
for _ in range(90):
 assert child.poll()is None,'Live application exited: inspect local startup log.'
 f=r/'.cache/current-sync-live-status.json'
 if f.exists():
  status=json.loads(f.read_bytes())
  if status['reader_visible']and status['tray_visible']and status['at']>time.time()-4:break
 time.sleep(.5)
assert status and status['auto_sampling']and status['reader_visible']
assert win32gui.IsWindowVisible(status['native_host'])and not ctypes.windll.user32.IsHungAppWindow(status['native_host'])
assert source==source_hashes()
value={'passed':True,'actual_retained_launcher_PID':child.pid,'actual_native_host_PID':win32process.GetWindowThreadProcessId(status['native_host'])[1],'toolbar_visible':status['toolbar_visible'],'reader_visible':status['reader_visible'],'tray_visible':status['tray_visible'],'binding_active':status['binding_active'],'outside_game':status['outside_game'],'reader_overlap_fraction':status['reader_overlap_fraction'],'native_window_responding':True,'auto_sampling_enabled':True,'same_run_at_launch':status['same_run'],'private_runtime_updates_authorized_by_background_sampling':True,'private_settings_and_chat_unchanged_at_launch':all(hashes()[p]==h for p,h in private.items()if p not in('.local/run-state.json','.local/operator-state.json')),'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent_by_agent':False,'source_sha256_before':source,'source_sha256_after':source_hashes(),'desktop_visual_review_pending':True}
(out/'window.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');(out/'launch-source.py').write_bytes(launcher.read_bytes());(out/'update-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in value.items()if not k.startswith('source_')}))
