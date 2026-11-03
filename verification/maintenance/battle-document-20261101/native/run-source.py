from pathlib import Path
import sys,subprocess,json,runpy
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/maintenance/battle-document-20261101/native'
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
  d=window.player_validation_target;p=d.panel;v=p.quick_table;t=p.enemy_overview.tree;images=[];sizes=[];p.tabs.setCurrentIndex(0);d.resize(920,720);gui.processEvents();QTest.qWait(60)
  def save(name):
   path=out/(name+'.png');require(d.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
  require(v.model()is t.model(),'document_actual_shared_Qt_model');require(v.itemDelegate()is not t.itemDelegate(),'document_independent_Qt_delegates');require(v.isVisible()and p.map_image.isVisible(),'document_map_and_mechanisms_in_same_original_page');require(p.tabs.count()==4,'document_no_new_main_category');require(p.quick_table_notice.text()==p.enemy_overview.notice.text(),'document_complete_unknown_limits_visible');p.overview_scroll.verticalScrollBar().setValue(0);gui.processEvents();save('battle-home-top')
  p.overview_scroll.ensureWidgetVisible(v);gui.processEvents();root=v.model().index(0,0);index=v.model().index(0,0,root);key=index.data(Qt.ItemDataRole.UserRole)
  require(key is not None,'document_exact_leaf_reference');require(v.isFirstColumnSpanned(0,root.parent()),'document_tier_heading_spans_all_columns');require(index.siblingAtColumn(6).data()==t.topLevelItem(0).child(0).text(6),'document_full_original_mechanisms_not_short_summary');v.scrollTo(index);gui.processEvents();save('battle-home-mechanisms')
  QTest.mouseClick(v.viewport(),Qt.MouseButton.LeftButton,pos=v.visualRect(index).center());gui.processEvents();require(p.tabs.currentIndex()==1 and p.enemy_key==key,'document_real_click_opens_exact_existing_enemy');require(key==p.enemy_combo.currentData(),'document_original_branch_choice_matches');save('battle-home-exact-enemy')
  p.tabs.setCurrentIndex(0);p.overview_scroll.ensureWidgetVisible(v);gui.processEvents();v.setCurrentIndex(index);v.setFocus();QTest.keyClick(v,Qt.Key.Key_Down);gui.processEvents();require(p.tabs.currentIndex()==0,'document_keyboard_browsing_stays_on_map');selected=v.currentIndex().siblingAtColumn(0).data(Qt.ItemDataRole.UserRole);require(selected is not None,'document_keyboard_has_exact_leaf');QTest.keyClick(v,Qt.Key.Key_Return);gui.processEvents();require(p.tabs.currentIndex()==1 and p.enemy_key==selected,'document_real_enter_opens_exact_existing_enemy')
  p.tabs.setCurrentIndex(0);v.setColumnWidth(6,500);v.doItemsLayout();v.horizontalScrollBar().setValue(25);v.setExpanded(root,False);gui.processEvents();before=(v.horizontalScrollBar().value(),v.verticalScrollBar().value(),v.currentIndex().siblingAtColumn(0).data(Qt.ItemDataRole.UserRole));QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(not v.isExpanded(v.model().index(0,0)),'document_refresh_keeps_independent_group_fold');require(t.topLevelItem(0).isExpanded(),'document_other_reader_group_remains_independent');require(v.columnWidth(6)==500,'document_refresh_keeps_manual_column_width');require((v.horizontalScrollBar().value(),v.verticalScrollBar().value(),v.currentIndex().siblingAtColumn(0).data(Qt.ItemDataRole.UserRole))==before,'document_refresh_keeps_real_reading_positions_and_leaf')
  for w,h in((640,650),(1250,720),(920,720)):
   d.resize(w,h);QTest.qWait(80);gui.processEvents();require((d.width(),d.height())==(w,h),'document_requested_window_size_'+str(w));require(p.overview_scroll.horizontalScrollBar().maximum()==0,'document_no_outer_horizontal_clip_'+str(w));p.overview_scroll.ensureWidgetVisible(v);gui.processEvents();require(v.isVisible(),'document_table_reachable_'+str(w));sizes.append({'requested':[w,h],'actual':[d.width(),d.height()]})
   if w==640:save('battle-home-640-manual-width')
  with patch.object(model,'stage_reference',return_value=None):require(not p.refresh_reference()and v.model().rowCount()==0 and not v.currentIndex().isValid(),'document_source_loss_clears_shared_rows_and_old_selection')
  require(p.refresh_reference()and p.enemy_key is None,'document_recovery_requires_manual_exact_choice');require(v.isExpanded(v.model().index(0,0)),'document_new_scope_does_not_keep_old_fold');(out/'document-images.json').write_text(json.dumps({'images':images,'sizes':sizes,'narrow_image_keeps_manual_500px_mechanism_column':True,'public_fixed_data_only':True,'whole_video_parity_claimed':False},indent=2)+'\n','utf8')
 with patch.object(player_acceptance,'check',check):return original_run(section,receipt)
ui.run=run
sys.argv=['scripts/verify_compact_battle_review.py','--receipt',str(out/'window.json')]
runpy.run_path(str(R/'scripts/verify_compact_battle_review.py'),run_name='__main__')
