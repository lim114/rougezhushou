from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/458-note-references/native-final'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/documented_readers.py','rouge/player_note_reference.py','rouge/player_reference_notes.py','rouge/player_inline_notes.py','rouge/player_note_library.py','rouge/expansion_view.py','research/note-references-458/reader-fixtures.json','tests/test_note_references_458.py'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from unittest.mock import patch
 from rouge.player_reference_notes import note_for
 from rouge.player_notes import content_key
 from rouge.player_note_library import NoteLibrary
 from rouge import expansion_reference as fixed
 before=deepcopy(window.run.state);notes=window.player_notes;notes.autosave.setChecked(False)
 normal=note_for('stages','ro6_n_1_2');elite=note_for('stages','ro6_e_1_2');scene=note_for('scenes','scene_ro6_normal2_enter')
 for i,content in enumerate([normal,elite,scene]):
  require(content is not None,'fixed_note_context_'+str(i));key=content_key(content);text='\n'.join('公开资料笔记 '+str(i)+' · 阅读 '+str(j)for j in range(140));notes.store.save(key,text,notes.store.read(key)[1]);NoteLibrary(notes.store.folder).record(content)
 window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 c.open_note_library();gui.processEvents();host=c.reference_window;handle=int(host.winId());library=c.note_library;root=c.note_library_page;images=[]
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 def choose(content):
  require(c.open_note_library(),'directory_present_'+content['event_id']);library.entries.setCurrentRow(next(i for i,row in enumerate(library.rows)if row['content']==content));gui.processEvents();require(library.reference_button.isEnabled(),'source_action_enabled_'+content['event_id'])
 choose(elite);library.detail.verticalScrollBar().setValue(30);offset=library.detail.verticalScrollBar().value();require(offset>0,'directory_scroll_is_nonzero');QTest.mouseClick(library.reference_button,Qt.MouseButton.LeftButton);gui.processEvents();stage=host.pages.currentWidget();require(stage.source_parent is root and stage.panel.stage_id=='ro6_e_1_2','directory_opens_exact_emergency_stage_in_main');require(stage.panel.result['stage']['isElite'],'emergency_mode_preserved');require(not window.isVisible(),'full_workspace_stays_hidden');save('note-to-emergency-stage')
 QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is root and library.detail.verticalScrollBar().value()==offset,'back_retains_directory_reading');QTest.mouseClick(library.reference_button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is stage,'same_stage_page_reused')
 choose(scene);QTest.mouseClick(library.reference_button,Qt.MouseButton.LeftButton);gui.processEvents();flow_page=host.pages.currentWidget();flow=flow_page.panel;require(flow_page.source_parent is root and flow.scene_id==scene['event_id'],'note_opens_exact_complete_event_directly');require(flow.choice_id is None and flow.choices.count()==3,'complete_event_lists_choices_without_picking_one');cid=next(v['id']for v in flow.result['choices'].values()if'choice_ro6_normal2_2'in v['variant_ids']);flow.choices.setCurrentRow(next(i for i in range(flow.choices.count())if flow.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));gui.processEvents();require(flow.battle_button.isVisible()and flow.battle_button.isEnabled(),'event_battle_action_visible');save('complete-event-from-note')
 QTest.mouseClick(flow.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();config_page=host.pages.currentWidget();configs=config_page.panel;require(config_page.source_parent is flow_page and configs.result is not None,'full_event_opens_battle_configurations_in_same_host');index=next(i for i in range(configs.stages.count())if configs.stages.itemData(i)=='ro6_t_13');configs.stages.setCurrentIndex(index);gui.processEvents();require(configs.open_button.isEnabled(),'exact_fixed_configuration_can_open');QTest.mouseClick(configs.open_button,Qt.MouseButton.LeftButton);gui.processEvents();battle=host.pages.currentWidget();require(battle.source_parent is config_page and battle.panel.stage_id=='ro6_t_13','note_event_chain_reaches_correct_fixed_battle');save('event-battle-from-note')
 with patch('rouge.player_reference_notes.model.packet',return_value=None):
  require(not host.present(battle),'expired_note_source_rejected');gui.processEvents();require(host.pages.currentWidget()is root,'expired_chain_returns_to_directory');require(all(page not in host.history for page in[flow_page,config_page,battle])and not any(page in host.linked_pages.values()for page in[flow_page,config_page,battle]),'expired_event_chain_removed_from_all_navigation')
 require(notes.store.read(content_key(scene))[0].startswith('公开资料笔记 2'),'source_loss_keeps_local_note_text')
 choose(scene)
 with patch('rouge.documented_readers.reader_plan',return_value=None):QTest.mouseClick(library.reference_button,Qt.MouseButton.LeftButton)
 gui.processEvents();raw=host.pages.currentWidget();expected=fixed._plain(fixed.detail('scenes',scene['event_id'])['row']['value']['description']);require(raw.panel.identity==scene['event_id']and raw.panel.text.toPlainText()==expected,'original_scene_remains_readable_without_full_provider');save('original-scene-in-main-window');QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();QTest.mouseClick(library.reference_button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is not raw and host.pages.currentWidget().panel.scene_id==scene['event_id'],'restored_full_provider_opens_direct_event')
 require(c.open_saved_note(normal),'saved_normal_note_opens');gui.processEvents();note=c.recent_notes_popup;inline=note.panel;require(notes.content==normal,'editor_owns_normal_note');inline.request_edit();inline.select_context(elite);inline.refresh(force=True);inline.more.setChecked(True);gui.processEvents();require(inline.reference_context()==elite and notes.content==normal,'preview_and_cached_editor_are_distinct');require(notes.reference_button.isVisible(),'preview_source_action_visible');QTest.mouseClick(notes.reference_button,Qt.MouseButton.LeftButton);gui.processEvents();preview_stage=host.pages.currentWidget();require(preview_stage.panel.stage_id=='ro6_e_1_2'and preview_stage.source_parent is note,'preview_source_opens_emergency_instead_of_cached_normal');save('reading-preview-source')
 QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is note and inline.reference_context()==elite,'back_retains_preview_context');require(c.open_saved_note(normal),'normal_editor_reopened');gui.processEvents();inline.more.setChecked(True);notes.editor.insertPlainText('本节草稿');history=list(host.history);QTest.mouseClick(notes.reference_button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is note and history==host.history,'draft_blocks_reference_navigation');require(notes.dirty and '本节草稿'in notes.editor.toPlainText(),'draft_remains_in_original_note');require(notes.save(),'draft_saved_in_temporary_store');QTest.mouseClick(notes.reference_button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget().panel.stage_id=='ro6_n_1_2','saved_note_can_open_its_source');require(notes.content==normal,'source_navigation_keeps_note_ownership')
 choose(scene);before_notes={v.name:v.read_bytes()for v in notes.store.folder.iterdir()};require(window.run.state==before,'current_run_unchanged');require(before_notes,'temporary_notes_exist');require(int(host.winId())==handle,'one_native_reference_host_through_chain');require(not errors,'no_Qt_slot_errors');require(all(w is host or w is c or not w.isVisible()for w in gui.topLevelWidgets()),'only_one_reference_window_and_toolbar_visible');require(not window.isVisible(),'developer_workspace_never_opened');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_temporary_notes_only':True,'scope':'Library->exact stage; library->complete event->configuration->battle; preview source and dirty-note ownership.'},indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(458,out/'window.json'))
