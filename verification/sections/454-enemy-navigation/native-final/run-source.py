from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/454-enemy-navigation/native-final'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['tests/test_enemy_navigation_454.py','tests/test_reference_copy_454.py'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from importlib import import_module
 from rouge import battle_enemy_readers as readers,current_boss_documents as boss
 from rouge.player_map_reader import make_reader
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 c.open_map();gui.processEvents();host=c.reference_window;handle=int(host.winId());images=[];pages=[]
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 for name,spec in readers._READERS.items():
  model=import_module('rouge.'+spec.provider);sid=model.STAGES[0];result=model.reference(sid);row=(result.get('rows')or result.get('entities'))[0];key=row['enemy_key']if name=='boss_documents'else row['key']
  root=make_reader('battle',{'id':sid,'title':result['stage_name']},c,historical=True,page_owner=c);require(root is not None,name+'_fixed_stage');root.prepare=root.panel.refresh_reference;pages.append(root);require(c.present(root),name+'_stage_present');parent=root.panel;require(parent.enemy_choices.select_value(key),name+'_exact_enemy_selected');parent.tabs.setCurrentIndex(1);gui.processEvents()
  button=getattr(parent,name+'_button');require(button.isEnabled(),name+'_mechanism_button_enabled');QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();page=host.pages.currentWidget();require(page is not root and page.source_parent is root,name+'_clicked_mechanism');require(page.window()is host and int(host.winId())==handle,name+'_same_native_window');require(getattr(parent,name+'_dialog',None)is None,name+'_no_parallel_native_dialog');require(page.panel.reading_header.scope.toggleButton().text()=='资料说明',name+'_concise_disclosure');require(not page.panel.reading_header.scope.isExpanded(),name+'_notes_initially_collapsed');require(model.NOTICE not in page.panel.player.toPlainText(),name+'_repeated_notice_removed_from_main_text');require(page.panel.notice.text().startswith(model.NOTICE),name+'_original_scope_available_in_details')
  cursor=page.panel.player.textCursor();cursor.setPosition(3);cursor.setPosition(12,cursor.MoveMode.KeepAnchor);page.panel.player.setTextCursor(cursor);reading=page.panel.player.toPlainText();selection=cursor.selectedText()
  QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is root,name+'_back_to_stage');QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is page and page.panel.player.toPlainText()==reading and page.panel.player.textCursor().selectedText()==selection,name+'_reopen_keeps_reading')
  if name=='hanko':save('mechanism-readable-in-main-window')
  if spec.map_cleanup is not None:
   QTest.mouseClick(page.panel.map_button,Qt.MouseButton.LeftButton);gui.processEvents();mapped=host.pages.currentWidget();require(mapped is not page and mapped.source_parent is page,name+'_clicked_fixed_map');require(mapped.panel.result['current_level_key']==page.panel.result['level_key'],name+'_same_exact_level');require(mapped.window()is host and int(host.winId())==handle,name+'_fixed_map_same_native_window');mapped.panel.combo.setCurrentIndex(1);tile=mapped.panel.selected
   if name=='guest_material':save('fixed-map-in-main-window')
   QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is page,name+'_map_back_to_mechanism');QTest.mouseClick(page.panel.map_button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is mapped and mapped.panel.selected==tile,name+'_fixed_map_keeps_tile')
   QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents()
  require(all(not w.isVisible()or w is host or w is c for w in gui.topLevelWidgets()),name+'_one_visible_reference_window');c.present(c.map_popup);host.discard(root,fallback=c.map_popup);gui.processEvents()
 root=make_reader('battle',{'id':'ro6_b_5','title':'关联实体测试'},c,historical=True,page_owner=c);root.prepare=root.panel.refresh_reference;c.present(root);root.panel.enemy_choices.select_value('0');root.panel.open_boss_documents();gui.processEvents();page=host.pages.currentWidget();request=next(r for r in boss.related_entities(page.panel.result,'0')if r['key']=='1');page.panel.related.setCurrentIndex(page.panel.related.findData(request));QTest.mouseClick(page.panel.related_button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is root and root.panel.enemy_key=='1'and root.panel.tabs.currentIndex()==1,'related_entity_click_returns_to_exact_enemy');require(page not in host.history,'related_enemy_old_mechanism_removed');save('related-enemy-returns-to-stage')
 c.present(c.map_popup);host.discard(root,fallback=c.map_popup);gui.processEvents();require(not host.linked_pages,'all_dependent_pages_cleaned');require(window.run.state==before,'temporary_run_unchanged');require(not errors,'no_Qt_slot_exceptions');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixtures_only':True,'scope':'Actual MainWindow shared-stage factories and seven mechanism click routes, five fixed maps, exact related-enemy return. Root map binding stays covered by section453; no fabricated catalogue binding for ro6_b_7/ro6_t_16.'},ensure_ascii=False,indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(454,out/'window.json'))
