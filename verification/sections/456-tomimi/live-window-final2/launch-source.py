from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;c.open_map()
def report():
 h=c.reference_window
 value={'toolbar_visible':c.isVisible(),'main_reference_visible':h.isVisible(),'current_page':h.windowTitle(),'native_host':int(h.winId()),'page_count':h.pages.count()}
 (Path(__file__).parent/'tomimi456-final-live-status.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
