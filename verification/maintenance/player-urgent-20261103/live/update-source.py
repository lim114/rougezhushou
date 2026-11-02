from pathlib import Path
from hashlib import sha256
import sys,subprocess,time,json,ctypes
r=Path.cwd();sys.path[:0]=[str(r/'scripts'),str(r/'.cache/305-window-tooldeps')]
import win32gui,win32process,psutil
from player_ui_verification import source_hashes
out=r/'verification/maintenance/player-urgent-20261103/live';out.mkdir(exist_ok=False)
private=json.loads((r/'.cache/urgent-player-private-before.json').read_bytes())
def hashes():return {p:sha256((r/p).read_bytes()).hexdigest()if(r/p).is_file()else None for p in private}
assert hashes()==private,'Private state changed independently: preserve current state, stop verification.'
for p in psutil.process_iter(['name','cmdline']):
 if 'python'not in(p.info['name']or'').lower():continue
 args=' '.join(p.info['cmdline']or[]).replace('\\','/')
 assert not any(n in args for n in('player_test_window_urgent.py','player_test_window_gate0.py','run_gate0_session.py')),'Owned application already runs; no duplicate.'
source=source_hashes();launcher=r/'.cache/player_test_window_urgent.py'
with(r/'.cache/urgent-live-startup.log').open('ab')as log:child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(launcher)],cwd=r,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
status=None
for _ in range(90):
 assert child.poll()is None,'New test application exited; inspect local log.'
 f=r/'.cache/urgent-live-status.json'
 if f.exists():
  status=json.loads(f.read_bytes())
  if (status['toolbar_visible']or status['outside_space_hidden'])and status['at']>time.time()-4:break
 time.sleep(.5)
assert status and status['tray_visible']and not status['auto_sampling']
assert (status['outside_game']is True)if status['toolbar_visible']and status['binding_active']else True
assert win32gui.IsWindow(status['native_bar'])and not ctypes.windll.user32.IsHungAppWindow(status['native_bar'])
assert source==source_hashes()and hashes()==private
value={'passed':True,'actual_retained_launcher_PID':child.pid,'actual_native_bar_PID':win32process.GetWindowThreadProcessId(status['native_bar'])[1],'toolbar_visible':status['toolbar_visible'],'tray_visible':status['tray_visible'],'outside_space_hidden':status['outside_space_hidden'],'binding_active':status['binding_active'],'outside_game':status['outside_game'],'native_window_responding':True,'auto_sampling_enabled':False,'hover_probe_enabled_for_idle_UI_validation':False,'private_six_paths_unchanged':True,'game_operated':False,'chat_sent':False,'private_desktop_image_published':False,'desktop_visual_review_pending':True,'source_sha256_before':source,'source_sha256_after':source_hashes()}
(out/'window.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');(out/'launch-source.py').write_bytes(launcher.read_bytes());(out/'update-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in value.items()if not k.startswith('source_')}))
