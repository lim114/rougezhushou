from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.player_map_reader import make_reader
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料'},c);d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);c.present(d);r=d.panel.rewards;d.panel.tabs.setCurrentWidget(r);started=time.monotonic();events=[];d.finished.connect(lambda code:events.append(int(code)))
def report():
 count=sum(r.overview.topLevelItem(i).childCount()for i in range(r.overview.topLevelItemCount()));value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'battle_visible':d.isVisible(),'reward_overview_visible':r.overview.isVisible(),'section_expanded':r.overview_section.isExpanded(),'all_exact_public_source_rows_shown':count==len(r.result['rows'])if r.result else False,'conditional_not_actual_total_notice':'不能相加'in r.overview_notice.text(),'finished_signal_seen':bool(events),'editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])};(Path(__file__).parent/'reward-overview-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
