from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/468-target-reference/native-final'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_calculation_target.py','rouge/battle_view.py','rouge/reporting.py','rouge/mechanism_reading.py','rouge/app.py','rouge/player_compact.py','rouge/player_workspace.py','rouge/player_theme.py','rouge/player_reference_window.py','rouge/player_map_reader.py','rouge/current_map_position_view.py','rouge/player_map_hover.py','rouge/player_cannot_links.py','rouge/current_cannot_view.py','rouge/current_battle_view.py'];data_paths += [p.relative_to(R).as_posix()for p in(R/'rouge/data/player-theme').rglob('*')if p.is_file()];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from PySide6.QtWidgets import QScrollArea,QPushButton
 from PySide6.QtGui import QTextCursor
 from rouge import current_battle_reference as model
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;host=c.reference_window;images=[];layouts=[]
 for timer in window.findChildren(QTimer):timer.stop()
 def settle(wait=100):gui.processEvents();QTest.qWait(wait);gui.processEvents()
 def click(button):
  ancestor=button.parentWidget()
  while ancestor is not None and ancestor is not host:
   if isinstance(ancestor,QScrollArea):ancestor.ensureWidgetVisible(button)
   ancestor=ancestor.parentWidget()
  settle();require(button.isVisible()and button.isEnabled(),'clickable_'+button.text());QTest.mouseClick(button,Qt.MouseButton.LeftButton);settle(200)
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');require(host.screen().availableGeometry().contains(host.geometry()),name+'_within_screen');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 def target(stage):
  require(window.target_stage_choices.select_value(stage),'choose_'+stage);e=model.stage_reference(stage)['enemies'][0];require(window.target_enemy_choices.select_value({'stage_id':stage,'enemy_id':e['id'],'level':e['level']}),'choose_enemy_'+stage);return e
 require(c.open_operators(),'calculator_entry');window.calculation_scope.setCurrentIndex(window.calculation_scope.findData('archive'));e=target('ro6_n_2_3');settle();original=deepcopy(window.damage_result);handle=int(host.winId());save('calculator-target-entry');click(window.target_preview_button);page=host.pages.currentWidget();p=page.panel;require(int(host.winId())==handle and page.source_parent is c.workspace_popup,'same_native_source_host');require(p.stage_id=='ro6_n_2_3'and p.enemy_key==e['key']and p.tabs.currentIndex()==1,'exact_target_enemy_reference');require(p.run_config=={},'fixed_reference_has_own_scope');require(window.damage_result==original,'calculation_unchanged_on_open');require(p.enemy_player.viewport().visibleRegion().boundingRect().height()>=4*p.enemy_player.fontMetrics().lineSpacing(),'direct_target_enemy_text_readable');require(not p.enemy_portrait.visibleRegion().isEmpty(),'direct_target_enemy_portrait_visible');save('exact-target-enemy')
 p.tabs.setCurrentIndex(0);p.map_section.expand(animate=False);click(p.position_button);mapped=host.pages.currentWidget();require(mapped.source_parent is page,'fixed_map_from_target_chain');save('target-fixed-map');click(host.back);require(host.pages.currentWidget()is page,'back_from_fixed_map');p.tabs.setCurrentIndex(1);p.enemy_search.setText(e['name']);settle();cursor=p.enemy_player.textCursor();cursor.setPosition(2);cursor.setPosition(6,QTextCursor.MoveMode.KeepAnchor);p.enemy_player.setTextCursor(cursor);reading=cursor.selectedText();click(next(b for b in page.header.findChildren(QPushButton)if b.text()=='返回计算'));require(host.pages.currentWidget()is c.workspace_popup and window.workspace.currentWidget()is window.damage_page,'return_to_exact_calculator');require(window.damage_result==original,'calculation_unchanged_on_return');click(window.target_preview_button);require(host.pages.currentWidget()is page and p.enemy_search.text()==e['name']and p.enemy_player.textCursor().selectedText()==reading,'same_target_retains_reference_reading');click(next(b for b in page.header.findChildren(QPushButton)if b.text()=='返回计算'))
 target('ro6_n_1_1');click(window.target_preview_button);changed=host.pages.currentWidget();require(changed is not page and changed.panel.stage_id=='ro6_n_1_1','changed_target_new_reference');require(page not in host.history and mapped not in host.history,'changed_target_discards_old_descendants');save('changed-target-reference');click(next(b for b in changed.header.findChildren(QPushButton)if b.text()=='返回计算'))
 require(c.open_full(window.battle_preview),'legacy_target_page');window.battle_preview.set_stage('ro6_n_2_3');settle();calc_stage=window.target_stage.currentData();calc=deepcopy(window.damage_result);require(window.battle_preview.grid.grab().toImage().pixelColor(1,1).name()=='#262528','legacy_grid_neutral_margin');require(window.battle_preview.original.grab().toImage().pixelColor(1,1).name()=='#262528','legacy_original_neutral_margin');save('legacy-target-entry');click(window.battle_preview.current_reference_button);legacy=host.pages.currentWidget();require(legacy.panel.stage_id=='ro6_n_2_3','legacy_entry_uses_its_own_stage');require(window.target_stage.currentData()==calc_stage and window.damage_result==calc,'legacy_preview_preserves_calculation_target');save('legacy-fixed-reference');click(next(b for b in legacy.header.findChildren(QPushButton)if b.text()=='返回计算'));require(window.workspace.currentWidget()is window.damage_page,'legacy_return_goes_to_calculator')
 for size in((1040,720),(760,600)):
  host.resize(*size);settle();c.workspace_popup.body_scroll.verticalScrollBar().setValue(0);settle();v=c.workspace_popup.body_scroll.viewport();require(v.rect().contains(window.target_preview_button.mapTo(v,window.target_preview_button.rect().bottomRight())),'target_button_on_screen_'+str(size[0]));require(c.workspace_popup.body_scroll.horizontalScrollBar().maximum()==0,'no_horizontal_scroll_'+str(size[0]));layouts.append({'window':list(size),'horizontal_scroll':c.workspace_popup.body_scroll.horizontalScrollBar().maximum(),'target_button_visible':window.target_preview_button.isVisible()});save('target-entry-'+str(size[0]))
 window.target_stage_choices.select_value(None);settle();require(window.target_preview_button.isHidden(),'empty_target_hides_entry');require(not window.open_calculation_target(),'empty_target_has_no_reference');require(window.run.state==before,'run_memory_preserved');require(not errors,'no_Qt_slot_errors');require(not window.isVisible(),'no_duplicate_main_window');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_stage_and_enemy_data_only':True},indent=2)+'\n','utf8');(out/'layout.json').write_text(json.dumps(layouts,indent=2)+'\n','utf8')


player_acceptance.check=check
raise SystemExit(ui.run(468,out/'window.json'))
