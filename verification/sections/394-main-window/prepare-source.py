from pathlib import Path
from hashlib import sha256
import sys,time,ctypes,json
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
import win32gui,win32process,win32con,win32api,psutil
from player_ui_verification import source_hashes
files=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json','.local/player-shortcut.json']
def fingerprint():return {n:sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None for n in files}
def windows():
 rows=[]
 def visit(h,_):
  if win32gui.GetWindowText(h).startswith('黑流树海助手'):
   p=psutil.Process(win32process.GetWindowThreadProcessId(h)[1])
   if Path(p.cwd()).resolve()==R and any('player_test_window391.py'in a or'player_test_window392.py'in a or'player_test_window393.py'in a or'player_test_window394.py'in a or'rouge.app'==a for a in p.cmdline()):rows.append({'hwnd':h,'pid':p.pid,'thread':win32process.GetWindowThreadProcessId(h)[0],'main':' · 'in win32gui.GetWindowText(h)})
 win32gui.EnumWindows(visit,None);return rows
before=fingerprint();source=source_hashes();rows=windows()
for row in rows:
 if row['main']:win32gui.PostMessage(row['hwnd'],win32con.WM_CLOSE,0,0)
deadline=time.monotonic()+25
while windows()and time.monotonic()<deadline:time.sleep(.2)
assert not windows(),'Normal close did not finish; leave owned window and unsaved state intact.'
for thread in {r['thread']for r in rows}:
 try:win32api.PostThreadMessage(thread,win32con.WM_QUIT,0,0)
 except Exception:pass
(R/'.cache/runtime394-before.json').write_text(json.dumps({'private':before,'source':source,'normal_closed_pids':sorted({r['pid']for r in rows})}))
print('normal closed owned project processes',len({r['pid']for r in rows}),'private five paths unchanged on normal close',before==fingerprint())
