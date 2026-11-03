from pathlib import Path
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/449-mechanism-reading/native-current'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from copy import deepcopy
from hashlib import sha256
from importlib import import_module
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QPushButton
from rouge import player_acceptance,battle_enemy_readers as readers
from rouge.player_map_reader import make_reader
import player_ui_verification as ui
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook
def check(section,window,gui,require):
 old={r['reader']:r for r in json.loads((R/'verification/maintenance/mechanism-reading-density-20261101/reading-before.json').read_bytes())};before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;images=[];last=None
 def click(w,label):
  require(w.isEnabled()and w.visibleRegion().contains(w.rect().center()),label+'_visible_enabled');QTest.mouseClick(w,Qt.MouseButton.LeftButton);QTest.qWait(30)
 def save(dialog,name):
  require(dialog.isVisible(),name+'_visible_at_capture');path=out/(name+'.png');require(dialog.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 for name,spec in readers._READERS.items():
  model=import_module('rouge.'+spec.provider);sid=model.STAGES[0];ref=model.reference(sid);row=(ref.get('rows')or ref.get('entities'))[0];key=row['enemy_key']if name=='boss_documents'else row['key']
  d=make_reader('battle',{'id':sid,'title':'公开固定资料'},c);c.present(d);d.resize(800,600);p=d.panel;p.tabs.setCurrentIndex(1);require(p.enemy_choices.select_value(key),name+'_parent_exact_enemy');gui.processEvents();button=getattr(p,name+'_button');p.enemy_scroll.ensureWidgetVisible(button);gui.processEvents();click(button,name+'_actual_parent_entry');child=getattr(p,name+'_dialog');q=child.panel;area=child.screen().availableGeometry()
  require(child.isVisible()and child.objectName()=='mapReferenceWindow'and child.rect().contains(child.titleBar.closeBtn.geometry()),name+'_actual_owned_dark_frame');require((child.width(),child.height())==(min(760,area.width()-40),min(600,area.height()-40)),name+'_actual_compact_size');require(all(not b.autoDefault()for b in child.findChildren(QPushButton)),name+'_no_auto_default');require(q.stage_id==sid and q.result is not None and q.selected_key==key,name+'_exact_stage_entity');require(q.player.viewport().visibleRegion().boundingRect().height()>=4*q.player.fontMetrics().lineSpacing(),name+'_four_readable_lines')
  require(q.player.viewport().height()-old[name]['body_height']>=48,name+'_actual_more_first_screen_body');require(sha256(q.player.toPlainText().encode('utf8')).hexdigest()==old[name]['player_sha256']and sha256(q.technical.toPlainText().encode('utf8')).hexdigest()==old[name]['technical_sha256'],name+'_full_original_texts_unchanged');scope=q.reading_header.scope;require(not scope.isExpanded()and not q.notice.isVisible(),name+'_notice_initially_collapsed')
  q.topic.setFocus();QTest.keyClick(q.topic,Qt.Key.Key_Home)
  if q.topic.count()>1:QTest.keyClick(q.topic,Qt.Key.Key_Down)
  gui.processEvents();require(bool(q.player.toPlainText())and q.topic.currentIndex()>=0,name+'_keyboard_topic_has_real_text')
  expected={'hanko':'【完整文献参考 · 闪现】','elbert':'【火种从哪里来】','sun_boss':'【文献中的信仰、状态与阶段】','boss_documents':'【第一形态】','guest_knights':'【另一位离场时的强化】','guest_crystals':'【捕杀另一晶兽】','guest_material':'【屏障与隐匿条件】'}
  require(q.player.textCursor().block().text()==expected[name],name+'_explicit_topic_reaches_own_heading');require(q.player.viewport().rect().intersects(q.player.cursorRect()),name+'_topic_cursor_visible');require(q.tabs.tabText(1)=='原始资料（调试）'and '非本局实况'in scope.toggleButton().text(),name+'_debug_and_scope_labels')
  save(child,name+'-mechanism')
  if name=='sun_boss':
   q.topic.setCurrentIndex(q.topic.findData('skills'));q.card.setFocus();QTest.keyClick(q.card,Qt.Key.Key_Home);QTest.keyClick(q.card,Qt.Key.Key_Down);gui.processEvents();selected=model.card(q.result,key,q.card.currentData());require(q.player.textCursor().block().text()=='【完整文献原项 · '+selected['title']+'】','sun_actual_card_reaches_own_heading');save(child,'sun-skill-card')
  q.tabs.setCurrentWidget(q.technical);cursor=q.technical.textCursor();cursor.setPosition(3);cursor.setPosition(13,QTextCursor.MoveMode.KeepAnchor);q.technical.setTextCursor(cursor);expected_selection=cursor.selectedText();bar=q.technical.verticalScrollBar();bar.setValue(min(3,bar.maximum()));child.resize(800,650);QTest.qWait(20);state=(q.selected_key,q.topic.currentData(),q.tabs.currentIndex(),cursor.anchor(),cursor.position(),bar.value());click(scope.toggleButton(),name+'_scope_expand');require(scope.isExpanded()and q.notice.isVisible()and q.notice.text()==old[name]['notice'],name+'_original_notice_readable');
  if name=='hanko':save(child,'hanko-scope-expanded')
  click(q.refresh_button,name+'_refresh');require(scope.isExpanded()and q.notice.isVisible(),name+'_refresh_keeps_scope_expanded');cur=q.technical.textCursor();require((q.selected_key,q.topic.currentData(),q.tabs.currentIndex(),cur.anchor(),cur.position(),bar.value())==state,name+'_refresh_preserves_reading');require((child.width(),child.height())==(800,650),name+'_refresh_preserves_user_size')
  click(scope.toggleButton(),name+'_scope_collapse');require(not q.notice.isVisible()and q.tabs.currentWidget()is q.technical and q.technical.textCursor().selectedText()==expected_selection,name+'_collapse_keeps_reading')
  if hasattr(q,'map_button'):
   if name=='sun_boss':
    index=q.topic.findData('terrain');require(index>=0,'sun_boss_has_exact_terrain_topic');q.topic.setFocus();QTest.keyClick(q.topic,Qt.Key.Key_Home)
    for _ in range(index):QTest.keyClick(q.topic,Qt.Key.Key_Down)
    gui.processEvents();require(q.topic.currentData()=='terrain','sun_boss_real_terrain_topic_selected')
   click(q.map_button,name+'_owned_map_entry');mapwin=q.map_dialog;require(mapwin.isVisible()and mapwin.panel.stage_id==sid and mapwin.panel.result is not None,name+'_exact_fixed_map');require(mapwin.objectName()==child.objectName(),name+'_map_theme_matches')
   if name=='guest_material':save(mapwin,'guest-material-fixed-map')
   with patch.object(mapwin.panel,'clear_reference',wraps=mapwin.panel.clear_reference)as clear:click(mapwin.titleBar.closeBtn,name+'_map_close');require(clear.call_count==1 and mapwin.panel.result is None and not mapwin.isVisible(),name+'_map_clear_once')
  with patch.object(q,'clear_reference',wraps=q.clear_reference)as clear:click(child.titleBar.closeBtn,name+'_close');require(clear.call_count==1 and q.result is None and not child.isVisible(),name+'_reader_clear_once')
  # Re-open via real parent, then source mismatch closes the old reader.
  click(button,name+'_reopen');owned=getattr(p,name+'_dialog');getattr(p,'_sync_'+name)(False);gui.processEvents();require(not owned.isVisible()and owned.panel.result is None,name+'_source_change_closes_reader');last=d
 require(window.run.state==before,'mechanism_no_fixture_run_change');require(not errors,'mechanism_no_swallowed_Qt_slot_errors');(out/'images.json').write_text(json.dumps({'images':images,'public_fixed_data_only':True,'whole_video_parity_claimed':False},indent=2)+'\n','utf8');c.present(last);QTest.qWait(30);require(last.isVisible(),'mechanism_final_feature_window_restored');window.player_validation_target=last
player_acceptance.check=check
raise SystemExit(ui.run(449,out/'window.json'))
