from pathlib import Path
import sys,subprocess,json,runpy
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/maintenance/spawn-reading-20261101/native-final'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code},flush=True);raise SystemExit(code)
from unittest.mock import patch
from hashlib import sha256
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from rouge import player_acceptance,current_battle_reference as model
import player_ui_verification as ui
original_run=ui.run
def run(section,receipt):
 original=player_acceptance.check
 def check(section,window,gui,require):
  original(section,window,gui,require)
  d=window.player_validation_target;p=d.panel;images=[];sizes=[];p.tabs.setCurrentIndex(2);d.resize(920,720);gui.processEvents();QTest.qWait(80)
  for control in(p.queue_kind,p.action_group,p.action_focus):control.setCurrentIndex(0)
  gui.processEvents()
  require(p.actions.count()==len(p.result['actions']),'spawn_original_full_candidate_rows')
  require(any(not p.actions.item(i).icon().isNull()for i in range(p.actions.count())),'spawn_real_exact_portraits_displayed')
  item=p.actions.item(1);p.actions.scrollToItem(item);gui.processEvents();QTest.mouseClick(p.actions.viewport(),Qt.MouseButton.LeftButton,pos=p.actions.visualItemRect(item).center());gui.processEvents();require(p.action_key==p.result['actions'][1]['key'],'spawn_real_click_exact_identity');require(p.action_player.toPlainText()==model.action_text(p.result['actions'][1]),'spawn_original_full_description')
  QTest.keyClick(p.actions,Qt.Key.Key_Down);gui.processEvents();require(p.action_key==p.result['actions'][2]['key'],'spawn_real_keyboard_exact_identity');key=p.action_key;cursor=p.action_player.textCursor();cursor.setPosition(3);cursor.setPosition(18,QTextCursor.MoveMode.KeepAnchor);p.action_player.setTextCursor(cursor)
  for w,h,name in [(920,720,'spawn-wide'),(640,650,'spawn-narrow'),(1250,720,'spawn-large'),(640,650,'spawn-narrow-return')]:
   d.resize(w,h);QTest.qWait(100);gui.processEvents();vertical=p.width()<p.fontMetrics().horizontalAdvance('界')*56
   require(p.action_split.orientation()==(Qt.Orientation.Vertical if vertical else Qt.Orientation.Horizontal),'spawn_orientation_'+name);require(d.width()==w and d.height()==h,'spawn_actual_size_'+name);require(all(x>0 for x in p.action_split.sizes()),'spawn_both_reading_panes_visible_'+name);require(p.action_key==key,'spawn_selection_survives_'+name);require((p.action_player.textCursor().anchor(),p.action_player.textCursor().position())==(3,18),'spawn_full_text_selection_survives_'+name)
   path=out/(name+'.png');require(d.grab().save(str(path)),'spawn_image_'+name);images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()});sizes.append({'requested':[w,h],'actual':[d.width(),d.height()],'splitter_sizes':p.action_split.sizes(),'vertical':vertical})
  p.actions.verticalScrollBar().setValue(p.actions.verticalScrollBar().maximum()//2);gui.processEvents();offset=p.actions.verticalScrollBar().value();require(offset>0,'spawn_list_has_real_scroll');QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(p.actions.verticalScrollBar().value()==offset and p.action_key==key,'spawn_refresh_preserves_list_and_exact_choice')
  require('准确时刻：未知'in p.action_player.toPlainText(),'spawn_no_invented_actual_clock');require(p.open_action_positions(),'spawn_original_map_position_entry_opens');require(p.action_position_dialog.panel.result is not None,'spawn_original_map_reference_present');p.action_position_dialog.close()
  with patch.object(model,'stage_reference',return_value=None):require(not p.refresh_reference()and not p._enemy_icons and p.actions.count()==0,'spawn_source_loss_clears_old_pictures_and_links')
  require(p.refresh_reference()and p.action_key is None,'spawn_recovery_requires_manual_selection');(out/'spawn-images.json').write_text(json.dumps({'images':images,'sizes':sizes,'public_fixed_data_only':True,'whole_video_parity_claimed':False},indent=2)+'\n','utf8')
 with patch.object(player_acceptance,'check',check):return original_run(section,receipt)
ui.run=run
sys.argv=['scripts/verify_compact_battle_review.py','--receipt',str(out/'window.json')]
runpy.run_path(str(R/'scripts/verify_compact_battle_review.py'),run_name='__main__')
