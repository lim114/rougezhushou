from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/470-spawn-reading/native02'
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
 from PySide6.QtWidgets import QScrollArea
 from PySide6.QtGui import QTextCursor
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;host=c.reference_window;images=[];layouts=[]
 for timer in window.findChildren(QTimer):timer.stop()
 def settle():gui.processEvents();QTest.qWait(100);gui.processEvents()
 def click(button):
  parent=button.parentWidget()
  while parent is not None and parent is not host:
   if isinstance(parent,QScrollArea):parent.ensureWidgetVisible(button)
   parent=parent.parentWidget()
  settle();require(button.isVisible()and button.isEnabled(),'clickable_'+button.text());QTest.mouseClick(button,Qt.MouseButton.LeftButton);settle()
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');require(host.screen().availableGeometry().contains(host.geometry()),name+'_within_screen');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 require(c.open_full(window.battle_preview),'original_target_workspace');window.battle_preview.set_stage('ro6_n_2_3');require(window.open_calculation_target(source='stage'),'fixed_stage_in_shared_host');page=host.pages.currentWidget();p=page.panel;p.tabs.setCurrentIndex(2);host.resize(900,600);settle()
 index=next(i for i,a in enumerate(p.result['actions'])if a['raw']['actionType']=='SPAWN');p.actions.setCurrentRow(index);settle();key=p.action_key;require(key==p.actions.item(index).data(Qt.ItemDataRole.UserRole),'exact_source_action_key');require('配置数量：'in p.actions.item(index).text(),'quantity_in_actual_list');require('间隔：'in p.actions.item(index).text(),'interval_in_actual_list');require('开场后的出怪时刻：待核对。'in p.action_player.toPlainText(),'short_timing_status');save('spawn-records-wide')
 for width,height in((900,600),(600,600)):
  host.resize(width,height);settle();require(p.wave_scroll.horizontalScrollBar().maximum()==0,'no_outer_horizontal_scroll_'+str(width));require(p.action_player.viewport().visibleRegion().boundingRect().height()==p.action_player.viewport().height(),'whole_spawn_body_visible_'+str(width));require(p.action_player.viewport().height()>=4*p.action_player.fontMetrics().lineSpacing(),'readable_body_'+str(width));require(p.actions.viewport().visibleRegion().boundingRect().height()==p.actions.viewport().height(),'whole_action_list_visible_'+str(width));layouts.append({'window':[width,height],'orientation':p.action_split.orientation().name,'body_visible_lines':p.action_player.viewport().height()/p.action_player.fontMetrics().lineSpacing(),'outer_horizontal_scroll':p.wave_scroll.horizontalScrollBar().maximum()});save('spawn-width-'+str(width))
 host.resize(900,600);settle();p.actions.setFocus();QTest.keyClick(p.actions,Qt.Key.Key_Return);settle();position=host.pages.currentWidget();require(position is not page and position.source_parent is page,'keyboard_opens_same_host_map');require(position.panel.action_key==key and position.panel.stage_id==p.stage_id,'keyboard_uses_exact_action_identity');save('keyboard-to-map');require(position.panel.combo.count()>1,'declared_positions_available');position.panel.combo.setCurrentIndex(1);settle();require(position.panel.grid.selected is not None,'grid_marks_selected_position');save('selected-map-position');click(host.back);require(host.pages.currentWidget()is page and p.action_key==key,'back_keeps_action_and_page')
 p.actions.scrollToItem(p.actions.currentItem());settle();QTest.mouseDClick(p.actions.viewport(),Qt.MouseButton.LeftButton,pos=p.actions.visualItemRect(p.actions.currentItem()).center());settle();require(host.pages.currentWidget()is position,'double_click_reuses_exact_map_page');click(host.back)
 cursor=p.action_player.textCursor();cursor.setPosition(2);cursor.setPosition(7,QTextCursor.MoveMode.KeepAnchor);p.action_player.setTextCursor(cursor);selected=cursor.selectedText();p.action_player.verticalScrollBar().setValue(4);offset=p.action_player.verticalScrollBar().value();click(p.refresh_button);require(p.action_key==key and p.action_player.textCursor().selectedText()==selected and p.action_player.verticalScrollBar().value()==offset,'refresh_keeps_selected_action_and_reading')
 click(p.details_toggle);require('这里的等待参数不能直接相加'in p.action_player.toPlainText(),'original_full_notes_available');save('spawn-complete-notes');click(p.details_toggle);require('这里的等待参数不能直接相加'not in p.action_player.toPlainText(),'short_notes_restored')
 p.queue_kind.setCurrentIndex(p.queue_kind.findData('branch'));settle();require(p.actions.count()==sum(a['queue']['kind']=='branch'for a in p.result['actions']),'branch_records_separate');require(p.action_key is None,'changed_filter_no_auto_selection');save('conditional-records');p.queue_kind.setCurrentIndex(0);p.action_focus.setCurrentIndex(p.action_focus.findData('enemy'));settle();require(p.actions.count()==0 and'请先选择敌人'in p.action_filter_notice.text(),'enemy_filter_requires_selected_identity')
 require(window.run.state==before,'run_memory_unchanged');require(not errors,'no_Qt_slot_errors');require(not window.isVisible(),'no_duplicate_main_window');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixed_sources_only':True},indent=2)+'\n','utf8');(out/'layout.json').write_text(json.dumps(layouts,indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(470,out/'window.json'))

