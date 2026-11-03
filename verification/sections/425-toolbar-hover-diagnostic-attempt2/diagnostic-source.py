"""Observe existing own Qt events without replacing hover or forcing a result."""
from pathlib import Path
import sys,json,time
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QCursor
from rouge.player_toolbar import DockButton
from rouge.player_compact import CompactAssistant
from player_ui_verification import run
import win32gui
out=R/'verification/sections/425-toolbar-hover-diagnostic-attempt2';assert not out.exists();out.mkdir()
(out/'diagnostic-source.py').write_bytes(Path(__file__).read_bytes());rows=[];began=time.monotonic();gui=QApplication([])
def capture(button,kind):
    if button.accessibleName()!='工具设置':return
    bar=button.parentWidget();p=button.mapFromGlobal(QCursor.pos());g=bar.geometry();position=QCursor.pos()
    rows.append({'t':round(time.monotonic()-began,3),'event':kind,'amount':button._amount,'target':button._target,'width':button.width(),'under_mouse':button.underMouse(),'keyboard':button._keyboard,'button_local_cursor':[p.x(),p.y()],'bar_geometry':[g.x(),g.y(),g.width(),g.height()],'button_x':button.x(),'visible':bar.isVisible(),'mask_contains_button_center':bar.mask().contains(button.geometry().center())})
for name in ('enterEvent','leaveEvent','focusInEvent','focusOutEvent'):
    original=getattr(DockButton,name)
    def replacement(self,event,_original=original,_name=name):
        capture(self,'before_'+_name);result=_original(self,event);capture(self,'after_'+_name);return result
    setattr(DockButton,name,replacement)
def sample():
    for bar in QApplication.topLevelWidgets():
        if isinstance(bar,CompactAssistant)and bar.isVisible():capture(bar.buttons['工具设置'],'timer_sample')
timer=QTimer();timer.setInterval(40);timer.timeout.connect(sample);timer.start()
try:code=run(412,out/'window.json')
finally:
    timer.stop();(out/'events.json').write_text(json.dumps({'product_event_handlers_not_bypassed':True,'own_Qt_only':True,'events':rows},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(code)
