from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication,QAbstractItemView
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.player_map_reader import make_reader
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;dialog=make_reader('battle',{'id':'ro6_b_5','title':'公开固定资料'},c);dialog.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);c.present(dialog);p=dialog.panel;p.tabs.setCurrentIndex(1);started=time.monotonic()
def report():
 t=p.enemy_overview.tree;value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'battle_visible':dialog.isVisible(),'table_visible':p.enemy_overview.isVisible(),'Qt_native_word_wrap':t.wordWrap(),'no_text_elision':t.textElideMode()==Qt.TextElideMode.ElideNone,'pixel_scrolling':t.verticalScrollMode()==QAbstractItemView.ScrollMode.ScrollPerPixel,'readable_default_mechanism_width':t.columnWidth(6)>=240,'close_control_visible':dialog.titleBar.closeBtn.isVisible(),'editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])}
 (Path(__file__).parent/'enemy-table-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
