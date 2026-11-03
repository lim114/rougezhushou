"""Post-full read-only recheck of the already opened, exact owned440 test window."""
from pathlib import Path
from hashlib import sha256
import json,sys,time,ctypes
import win32gui,win32process
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from player_ui_verification import source_hashes
full=R/'verification/full-440/summary.json';summary=json.loads(full.read_bytes());assert summary['available_checks_passed']and summary['scope_not_reduced']and summary['actual_root_controller_exit']==0
out=R/'verification/sections/440-main-window-attempt2/final-response.json';assert not out.exists();original=out.with_name('window.json');runtime=json.loads(original.read_bytes());source=source_hashes();assert runtime['source_sha256_before']==runtime['source_sha256_after']==source
freeze=json.loads((R/summary['source_freeze']).read_bytes());union={**freeze['source_sha256'],**freeze['supplemental_public_inputs_sha256']};assert all(union[n]==h for n,h in source.items())
rows=[]
for old in runtime['owned_windows']:
 h=old['hwnd'];assert win32gui.IsWindow(h)and win32process.GetWindowThreadProcessId(h)[1]==old['pid']and win32gui.IsWindowVisible(h)and not win32gui.IsIconic(h)and not ctypes.windll.user32.IsHungAppWindow(h)
 ctypes.windll.user32.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4));rect=win32gui.GetWindowRect(h);rows.append({'hwnd':h,'pid':old['pid'],'visible':True,'responding':True,'physical_rect':list(rect)})
def read_owned_telemetry(path):
 for attempt in range(10):
  try:return json.loads(path.read_bytes())
  except (OSError,json.JSONDecodeError):
   if attempt==9:raise
   time.sleep(.02)
live=R/'.cache/runtime440-live-status.json';a=read_owned_telemetry(live);time.sleep(2.5);b=read_owned_telemetry(live);assert b['elapsed_since_launch']>a['elapsed_since_launch']and b['toolbar_visible'];assert source_hashes()==source
result={'section':440,'passed':True,'actual_after_complete_full_scope':True,'complete_full_summary_sha256':sha256(full.read_bytes()).hexdigest(),'original_runtime_receipt_sha256':sha256(original.read_bytes()).hexdigest(),'owned_windows':rows,'actual_Qt_timer_status_advanced':True,'source_sha256_before':source,'source_sha256_after':source,'all_runtime_source_paths_match_completed_full_freeze':True,'game_operated':False,'chat_sent':False,'private_contents_or_hashes_published':False,'private_state_not_restored':True,'new_or_duplicate_application_started':False,'desktop_visual_recheck_pending':True}
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');out.with_name('final-probe-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'actual_runtime_rechecked_after_full':True,'windows':rows,'summary_sha256':result['complete_full_summary_sha256']},ensure_ascii=False))
