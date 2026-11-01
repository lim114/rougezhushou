from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;None
from rouge.player_map_reader import make_reader
page=make_reader('battle',{'id':'ro6_n_2_3','title':'本性难移'},window,historical=True,page_owner=c);page.prepare=page.panel.refresh_reference;c.present(page);page.panel.open_stage_objects()
objects=c.reference_window.pages.currentWidget().panel;objects.entries.setCurrentIndex(1);objects.open_position()

def report():
 h=c.reference_window
 value={'toolbar_visible':c.isVisible(),'main_reference_visible':h.isVisible(),'current_page':h.windowTitle(),'native_host':int(h.winId()),'page_count':h.pages.count()}
 (Path(__file__).parent/'battletools464-live-status.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
