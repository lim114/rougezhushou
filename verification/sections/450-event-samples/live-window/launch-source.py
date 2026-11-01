from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QTimer,Qt
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel
from rouge.app import MainWindow
from rouge.player_compact import ToolPopover
from rouge.player_map import PreviewMapView
from rouge.player_map_hover import NodeHoverCard
from rouge.player_map_acceptance import fixtures
app=QApplication([]);window=MainWindow();window.show_compact();c=window.compact_window;content=QWidget();body=QVBoxLayout(content);notice=QLabel('公开模板与历史样本示例 · 非当前对局；样本比例不是本局概率');notice.setWordWrap(True);body.addWidget(notice);view=PreviewMapView();body.addWidget(view,1);graphs,candidate,_,_=fixtures();view.set_map(graphs[0]);d=ToolPopover('第450节测试 · 公开事件历史样本',content,c,theme='light');d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);d.resize(900,550);c.present(d);card=NodeHoverCard(d);card.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,True);card.install(('public-not-current-run',graphs[0]['zone_id'],graphs[0]['template_id'],candidate),graphs[0],candidate,{},view);card.title.setText('公开样本示例 · 事件候选');card.pin.setChecked(True);area=card.screen().availableGeometry();card.move(area.right()-card.width()-25,area.top()+70);card.show();started=time.monotonic()
def report():
 buttons=[b for k,i,b in card.entry_buttons if k=='event'];value={'elapsed':time.monotonic()-started,'toolbar_visible':c.isVisible(),'public_map_demo_visible':d.isVisible(),'event_card_visible':card.isVisible(),'five_exact_event_samples':len(buttons)==5 and all(b.sample_reference and b.sample_reference['total']==438 for b in buttons),'public_not_current_run':True,'editor_dirty':window.player_notes.dirty,'game_binding_active':bool(c.game_binding.snapshot and c.game_binding.snapshot['active'])};(Path(__file__).parent/'event450-live-status.json').write_text(json.dumps(value,indent=2),'utf8')
timer=QTimer();timer.setInterval(2000);timer.timeout.connect(report);timer.start();raise SystemExit(app.exec())
