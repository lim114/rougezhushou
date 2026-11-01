from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/460-notebook/native01'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_note_preview.py','rouge/player_note_library.py','requirements.txt','requirements-cloud.txt','pyproject.toml','rouge/data/mistune-LICENSE.txt'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from rouge.player_reference_notes import note_for
 from rouge.player_notes import content_key
 from rouge.player_note_library import NoteLibrary
 from rouge.player_note_preview import NotePreview
 from rouge.player_note_scopes import parents
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;notes=window.player_notes
 for timer in window.findChildren(QTimer):timer.stop()
 notes.autosave.setChecked(False);context=note_for('stages','ro6_b_2');key=content_key(context);images=[];observations=[]
 plain='第一波：先处理左侧敌人\n第二波：留一个技能\n高压时留意敌方技能\n回收费用后补位\n开局先看地图\n最后检查队伍'
 def save_text(text):notes.store.save(key,text,notes.store.read(key)[1]);NoteLibrary(notes.store.folder).record(context)
 def settle():gui.processEvents();QTest.qWait(140);gui.processEvents()
 def snapshot(name):
  path=out/(name+'.png');require(c.reference_window.grab().save(str(path)),name+'_snapshot');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 save_text(plain);require(c.open_saved_note(context),'open_existing_note');p=c.recent_notes_popup.panel;host=c.reference_window;handle=int(host.winId());p.request_edit();settle()
 require(p.stack.currentWidget()is p.preview,'read_mode');require(p.preview.toPlainText().splitlines()==plain.splitlines(),'all_entered_lines_preserved')
 ys=[p.preview.cursorRect(p.preview.document().find(line)).top()for line in plain.splitlines()];require(all(a<b for a,b in zip(ys,ys[1:])),'six_lines_have_distinct_visual_positions');require([host.width(),host.height()]==[900,360],'compact_default_size');snapshot('plain-reading')
 p.request_edit();settle();require(p.stack.currentWidget()is notes,'click_or_action_enters_same_editor');require(notes.editor.toPlainText()==plain,'exact_edit_source');require(notes.editor.viewport().height()>=notes.editor.fontMetrics().lineSpacing()*4,'editor_has_four_lines');snapshot('plain-editing');p.request_edit();settle()
 markdown='# 关卡提醒\n\n**先看敌方技能**\n再安排技能回转\n\n- [x] 确认关卡\n- [ ] 检查队伍\n\n| 波次 | 注意事项 |\n| --- | --- |\n| 第一波 | 先处理远程敌人 |\n\n```text\n保留示例原文\n  保留缩进\n```'
 save_text(markdown);p.refresh(force=True);settle();require(p.preview.document().begin().blockFormat().headingLevel()==1,'markdown_heading_visible');require('☑ 确认关卡'in p.preview.toPlainText()and '☐ 检查队伍'in p.preview.toPlainText(),'task_states_readable');snapshot('markdown-reading')
 parent_contexts=parents(p.context,p.selector.rows,p.selector.floor.currentData(),p.selector.node.currentData())
 require(bool(parent_contexts),'has_parent_note_scope');parent=parent_contexts[0];parent_key=content_key(parent);notes.store.save(parent_key,'上级提醒甲\n上级提醒乙',notes.store.read(parent_key)[1]);p.parent_toggle.setChecked(True);p.refresh_parents();settle();require(any(v.toPlainText().splitlines()==['上级提醒甲','上级提醒乙']for v in p.parent_views),'ancestor_preview_keeps_lines');p.parent_toggle.setChecked(False)
 long='\n'.join('第'+str(i)+'条公开提醒'for i in range(180));save_text(long);p.refresh(force=True);settle();p.preview.verticalScrollBar().setValue(160);offset=p.preview.verticalScrollBar().value();require(offset>0,'long_note_scrollable');cursor=p.preview.document().find('第12条公开提醒');p.preview.setTextCursor(cursor);offset=p.preview.verticalScrollBar().value();selected=p.preview.textCursor().selectedText();p.refresh();settle();require(p.preview.textCursor().selectedText()==selected,'refresh_keeps_selection');require(p.preview.verticalScrollBar().value()==offset,'refresh_keeps_scroll')
 for width,height in [(600,400),(1100,450),(900,360)]:
  host.resize(width,height);settle();require([host.width(),host.height()]==[width,height],str(width)+'_size_retained');require(p.preview.viewport().width()>250,str(width)+'_body_width');require(p.preview.toPlainText().splitlines()==long.splitlines(),str(width)+'_all_lines_still_present');observations.append({'requested':[width,height],'actual':[host.width(),host.height()],'preview_size':[p.preview.width(),p.preview.height()]})
 require(c.open_note_library(),'open_shared_directory');settle();lib=c.note_library
 lib.entries.setCurrentRow(next(i for i in range(lib.entries.count())if lib.entries.item(i).text().startswith(context['title'])));settle();require(isinstance(lib.detail,NotePreview),'directory_uses_same_rendering');require(lib.detail.toPlainText().splitlines()==long.splitlines(),'directory_keeps_all_lines');lib.detail.verticalScrollBar().setValue(150);offset=lib.detail.verticalScrollBar().value();lib.refresh();settle();require(lib.detail.verticalScrollBar().value()==offset,'directory_refresh_keeps_reading');snapshot('directory-reading')
 require(notes.store.read(key)[0]==long,'store_text_is_exact');require(not notes.dirty,'no_unsaved_draft_created_by_reading');require(window.run.state==before,'run_state_unchanged');require(int(host.winId())==handle,'one_native_host');require(not errors,'no_Qt_slot_errors');window.player_validation_target=host
 (out/'observations.json').write_text(json.dumps({'video_reference_seconds':[207,213],'line_y_positions':ys,'sizes':observations,'public_fixture_only':True},ensure_ascii=False,indent=2)+'\n','utf8')
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixture_only':True},ensure_ascii=False,indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(460,out/'window.json'))
