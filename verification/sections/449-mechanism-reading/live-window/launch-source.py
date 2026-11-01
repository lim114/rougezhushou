from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,Qt
from rouge.app import MainWindow
from rouge.player_map_reader import make_reader
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window
d=make_reader('battle',{'id':'ro6_b_4','title':'公开固定机制资料'},c)
d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);c.present(d);d.resize(800,650);p=d.panel;p.tabs.setCurrentIndex(1)
from rouge import current_hanko as model
sid=model.STAGES[0]
if p.stage_id!=sid:
 d.reject();d=make_reader('battle',{'id':sid,'title':'公开固定机制资料'},c);d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);c.present(d);d.resize(800,650);p=d.panel;p.tabs.setCurrentIndex(1)
ref=model.reference(sid);p.enemy_choices.select_value(ref['entities'][0]['key'] if 'entities' in ref else ref['rows'][0]['key']);assert p.open_hanko();child=p.hanko_dialog;q=child.panel;child.setWindowTitle('公开固定资料 · 汉科闪现机制');q.topic.setCurrentIndex(q.topic.findData('blink'));started=time.monotonic()
def report():
 value={'elapsed_since_launch':time.monotonic()-started,'toolbar_visible':c.isVisible(),'battle_visible':d.isVisible(),'mechanism_visible':child.isVisible(),'topic_blink':q.topic.currentData()=='blink','correct_focused_heading':q.player.textCursor().block().text()=='【完整文献参考 · 闪现】','full_text_retained':len(q.player.toPlainText())>800,'debug_label_chinese':q.tabs.tabText(1)=='原始资料（调试）','editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active']),'public_reference_not_current_run':True};(Path(__file__).parent/'mechanism449-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
