from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import win32gui
from rouge.app import MainWindow
app=QApplication([]);before=win32gui.GetForegroundWindow();window=MainWindow();window.show_compact();started=time.monotonic()
def report():
 c=window.compact_window;h=c.game_hover;b=c.game_binding
 value={'game_binding_active':bool(b.snapshot and b.snapshot['active']),'actual_hover_card_visible':bool(h.card and h.card.isVisible()),'hover_diagnostics':h.last_report,'foreground_before':before,'foreground_after':win32gui.GetForegroundWindow(),'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible()}
 (Path(__file__).parent/'calculation-context-review-live-status.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
report_timer=QTimer();report_timer.setInterval(2000);report_timer.timeout.connect(report);report_timer.start()
raise SystemExit(app.exec())
