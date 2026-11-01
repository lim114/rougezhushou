from pathlib import Path
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/maintenance/remaining-event-window-20261101/native-final'
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
from rouge import player_acceptance,current_lake
from rouge.current_sand_view import CurrentSandDialog
from rouge.current_lake_view import CurrentLakeDialog
from rouge.current_ritual_view import CurrentRitualDialog
import player_ui_verification as ui
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook
def check(section,window,gui,require):
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;d=CurrentSandDialog('curiosity',parent=c);c.present(d);QTest.qWait(30);p=d.panel;images=[];sizes=[]
 def save(dialog,name):
  path=out/(name+'.png');require(dialog.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 def current_size(dialog,name):
  area=dialog.screen().availableGeometry();require((dialog.width(),dialog.height())==(min(760,area.width()-40),min(600,area.height()-40)),name+'_actual_default_size');require(dialog.objectName()=='mapReferenceWindow'and dialog.rect().contains(dialog.titleBar.closeBtn.geometry()),name+'_shared_dark_frame_and_close')
 current_size(d,'sand');require(p.conditions.isVisible()and not p.gold.isVisible()and not any(w.isVisible()for w in p.controls.values()),'sand_default_genuinely_hides_all8_inputs');height=p.player.height();save(d,'sand-default')
 QTest.mouseClick(p.conditions.toggleButton(),Qt.MouseButton.LeftButton);QTest.qWait(30);require(p.conditions.isExpanded()and p.conditions.content().isVisible(),'sand_real_expand')
 for name,w in list(p.controls.items())+[('gold',p.gold)]:
  p.condition_scroll.ensureWidgetVisible(w);gui.processEvents();require(w.visibleRegion().contains(w.rect().center()),'sand_real_visible_'+name)
 require(p.player.viewport().height()>=4*p.player.fontMetrics().lineSpacing(),'sand_expanded_body_at_least4_lines');save(d,'sand-expanded');p.gold.setFocus();QTest.keyClick(p.gold,Qt.Key.Key_A,Qt.KeyboardModifier.ControlModifier);QTest.keyClicks(p.gold,'50');QTest.keyClick(p.gold,Qt.Key.Key_Enter);gui.processEvents();require(p.gold.value()==50 and p.result['context']['gold']==50,'sand_real_local_gold_edit')
 QTest.mouseClick(p.conditions.toggleButton(),Qt.MouseButton.LeftButton);QTest.qWait(30);require(not p.conditions.isExpanded()and not p.gold.isVisible(),'sand_real_collapse_hides_input');require(p.player.height()>=height,'sand_reflow_returns_reading_space');require(p.gold.value()==50,'sand_collapse_retains_local_input');item=p.choices.item(0);p.choices.scrollToItem(item);gui.processEvents();rect=p.choices.visualItemRect(item);require(p.choices.viewport().rect().contains(rect.center()),'sand_choice_actual_visible');QTest.mouseClick(p.choices.viewport(),Qt.MouseButton.LeftButton,pos=rect.center());gui.processEvents();require(p.choice_id==item.data(Qt.ItemDataRole.UserRole),'sand_real_exact_choice_click');cursor=p.player.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);p.player.setTextCursor(cursor);old=(p.scene_id,p.choice_id,p.player.toPlainText(),deepcopy(p.result['context']));QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);QTest.qWait(30);require((p.scene_id,p.choice_id,p.player.toPlainText(),p.result['context'])==old,'sand_refresh_retains_exact_choice_text_context');require((p.player.textCursor().anchor(),p.player.textCursor().position())==(3,15),'sand_refresh_retains_reading_selection')
 require(p.related_button.visibleRegion().contains(p.related_button.rect().center()),'sand_box_entry_actual_visible');QTest.mouseClick(p.related_button,Qt.MouseButton.LeftButton);gui.processEvents();child=p.related_dialog;require(child is not None and child.isVisible()and child.objectName()==d.objectName()and child.panel.scene_id=='scene_ro6_end2_enter','sand_actual_box_entry_same_theme_exact_source');QTest.mouseClick(d.titleBar.closeBtn,Qt.MouseButton.LeftButton);gui.processEvents();require(not d.isVisible()and not child.isVisible(),'sand_native_close_closes_owned_box')
 lake=CurrentLakeDialog(parent=c);c.present(lake);QTest.qWait(30);current_size(lake,'lake');p=lake.panel;selected=None
 for sid,scene in p.result['scenes'].items():
  for cid in scene['choice_ids']:
   choice=p.reference_model.choice_reference(p.result,sid,cid)
   if choice['documented_outcomes']:selected=(sid,cid,choice);break
  if selected:break
 require(selected is not None,'lake_original_result_pair_exists');sid,cid,choice=selected;p.scene.setCurrentIndex(p.scene.findData(sid));i=next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid);p.choices.setCurrentRow(i);gui.processEvents();require(p.outcome_buttons[0].visibleRegion().contains(p.outcome_buttons[0].rect().center()),'lake_outcome_button_visible');save(lake,'lake-results');QTest.mouseClick(p.outcome_buttons[0],Qt.MouseButton.LeftButton);gui.processEvents();require(p.scene_id==choice['documented_outcomes'][0]['scene_id'],'lake_real_outcome_button_opens_exact_documented_scene');lake.close()
 ritual=CurrentRitualDialog('ritual','scene_ro6_end3_1','choice_ro6_end3_3',c);c.present(ritual);QTest.qWait(30);current_size(ritual,'ritual');p=ritual.panel;require(p.material_button.visibleRegion().contains(p.material_button.rect().center()),'ritual_material_entry_actual_visible');save(ritual,'ritual-material');QTest.mouseClick(p.material_button,Qt.MouseButton.LeftButton);gui.processEvents();material=p.material_dialog;require(material is not None and material.isVisible()and material.objectName()==ritual.objectName()and material.panel.choice_id=='choice_ro6_chimera2_1','ritual_actual_material_exact_source_same_theme');material.close();QTest.mouseClick(p.related_button,Qt.MouseButton.LeftButton);gui.processEvents();battle=p.battle_dialog;require(battle is not None and battle.isVisible()and battle.panel.stage_id==p.result['data']['related_boss_stage_id'],'ritual_actual_related_exact_fixed_battle')
 for w,h in((640,600),(1040,700),(760,600)):
  ritual.resize(w,h);QTest.qWait(30);require((ritual.width(),ritual.height())==(w,h),'ritual_actual_resize_'+str(w));sizes.append({'requested':[w,h],'actual':[ritual.width(),ritual.height()]})
 QTest.mouseClick(ritual.titleBar.closeBtn,Qt.MouseButton.LeftButton);gui.processEvents();require(not ritual.isVisible()and not battle.isVisible(),'ritual_native_close_closes_owned_battle');d=CurrentSandDialog('curiosity',parent=c);c.present(d);QTest.qWait(30);p=d.panel
 with patch.object(p.reference_model,'reference',return_value=None):require(not p.refresh_reference()and p.result is None,'sand_source_loss_clears_result')
 require(p.refresh_reference()and p.scene_id is None and p.choice_id is None,'sand_recovery_requires_new_manual_scene');require(window.run.state==before,'event_reading_never_resets_fixture_run');require(not errors,'event_no_swallowed_Qt_slot_error');(out/'images.json').write_text(json.dumps({'images':images,'sizes':sizes,'public_fixed_data_only':True,'whole_video_parity_claimed':False},indent=2)+'\n','utf8');window.player_validation_target=d
player_acceptance.check=check
raise SystemExit(ui.run(419,out/'window.json'))
