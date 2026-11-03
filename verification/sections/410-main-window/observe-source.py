"""Observe exact owned final window and hash-only private-state preservation."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import sys,ctypes,json
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
from player_ui_verification import source_hashes
import psutil,win32gui,win32process
before=json.loads((R/'.cache/runtime410-before.json').read_bytes());rows=[]
def visit(hwnd,_):
    pid=win32process.GetWindowThreadProcessId(hwnd)[1]
    try:
        process=psutil.Process(pid)
        if Path(process.cwd()).resolve()!=R or not any('player_test_window410.py'in arg for arg in process.cmdline()):return
    except(psutil.Error,OSError):return
    if not win32gui.IsWindowVisible(hwnd):return
    rows.append({'hwnd':hwnd,'pid':pid,'title':win32gui.GetWindowText(hwnd),'visible':True,'responding':not bool(ctypes.windll.user32.IsHungAppWindow(hwnd))})
win32gui.EnumWindows(visit,None)
after={name:sha256((R/name).read_bytes()).hexdigest()if(R/name).is_file()else None for name in before['private']}
sources=source_hashes();passed=before['private']==after and before['source']==sources and bool(rows) and all(row['responding']for row in rows)
record={'section':410,'passed':passed,'source_sha256_before':before['source'],'source_sha256_after':sources,'owned_windows':rows,'private_six_paths_including_shortcut_unchanged':before['private']==after,'private_contents_or_hashes_published':False,'preparation_closed_existing_windows':False,'automatic_sampling_started_by_launcher':False,'chat_sent_by_launcher':False,'game_operated_by_launcher':False,'actual_game_or_chat_validation_claimed':False,'desktop_visual_review_pending':True,'at_UTC':datetime.now(timezone.utc).isoformat()}
out=R/'verification/sections/410-main-window';assert not out.exists();out.mkdir()
(out/'window.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
for name,leaf in [('prepare_runtime410.py','prepare-source.py'),('player_test_window410.py','launch-source.py'),('observe_runtime410.py','observe-source.py')]:
    (out/leaf).write_bytes((R/'.cache'/name).read_bytes())
print(json.dumps({'passed':passed,'visible_owned_windows':rows,'private_contents_or_hashes_printed':False},ensure_ascii=False))
