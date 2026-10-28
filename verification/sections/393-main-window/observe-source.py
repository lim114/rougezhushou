from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import sys,ctypes,json
sys.path[:0]=['scripts','.cache/305-window-tooldeps'];from player_ui_verification import source_hashes
import psutil,win32gui,win32process
R=Path.cwd();before=json.loads(Path('.cache/runtime393-before.json').read_text('utf8'));rows=[]
def visit(h,_):
 if win32gui.GetWindowText(h)in('黑流树海助手','工具设置'):
  pid=win32process.GetWindowThreadProcessId(h)[1];p=psutil.Process(pid)
  if Path(p.cwd()).resolve()==R and any('player_test_window393.py'in a for a in p.cmdline()):rows.append({'hwnd':h,'pid':pid,'title':win32gui.GetWindowText(h),'visible':bool(win32gui.IsWindowVisible(h)),'responding':not bool(ctypes.windll.user32.IsHungAppWindow(h))})
win32gui.EnumWindows(visit,None)
private_after={n:sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None for n in before['private']};after=source_hashes()
passed=before['private']==private_after and before['source']==after and any(r['visible']and r['responding']for r in rows)
d={'section':393,'passed':passed,'source_sha256_before':before['source'],'source_sha256_after':after,'owned_windows':rows,'private_five_paths_unchanged':before['private']==private_after,'private_contents_or_hashes_published':False,'normal_closed_project_pids':before['normal_closed_pids'],'automatic_sampling':False,'chat_sent':False,'game_operated':False,'actual_game_or_chat_validation_claimed':False,'desktop_visual_review_pending':True,'runtime_launch':'Retained foreground exec session, foreground console Python actual project Qt application.','at_UTC':datetime.now(timezone.utc).isoformat()}
out=R/'verification/sections/393-main-window';out.mkdir(exist_ok=True);(out/'window.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for a,b in [('prepare_runtime393.py','prepare-source.py'),('player_test_window393.py','launch-source.py'),('observe_runtime393.py','observe-source.py')]: (out/b).write_bytes((R/'.cache'/a).read_bytes())
print('passed',passed,'visible',[(r['title'],r['visible'])for r in rows])
