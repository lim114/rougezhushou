from pathlib import Path
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/maintenance/battle-reference-chain-20261101/native-final'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QPushButton
import shiboken6
from rouge import player_acceptance,current_stage_objects as objects
from rouge.player_map_reader import make_reader
from rouge.current_event_battles_view import CurrentEventBattlesDialog
import player_ui_verification as ui
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook
def check(section,window,gui,require):
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;d=make_reader('battle',{'id':'ro6_n_1_1','title':'公开资料'},c);c.present(d);d.resize(800,600);QTest.qWait(30);p=d.panel;images=[]
 def save(dialog,name):
  path=out/(name+'.png');require(dialog.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 def click(w,label):
  require(w.isEnabled()and w.visibleRegion().contains(w.rect().center()),label+'_actually_visible_enabled');QTest.mouseClick(w,Qt.MouseButton.LeftButton);QTest.qWait(30)
 def frame(dialog,w,h,label):
  area=dialog.screen().availableGeometry();require(dialog.isVisible()and dialog.objectName()=='mapReferenceWindow'and dialog.rect().contains(dialog.titleBar.closeBtn.geometry()),label+'_dark_owned_frame');require((dialog.width(),dialog.height())==(min(w,area.width()-40),min(h,area.height()-40)),label+'_actual_size');require(all(not b.autoDefault()for b in dialog.findChildren(QPushButton)),label+'_no_unrelated_default_button')
 p.tabs.setCurrentIndex(1);gui.processEvents();t=p.enemy_overview.tree;p.enemy_scroll.ensureWidgetVisible(t);gui.processEvents();require([i for i in range(7)if not t.isColumnHidden(i)]==[0,5,6],'chain_full_enemy_view_three_usable_columns');require(t.model()is p.quick_table.model()and t.model().columnCount()==7,'chain_original_seven_fields_shared');require(t.viewport().visibleRegion().boundingRect().height()>=t.fontMetrics().lineSpacing()*2,'chain_actual_full_mechanism_viewport');save(d,'enemy-table-focused')
 p.enemy_choices.select_value('5');gui.processEvents();p.enemy_scroll.ensureWidgetVisible(p.enemy_spawns_button);gui.processEvents();click(p.enemy_spawns_button,'enemy_spawn_entry');spawn=p.enemy_spawns_dialog;frame(spawn,760,600,'spawn');s=spawn.panel;require(s.result['stage_id']=='ro6_n_1_1'and s.result['enemy_key']=='5','spawn_exact_parent_reference');s.entries.setFocus();QTest.keyClick(s.entries,Qt.Key.Key_Home);QTest.keyClick(s.entries,Qt.Key.Key_Down);gui.processEvents();entry=s.selected();require(entry is not None and s.entries.currentData()==entry['key'],'spawn_real_keyboard_exact_entry');save(spawn,'enemy-spawn-reader');click(s.position_button,'spawn_map_entry');position=p.action_position_dialog;frame(position,960,640,'spawn_position');require(position.panel.action_key==entry['key']and position.panel.stage_id==p.stage_id,'spawn_map_exact_action');save(position,'spawn-position-reader');click(position.titleBar.closeBtn,'position_close');require(not position.isVisible(),'spawn_position_normal_closed');click(spawn.titleBar.closeBtn,'spawn_close');require(not spawn.isVisible()and s.result is None,'spawn_normal_close_clears_source')
 p.tabs.setCurrentIndex(0);gui.processEvents();p.overview_scroll.ensureWidgetVisible(p.map_details.toggleButton());gui.processEvents();click(p.map_details.toggleButton(),'map_details_expand');p.overview_scroll.ensureWidgetVisible(p.stage_objects_button);gui.processEvents();click(p.stage_objects_button,'stage_objects_entry');od=p.stage_objects_dialog;frame(od,760,600,'objects');q=od.panel;q.entries.setFocus();QTest.keyClick(q.entries,Qt.Key.Key_Home);QTest.keyClick(q.entries,Qt.Key.Key_Down);gui.processEvents();row=q.selected();require(row is not None,'objects_real_keyboard_select');save(od,'stage-objects-reader');click(q.position_button,'object_position_entry');op=q.position_dialog;frame(op,960,640,'object_position');require(op.panel.key==row['key']and op.panel.result['row']['raw']['position']==row['raw']['position'],'object_position_original_declared_location');save(op,'object-position-reader')
 with patch.object(objects,'packet',return_value=None):require(not q.refresh_reference()and q.result is None,'objects_source_loss_clears_reference')
 require(not op.isVisible()and op.panel.result is None,'objects_source_loss_closes_owned_position');require(q.refresh_reference()and q.selected()is None,'objects_recovery_manual_reselection');click(od.titleBar.closeBtn,'objects_close');require(not od.isVisible(),'objects_normal_closed')
 ed=CurrentEventBattlesDialog('鸭托邦','choice_ro6_bat3_5',parent=c);c.present(ed);QTest.qWait(30);frame(ed,760,600,'event_battles');e=ed.panel;require(e.stages.currentData()is None and not e.open_button.isEnabled(),'event_no_default_battle_version');click(e.flow_button,'event_full_flow_entry');flow=e.flow_dialog;frame(flow,760,600,'event_full_flow');require(flow.panel.event_id=='鸭托邦'and flow.panel.choice_id in flow.panel.result['choices'],'event_full_flow_exact_document');save(flow,'event-full-flow-reader');click(flow.titleBar.closeBtn,'event_flow_close');require(not flow.isVisible(),'event_full_flow_normal_closed');e.stages.setFocus();QTest.keyClick(e.stages,Qt.Key.Key_Home);QTest.keyClick(e.stages,Qt.Key.Key_Down);gui.processEvents();stage=e.stages.currentData();require(stage=='ro6_e_t_3','event_real_keyboard_exact_variant');click(e.open_button,'event_battle_entry');battle=e.battle_dialog;require(battle.isVisible()and battle.objectName()==ed.objectName()and battle.panel.stage_id==stage,'event_actual_fixed_preview_exact_variant');save(ed,'event-battle-reader');cursor=e.player.textCursor();cursor.setPosition(3);cursor.setPosition(13,QTextCursor.MoveMode.KeepAnchor);e.player.setTextCursor(cursor);ed.resize(800,650);QTest.qWait(30);old=deepcopy(e.result);click(e.refresh_button,'event_refresh');require(e.result==old and e.stages.currentData()==stage and e.player.textCursor().selectedText()==cursor.selectedText(),'event_refresh_keeps_source_stage_reading');require((ed.width(),ed.height())==(800,650),'event_refresh_keeps_user_size');click(ed.titleBar.closeBtn,'event_parent_close');require(not ed.isVisible()and not shiboken6.isValid(battle)and e.battle_dialog is None,'event_native_close_deletes_owned_preview');require(window.run.state==before,'chain_no_fixture_run_change');require(not errors,'chain_no_swallowed_Qt_slot_errors');(out/'images.json').write_text(json.dumps({'images':images,'public_fixed_data_only':True,'whole_video_parity_claimed':False},indent=2)+'\n','utf8');c.present(d);QTest.qWait(30);require(d.isVisible(),'chain_final_feature_window_restored');window.player_validation_target=d
player_acceptance.check=check
raise SystemExit(ui.run(419,out/'window.json'))
