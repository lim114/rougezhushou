from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/463-material-sources/native02'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/current_ritual_view.py','rouge/player_reference_links.py','rouge/current_exchange_view.py','rouge/reference_copy.py','rouge/data/current-ritual-reference.json','rouge/data/current-exchange-reference.json'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from rouge.player_reference_notes import note_for
 from rouge.current_exchange_view import CurrentExchangePanel
 from PySide6.QtGui import QTextCursor
 from unittest.mock import patch
 before=deepcopy(window.run.state);window.player_notes.autosave.setChecked(False);images=[];layouts=[]
 window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 def settle():gui.processEvents();QTest.qWait(100);gui.processEvents()
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 content=note_for('scenes','scene_ro6_end3_1');require(content is not None,'exact_ritual_scene_note');require(c.open_saved_note(content),'note_entry');settle();note=c.recent_notes_popup;note.panel.more.setChecked(True);settle();require(window.player_notes.reference_button.isVisible(),'note_source_visible');QTest.mouseClick(window.player_notes.reference_button,Qt.MouseButton.LeftButton);settle();host=c.reference_window;handle=int(host.winId());root=host.pages.currentWidget();p=root.panel;require(p.scene_id=='scene_ro6_end3_1','note_reaches_exact_ritual_scene');require(root.source_parent is note,'note_source_chain_kept')
 def choose(sid,cid):
  p.scene.setCurrentIndex(p.scene.findData(sid));p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));settle();require(p.choice_id==cid,'selected_'+cid)
 def click_material():
  require(p.material_button.isVisible()and p.material_button.isEnabled(),'material_entry_ready_'+p.choice_id);root.body_scroll.ensureWidgetVisible(p.material_button);settle();QTest.mouseClick(p.material_button,Qt.MouseButton.LeftButton);settle();require(host.pages.currentWidget()is not root,'material_navigation_changed_page');require(int(host.winId())==handle,'material_reuses_native_host_'+p.choice_id);return host.pages.currentWidget()
 def back_root():host.navigate(host.history.index(root));settle();require(host.pages.currentWidget()is root,'back_to_ritual')
 choose('scene_ro6_end3_1','choice_ro6_end3_3');require('首次灾厄之口'in p.player.toPlainText(),'first_use_condition_kept');require('交付数量：暂无资料'in p.player.toPlainText(),'missing_amount_short_label');require(not p.reference_scope.isExpanded(),'ritual_scope_collapsed');save('ritual-material-entry')
 event=click_material();r=event.panel;require((r.event_id,r.scene_id,r.choice_id)==('tears','scene_ro6_chimera2_enter','choice_ro6_chimera2_1'),'exact_tears_source_choice');require('全部源石锭'in r.player.toPlainText(),'full_gold_cost_kept');save('material-source-event');cursor=r.player.textCursor();cursor.setPosition(2);cursor.setPosition(13,QTextCursor.MoveMode.KeepAnchor);r.player.setTextCursor(cursor);selected=cursor.selectedText();back_root();require(p.choice_id=='choice_ro6_end3_3','parent_choice_retained');require(click_material()is event,'same_event_reader_reused');require(r.player.textCursor().selectedText()==selected,'event_reader_selection_retained')
 back_root();choose('scene_ro6_end3_3','choice_ro6_end3_6');exchange=click_material();r=exchange.panel;require(isinstance(r,CurrentExchangePanel)and r.tabs.currentIndex()==1,'exchange_document_direct');require('焚毁'in r.doc_player.toPlainText(),'exchange_exact_reward_document');from PySide6.QtWidgets import QPushButton;recipe=next(b for b in exchange.header.findChildren(QPushButton)if b.text()=='查看复原条件');QTest.mouseClick(recipe,Qt.MouseButton.LeftButton);settle();require('随机消耗2件自然物'in r.doc_player.toPlainText(),'exchange_recipe_and_exact_cost');require('本局与奖励仍未知'not in r.doc_player.toPlainText()and'本局与奖励仍未知'in r.doc_technical.toPlainText(),'exchange_scope_in_details');save('material-source-exchange');r.search.setText('生命');cursor=r.doc_player.textCursor();cursor.setPosition(3);cursor.setPosition(17,QTextCursor.MoveMode.KeepAnchor);r.doc_player.setTextCursor(cursor);selected=cursor.selectedText();back_root();require(click_material()is exchange,'same_exchange_reader_reused');require(r.search.text()=='生命'and r.doc_player.textCursor().selectedText()==selected,'exchange_query_and_reading_retained')
 r.tabs.setCurrentIndex(0)
 for width,height in[(760,600),(600,500),(960,600)]:
  host.resize(width,height);settle();widgets=[r.offer,r.rarity,r.change,r.search];viewport=exchange.body_scroll.viewport();positions=[(w.mapTo(viewport,QPoint()).x(),w.mapTo(viewport,QPoint()).y(),w.width(),w.height())for w in widgets];layouts.append({'host':[host.width(),host.height()],'viewport':[viewport.width(),viewport.height()],'filters':positions});require(all(x>=0 and x+w<=viewport.width()for x,y,w,h in positions),str(width)+'_exchange_filters_fit_width');require(r.search.text()=='生命',str(width)+'_resize_keeps_query')
 save('exchange-narrow-layout')
 back_root();choose('scene_ro6_end3_4','choice_ro6_end3_9');battle=click_material();require(battle.panel.stage_id=='ro6_t_12','exact_material_source_stage');require(battle.source_parent is root,'battle_source_parent_is_ritual');require(battle.panel.result is not None,'fixed_stage_data_available');save('material-source-battle');back_root();choose('scene_ro6_end3_1','choice_ro6_end3_4');old_index=host.cursor+1;host.navigate(old_index);settle();require(host.pages.currentWidget()is root and battle not in host.history,'old_material_page_removed_after_parent_choice_change');require(not p.material_button.isEnabled(),'no_material_on_alternative_choice');require(p.material_dialog is None,'legacy_material_dialog_not_created');require(not window.isVisible(),'full_workspace_hidden');require(all(w is host or w is c or not w.isVisible()for w in gui.topLevelWidgets()),'single_reference_window_visible');require(window.run.state==before,'current_run_memory_unchanged');require(not errors,'no_Qt_slot_errors');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixed_data_only':True},indent=2)+'\n','utf8');(out/'layout.json').write_text(json.dumps(layouts,indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(463,out/'window.json'))
