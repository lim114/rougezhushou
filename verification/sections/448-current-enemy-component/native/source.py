from pathlib import Path
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/448-current-enemy-component/native'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from rouge import player_acceptance,current_battle_reference as model
from rouge.player_map_reader import make_reader
import player_ui_verification as ui
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook
def check(section,window,gui,require):
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;images=[]
 def cfg(grade=15,zone='zone_1'):return {'difficulty':{'value':grade},'zone':{'id':zone}}
 def save(d,name):
  require(d.isVisible(),name+'_visible_at_capture');p=out/(name+'.png');require(d.grab().save(str(p)),name+'_saved');images.append({'file':p.relative_to(R).as_posix(),'sha256':sha256(p.read_bytes()).hexdigest()})
 d=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定算例'},c,config=cfg());c.present(d);d.resize(800,650);p=d.panel;p.tabs.setCurrentIndex(1);QTest.qWait(30);t=p.enemy_overview.tree;p.enemy_scroll.ensureWidgetVisible(t);gui.processEvents()
 require([i for i in range(7)if not t.isColumnHidden(i)]==list(range(7)),'current448_four_qualified_numeric_columns_visible');require(p.enemy_forecasts['0']['environment_component']=={'maxHp':12480,'atk':480,'def':200,'magicResistance':50},'current448_normal_exact_public_example');require(all(x['complete_current_total']is None for x in p.enemy_forecasts.values()),'current448_no_full_total_claim');save(d,'normal-current-table')
 p.enemy_scroll.ensureWidgetVisible(p.enemy_combo);gui.processEvents();p.enemy_combo.setFocus();QTest.keyClick(p.enemy_combo,Qt.Key.Key_Home);QTest.keyClick(p.enemy_combo,Qt.Key.Key_Down);gui.processEvents();require(p.enemy_key=='0','current448_actual_keyboard_select_exact_reference');p.enemy_scroll.ensureWidgetVisible(p.enemy_player);gui.processEvents();text=p.enemy_player.toPlainText();require(all(s in text for s in ('12,480','480','防御：200','法抗：50','完整本局面板：未知','关卡特殊规则未计入')),'current448_normal_useful_values_and_limits_in_player_text');require('env_system_new'not in text,'current448_no_internal_script_key_in_player_notes');save(d,'normal-current-detail')
 cursor=p.enemy_player.textCursor();cursor.setPosition(3);cursor.setPosition(13,QTextCursor.MoveMode.KeepAnchor);p.enemy_player.setTextCursor(cursor);p.set_context(cfg(zone='zone_2'));gui.processEvents();require(p.enemy_key=='0'and '14,976'in p.enemy_player.toPlainText(),'current448_new_conditions_update_same_selection');require(p.enemy_player.textCursor().selectedText()==cursor.selectedText(),'current448_condition_change_preserves_reading_selection');p.refresh_reference();gui.processEvents();require(p.enemy_key=='0'and '14,976'in p.enemy_player.toPlainText(),'current448_same_source_refresh_keeps_current_conditions');save(d,'region-growth-current-detail')
 with patch.object(model,'stage_reference',return_value=None):require(not p.refresh_reference(),'current448_source_loss_refuses_old_stage')
 require(p.result is None and not p.enemy_forecasts and p.enemy_key is None,'current448_source_loss_clears_numbers_selection');require(p.refresh_reference()and p.enemy_key is None,'current448_source_recovery_requires_manual_selection');require(p.enemy_choices.select_value('0'),'current448_manual_selection_after_recovery');require(p.enemy_forecasts['0']['environment_component']['maxHp']==14976,'current448_recovery_reuses_only_valid_current_conditions')
 ed=make_reader('battle',{'id':'ro6_e_2_6','title':'公开紧急算例'},c,config=cfg());c.present(ed);ed.resize(800,650);q=ed.panel;q.tabs.setCurrentIndex(1);require(q.enemy_choices.select_value('0'),'current448_exact_emergency_reference');q.enemy_scroll.ensureWidgetVisible(q.enemy_player);gui.processEvents();require(q.enemy_forecasts['0']['environment_component']=={'maxHp':18720,'atk':528,'def':240,'magicResistance':50},'current448_emergency_source_mask_applies_once');save(ed,'emergency-current-detail')
 q.set_context(cfg(16,'zone_2'));gui.processEvents();values=q.enemy_forecasts['0']['environment_component'];require(values=={'maxHp':24375,'atk':687.5,'def':240,'magicResistance':50},'current448_grade16_emergency_two_regions');require(q.enemy_key=='0'and '24,375'in q.enemy_player.toPlainText(),'current448_grade16_display_and_selection');save(ed,'grade16-current-detail')
 historical=make_reader('battle',{'id':'ro6_n_2_6','title':'历史资料'},c,historical=True,config=cfg());require(not historical.panel.run_config and not historical.panel.enemy_forecasts,'current448_history_does_not_borrow_live_conditions');historical.close();require(window.run.state==before,'current448_no_fixture_run_change');require(not errors,'current448_no_swallowed_Qt_slot_errors');(out/'images.json').write_text(json.dumps({'images':images,'public_fixed_conditions_only':True,'actual_game_panel_verified':False},indent=2)+'\n','utf8');c.present(ed);QTest.qWait(30);window.player_validation_target=ed
player_acceptance.check=check
raise SystemExit(ui.run(448,out/'window.json'))
