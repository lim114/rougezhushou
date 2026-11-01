from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.player_map_reader import make_reader
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;d=make_reader('battle',{'id':'ro6_n_1_1','title':'公开固定资料'},c);d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);c.present(d);d.resize(800,600);p=d.panel;p.tabs.setCurrentIndex(1);QTimer.singleShot(200,lambda:p.enemy_scroll.ensureWidgetVisible(p.enemy_overview.tree));started=time.monotonic()
def report():
 views=(p.quick_table,p.enemy_overview.tree);value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'battle_visible':d.isVisible(),'actual_window_size':[d.width(),d.height()],'full_enemy_page_selected':p.tabs.currentIndex()==1,'unknown_columns_hidden_in_both_views':all([i for i in range(7)if not v.isColumnHidden(i)]==[0,5,6]for v in views),'original_seven_field_model':views[0].model()is views[1].model()and views[1].model().columnCount()==7,'editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])};(Path(__file__).parent/'battle-reference-chain-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
