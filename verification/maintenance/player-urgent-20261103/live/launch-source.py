from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window
# This is an idle UI validation launch, not the next recording session.
c.game_hover.set_enabled(False)
def report():
 b=c.game_binding;s=b.snapshot;h=c.reference_window
 value={'toolbar_visible':c.isVisible(),'tray_visible':c.tray.isVisible(),'outside_space_hidden':bool(c.property('outsideSpaceHidden')),'main_reference_visible':h.isVisible(),'native_bar':int(c.winId()),'native_host':int(h.winId()),'auto_sampling':window.auto.isChecked(),'binding_active':bool(s and s['active']),'bar_geometry':[c.x(),c.y(),c.width(),c.height()],'game_client':list(s['logical_client'].getRect())if s and s['active']else None,'outside_game':not c.geometry().intersects(s['logical_client'])if s and s['active']and c.isVisible()else None,'at':time.time()}
 (Path(__file__).parent/'urgent-live-status.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
timer=QTimer();timer.setInterval(1000);timer.timeout.connect(report);timer.start();QTimer.singleShot(1200,report)
raise SystemExit(app.exec())
