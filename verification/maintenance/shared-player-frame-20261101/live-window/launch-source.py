from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.player_map_reader import make_reader
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window
record=next(row['record']for row in window.node_catalog.entries if row['key']=='event:community_group_009')
dialog=make_reader('event',record,c);dialog.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);dialog.show();dialog.panel.choices.setCurrentRow(0);started=time.monotonic()
def report():
 value={'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active']),'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'event_reader_visible':dialog.isVisible(),'conditions_collapsed':not dialog.panel.conditions.isExpanded(),'common_dark_theme':dialog.property('playerTheme')=='dark','external_frame_visible':dialog.titleBar.isVisible(),'close_control_visible':dialog.titleBar.closeBtn.isVisible(),'single_frame_header':sum(dialog.layout().itemAt(i).widget()is dialog.titleBar for i in range(dialog.layout().count()))==1}
 (Path(__file__).parent/'shared-frame-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
report_timer=QTimer();report_timer.setInterval(2000);report_timer.timeout.connect(report);report_timer.start()
raise SystemExit(app.exec())
