from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.player_map_reader import make_reader
from rouge import current_battle_reference as model
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},c);d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);c.present(d);p=d.panel;p.tabs.setCurrentIndex(2);row=next(i for i,a in enumerate(p.result['actions'])if len(a['enemy_candidates'])==1);p.actions.setCurrentRow(row);p.actions.scrollToItem(p.actions.item(row));started=time.monotonic();events=[];d.finished.connect(lambda code:events.append(int(code)))
def report():
 a=next((a for a in p.result['actions']if a['key']==p.action_key),None)if p.result else None
 value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'battle_visible':d.isVisible(),'spawn_list_visible':p.actions.isVisible(),'all_exact_public_rows_shown':p.actions.count()==len(p.result['actions'])if p.result else False,'exact_full_original_description':a is not None and p.action_player.toPlainText()==model.action_text(a),'finished_signal_seen':bool(events),'editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])};(Path(__file__).parent/'spawn-reading-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
