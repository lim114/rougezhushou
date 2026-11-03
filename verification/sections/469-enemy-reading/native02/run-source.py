from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/469-enemy-reading/native02'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_calculation_target.py','rouge/battle_view.py','rouge/reporting.py','rouge/mechanism_reading.py','rouge/app.py','rouge/player_compact.py','rouge/player_workspace.py','rouge/player_theme.py','rouge/player_reference_window.py','rouge/player_map_reader.py','rouge/current_map_position_view.py','rouge/player_map_hover.py','rouge/player_cannot_links.py','rouge/current_cannot_view.py','rouge/current_battle_view.py','rouge/reference_copy.py','rouge/enemy_overview.py'];data_paths += [p.relative_to(R).as_posix()for p in(R/'rouge/data/player-theme').rglob('*')if p.is_file()];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from PySide6.QtWidgets import QScrollArea,QPushButton
 from PySide6.QtGui import QTextCursor
 from rouge import current_battle_reference as battle
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
 def stage(sid):
  require(c.open_full(window.battle_preview),'open_legacy_target_'+sid);window.battle_preview.set_stage(sid);require(window.open_calculation_target(source='stage'),'fixed_reference_'+sid);settle();return host.pages.currentWidget()
 page=stage('ro6_n_2_3');p=page.panel;e=p.result['enemies'][0];p.enemy_choices.select_value(e['key']);p.tabs.setCurrentIndex(1);host.resize(800,480);settle()
 require(p.enemy_key==e['key'],'exact_enemy_selected');require(not p.enemy_search_notice.isVisible(),'no_idle_search_notice');require(p.enemy_topics.count()>3,'report_topics_available');save('compact-enemy')
 for width in(800,600):
  host.resize(width,480);settle();p.enemy_scroll.verticalScrollBar().setValue(0);settle();lines=p.enemy_player.viewport().height()/p.enemy_player.fontMetrics().lineSpacing()
  require(lines>=6,'compact_body_six_lines_'+str(width));require(p.enemy_scroll.horizontalScrollBar().maximum()==0,'no_enemy_horizontal_scroll_'+str(width));require(p.enemy_topics.isVisible(),'topic_visible_'+str(width));require(p.enemy_spawns_button.isVisible(),'spawn_link_visible_'+str(width));layouts.append({'window':[width,480],'visible_body_lines':lines,'outer_horizontal_scroll':p.enemy_scroll.horizontalScrollBar().maximum()});save('enemy-width-'+str(width))
 p.enemy_topics.setFocus();QTest.keyClick(p.enemy_topics,Qt.Key.Key_End);settle();topic=p.enemy_topics.currentData();require(topic is not None,'keyboard_chose_last_topic');require(p.enemy_player.verticalScrollBar().value()>0,'topic_scrolled_actual_body');save('enemy-topic-jump')
 cursor=p.enemy_player.textCursor();cursor.setPosition(2);cursor.setPosition(6,QTextCursor.MoveMode.KeepAnchor);p.enemy_player.setTextCursor(cursor);reading=cursor.selectedText();p.enemy_player.verticalScrollBar().setValue(36);offset=p.enemy_player.verticalScrollBar().value();click(p.refresh_button);require(p.enemy_topics.currentData()==topic and p.enemy_player.textCursor().selectedText()==reading and p.enemy_player.verticalScrollBar().value()==offset,'refresh_keeps_topic_reading_and_selection')
 p.enemy_search.setText(e['name']);settle();require(p.enemy_search_notice.isVisible()and p.enemy_key==e['key'],'active_search_count_and_exact_selection');p.enemy_search.clear();settle();require(not p.enemy_search_notice.isVisible(),'clear_query_returns_space')
 click(p.details_toggle);require('适用提醒'in[p.enemy_topics.itemText(i)for i in range(p.enemy_topics.count())],'details_adds_source_topics');click(p.details_toggle);require(p.enemy_topics.findText('适用提醒')<0,'short_body_again')
 host.resize(800,620);settle();click(p.enemy_grid_toggle);require(p.enemy_grid.isVisible(),'atlas_expanded');p.enemy_grid.doItemsLayout();settle();item=p.enemy_grid.item(1);rect=p.enemy_grid.visualItemRect(item);QTest.mouseClick(p.enemy_grid.viewport(),Qt.MouseButton.LeftButton,pos=rect.center());settle();require(p.enemy_key==item.data(Qt.ItemDataRole.UserRole),'atlas_native_click_exact_enemy');require(p.enemy_topics.currentText()=='总览','changed_enemy_resets_topic');save('enemy-atlas');click(p.enemy_grid_toggle)
 click(p.enemy_spawns_button);spawn=host.pages.currentWidget();require(spawn is not page and spawn.source_parent is page,'related_spawns_same_host');save('same-host-spawns');click(host.back);require(host.pages.currentWidget()is page,'back_keeps_enemy_page')
 boss_page=stage('ro6_b_1');boss=boss_page.panel;entity=next(e for e in boss.result['enemies']if '汉科'in e['name']);boss.enemy_choices.select_value(entity['key']);boss.tabs.setCurrentIndex(1);host.resize(800,480);settle();require(boss.hanko_button.isVisible(),'specific_hanko_link_present');require(not boss.guest_crystals_button.isVisible(),'unrelated_guest_link_absent');save('boss-compact-links');click(boss.hanko_button);require(host.pages.currentWidget().source_parent is boss_page,'boss_reader_same_host');save('same-host-boss');click(host.back);require(host.pages.currentWidget()is boss_page,'back_from_boss')
 require(window.run.state==before,'run_memory_unchanged');require(not errors,'no_Qt_slot_errors');require(not window.isVisible(),'no_duplicate_original_main');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixed_sources_only':True},indent=2)+'\n','utf8');(out/'layout.json').write_text(json.dumps(layouts,indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(469,out/'window.json'))

