from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R))
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge.current_event_battles_view import CurrentEventBattlesDialog
app=QApplication([]);d=CurrentEventBattlesDialog('鸭托邦','choice_ro6_bat3_5');d.show();QTest.qWait(100);image=d.grab();out=R/'verification/maintenance/battle-reference-chain-20261101';image.save(str(out/'event-standalone-probe.png'));value={'actual_size':[d.width(),d.height()],'titlebar':d.titleBar.geometry().getRect(),'title_label':d.titleBar.titleLabel.geometry().getRect(),'panel':d.panel.geometry().getRect(),'layout_margins':list(d.layout().getContentsMargins()),'layout_count':d.layout().count(),'frame_ready':d.frame_ready,'corner_pixel_rgba':image.toImage().pixelColor(2,2).getRgb()};(out/'event-standalone-probe.json').write_text(json.dumps(value,indent=2)+'\n','utf8');print(value);d.close()
