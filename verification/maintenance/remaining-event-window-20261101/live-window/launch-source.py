from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.current_sand_view import CurrentSandDialog
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;d=CurrentSandDialog('curiosity',parent=c);d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);c.present(d);p=d.panel;started=time.monotonic()
def report():
 value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'event_visible':d.isVisible(),'actual_window_size':[d.width(),d.height()],'dark_shared_frame':d.objectName()=='mapReferenceWindow','conditions_closed':not p.conditions.isExpanded(),'gold_input_hidden':not p.gold.isVisible(),'exact_original_reference_available':p.result is not None,'editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])};(Path(__file__).parent/'remaining-event-window-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
