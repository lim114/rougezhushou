from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from rouge.app import MainWindow
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;c.open_replay();p=c.replay_popup.panel;p.tabs.setCurrentWidget(p.statistics);controls=p.statistics.card_controls;controls.pages.setCurrentIndex(1)
if controls.generate():controls.open_viewer()
started=time.monotonic()
def report():
 value={'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active']),'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'history_visible':c.replay_popup.isVisible(),'card_preview_has_image':not controls.preview.original.isNull(),'viewer_visible':bool(controls.viewer and controls.viewer.isVisible())}
 (Path(__file__).parent/'card447-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
report_timer=QTimer();report_timer.setInterval(2000);report_timer.timeout.connect(report);report_timer.start()
raise SystemExit(app.exec())
