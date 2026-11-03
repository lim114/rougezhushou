"""Normally close only the exact old project test runtime; preserve private state."""
from pathlib import Path
from hashlib import sha256
import json,sys,runpy,time
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'.cache/305-window-tooldeps')]
import psutil,win32gui,win32process,win32con
files=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json','.local/player-shortcut.json']
def private():return {n:sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None for n in files}
before=private();(R/'.cache/runtime425-validation-close-before.json').write_text(json.dumps(before),'utf8')
def owned():
    result=set()
    for p in psutil.process_iter(['pid','cmdline']):
        try:
            if Path(p.cwd()).resolve()==R and any(str(arg).replace('\\','/').endswith('/.cache/player_test_window417.py')for arg in(p.info['cmdline']or[])):result.add(p.pid)
        except(psutil.Error,OSError):pass
    return result
pids=owned();requested=[]
def visit(h,_):
    pid=win32process.GetWindowThreadProcessId(h)[1]
    if pid in pids and win32gui.GetWindowText(h)=='黑流树海助手 · 局外计算与节点测试':
        win32gui.PostMessage(h,win32con.WM_CLOSE,0,0);requested.append(pid)
win32gui.EnumWindows(visit,None)
for _ in range(40):
    if not owned():break
    time.sleep(.25)
assert not owned(),'Old runtime still alive; do not force close or overlap.'
same=private()==before
out=R/'verification/sections/425-old-runtime-validation-isolation';assert not out.exists();out.mkdir()
(out/'close-source.py').write_bytes(Path(__file__).read_bytes())
(out/'receipt.json').write_text(json.dumps({'section':425,'exact_owned_pids':sorted(pids),'normal_close_requested_for':requested,'all_exact_old_launchers_exited':True,'private_six_paths_unchanged':same,'forced_termination':False,'game_input_or_chat_sent':False,'limits':'Close only the old417 project test app to prevent its floating card from overlapping isolated test windows. Restore the actual updated425 test app after current validation. No private contents or hash values are published.'},ensure_ascii=False,indent=2)+'\n','utf8')
assert same,'Private state changed; preserve it and do not restore an old run.'
print('Exact old test runtime closed normally; private six paths unchanged. Updated425 test window is still required at final delivery.')
