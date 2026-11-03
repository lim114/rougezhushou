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
 value={'game_binding_active':bool(b.snapshot and b.snapshot['active']),'cursor_on_game':bool(b.snapshot and b.snapshot['cursor_on_game']),'actual_hover_card_visible':bool(h.card and h.card.isVisible()),'actual_hover_item_name':h.card.title.text()if h.card else None,'last_request_exists':h.last_request is not None,'busy':h.busy,'foreground_before':before,'foreground_after':win32gui.GetForegroundWindow(),'elapsed_since_launch':time.monotonic()-started}
 (Path(__file__).parent/'runtime417-live-status.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
QTimer.singleShot(18000,report)
raise SystemExit(app.exec())
