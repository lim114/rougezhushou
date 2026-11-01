from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;None
window.calculation_scope.setCurrentIndex(window.calculation_scope.findData('archive'));c.open_full(window.battle_preview);window.battle_preview.set_stage('ro6_n_2_3');window.open_calculation_target(source='stage');p=c.reference_window.pages.currentWidget().panel;p.enemy_choices.select_value(p.result['enemies'][0]['key']);p.tabs.setCurrentIndex(1);p.enemy_topics.setCurrentIndex(p.enemy_topics.findText('介绍与机制'))

def report():
 h=c.reference_window
 value={'toolbar_visible':c.isVisible(),'main_reference_visible':h.isVisible(),'current_page':h.windowTitle(),'native_host':int(h.winId()),'page_count':h.pages.count(),'calculation_mode':window.damage_result.get('calculation_mode')if window.damage_result else None,'report_available':window.damage_result is not None}
 (Path(__file__).parent/'enemy469-live-status.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
