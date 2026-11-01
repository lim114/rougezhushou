from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.player_map_reader import make_reader
from rouge import current_hanko
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;sid=current_hanko.STAGES[0];key=current_hanko.reference(sid)['rows'][0]['key'];d=make_reader('battle',{'id':sid,'title':'公开固定资料'},c);d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);c.present(d);d.resize(800,600);p=d.panel;p.tabs.setCurrentIndex(1);p.enemy_choices.select_value(key);p.open_hanko();reader=p.hanko_dialog;started=time.monotonic()
def report():
 value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'battle_visible':d.isVisible(),'mechanism_visible':reader.isVisible(),'actual_mechanism_size':[reader.width(),reader.height()],'shared_dark_frame':reader.objectName()=='mapReferenceWindow','public_reference_present':reader.panel.result is not None,'notice_collapsed':not reader.panel.reading_header.scope.isExpanded()and not reader.panel.notice.isVisible(),'body_height':reader.panel.player.viewport().height(),'editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])};(Path(__file__).parent/'mechanism-reading-density-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
