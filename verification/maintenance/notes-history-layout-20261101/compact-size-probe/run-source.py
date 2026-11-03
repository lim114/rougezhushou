from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,sys,subprocess
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/maintenance/notes-history-layout-20261101/compact-size-probe'
if len(sys.argv)==1:
 out.mkdir()
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__)),'child'],stdout=a,stderr=b);print({'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance
from rouge.run_state import RunState
from rouge.player_replay_archive import reload_history
from tests.test_history_reader_review import history_example
from tests.test_inventory_modes_446 import observe,KETTLE,OTHER,TOOL
from player_ui_verification import run
images=[]
def check(section,w,gui,require):
 before=deepcopy(w.run.state)
 for timer in w.findChildren(QTimer):timer.stop()
 try:
  w.show_compact();bar=w.compact_window;bar.open_recent_notes();gui.processEvents();popup=bar.recent_notes_popup;p=popup.panel;e=w.player_notes
  combo=p.selector.floor;combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home);QTest.keyClick(combo,Qt.Key.Key_Down);gui.processEvents();require(p.context is not None,'compact_notes_real_floor_selection_binds_exact_context')
  require(popup.width()==900 and popup.height()==360,'compact_notes_actual_default900_by360')
  QTest.mouseClick(p.preview.viewport(),Qt.MouseButton.LeftButton,pos=QPoint(12,12));gui.processEvents();require(p.stack.currentWidget()is e,'compact_notes_same_editor_opens_from_body')
  text='第一层：先确认关卡机制。';e.editor.setPlainText(text);gui.processEvents();require(p.stack.height()<150 and e.editor.verticalScrollBar().maximum()==0,'compact_notes_short_text_fits_without_scrollbar')
  short=p.stack.height();e.editor.setPlainText('\n'.join('机制提醒'+str(i)for i in range(8)));gui.processEvents();require(p.stack.height()>short,'compact_notes_native_editor_grows_for_more_actual_lines')
  e.editor.setPlainText(text);require(e.save(),'compact_notes_explicit_save_uses_existing_temporary_store');e.editor.clearFocus();p.leave_editor();gui.processEvents();require(p.stack.currentWidget()is p.preview and p.preview.toPlainText()==text,'compact_notes_blur_returns_exact_saved_reading')
  def image(widget,name):
   gui.processEvents();f=out/(name+'.png');assert widget.grab().save(str(f));images.append({'file':f.relative_to(R).as_posix(),'sha256':sha256(f.read_bytes()).hexdigest()})
  image(popup,'plain-note')
  QTest.mouseClick(p.preview.viewport(),Qt.MouseButton.LeftButton,pos=QPoint(12,12));gui.processEvents();long='较长的中文机制提醒，需要自动换行。'*300;e.editor.setPlainText(long);popup.resize(640,420);gui.processEvents();require(e.editor.verticalScrollBar().maximum()>0 and e.editor.toPlainText()==long,'compact_notes_narrow_long_paragraph_scrolls_without_loss');require(p.card.geometry().bottom()<=p.height(),'compact_notes_narrow_card_inside_actual_window')
  e.editor.setPlainText(text);e.save();e.editor.clearFocus();p.leave_editor();gui.processEvents();bar.open_replay();gui.processEvents();history=bar.replay_popup;rp=history.panel;(out/'actual-size.json').write_text(json.dumps({'actual':[history.width(),history.height()],'minimum_hint':[history.minimumSizeHint().width(),history.minimumSizeHint().height()],'pages':[{'index':i,'title':rp.tabs.tabText(i),'minimum':[rp.tabs.widget(i).minimumSizeHint().width(),rp.tabs.widget(i).minimumSizeHint().height()]}for i in range(rp.tabs.count())]},ensure_ascii=False,indent=2),'utf8');require(history.width()==640 and history.height()==650,'compact_history_actual_default640_by650')
  state,t,ids=history_example();state['id']='public-compact-history';fixture=RunState(Path(w.run.file).parent/'public-count-fixture.json');observe(fixture,[KETTLE]*3+[OTHER,TOOL])
  for key in('relics','tactical_tools','relic_count','inventory_verified','relic_icon_memory'):state[key]=deepcopy(fixture.state[key])
  rp.history_store.archive(state);reload_history(rp);gui.processEvents();require(rp.session_cards.count()==2,'compact_history_real_temp_archive_listed_with_current_run');item=next(rp.session_cards.item(i)for i in range(rp.session_cards.count())if rp.session_cards.item(i).data(Qt.ItemDataRole.UserRole)=='archive:public-compact-history')
  require('已确认藏品 4 件'in item.text(),'compact_history_kettle_copy_count_matches_confirmed_slots');require('结算分数与种子尚未确认'in item.toolTip()and len(item.text().splitlines())==3,'compact_history_canonical_scope_retained_beside_short_card')
  image(history,'compact-session-cards');rp.session_cards.scrollToItem(item);gui.processEvents();QTest.mouseClick(rp.session_cards.viewport(),Qt.MouseButton.LeftButton,pos=rp.session_cards.visualItemRect(item).center());gui.processEvents()
  require(rp.snapshot['id']=='public-compact-history'and rp.tabs.currentWidget()is rp.nodes,'compact_history_actual_card_click_opens_exact_saved_map')
  require(rp.reading_label.isVisible()and not rp.notice.isVisible()and not rp.nodes.notice.isVisible(),'compact_history_short_source_visible_full_scope_folded')
  selected=rp.nodes.view.selected;image(history,'compact-history-map');rp.history_scope_button.setFocus();QTest.keyClick(rp.history_scope_button,Qt.Key.Key_Space);gui.processEvents();require(rp.notice.isVisible()and rp.nodes.notice.isVisible(),'compact_history_keyboard_expands_full_scope')
  bar.refresh();gui.processEvents();require(rp.nodes.view.selected==selected and rp.history_scope_button.isChecked(),'compact_history_scope_refresh_keeps_exact_prefix');image(history,'expanded-history-scope');w.player_validation_target=history
 finally:w.run.state=before
with patch.object(player_acceptance,'check',check):code=run(999,out/'window.json')
(out/'images.json').write_text(json.dumps(images,ensure_ascii=False,indent=2)+'\n','utf8');raise SystemExit(code)
