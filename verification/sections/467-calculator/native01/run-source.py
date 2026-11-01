from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/467-calculator/native01'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/reporting.py','rouge/mechanism_reading.py','rouge/app.py','rouge/player_compact.py','rouge/player_workspace.py','rouge/player_theme.py','rouge/player_reference_window.py','rouge/player_map_reader.py','rouge/current_map_position_view.py','rouge/player_map_hover.py','rouge/player_cannot_links.py','rouge/current_cannot_view.py','rouge/current_battle_view.py'];data_paths += [p.relative_to(R).as_posix()for p in(R/'rouge/data/player-theme').rglob('*')if p.is_file()];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from PySide6.QtWidgets import QScrollArea,QPushButton
 from PySide6.QtGui import QTextCursor
 from rouge.reporting import format_report
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;host=c.reference_window;images=[];cases=[];layouts=[]
 for timer in window.findChildren(QTimer):timer.stop()
 def settle(wait=100):gui.processEvents();QTest.qWait(wait);gui.processEvents()
 def click(button):
  ancestor=button.parentWidget()
  while ancestor is not None and ancestor is not host:
   if isinstance(ancestor,QScrollArea):ancestor.ensureWidgetVisible(button)
   ancestor=ancestor.parentWidget()
  settle();require(button.isVisible()and button.isEnabled(),'clickable_'+button.text());QTest.mouseClick(button,Qt.MouseButton.LeftButton);settle(350)
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');require(host.screen().availableGeometry().contains(host.geometry()),name+'_within_screen');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 click(c.buttons['干员与技能']);page=c.workspace_popup;require(host.pages.currentWidget()is page,'same_reference_host');require(window.workspace.currentWidget()is window.damage_page,'original_calculator_page');require(not window.damage_settings_fold.isExpanded(),'settings_collapsed');require(window.operator_choices.isVisible()and window.skill.isVisible(),'direct_operator_and_skill_selectors');require(not window.level.isVisible(),'settings_hidden');require(window.damage_text.isReadOnly(),'read_only_result');save('result-first-calculator')
 for op in('kaltsit','silverash','mechanist'):
  window.select_operator(op)
  for skill in(1,2,3):
   window.skill.setCurrentIndex(window.skill.findData(skill));settle();require(window.damage_result is not None,'calculated_'+op+'_'+str(skill));r=window.damage_result;require(r['scenario']['operator']==op and r['scenario']['skill']==skill,'exact_model_'+op+'_'+str(skill));require(window.damage_text.toPlainText()==format_report(r['result']),'original_report_'+op+'_'+str(skill));require(not window.damage_settings_fold.isExpanded(),'settings_stay_closed_'+op+'_'+str(skill));cases.append({'operator':op,'skill':skill,'same_original_report':True,'unchanged_model':True});require(window.damage_form.isRowVisible(window.cooperative)==(op=='silverash'and skill==3),'scoped_silverash_option_'+op+'_'+str(skill))
 index=window.damage_sections.findText('技能时序');require(index>0,'timing_navigation_available');window.damage_sections.setCurrentIndex(index);settle();block=next(b for b in iter_blocks(window.damage_text.document())if b.text()=='【技能时序】');rect=window.damage_text.cursorRect(QTextCursor(block));require(-window.damage_text.fontMetrics().lineSpacing()<=rect.top()<window.damage_text.viewport().height(),'timing_heading_visible_after_jump');save('timing-jump')
 cursor=window.damage_text.textCursor();cursor.setPosition(2);cursor.setPosition(8,QTextCursor.MoveMode.KeepAnchor);window.damage_text.setTextCursor(cursor);selected=cursor.selectedText();scroll=window.damage_text.verticalScrollBar().value();window.render_damage();settle();require(window.damage_sections.currentText()=='技能时序'and window.damage_text.textCursor().selectedText()==selected and window.damage_text.verticalScrollBar().value()==scroll,'unchanged_refresh_retains_jump_selection_and_reading')
 click(window.damage_settings_fold.toggleButton());require(window.damage_settings_fold.isExpanded(),'settings_open');require(window.level.isVisible()and window.auto_relics.isVisible(),'original_settings_available');scroll_area=window.damage_settings_fold.content().findChild(QScrollArea);scroll_area.ensureWidgetVisible(window.level);level=window.level.value();window.level.setValue(max(1,level-1));settle();require(window.level.value()==max(1,level-1)and window.level_override,'manual_level_simulation');save('expanded-calculation-settings');click(window.damage_settings_fold.toggleButton());require(not window.damage_settings_fold.isExpanded(),'settings_close');simulation=deepcopy(window.damage_result)
 require(c.open_chat(),'other_page');require(c.open_operators(),'return_to_calculator');settle();require(window.workspace.currentWidget()is window.damage_page and window.damage_result==simulation,'same_calculator_and_simulation_retained');require(not window.damage_settings_fold.isExpanded(),'fold_state_retained')
 for op,has_fee,has_heal in(('char_151_myrtle',True,False),('char_298_susuro',False,True)):
  window.select_operator(op);window.skill.setCurrentIndex(window.skill.findData(1));settle();names=[window.damage_sections.itemText(i)for i in range(window.damage_sections.count())];require(('费用收益'in names)==has_fee and('治疗输出'in names)==has_heal,'specific_capability_'+op);save('vanguard-fee'if has_fee else'medic-healing')
 window.select_operator('mechanist');window.skill.setCurrentIndex(window.skill.findData(3));settle()
 for size in((1040,720),(760,600)):
  host.resize(*size);settle();page.body_scroll.verticalScrollBar().setValue(0);settle();visible=window.damage_text.viewport().visibleRegion().boundingRect().height();line=window.damage_text.fontMetrics().lineSpacing();require(visible>=8*line,'at_least_eight_result_lines_'+str(size[0]));require(window.skill.isVisible()and window.operator_choices.isVisible(),'selectors_visible_'+str(size[0]));layouts.append({'window':list(size),'visible_result_height':visible,'line_height':line,'visible_result_lines':visible//line});save('calculator-'+str(size[0]))
 click(window.damage_tools_fold.toggle);require(window.damage_technical.isVisible(),'technical_sources_accessible');window.raw_damage.setChecked(True);settle();require(window.damage_sections.count()==1 and window.damage_text.toPlainText().startswith('{'),'debug_replaces_result_navigation');window.raw_damage.setChecked(False);window.damage_tools_fold.toggle.setChecked(False);require(window.run.state==before,'run_state_preserved');require(not errors,'no_Qt_slot_errors');require(not window.isVisible(),'no_extra_main_window');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_profiles_temporary_state_only':True},indent=2)+'\n','utf8');(out/'layout.json').write_text(json.dumps(layouts,indent=2)+'\n','utf8');(out/'nine-skill-cases.json').write_text(json.dumps(cases,indent=2)+'\n','utf8')

def iter_blocks(document):
 block=document.firstBlock()
 while block.isValid():
  yield block;block=block.next()


player_acceptance.check=check
raise SystemExit(ui.run(467,out/'window.json'))
