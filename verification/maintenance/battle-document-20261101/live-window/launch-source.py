from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.player_map_reader import make_reader
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},c);d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);c.present(d);p=d.panel;p.tabs.setCurrentIndex(0);QTimer.singleShot(200,lambda:p.overview_scroll.ensureWidgetVisible(p.quick_table));started=time.monotonic();events=[];d.finished.connect(lambda code:events.append(int(code)))
def report():
 value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'battle_visible':d.isVisible(),'same_home_page_selected':p.tabs.currentIndex()==0,'mechanism_table_visible':p.quick_table.isVisible(),'native_model_shared':p.quick_table.model()is p.enemy_overview.tree.model(),'exact_source_rows':sum(p.quick_table.model().rowCount(p.quick_table.model().index(i,0))for i in range(p.quick_table.model().rowCount()))==p.enemy_grid.count(),'finished_signal_seen':bool(events),'editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])};(Path(__file__).parent/'battle-document-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
