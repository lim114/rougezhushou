from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R))
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge.current_sand_view import CurrentSandDialog
from rouge.current_lake_view import CurrentLakeDialog
from rouge.current_ritual_view import CurrentRitualDialog
app=QApplication([]);rows=[]
for name,constructor in[('sand',CurrentSandDialog),('lake',CurrentLakeDialog),('ritual',CurrentRitualDialog)]:
 d=constructor();d.show();QTest.qWait(30);p=d.panel
 rows.append({'kind':name,'actual_default':[d.width(),d.height()],'player_height':p.player.height(),'shared_frame':hasattr(d,'titleBar'),'object_name':d.objectName(),'condition_section_visible':p.conditions.isVisible(),'minimum':[d.minimumSizeHint().width(),d.minimumSizeHint().height()]})
 d.resize(760,600);QTest.qWait(30);rows[-1]['actual_after_760x600']=[d.width(),d.height()];rows[-1]['reader_after_760x600']=p.player.height();d.close()
(R/'verification/maintenance/remaining-event-window-20261101/before-geometry.json').write_text(json.dumps(rows,indent=2)+'\n','utf8');print(json.dumps(rows))
