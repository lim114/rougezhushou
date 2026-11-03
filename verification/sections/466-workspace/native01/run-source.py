from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/466-workspace/native01'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/app.py','rouge/player_compact.py','rouge/player_workspace.py','rouge/player_theme.py','rouge/player_reference_window.py','rouge/player_map_reader.py','rouge/current_map_position_view.py','rouge/player_map_hover.py','rouge/player_cannot_links.py','rouge/current_cannot_view.py','rouge/current_battle_view.py'];data_paths += [p.relative_to(R).as_posix()for p in(R/'rouge/data/player-theme').rglob('*')if p.is_file()];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from rouge.player_reference_notes import note_for
 from rouge.player_notes import content_key
 from PySide6.QtWidgets import QScrollArea,QPushButton
 from PySide6.QtGui import QPalette,QTextCursor
 before=deepcopy(window.run.state);app_palette=gui.palette();ws=window.workspace;question=window.question;operator=window.operator;level=window.level;skill=window.skill;images=[];layouts=[]
 window.show_compact();c=window.compact_window;host=c.reference_window
 for timer in window.findChildren(QTimer):timer.stop()
 def settle():gui.processEvents();QTest.qWait(100);gui.processEvents()
 def click(button):
  ancestor=button.parentWidget()
  while ancestor is not None and ancestor is not host:
   if isinstance(ancestor,QScrollArea):ancestor.ensureWidgetVisible(button)
   ancestor=ancestor.parentWidget()
  settle();require(button.isVisible()and button.isEnabled(),'clickable_'+button.text());QTest.mouseClick(button,Qt.MouseButton.LeftButton);settle()
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');require(host.screen().availableGeometry().contains(host.geometry()),name+'_within_screen');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 click(c.buttons['干员与技能']);page=c.workspace_popup;handle=int(host.winId());require(page is host.pages.currentWidget(),'calculator_in_shared_host');require(page.panel is ws and page.body_scroll.widget()is ws,'one_original_workspace_reparented');require(window.centralWidget()is None and not window.isVisible(),'no_duplicate_main_window');require(window.operator is operator and window.level is level and window.skill is skill,'same_calculator_controls');require(ws.currentWidget()is ws.groups['干员计算'].widget(0),'calculator_group_selected');require(host.palette().color(QPalette.ColorRole.Window).name()=='#262528','reference_palette');save('shared-operator-calculator')
 snapshot=(operator.currentData(),level.value(),skill.currentData(),window.damage_result)
 require(c.open_full(window.battle_preview),'exact_battle_target_workspace_route');settle();require(ws.currentWidget()is window.battle_preview,'exact_battle_page');require(c.open_operators(),'operator_shortcut_retains_child');require(ws.currentWidget()is window.battle_preview,'retained_target_child');save('shared-target-reference')
 click(c.buttons['聊天分析']);require(int(host.winId())==handle and host.pages.currentWidget()is page,'chat_in_same_native_host');require(window.question is question,'original_chat_editor');question.setPlainText('如何理解这个干员的技能周期？');draft=question.toPlainText();require(c.open_operators(),'back_to_operator_group');require(ws.currentWidget()is window.battle_preview,'previous_operator_tab_kept');require(c.open_chat(),'chat_return');settle();require(question.toPlainText()==draft,'unsent_chat_draft_kept');require(snapshot==(operator.currentData(),level.value(),skill.currentData(),window.damage_result),'calculation_unchanged_by_navigation');save('shared-chat-draft')
 item=window.reference_panel('relics');settle();require(ws.currentWidget()is item,'reference_panel_after_transfer');item.search.setText('支援');query=item.search.text();c.open_chat();window.reference_panel('relics');settle();require(item.search.text()==query,'reference_query_retained_after_transfer')
 content=note_for('stages','ro6_t_6');require(c.open_saved_note(content),'notebook_before_return');note_page=host.pages.currentWidget();notes=window.player_notes;notes.autosave.setChecked(False);c.recent_notes_popup.panel.more.setChecked(True);settle();click(notes.reference_button);source=host.pages.currentWidget();require(source.panel.stage_id=='ro6_t_6','exact_reference_from_note');click(source.panel.map_button)if hasattr(source.panel,'map_button')else None
 require(c.open_chat(),'workspace_return_from_fixed_reader');settle();require(host.pages.currentWidget()is page and question.toPlainText()==draft,'draft_survives_other_reference_pages');require(c.open_full(),'full_entry_reuses_same_page');require(c.workspace_popup is page,'single_workspace_page');window.show();settle();require(not window.isVisible()and host.pages.currentWidget()is page,'ordinary_show_routes_to_existing_reference_host');host.back.click();settle();require(host.pages.currentWidget()is source,'host_back_to_exact_fixed_reader');host.forward.click();settle();require(host.pages.currentWidget()is page,'host_forward_to_workspace')
 for size in((1040,720),(760,600)):
  host.resize(*size);settle();layouts.append({'window':list(size),'workspace_size':[ws.width(),ws.height()],'outer_horizontal_maximum':page.body_scroll.horizontalScrollBar().maximum(),'outer_vertical_maximum':page.body_scroll.verticalScrollBar().maximum(),'question_visible':question.isVisible()});require(question.isVisible(),'chat_accessible_'+str(size[0]));save('chat-'+str(size[0]))
 host.close();settle();require(not host.isVisible(),'reader_close');require(c.open_chat(),'reopen_chat');settle();require(host.isVisible()and question.toPlainText()==draft and c.workspace_popup is page,'reopen_keeps_chat_and_workspace');require(gui.palette()==app_palette,'application_palette_unchanged');require(window.run.state==before,'run_memory_unchanged');require(all(w is host or w is c or not w.isVisible()for w in gui.topLevelWidgets()),'one_reference_host_visible');require(not errors,'no_Qt_slot_errors');question.clear();window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_data_temporary_draft_only':True},indent=2)+'\n','utf8');(out/'layout.json').write_text(json.dumps(layouts,indent=2)+'\n','utf8')


player_acceptance.check=check
raise SystemExit(ui.run(466,out/'window.json'))
