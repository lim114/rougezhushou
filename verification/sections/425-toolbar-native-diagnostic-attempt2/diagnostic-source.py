"""Read-only native geometry diagnostics in isolated412; preserve real failures."""
from pathlib import Path
import json,sys,runpy
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
assert json.loads((R/'.cache/full425-prepared/attempt-1/root-launch/controller-process.json').read_bytes())['status']=='completed'
import win32gui,win32process
from unittest.mock import patch
from player_ui_verification import run
from PySide6.QtWidgets import QApplication
from rouge.player_game_binding import physical_pixels
out=R/'verification/sections/425-toolbar-native-diagnostic-attempt2';assert not out.exists();out.mkdir()
(out/'diagnostic-source.py').write_bytes(Path(__file__).read_bytes())
original=win32gui.WindowFromPoint;rows=[]
def observe(point):
    result=original(point)
    own=[]
    import os
    def inspect(h,_):
        if win32process.GetWindowThreadProcessId(h)[1]==os.getpid() and win32gui.IsWindowVisible(h):
            with physical_pixels():
                own.append({'hwnd':h,'rect':win32gui.GetWindowRect(h),'client':win32gui.GetClientRect(h),'client_origin':win32gui.ClientToScreen(h,(0,0)),'contains_query_phys':win32gui.PtInRect(win32gui.GetWindowRect(h),point),'native_exstyle':win32gui.GetWindowLong(h,-20)})
    win32gui.EnumWindows(inspect,None)
    with physical_pixels(): physical_hit=original(point)
    qt=[]
    app=QApplication.instance()
    if app:
        for w in app.topLevelWidgets():
            if w.isVisible():
                g=w.geometry();qt.append({'hwnd':int(w.winId()),'class':type(w).__name__,'geometry':[g.x(),g.y(),g.width(),g.height()],'dpr':w.devicePixelRatioF()})
    root=win32gui.GetAncestor(result,2)if result else 0
    rank=[];cursor=win32gui.GetTopWindow(0);seen=set()
    for _ in range(2048):
        if not cursor or cursor in seen:break
        seen.add(cursor)
        if cursor in [x['hwnd']for x in own] or cursor==root:rank.append({'own':cursor in [x['hwnd']for x in own],'hwnd_if_own':cursor if cursor in [x['hwnd']for x in own]else None,'is_hit_root':cursor==root})
        cursor=win32gui.GetWindow(cursor,2)
    rows.append({'input_point':point,'returned_handle_is_own':result in [x['hwnd']for x in own],'hit_process_is_own':bool(result and win32process.GetWindowThreadProcessId(result)[1]==os.getpid()),'hit_root_is_own':root in [x['hwnd']for x in own],'hit_class':win32gui.GetClassName(result)if result else None,'physical_context_same_hit':physical_hit==result,'own_and_hit_relative_z_order':rank,'own_windows':own,'qt_own_visible':qt})
    return result
try:
    with patch.object(win32gui,'WindowFromPoint',side_effect=observe):code=run(412,out/'window.json')
finally:
    (out/'geometry.json').write_text(json.dumps({'scope':'owned isolated windows only; no game input or private state','queries':rows},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(code)
