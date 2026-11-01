from pathlib import Path
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/maintenance/compact-battle-window-20261101/native'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from hashlib import sha256
from copy import deepcopy
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QAbstractScrollArea
from PySide6.QtGui import QTextCursor
from rouge import player_acceptance,current_battle_reference as model
from rouge.player_map_reader import make_reader
from rouge.current_battle_view import CurrentBattleDialog
import player_ui_verification as ui
slot_errors=[]
def hook(kind,value,tb):slot_errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook
def check(section,window,gui,require):
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开资料'},c);c.present(d);gui.processEvents();QTest.qWait(60);p=d.panel;images=[];sizes=[]
 def save(name):
  path=out/(name+'.png');require(d.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 def tab(tabs,widget,label):
  index=tabs.indexOf(widget);bar=tabs.tabBar();rect=bar.tabRect(index);require(index>=0 and bar.visibleRegion().contains(rect.center()),label+'_visible_tab');QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=rect.center());gui.processEvents();require(tabs.currentWidget()is widget,label+'_actual_tab_click')
 def reach(area,widget,label):
  area.ensureWidgetVisible(widget);gui.processEvents()
  if isinstance(widget,QAbstractScrollArea):require(widget.viewport().visibleRegion().boundingRect().height()>=2*widget.fontMetrics().lineSpacing(),label+'_actual_readable_text_viewport')
  else:require(widget.visibleRegion().contains(widget.rect().center()),label+'_actual_visible_control')
 area=d.screen().availableGeometry();require((d.width(),d.height())==(min(800,area.width()-40),min(340,area.height()-40)),'compact_actual_default_size');require(p.tabs.count()==4,'compact_original_four_main_pages');require(p.result==model.stage_reference(p.stage_id),'compact_original_exact_battle_model');require(d.rect().contains(d.titleBar.closeBtn.geometry()),'compact_real_outer_close_in_client');save('compact-map-default')
 tab(p.tabs,p.enemy_scroll,'enemy');reach(p.enemy_scroll,p.enemy_combo,'enemy_choice');p.enemy_combo.setFocus();QTest.keyClick(p.enemy_combo,Qt.Key.Key_Home);QTest.keyClick(p.enemy_combo,Qt.Key.Key_Down);gui.processEvents();require(p.enemy_key is not None and p.enemy_key==p.enemy_combo.currentData(),'compact_real_keyboard_exact_enemy');reach(p.enemy_scroll,p.enemy_player,'enemy_full_text');require('【介绍与机制】'in p.enemy_player.toPlainText(),'compact_complete_enemy_mechanisms_retained');save('compact-enemy-readable')
 reach(p.enemy_scroll,p.enemy_spawns_button,'enemy_spawns');QTest.mouseClick(p.enemy_spawns_button,Qt.MouseButton.LeftButton);gui.processEvents();require(p.enemy_spawns_dialog is not None and p.enemy_spawns_dialog.isVisible()and p.enemy_spawns_dialog.panel.result is not None,'compact_actual_enemy_spawn_entry');p.enemy_spawns_dialog.close()
 tab(p.tabs,p.wave_scroll,'wave');row=next(i for i,a in enumerate(p.result['actions'])if a['raw'].get('actionType')=='SPAWN');reach(p.wave_scroll,p.actions,'action_list');item=p.actions.item(row);p.actions.scrollToItem(item);gui.processEvents();rect=p.actions.visualItemRect(item);require(p.actions.viewport().visibleRegion().contains(rect.center()),'compact_spawn_row_actually_visible');QTest.mouseClick(p.actions.viewport(),Qt.MouseButton.LeftButton,pos=rect.center());gui.processEvents();key=p.result['actions'][row]['key'];require(p.action_key==key,'compact_real_click_exact_spawn');reach(p.wave_scroll,p.action_position_button,'action_position');QTest.mouseClick(p.action_position_button,Qt.MouseButton.LeftButton);gui.processEvents();require(p.action_position_dialog is not None and p.action_position_dialog.isVisible()and p.action_position_dialog.panel.result is not None,'compact_actual_fixed_map_entry');p.action_position_dialog.close()
 tab(p.tabs,p.rewards,'rewards');r=p.rewards;tab(r.sections,r.body_scroll,'possible_rewards');target=next(x for x in r.result['rows']if x['source_action_keys']);reach(r.body_scroll,r.combo,'reward_choice');index=r.combo.findData(target['id']);r.combo.setFocus();QTest.keyClick(r.combo,Qt.Key.Key_Home)
 for _ in range(index):QTest.keyClick(r.combo,Qt.Key.Key_Down)
 gui.processEvents();require(r.row_id==target['id'],'compact_actual_keyboard_exact_reward');reach(r.body_scroll,r.source_combo,'reward_condition');r.source_combo.setFocus();QTest.keyClick(r.source_combo,Qt.Key.Key_Home);QTest.keyClick(r.source_combo,Qt.Key.Key_Down);gui.processEvents();reward_key=r.source_combo.currentData();reach(r.body_scroll,r.source_button,'reward_action_entry');QTest.mouseClick(r.source_button,Qt.MouseButton.LeftButton);gui.processEvents();require(p.tabs.currentIndex()==2 and p.action_key==reward_key,'compact_actual_reward_to_exact_original_action')
 tab(p.tabs,p.rewards,'rewards_return');tab(r.sections,p.settlement,'settlement');QTest.mouseClick(p.details_toggle,Qt.MouseButton.LeftButton);gui.processEvents();s=p.settlement;reach(s.body_scroll,s.entry,'settlement_entry');reach(s.body_scroll,s.region,'settlement_region');reach(s.body_scroll,s.player,'settlement_expanded_text');require(s.player.height()>7,'compact_no_seven_pixel_reader');require(bool(s.player.toPlainText()),'compact_complete_settlement_text_available');save('compact-settlement-readable');cursor=s.player.textCursor();cursor.setPosition(3);cursor.setPosition(18,QTextCursor.MoveMode.KeepAnchor);s.player.setTextCursor(cursor);offset=s.body_scroll.verticalScrollBar().value();old=deepcopy(s.result);QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(p.tabs.currentWidget()is r and r.sections.currentWidget()is s,'compact_refresh_keeps_nested_page');require(s.result==old and(cursor.anchor(),cursor.position())==(s.player.textCursor().anchor(),s.player.textCursor().position()),'compact_refresh_keeps_original_result_and_text_selection');require(s.body_scroll.verticalScrollBar().value()==offset,'compact_refresh_keeps_settlement_reading');require((d.width(),d.height())==(800,340),'compact_refresh_does_not_expand_default')
 QTest.mouseClick(p.source_toggle,Qt.MouseButton.LeftButton);gui.processEvents();require(p.reading_stack.currentWidget()is p.technical and json.loads(p.technical.toPlainText())==p.result,'compact_complete_raw_source_unchanged');require(p.technical.viewport().visibleRegion().boundingRect().height()>=p.technical.fontMetrics().lineSpacing()*2,'compact_raw_source_readable');QTest.mouseClick(p.source_toggle,Qt.MouseButton.LeftButton);gui.processEvents()
 for w,h in((640,360),(1040,600),(800,340)):
  d.resize(w,h);QTest.qWait(60);gui.processEvents();require((d.width(),d.height())==(w,h),'compact_actual_resize_'+str(w));require(p.tabs.currentWidget()is r and r.sections.currentWidget()is s,'compact_page_survives_resize_'+str(w));sizes.append({'requested':[w,h],'actual':[d.width(),d.height()]})
 direct=CurrentBattleDialog(p.stage_id,c);direct.show();gui.processEvents();QTest.qWait(40);require(direct.objectName()==d.objectName()and direct.size()==d.size(),'compact_direct_and_factory_same_theme_and_size');require(direct.panel.result==p.result,'compact_direct_and_factory_same_source');path=out/'compact-direct-default.png';require(direct.grab().save(str(path)),'compact_direct_image_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()});QTest.mouseClick(direct.titleBar.closeBtn,Qt.MouseButton.LeftButton);gui.processEvents();require(not direct.isVisible(),'compact_direct_normal_close')
 with patch.object(model,'stage_reference',return_value=None):require(not p.refresh_reference()and p.result is None,'compact_source_loss_clears_reference')
 require(p.refresh_reference()and p.enemy_key is None,'compact_recovery_requires_new_exact_choice');require((d.width(),d.height())==(800,340),'compact_source_recovery_keeps_user_size');require(window.run.state==before,'compact_reading_never_resets_fixture_run');require(not slot_errors,'compact_no_swallowed_Qt_slot_error');(out/'compact-images.json').write_text(json.dumps({'images':images,'sizes':sizes,'public_fixed_data_only':True,'whole_video_parity_claimed':False},indent=2)+'\n','utf8');window.player_validation_target=d
player_acceptance.check=check
raise SystemExit(ui.run(419,out/'window.json'))
