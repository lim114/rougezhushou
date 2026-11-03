from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/maintenance/event-reader-layout-20261101/geometry-trace';B.mkdir(exist_ok=False)
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge.current_vine_events_view import CurrentVineEventsDialog
from rouge.player_map_reader import readable
q=QApplication([]);d=readable(CurrentVineEventsDialog('呼吸的红苔'));d.show();q.processEvents();p=d.panel;rows=[]
def record(label):
 h=p.conditions.parentWidget();rows.append({'stage':label,'header_y_h':[h.y(),h.height()],'section_h':p.conditions.height(),'content_hidden':p.conditions.content().isHidden(),'max_content_h':p.conditions.content().maximumHeight(),'scene_y':p.scene.y(),'tabs_y_h':[p.tabs.y(),p.tabs.height()]})
record('initial');p.conditions.toggleButton().click();q.processEvents();record('open_one_events');p.conditions.toggleButton().click();q.processEvents();record('close_one_events')
for delay in(16,40,120):QTest.qWait(delay);q.processEvents();record('close_wait_'+str(delay))
assert d.grab().save(str(B/'settled-collapsed.png'));(B/'actual.json').write_text(json.dumps(rows,indent=2)+'\n','utf8');(B/'probe-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(rows));d.close()
