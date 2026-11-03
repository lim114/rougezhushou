from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/457-note-library/native-01'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_compact.py','rouge/player_note_library.py','rouge/player_reference_window.py','rouge/player_inline_notes.py','tests/test_note_library_457.py'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from unittest.mock import patch
 from PySide6.QtCore import QObject,QEvent
 from PySide6.QtWidgets import QPushButton
 from rouge.player_reference_notes import note_for
 from rouge.player_notes import content_key
 from rouge.player_note_library import NoteLibrary
 before=deepcopy(window.run.state);notes=window.player_notes;notes.autosave.setChecked(False);contexts=[note_for('stages',sid)for sid in ['ro6_n_1_2','ro6_e_1_2']]
 for i,content in enumerate(contexts):
  require(content is not None,'exact_fixed_context_'+str(i));key=content_key(content);text='\n'.join('公开笔记 '+str(i)+' · 机关提醒 '+str(j)for j in range(180));notes.store.save(key,text,notes.store.read(key)[1]);NoteLibrary(notes.store.folder).record(content)
 window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 c.open_map();gui.processEvents();host=c.reference_window;handle=int(host.winId());images=[];trace=[]
 class Geometry(QObject):
  def eventFilter(self,obj,event):
   if event.type()in(QEvent.Type.Resize,QEvent.Type.LayoutRequest):
    p=host.pages.currentWidget();trace.append({'event':str(event.type()),'title':host.windowTitle(),'size':[host.width(),host.height()],'layout_min':[host.layout().minimumSize().width(),host.layout().minimumSize().height()],'page_hint':[p.sizeHint().width(),p.sizeHint().height()]if p else None,'window_min':[host.minimumWidth(),host.minimumHeight()]})
   return False
 observer=Geometry(host);host.installEventFilter(observer)
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 def select(content):
  p=c.note_library;p.entries.setCurrentRow(next(i for i,row in enumerate(p.rows)if row['content']==content));gui.processEvents()
 require(c.present(c.settings_popup),'settings_present');gui.processEvents();c.settings_scroll.ensureWidgetVisible(c.note_library_button);gui.processEvents();require(c.note_library_button.isVisible(),'directory_entry_visible_in_settings');QTest.mouseClick(c.note_library_button,Qt.MouseButton.LeftButton);gui.processEvents();QTest.qWait(160)
 p=c.note_library;page=c.note_library_page;require(host.pages.currentWidget()is page and p.window()is host,'directory_in_existing_main_window');require(not p.isWindow(),'directory_is_embedded_widget');require(p.entries.count()==2 and p.notice.text()=='共2条笔记','saved_notes_and_simple_count_visible');require((host.width(),host.height())==(800,430),'directory_initial_actual_size');require(p.detail.isReadOnly(),'directory_preview_read_only');select(contexts[0]);save('directory-main-window')
 p.search.setText('机关提醒');QTest.keyClick(p.search,Qt.Key.Key_Return);gui.processEvents();require(not p.search_timer.isActive()and p.entries.count()==2,'return_performs_search_without_opening_editor');select(contexts[0]);p.detail.verticalScrollBar().setValue(35);cursor=p.detail.textCursor();cursor.setPosition(4);cursor.setPosition(12,cursor.MoveMode.KeepAnchor);p.detail.setTextCursor(cursor);p.detail.verticalScrollBar().setValue(35);offset=p.detail.verticalScrollBar().value();selected=cursor.selectedText();p.split.setSizes([230,500]);sizes=p.split.sizes();require(offset>0,'long_note_scroll_is_real')
 QTest.mouseClick(p.open_button,Qt.MouseButton.LeftButton);gui.processEvents();note=c.recent_notes_popup;require(host.pages.currentWidget()is note and notes.isVisible(),'edit_action_opens_existing_inline_editor');require(notes.key==content_key(contexts[0]),'edit_keeps_exact_saved_context');note_size=[host.width(),host.height()];save('editor-in-main-window')
 button=next(x for x in note.header.findChildren(QPushButton)if x.text()=='笔记目录');require(button.isVisible(),'directory_entry_visible_on_notebook');QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is page,'notebook_directory_button_returns_to_same_page');require(p.search.text()=='机关提醒'and p.entries.currentItem().data(Qt.ItemDataRole.UserRole)==str(notes.store.path(content_key(contexts[0]))),'directory_search_and_exact_selection_retained');require(p.detail.textCursor().selectedText()==selected and p.detail.verticalScrollBar().value()==offset,'directory_text_selection_and_scroll_retained');require(p.split.sizes()==sizes,'directory_column_sizes_retained')
 QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is note,'back_returns_to_same_notebook');notes.editor.insertPlainText('本节未保存草稿');require(notes.dirty,'actual_editor_is_dirty');history=list(host.history);QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is note and host.history==history,'draft_veto_keeps_page_and_history');require(notes.dirty and '本节未保存草稿'in notes.editor.toPlainText(),'draft_stays_in_original_editor');QTest.keyClick(host,Qt.Key.Key_Escape);gui.processEvents();require(host.isVisible()and notes.dirty,'escape_preserves_dirty_editor');require(notes.save(),'draft_saved_to_temporary_note');QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is page,'saved_editor_can_open_directory')
 geometries=[]
 for width in [600,900]:
  host.resize(width,430);gui.processEvents();QTest.qWait(120);geometries.append({'requested':[width,430],'actual':[host.width(),host.height()],'panel':[p.width(),p.height()]})
  require(host.width()==width and host.height()==430,'actual_directory_geometry_'+str(width))
  require(p.detail.viewport().width()>200 and p.entries.viewport().width()>100,'both_reading_columns_available_'+str(width))
  for name,w in [('edit',p.open_button),('reference',p.reference_button),('search',p.search)]:
   rect=w.rect();top=w.mapTo(p,rect.topLeft());bottom=w.mapTo(p,rect.bottomRight());require(p.rect().contains(top)and p.rect().contains(bottom),'action_visible_'+name+'_'+str(width))
  save('directory-'+str(width))
 select(contexts[0]);notes.store.path(content_key(contexts[0])).unlink();p.refresh();require(p.entries.currentItem()is None and not p.open_button.isEnabled()and not p.reference_button.isEnabled(),'removed_file_clears_selection_and_actions');require(p.detail.toPlainText()=='选择一条本机笔记。','removed_file_clears_old_body')
 with patch.object(p.library,'rows',side_effect=OSError('测试：目录拒绝访问')):
  require(c.open_note_library(),'failed_directory_stays_readable');require(p.notice.isVisible()and p.notice.text()=='测试：目录拒绝访问','read_error_cause_visible');require(p.entries.count()==0 and not p.open_button.isEnabled(),'read_error_has_no_stale_edit_action')
 require(c.open_note_library(),'directory_recovers_after_read_error');require(p.entries.count()==1,'remaining_note_visible_after_recovery');select(contexts[1]);save('directory-recovered');require(notes.store.read(content_key(contexts[1]))[0].startswith('公开笔记 1'),'other_note_unchanged')
 require(int(host.winId())==handle,'one_native_host_for_directory_and_editor');require(not errors,'no_Qt_slot_errors');require(all(w is host or w is c or not w.isVisible()for w in gui.topLevelWidgets()),'only_main_reference_and_toolbar_visible');require(window.run.state==before,'current_run_unchanged');window.player_validation_target=host
 (out/'geometry.json').write_text(json.dumps({'directory_sizes':geometries,'first_notebook_actual_size':note_size,'notebook_initial_geometry_issue451':'observed only; no new fix claimed','events':trace},ensure_ascii=False,indent=2)+'\n','utf8')
 (out/'images.json').write_text(json.dumps({'images':images,'public_temporary_notes_only':True},indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(457,out/'window.json'))
