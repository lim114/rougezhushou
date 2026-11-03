from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.player_map_reader import make_reader
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;conditions={'difficulty':{'value':15},'zone':{'id':'zone_2'}};d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定资料算例'},c,config=conditions);d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);d.setWindowTitle('公开固定算例 · 木本玉米 · 保密15 / 第二主区域');c.present(d);d.resize(800,650);p=d.panel;p.tabs.setCurrentIndex(1);QTimer.singleShot(200,lambda:p.enemy_scroll.ensureWidgetVisible(p.enemy_overview.tree));started=time.monotonic()
def report():
 value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'battle_visible':d.isVisible(),'actual_window_size':[d.width(),d.height()],'all_seven_columns_visible':all(not p.enemy_overview.tree.isColumnHidden(i)for i in range(7)),'public_demo_conditions_only':True,'public_normal_reference_hp14976':p.enemy_forecasts['0']['environment_component']['maxHp']==14976,'complete_totals_remain_unknown':all(r['complete_current_total']is None for r in p.enemy_forecasts.values()),'editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])};(Path(__file__).parent/'current-enemy448-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
