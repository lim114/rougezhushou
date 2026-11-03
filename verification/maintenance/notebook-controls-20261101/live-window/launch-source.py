from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from rouge.app import MainWindow
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window
c.open_recent_notes();dialog=c.recent_notes_popup;p=dialog.panel;p.more.setChecked(True);started=time.monotonic()
def report():
 value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'notebook_visible':dialog.isVisible(),'options_visible':p.options_scroll.isVisible(),'external_header_visible':dialog.titleBar.isVisible(),'close_control_visible':dialog.titleBar.closeBtn.isVisible(),'light_notebook_theme':dialog.property('playerTheme')=='light','editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])}
 (Path(__file__).parent/'notebook-controls-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start()
raise SystemExit(app.exec())
