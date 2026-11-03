from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import win32gui
from rouge.app import MainWindow
app=QApplication([]);before=win32gui.GetForegroundWindow();window=MainWindow();window.show_compact();started=time.monotonic()
# Local-only diagnostics of the two actual read sessions, no extra screenshots or uploads.
h=window.compact_window.game_hover;provider=h.frame_provider;frame_number=0
def debug_frame(request):
 global frame_number
 value=provider(request);frame_number+=1
 import numpy as np
 root=Path(__file__).parent/'hover417-live-flow';root.mkdir(exist_ok=True)
 np.save(root/f'frame-{frame_number}.npy',value['image'])
 meta={k:v for k,v in value.items()if k!='image'};meta['request']={k:v for k,v in request.items()if k not in('difficulty',)}
 (root/f'frame-{frame_number}.json').write_text(json.dumps(meta),'utf8')
 return value
h.frame_provider=debug_frame
def report():
 c=window.compact_window;h=c.game_hover;b=c.game_binding
 value={'game_binding_active':bool(b.snapshot and b.snapshot['active']),'cursor_on_game':bool(b.snapshot and b.snapshot['cursor_on_game']),'actual_hover_card_visible':bool(h.card and h.card.isVisible()),'actual_hover_item_name':h.card.title.text()if h.card else None,'last_request_exists':h.last_request is not None,'busy':h.busy,'hover_diagnostics':h.last_report,'foreground_before':before,'foreground_after':win32gui.GetForegroundWindow(),'elapsed_since_launch':time.monotonic()-started}
 (Path(__file__).parent/'runtime417-live-status.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
report_timer=QTimer();report_timer.setInterval(2000);report_timer.timeout.connect(report);report_timer.start()
raise SystemExit(app.exec())
