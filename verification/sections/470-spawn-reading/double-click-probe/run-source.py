from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/470-spawn-reading/double-click-probe'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_calculation_target.py','rouge/battle_view.py','rouge/reporting.py','rouge/mechanism_reading.py','rouge/app.py','rouge/player_compact.py','rouge/player_workspace.py','rouge/player_theme.py','rouge/player_reference_window.py','rouge/player_map_reader.py','rouge/current_map_position_view.py','rouge/player_map_hover.py','rouge/player_cannot_links.py','rouge/current_cannot_view.py','rouge/current_battle_view.py','rouge/reference_copy.py','rouge/enemy_overview.py','rouge/player_spawn_filters.py'];data_paths += [p.relative_to(R).as_posix()for p in(R/'rouge/data/player-theme').rglob('*')if p.is_file()];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from PySide6.QtTest import QSignalSpy
 window.show_compact();c=window.compact_window;host=c.reference_window
 for timer in window.findChildren(QTimer):timer.stop()
 def settle():gui.processEvents();QTest.qWait(150);gui.processEvents()
 c.open_full(window.battle_preview);window.battle_preview.set_stage('ro6_n_2_3');window.open_calculation_target(source='stage');page=host.pages.currentWidget();p=page.panel;p.tabs.setCurrentIndex(2);host.resize(900,600);settle();index=next(i for i,a in enumerate(p.result['actions'])if a['raw']['actionType']=='SPAWN');p.actions.setCurrentRow(index);p.actions.setFocus();settle();key=p.action_key;QTest.keyClick(p.actions,Qt.Key.Key_Return);settle();position=host.pages.currentWidget();position.panel.combo.setCurrentIndex(1);settle();QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);settle();p.actions.scrollToItem(p.actions.currentItem());settle();point=p.actions.visualItemRect(p.actions.currentItem()).center();activated=QSignalSpy(p.actions.itemActivated);double=QSignalSpy(p.actions.itemDoubleClicked);report={'in_viewport':p.actions.viewport().visibleRegion().contains(point),'position_key':key,'parent_page_restored':host.pages.currentWidget()is page,'button_enabled':p.action_position_button.isEnabled()}
 QTest.mouseDClick(p.actions.viewport(),Qt.MouseButton.LeftButton,pos=point);settle();report['double_only']={'activated':activated.count(),'double':double.count(),'reused':host.pages.currentWidget()is position,'still_parent':host.pages.currentWidget()is page}
 if host.pages.currentWidget()is not page:QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);settle()
 QTest.mouseClick(p.actions.viewport(),Qt.MouseButton.LeftButton,pos=point);QTest.mouseDClick(p.actions.viewport(),Qt.MouseButton.LeftButton,pos=point);settle();report['full_sequence']={'activated':activated.count(),'double':double.count(),'reused':host.pages.currentWidget()is position,'still_parent':host.pages.currentWidget()is page};(out/'observation.json').write_text(json.dumps(report,indent=2)+'\n','utf8');require(report['full_sequence']['activated']>0,'native_complete_mouse_sequence_activates_item');window.player_validation_target=host
player_acceptance.check=check
raise SystemExit(ui.run(470,out/'window.json'))
