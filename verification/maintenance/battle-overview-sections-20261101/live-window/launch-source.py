from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.player_map_reader import make_reader
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window
dialog=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},c)
dialog.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);c.present(dialog);p=dialog.panel;started=time.monotonic()
def report():
 value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'battle_visible':dialog.isVisible(),'map_expanded':p.map_section.isExpanded(),'quick_expanded':p.quick_section.isExpanded(),'details_collapsed':not p.map_details.isExpanded(),'model_shared':p.quick_enemies.model()is p.enemy_grid.model(),'selection_shared':p.quick_enemies.selectionModel()is p.enemy_grid.selectionModel(),'outside_close_same_window':dialog.titleBar.closeBtn.parentWidget()is dialog,'outside_close_inside_native_client':dialog.rect().contains(dialog.titleBar.closeBtn.geometry()),'close_control_visible':dialog.titleBar.closeBtn.isVisible(),'editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])}
 (Path(__file__).parent/'battle-overview-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start()
raise SystemExit(app.exec())
